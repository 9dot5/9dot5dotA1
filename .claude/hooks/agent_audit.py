#!/usr/bin/env python3
"""Hash-chained audit log for agent tool calls (ADR-0017).

Claude Code runs this script from its hooks:
  agent_audit.py pre     before each tool call (hook input JSON on stdin)
  agent_audit.py post    after each tool call
  agent_audit.py verify  check the hash chain of the whole log

Fails closed: without a registered AGENT_ID, or when a record cannot be written,
`pre` exits with code 2, which blocks the tool call.

The log lives outside the repository, in AGENT_AUDIT_DIR (default ~/.9dot5dotA1/audit).
Each line holds prev_hash and hash, so an edited or removed line breaks the chain.
Truncation at the end is only detectable against a head hash exported elsewhere.
"""
import datetime
import getpass
import hashlib
import json
import os
import platform
import re
import sys
import time
import urllib.request
from pathlib import Path

# Keep in step with .claude/agent-identities.json and scripts/start-agent.ps1.
ALLOWED_AGENTS = {"architect", "governance-checker", "security-reviewer", "docs-maintainer", "executor"}

GENESIS = "0" * 64
MAX_FIELD = 2000
LOCK_TIMEOUT_S = 10
LOCK_STALE_S = 30
LOG_NAME = "agent-audit.jsonl"
LOCK_NAME = "agent-audit.lock"

# Tool inputs whose content is replaced by its length, so documents and code are not copied to the log.
CONTENT_FIELDS = {"content", "new_string", "old_string", "edits"}

SECRET_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(password|passwd|pwd|token|secret|api[_-]?key|authorization)(\s*[=:]\s*|\"\s*:\s*\"?)[^\s\"',;&]+"
)
SECRET_TOKEN = re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})\b")
SECRET_URL_CREDENTIALS = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@]+:[^\s@]+@")


def audit_dir() -> Path:
    return Path(os.environ.get("AGENT_AUDIT_DIR") or os.path.expanduser("~/.9dot5dotA1/audit"))


def clip(text: str) -> str:
    if len(text) <= MAX_FIELD:
        return text
    return text[:MAX_FIELD] + f"...<truncated {len(text) - MAX_FIELD} chars>"


def redact_text(text: str) -> str:
    text = SECRET_PRIVATE_KEY.sub("<REDACTED>", text)
    text = SECRET_ASSIGNMENT.sub(lambda m: m.group(1) + m.group(2) + "<REDACTED>", text)
    text = SECRET_TOKEN.sub("<REDACTED>", text)
    text = SECRET_URL_CREDENTIALS.sub("<REDACTED>", text)
    return text


def clean(value):
    """Redact, clip and bound a value before it enters the log."""
    if isinstance(value, str):
        return clip(redact_text(value))
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return clip(redact_text(str(value)))


def tool_input_for_log(tool_input) -> dict:
    if not isinstance(tool_input, dict):
        return {"value": clean(tool_input)}
    out = {}
    for key, value in tool_input.items():
        if key in CONTENT_FIELDS:
            size = len(json.dumps(value, ensure_ascii=False)) if not isinstance(value, str) else len(value)
            out[key] = f"<{size} chars, not logged>"
        else:
            out[key] = clean(value)
    return out


def digest(record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "hash"}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FileLock:
    """Exclusive lock using O_EXCL, so concurrent hooks append in order."""

    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        deadline = time.time() + LOCK_TIMEOUT_S
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode("ascii"))
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > LOCK_STALE_S:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.time() > deadline:
                    raise TimeoutError("audit log lock is busy")
                time.sleep(0.05)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        return False


def append(record: dict) -> None:
    directory = audit_dir()
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / LOG_NAME
    with FileLock(directory / LOCK_NAME):
        prev = GENESIS
        if log.exists():
            last = ""
            with log.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        last = line
            if last:
                prev = json.loads(last)["hash"]
        record["prev_hash"] = prev
        record["hash"] = digest(record)
        with log.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def verify() -> int:
    log = audit_dir() / LOG_NAME
    if not log.exists():
        print(f"No audit log at {log}")
        return 0
    prev = GENESIS
    count = 0
    for number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        count += 1
        if record.get("prev_hash") != prev:
            print(f"BROKEN chain at line {number}: prev_hash does not match the previous record")
            return 1
        if digest(record) != record.get("hash"):
            print(f"BROKEN record at line {number}: content does not match its hash")
            return 1
        prev = record["hash"]
    print(f"OK {count} records. Head hash: {prev}")
    print("Export the head hash to monitoring to detect truncation.")
    return 0


