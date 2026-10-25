"""MCP server over stdio (JSON-RPC 2.0). Implements initialize, tools/list and tools/call.

The client's token is read once from the environment at start (OPS_MCP_TOKEN). It is bound to
the server process, so one client process = one principal. Tokens are never accepted as tool arguments.
Approval is not an MCP tool: it runs in the owner's own terminal (python -m ops_mcp approve).
"""

import json
import sys
from typing import Any, Dict, Optional

from . import capabilities as caps
from .errors import OpsError
from .gateway import Gateway

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "ops-mcp", "version": "0.1.0"}


def _schema(capability: caps.Capability) -> Dict:
    properties = {}
    required = []
    for name, spec in capability.args.items():
        prop: Dict[str, Any] = {"type": "string" if spec.type == "string" else "integer",
                                "description": spec.description}
        if spec.pattern:
            prop["pattern"] = spec.pattern
        if spec.enum:
            prop["enum"] = list(spec.enum)
        if spec.minimum is not None:
            prop["minimum"] = spec.minimum
        if spec.maximum is not None:
            prop["maximum"] = spec.maximum
        properties[name] = prop
        if spec.required:
            required.append(name)
    return {"type": "object", "properties": properties, "required": required,
            "additionalProperties": False}


def tools_list() -> Dict:
    return {"tools": [
        {"name": c.name,
         "description": f"[{c.tier}] {c.description}",
         "inputSchema": _schema(c)}
        for c in caps.CAPABILITIES.values()
    ]}


class McpServer:
    def __init__(self, gateway: Gateway, token: Optional[str], client_id: str = "mcp-client"):
        self._gateway = gateway
        self._token = token
        self._client_id = client_id

    def handle(self, message: Dict) -> Optional[Dict]:
        method = message.get("method")
        msg_id = message.get("id")
        if msg_id is None:  # notification: no response
            return None
        try:
            if method == "initialize":
                return _ok(msg_id, {"protocolVersion": PROTOCOL_VERSION,
                                    "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO})
            if method == "tools/list":
                return _ok(msg_id, tools_list())
            if method == "tools/call":
                return _ok(msg_id, self._call(message.get("params") or {}))
            return _err(msg_id, -32601, f"method not found: {method}")
        except OpsError as error:
            return _ok(msg_id, _text({"error": error.code, "message": error.message}, is_error=True))
        except Exception as error:  # noqa: BLE001 - never leak a traceback to a client
            return _err(msg_id, -32603, f"internal error ({type(error).__name__})")

    def _call(self, params: Dict) -> Dict:
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        run_id = str(arguments.pop("run_id", "")) if isinstance(arguments, dict) else ""
        result = self._gateway.call(self._token, name, arguments, run_id=run_id, client_id=self._client_id)
        return _text(result)

    def serve(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except ValueError:
                response = _err(None, -32700, "parse error")
            else:
                response = self.handle(message)
            if response is not None:
                stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                stdout.flush()


def _ok(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _err(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _text(data: Dict, is_error: bool = False) -> Dict:
    out = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]}
    if is_error:
        out["isError"] = True
    return out
