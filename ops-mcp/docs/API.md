# Operations MCP API

**Owner:** Rui Silva (`9dot5`) · **Status:** Proposed · **Review by:** 2027-01-25
**Decision:** [ADR-0029](../../adr/ADR-0029-operations-mcp.md) · **Version:** 0.1.0

The API is a set of named capabilities, exposed as MCP tools (JSON-RPC 2.0 over stdio, protocol version 2024-11-05). The names, arguments and tiers below are the public contract. Changing a name or a tier is a breaking change and needs a new ADR.

## Calling convention

- Each MCP client process is bound to one principal by the token in the environment variable `OPS_MCP_TOKEN`. Tokens are never tool arguments.
- Every argument object is validated against its schema. Unknown fields are refused.
- Optional argument `run_id` (string) ties the call to a workflow or session run. It is recorded in the audit log and is not a capability argument.
- Write capabilities return `status: "approval_required"` with a `request_id` on the first call. An owner approves that request in a terminal (`python -m ops_mcp approve <request_id>`), then the same call is repeated. Each approval is used once and expires after 15 minutes.

## Result and error shapes

- Success: the capability's JSON object, as text in the MCP result.
- Refusal: `isError: true`, with `{"error": "<code>", "message": "<text>"}`. Codes: `invalid_request`, `unauthenticated`, `forbidden`, `audit_unavailable`.
- `status: "not_configured"` means the capability exists but no backend is connected in this version. It is not an error.

## Tiers

- **read**: runs directly, logged.
- **write**: needs an approval from a different human owner, bound to the exact arguments, logged before and after.
- **manual** (not a tier of any capability here): the system never executes it. The owner runs it by hand (M2M_ARCHITECTURE section 6).

## Inventory

### `get_nodes`
- Tier: read. Node required: no.
- Arguments: none.
- Returns: the node registry, with `enabled` and `manual_only` for each node.

### `get_inventory`
- Tier: read. Node required: yes.
- Arguments: `node` (string, required).
- Returns: hardware and software inventory of the node. Not configured in 0.1.

### `get_system_status`
- Tier: read. Node required: yes.
- Arguments: `node` (string, required).
- Returns: uptime, OS and load. Not configured in 0.1.

## Infrastructure

### `get_vm_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: virtual machines or containers and their state. Not configured in 0.1.

### `get_storage_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: volumes and free space. Not configured in 0.1.

### `get_network_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: interfaces, bound ports and zone. Not configured in 0.1.

## AI

### `get_gpu_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: GPU model, memory and temperature. Not configured in 0.1.

### `get_openwebui_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: Open WebUI health. Not configured in 0.1.

### `get_ollama_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: Ollama health. Not configured in 0.1.

### `get_qdrant_status`
- Tier: read. Node required: yes. Arguments: `node`. Returns: Qdrant health. Not configured in 0.1.

### `get_models`
- Tier: read. Node required: yes. Arguments: `node`. Returns: models loaded or available. Not configured in 0.1.

## Operations (write)

### `start_service`
- Tier: write. Node required: yes. Arguments: `node` (string, required), `service` (string, required, as documented in SERVICE_CATALOG).
- Returns: on first call, `approval_required`. After approval, the adapter result. Not configured in 0.1: an approved call returns `not_configured` and is still logged.

### `stop_service`
- Tier: write. Node required: yes. Arguments: `node`, `service`. Same behaviour as `start_service`.

### `restart_service`
- Tier: write. Node required: yes. Arguments: `node`, `service`. Same behaviour as `start_service`.

### `deploy_service`
- Tier: write. Node required: yes. Arguments: `node`, `service`, `digest` (string, required, format `sha256:` followed by 64 lowercase hex characters). Tags are refused.
- Returns: as `start_service`.

## Monitoring

### `get_alerts`
- Tier: read. Node required: no. Arguments: `node` (string, optional filter). Returns: open alerts with owner and runbook link (MONITORING_STRATEGY). Not configured in 0.1.

### `get_incidents`
- Tier: read. Node required: no. Arguments: none. Returns: open incident records by severity. Not configured in 0.1.

### `get_availability`
- Tier: read. Node required: yes. Arguments: `node`. Returns: availability of the node over a period. Not configured in 0.1.

## Knowledge

### `search_adr`
- Tier: read. Node required: no. Arguments: `query` (string, required, up to 200 characters), `limit` (integer, 1 to 50, optional, default 10).
- Returns: `count` and `results`. Each result has `adr`, `title`, `status`, `path` and `snippet`. Searches `adr/` in the repository only. Implemented in 0.1.

### `search_confluence`
- Tier: read. Node required: no. Arguments: `query`, `limit`. Returns: `not_configured` in 0.1.

### `search_jira`
- Tier: read. Node required: no. Arguments: `query`, `limit`. Returns: `not_configured` in 0.1.

## Versioning

The 0.1 API is unstable until ADR-0029 is accepted. After acceptance, names and tiers are stable, and new capabilities are additive.
