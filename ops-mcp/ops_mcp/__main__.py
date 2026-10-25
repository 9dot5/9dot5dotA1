"""Command line: serve (MCP over stdio), approve (owner only), verify (audit chain)."""

import argparse
import json
import os
import sys
from pathlib import Path

from .app import build_gateway
from .audit import AuditLog
from .errors import OpsError
from .server import McpServer

DEFAULT_AUDIT = Path(os.environ.get("OPS_MCP_AUDIT", str(Path.home() / ".ops-mcp" / "audit.jsonl")))


def _key() -> bytes:
    raw = os.environ.get("OPS_MCP_KEY", "")
    if not raw:
        raise SystemExit("OPS_MCP_KEY is not set (signing key, at least 32 bytes, from the secret broker)")
    return raw.encode("utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="ops_mcp")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="serve MCP over stdio; token from OPS_MCP_TOKEN")
    approve = sub.add_parser("approve", help="approve a pending request (owner token from OPS_MCP_TOKEN)")
    approve.add_argument("request_id")
    sub.add_parser("verify", help="check the hash chain of the audit log")
    args = parser.parse_args(argv)

    if args.command == "verify":
        ok, count, message = AuditLog(DEFAULT_AUDIT).verify()
        print(f"{'OK' if ok else 'FAILED'}: {count} records, {message}")
        return 0 if ok else 1

    gateway = build_gateway(_key(), DEFAULT_AUDIT)
    token = os.environ.get("OPS_MCP_TOKEN")
    if args.command == "approve":
        try:
            print(json.dumps(gateway.approve(token, args.request_id), indent=2))
            return 0
        except OpsError as error:
            print(f"refused: {error.code}: {error.message}", file=sys.stderr)
            return 2
    McpServer(gateway, token).serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
