"""Approval engine for write capabilities (ADR-0029 decision 4, ADR-0010 rule 2, ADR-0032).

Rules, enforced in code:
- An approval is bound to one request hash, one requester and one approver.
- The approver must be a human holding a role with may_approve, and must not be the requester.
- An approval expires after TTL seconds and can be used once.

Every state change is two-phase: a check that changes nothing, then a journal write, then a commit.
The gateway writes its audit record between the check and the commit (R-22). If the audit write fails,
the state is unchanged and the action does not happen.

Persistence (R-23, ADR-0032): an append-only JSON Lines journal, fsynced on every change and replayed at
start. A restart keeps pending and approved requests, and keeps used ones used.
"""

import json
import os
import secrets
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

from .errors import Forbidden, InvalidRequest, StoreUnavailable
from .identity import Principal

DEFAULT_TTL_S = 15 * 60


@dataclass
class ApprovalRecord:
    request_id: str
    request_hash: str
    requester_sub: str
    capability: str
    node: Optional[str]
    created: float
    expires: float
    approver_sub: Optional[str] = None
    approved_at: Optional[float] = None
    used: bool = False


class ApprovalStore:
    def __init__(self, ttl_s: int = DEFAULT_TTL_S, clock: Callable[[], float] = time.time,
                 journal: Optional[Path] = None):
        self._ttl = ttl_s
        self._clock = clock
        self._journal_path = Path(journal) if journal is not None else None
        self._records: Dict[str, ApprovalRecord] = {}
        self._lock = threading.Lock()
        if self._journal_path is not None:
            self._replay()

    # ----- journal -------------------------------------------------------------------------

    def _write(self, entry: dict) -> None:
        if self._journal_path is None:
            return
        try:
            self._journal_path.parent.mkdir(parents=True, exist_ok=True)
            with self._journal_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as error:
            raise StoreUnavailable(f"approval journal not written ({type(error).__name__})") from error

    def _replay(self) -> None:
        if not self._journal_path.exists():
            return
        for line in self._journal_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            op = entry["op"]
            if op == "request":
                self._records[entry["request_id"]] = ApprovalRecord(
                    request_id=entry["request_id"], request_hash=entry["request_hash"],
                    requester_sub=entry["requester_sub"], capability=entry["capability"],
                    node=entry.get("node"), created=entry["created"], expires=entry["expires"])
            elif op == "approve":
                record = self._records[entry["request_id"]]
                record.approver_sub = entry["approver_sub"]
                record.approved_at = entry["at"]
            elif op == "use":
                self._records[entry["request_id"]].used = True

    # ----- request -------------------------------------------------------------------------

    def request(self, request_hash: str, requester: Principal, capability: str,
                node: Optional[str]) -> ApprovalRecord:
        now = self._clock()
        record = ApprovalRecord(
            request_id=secrets.token_urlsafe(12), request_hash=request_hash,
            requester_sub=requester.sub, capability=capability, node=node,
            created=now, expires=now + self._ttl,
        )
        with self._lock:
            self._write({"op": "request", "request_id": record.request_id, "request_hash": request_hash,
                         "requester_sub": requester.sub, "capability": capability, "node": node,
                         "created": now, "expires": record.expires})
            self._records[record.request_id] = record
        return record

    # ----- approve: check, then commit -----------------------------------------------------

    def check_approve(self, request_id: str, approver: Principal, may_approve: bool) -> ApprovalRecord:
        with self._lock:
            record = self._records.get(request_id)
            if record is None:
                raise InvalidRequest("unknown approval request")
            if approver.kind != "human":
                raise Forbidden("only a human can approve")
            if not may_approve:
                raise Forbidden("approver role cannot approve")
            if approver.sub == record.requester_sub:
                raise Forbidden("a principal cannot approve its own request")
            if record.used or record.approver_sub is not None:
                raise Forbidden("request already decided")
            if self._clock() >= record.expires:
                raise Forbidden("approval request expired")
            return record

    def commit_approve(self, request_id: str, approver_sub: str) -> ApprovalRecord:
        with self._lock:
            record = self._records[request_id]
            if record.used or record.approver_sub is not None or self._clock() >= record.expires:
                raise Forbidden("approval state changed before commit")
            at = self._clock()
            self._write({"op": "approve", "request_id": request_id, "approver_sub": approver_sub, "at": at})
            record.approver_sub = approver_sub
            record.approved_at = at
            return record

    # ----- use: find, then commit ----------------------------------------------------------

    def find_usable(self, requester: Principal, request_hash: str) -> Optional[ApprovalRecord]:
        with self._lock:
            now = self._clock()
            for record in self._records.values():
                if (record.requester_sub == requester.sub and record.request_hash == request_hash
                        and record.approver_sub is not None and not record.used and now < record.expires):
                    return record
        return None

    def commit_use(self, request_id: str) -> ApprovalRecord:
        with self._lock:
            record = self._records[request_id]
            if record.used or self._clock() >= record.expires:
                raise Forbidden("approval already used or expired")
            self._write({"op": "use", "request_id": request_id, "at": self._clock()})
            record.used = True
            return record
