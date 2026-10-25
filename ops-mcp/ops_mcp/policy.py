"""Policy engine: RBAC by role, node scope, and manual-only nodes.

Default deny. A principal is allowed a capability only when one of its roles lists it, or lists its tier.
Configuration lives in config/policy.json and config/nodes.json. It holds no credentials.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional

from .capabilities import Capability, READ, WRITE
from .identity import Principal

ALLOW = "allow"
APPROVAL = "approval"
DENY = "deny"


@dataclass(frozen=True)
class Decision:
    outcome: str  # allow | approval | deny
    reason: str


@dataclass(frozen=True)
class Role:
    name: str
    tiers: frozenset
    capabilities: frozenset
    may_approve: bool


def load_roles(raw: Mapping[str, Mapping]) -> Dict[str, Role]:
    roles = {}
    for name, spec in raw.items():
        roles[name] = Role(
            name=name,
            tiers=frozenset(spec.get("tiers", [])),
            capabilities=frozenset(spec.get("capabilities", [])),
            may_approve=bool(spec.get("may_approve", False)),
        )
    return roles


class PolicyEngine:
    def __init__(self, roles: Mapping[str, Role], nodes: Mapping[str, Mapping]):
        self._roles = dict(roles)
        self._nodes = dict(nodes)

    def role_names_known(self, names: Iterable[str]) -> tuple:
        return tuple(n for n in names if n in self._roles)

    def may_approve(self, principal: Principal) -> bool:
        return any(self._roles[r].may_approve for r in self.role_names_known(principal.roles))

    def decide(self, principal: Principal, capability: Capability, node: Optional[str]) -> Decision:
        granted = [
            self._roles[r] for r in self.role_names_known(principal.roles)
            if capability.name in self._roles[r].capabilities or capability.tier in self._roles[r].tiers
        ]
        if not granted:
            return Decision(DENY, f"no role of {principal.sub!r} grants {capability.name}")

        if capability.needs_node:
            entry = self._nodes.get(node or "")
            if entry is None:
                return Decision(DENY, f"unknown node {node!r}")
            if not entry.get("enabled", False):
                return Decision(DENY, f"node {node} is not enabled (identity or access not confirmed)")
            if capability.tier == WRITE and entry.get("manual_only", False):
                return Decision(DENY, f"node {node} is manual only (M2M_ARCHITECTURE section 6)")

        if capability.tier == WRITE:
            return Decision(APPROVAL, "write capability: approval required")
        return Decision(ALLOW, "read capability granted by role")
