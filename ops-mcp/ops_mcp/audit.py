"""Hash-chained audit log for OPS-MCP (ADR-0017 model, ADR-0029 decision 5).

Each line holds prev_hash and hash. Editing, inserting or deleting a line breaks the chain.
Writes are fenced by a lock and fsynced. A failed write raises AuditUnavailable, and the gateway
then refuses the action (fail closed).

This module is independent of .claude/hooks/agent_audit.py on purpose. Sharing code would couple
OPS-MCP to the agent hook, which is owned by a different control. The two chains use the same format.
"""

import datetime
import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple

from .errors import AuditUnavailable

GENESIS = "0" * 64


def _digest(record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "hash"}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: Path, clock: Callable[[], datetime.datetime] = None):
        self._path = Path(path)
        self._clock = clock or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def _last_hash(self) -> str:
        if not self._path.exists():
            return GENESIS
        last = ""
        with self._path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last = line
        return json.loads(last)["hash"] if last else GENESIS

    def append(self, event: str, fields: dict) -> dict:
        record = {"ts": self._clock().isoformat(timespec="seconds"), "event": event}
        record.update(fields)
        try:
            with self._lock:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                record["prev_hash"] = self._last_hash()
                record["hash"] = _digest(record)
                with self._path.open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
        except OSError as error:
            raise AuditUnavailable(f"audit record not written ({type(error).__name__})") from error
        return record

    def verify(self) -> Tuple[bool, int, str]:
        if not self._path.exists():
            return True, 0, "no audit log yet"
        prev = GENESIS
        count = 0
        for number, line in enumerate(self._path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            count += 1
            if record.get("prev_hash") != prev:
                return False, count, f"chain broken at line {number}"
            if _digest(record) != record.get("hash"):
                return False, count, f"record altered at line {number}"
            prev = record["hash"]
        return True, count, f"ok, head {prev}"
