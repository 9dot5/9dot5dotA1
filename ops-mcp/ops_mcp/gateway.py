"""The gateway: the one path every call takes (ADR-0029 decisions 1 to 6, ADR-0032).

Order of checks for every call:
  1. capability exists and arguments match its schema (refuse otherwise)
  2. authenticate the token (refusal is audited)
  3. "attempt" record is written. If it cannot be written, nothing else happens
  4. policy decision: deny (audited), or allow, or approval required
  5. security gate: a gated capability is refused while the gate is closed (audited)
  6. write tier, in two phases (R-22):
       - no usable approval: record the request, audit it, return approval_required
       - usable approval: audit "approval_used", then mark it used
  7. execute through the adapter, then audit "result"

Every state change is preceded by its audit record. If the audit write fails, the state does not change.
"""

import hashlib
import json
from typing import Any, Dict, Mapping, Optional
import re

from . import capabilities as caps
from .approval import ApprovalStore
from .audit import AuditLog
from .errors import Forbidden, GateClosed, InvalidRequest, Unauthenticated
from .gate import is_gated
from .identity import Principal, TokenVerifier
from .policy import APPROVAL, DENY, PolicyEngine

MAX_STRING = 200


def request_hash(capability: str, node: Optional[str], args: Mapping[str, Any]) -> str:
    canonical = json.dumps({"capability": capability, "node": node, "args": args},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate(capability: caps.Capability, args: Mapping[str, Any], nodes: Mapping[str, Mapping]) -> Dict:
    unknown = set(args) - set(capability.args)
    if unknown:
        raise InvalidRequest(f"unknown argument(s): {', '.join(sorted(unknown))}")
    clean: Dict[str, Any] = {}
    for name, spec in capability.args.items():
        if name not in args:
            if spec.required:
                raise InvalidRequest(f"missing argument: {name}")
            continue
        value = args[name]
        if spec.type == "string":
            if not isinstance(value, str) or not value or len(value) > MAX_STRING:
                raise InvalidRequest(f"{name} must be a non-empty string up to {MAX_STRING} characters")
            if spec.pattern and not re.match(spec.pattern, value):
                raise InvalidRequest(f"{name} does not match the required format")
            if spec.enum and value not in spec.enum:
                raise InvalidRequest(f"{name} is not one of the allowed values")
        elif spec.type == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise InvalidRequest(f"{name} must be an integer")
            if spec.minimum is not None and value < spec.minimum:
                raise InvalidRequest(f"{name} is below {spec.minimum}")
            if spec.maximum is not None and value > spec.maximum:
                raise InvalidRequest(f"{name} is above {spec.maximum}")
        clean[name] = value
    if capability.needs_node and clean.get("node") not in nodes:
        raise InvalidRequest(f"unknown node: {clean.get('node')!r}")
    return clean


class Gateway:
    def __init__(self, verifier: TokenVerifier, policy: PolicyEngine, approvals: ApprovalStore,
                 audit: AuditLog, adapters: Mapping[str, Any], nodes: Mapping[str, Mapping], gate):
        self._verifier = verifier
        self._policy = policy
        self._approvals = approvals
        self._audit = audit
        self._adapters = dict(adapters)
        self._nodes = dict(nodes)
        self._gate = gate

    def call(self, token: Optional[str], capability_name: str, arguments: Mapping[str, Any],
             run_id: str = "", client_id: str = "") -> Dict:
        capability = caps.get(capability_name)
        if capability is None:
            raise InvalidRequest(f"unknown capability: {capability_name}")
        args = validate(capability, dict(arguments or {}), self._nodes)
        node = args.get("node")
        digest = request_hash(capability.name, node, args)

        try:
            principal = self._verifier.verify(token)
        except Unauthenticated as error:
            self._audit.append("denied", {"reason": error.message, "capability": capability.name,
                                          "node": node, "request_hash": digest, "run_id": run_id,
                                          "client_id": client_id, "actor": None})
            raise

        actor = {"sub": principal.sub, "kind": principal.kind, "roles": list(principal.roles)}
        base = {"capability": capability.name, "tier": capability.tier, "node": node,
                "request_hash": digest, "run_id": run_id, "client_id": client_id, "actor": actor}
        self._audit.append("attempt", base)

        decision = self._policy.decide(principal, capability, node)
        if decision.outcome == DENY:
            self._audit.append("denied", dict(base, reason=decision.reason))
            raise Forbidden(decision.reason)

        if is_gated(capability) and not self._gate.is_open():
            reason = "security gate is closed: no node may be contacted (ADR-0031)"
            self._audit.append("denied", dict(base, reason=reason))
            raise GateClosed(reason)

        if decision.outcome == APPROVAL:
            usable = self._approvals.find_usable(principal, digest)
            if usable is None:
                request = self._approvals.request(digest, principal, capability.name, node)
                self._audit.append("approval_requested", dict(base, approval_id=request.request_id))
                return {"status": "approval_required", "request_id": request.request_id,
                        "request_hash": digest, "expires_in_s": int(request.expires - request.created),
                        "next": "an owner approves with approve(request_id), then repeat this call"}
            self._audit.append("approval_used", dict(base, approval_id=usable.request_id,
                                                     approved_by=usable.approver_sub))
            self._approvals.commit_use(usable.request_id)
            base["approval_id"] = usable.request_id
            base["approved_by"] = usable.approver_sub

        adapter = self._adapters.get(capability.name)
        if adapter is None:
            self._audit.append("denied", dict(base, reason="no adapter registered"))
            raise Forbidden("no adapter registered for this capability")
        try:
            result = adapter.execute(capability.name, node, args)
        except Exception as error:  # noqa: BLE001 - every adapter failure is recorded, then re-raised
            self._audit.append("result", dict(base, outcome="error", error=type(error).__name__))
            raise
        self._audit.append("result", dict(base, outcome="ok", result_status=result.get("status", "ok")))
        return result

    def approve(self, token: Optional[str], request_id: str) -> Dict:
        approver: Principal = self._verifier.verify(token)
        record = self._approvals.check_approve(request_id, approver, self._policy.may_approve(approver))
        self._audit.append("approval_granted", {
            "approval_id": record.request_id, "capability": record.capability, "node": record.node,
            "request_hash": record.request_hash,
            "requester": record.requester_sub, "approver": {"sub": approver.sub, "kind": approver.kind},
        })
        self._approvals.commit_approve(record.request_id, approver.sub)
        return {"status": "approved", "request_id": record.request_id, "capability": record.capability,
                "node": record.node, "expires_at": record.expires}