SINK_KINDS = {"json", "elastic", "dynatrace"}
SINK_TIMEOUT_S = 5


def sink_settings() -> tuple:
    """Read the monitoring destination from the environment (set by scripts/start-agent.ps1)."""
    kind = os.environ.get("AUDIT_SINK_KIND", "")
    url = os.environ.get("AUDIT_SINK_URL", "").rstrip("/")
    token = os.environ.get("AUDIT_SINK_TOKEN", "")
    token_file = os.environ.get("AUDIT_SINK_TOKEN_FILE", "")
    if token_file:
        token = Path(token_file).read_text(encoding="utf-8").strip()
    if kind not in SINK_KINDS or not url or not token:
        raise RuntimeError("audit sink is not configured")
    return kind, url, token


def ship(record: dict) -> None:
    """Send one record to monitoring. Raises if the sink does not accept it (fail closed)."""
    kind, url, token = sink_settings()
    if kind == "json":
        body = json.dumps(record, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        )
    elif kind == "elastic":
        # Elasticsearch and OpenSearch bulk API. The record hash is the document id, so a retry cannot duplicate.
        index = os.environ.get("AUDIT_SINK_INDEX", "agent-audit")
        action = {"create": {"_index": index, "_id": record["hash"]}}
        body = (json.dumps(action) + "\n" + json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
        request = urllib.request.Request(
            f"{url}/_bulk", data=body, method="POST",
            headers={"Content-Type": "application/x-ndjson", "Authorization": f"ApiKey {token}"},
        )
    else:
        # Dynatrace log ingestion API v2. Token needs the logs.ingest scope.
        millis = int(datetime.datetime.fromisoformat(record["ts"]).timestamp() * 1000)
        entry = {
            "content": json.dumps(record, ensure_ascii=False, sort_keys=True),
            "timestamp": millis,
            "log.source": "9dot5dotA1-agent-audit",
            "agent.id": record["agent_id"],
            "audit.event": record["event"],
            "audit.hash": record["hash"],
        }
        request = urllib.request.Request(
            f"{url}/api/v2/logs/ingest", data=json.dumps([entry]).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Api-Token {token}"},
        )
    with urllib.request.urlopen(request, timeout=SINK_TIMEOUT_S) as response:
        if response.status >= 300:
            raise RuntimeError(f"sink returned HTTP {response.status}")
        if kind == "elastic":
            result = json.loads(response.read() or b"{}")
            statuses = [item.get("create", {}).get("status") for item in result.get("items", [])]
            # 409 means the record was already stored, which is the desired outcome on a retry.
            if result.get("errors") and any(s not in (201, 409) for s in statuses):
                raise RuntimeError("sink rejected the record")


def build_record(mode: str, hook: dict, agent: str) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    record = {
        "ts": now,
        "event": "tool_call_attempt" if mode == "pre" else "tool_call_result",
        "agent_id": agent,
        "session_id": hook.get("session_id"),
        "tool_name": hook.get("tool_name"),
        "tool_use_id": hook.get("tool_use_id"),
        "tool_input": tool_input_for_log(hook.get("tool_input")),
        "agent_type_reported": hook.get("agent_type") or hook.get("subagent_type"),
        "os_user": getpass.getuser(),
        "host": platform.node(),
        "cwd": hook.get("cwd"),
    }
    if mode == "post":
        response = hook.get("tool_response")
        record["is_error"] = bool(response.get("is_error")) if isinstance(response, dict) else False
    return record


def main(argv: list) -> int:
    if not argv or argv[0] not in ("pre", "post", "verify"):
        print("usage: agent_audit.py pre|post|verify", file=sys.stderr)
        return 1
    mode = argv[0]
    if mode == "verify":
        return verify()

    raw = sys.stdin.read()
    try:
        hook = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        hook = {}

    agent = os.environ.get("AGENT_ID", "")
    if agent not in ALLOWED_AGENTS:
        print(
            f"Blocked: AGENT_ID is missing or not registered ({agent!r}). "
            "Start agents with scripts/start-agent.ps1.",
            file=sys.stderr,
        )
        return 2

    try:
        record = build_record(mode, hook, agent)
        append(record)
    except Exception as error:  # noqa: BLE001 - any failure to audit must block the action
        print(f"Blocked: audit record could not be written ({type(error).__name__}).", file=sys.stderr)
        return 2

    try:
        ship(record)
    except Exception as error:  # noqa: BLE001 - an unshipped record must block the action
        print(f"Blocked: monitoring did not accept the audit record ({type(error).__name__}).", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
