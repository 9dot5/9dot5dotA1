"""The capability registry. The names and schemas here are the public API (docs/API.md).

A capability is the only thing a client can ask for. There is no generic command or shell capability.
Tier "read" runs directly. Tier "write" needs an approval record (ADR-0029 decision 4).
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

READ = "read"
WRITE = "write"


@dataclass(frozen=True)
class Arg:
    type: str  # "string" or "integer"
    required: bool = False
    enum: Optional[tuple] = None
    pattern: Optional[str] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    description: str = ""


@dataclass(frozen=True)
class Capability:
    name: str
    tier: str
    needs_node: bool
    description: str
    args: Dict[str, Arg] = field(default_factory=dict)


NODE_ARG = Arg("string", required=True, description="Node id from config/nodes.json")
SERVICE_ARG = Arg("string", required=True, description="Service name as documented in SERVICE_CATALOG")
DIGEST_ARG = Arg(
    "string",
    required=True,
    pattern=r"^sha256:[a-f0-9]{64}$",
    description="Image digest. Tags are refused so that a deploy is reproducible",
)
QUERY_ARG = Arg("string", required=True, description="Search text")
LIMIT_ARG = Arg("integer", minimum=1, maximum=50, description="Maximum results (default 10)")

_CAPS = [
    Capability("get_nodes", READ, False, "List the nodes known to the platform, with their enabled state."),
    Capability("get_inventory", READ, True, "Hardware and software inventory of one node.", {"node": NODE_ARG}),
    Capability("get_system_status", READ, True, "Uptime, OS and load of one node.", {"node": NODE_ARG}),
    Capability("get_vm_status", READ, True, "Virtual machines or containers on one node.", {"node": NODE_ARG}),
    Capability("get_storage_status", READ, True, "Volumes and free space on one node.", {"node": NODE_ARG}),
    Capability("get_network_status", READ, True, "Interfaces, bound ports and zone of one node.", {"node": NODE_ARG}),
    Capability("get_gpu_status", READ, True, "GPU model, memory and temperature of one node.", {"node": NODE_ARG}),
    Capability("get_openwebui_status", READ, True, "Open WebUI health on one node.", {"node": NODE_ARG}),
    Capability("get_ollama_status", READ, True, "Ollama health on one node.", {"node": NODE_ARG}),
    Capability("get_qdrant_status", READ, True, "Qdrant health on one node.", {"node": NODE_ARG}),
    Capability("get_models", READ, True, "Models loaded or available on one node.", {"node": NODE_ARG}),
    Capability("start_service", WRITE, True, "Start a documented service. Needs approval.",
               {"node": NODE_ARG, "service": SERVICE_ARG}),
    Capability("stop_service", WRITE, True, "Stop a documented service. Needs approval.",
               {"node": NODE_ARG, "service": SERVICE_ARG}),
    Capability("restart_service", WRITE, True, "Restart a documented service. Needs approval.",
               {"node": NODE_ARG, "service": SERVICE_ARG}),
    Capability("deploy_service", WRITE, True, "Deploy a service at a pinned image digest. Needs approval.",
               {"node": NODE_ARG, "service": SERVICE_ARG, "digest": DIGEST_ARG}),
    Capability("get_alerts", READ, False, "Open alerts, with owner and runbook link (MONITORING_STRATEGY).",
               {"node": Arg("string", description="Optional node filter")}),
    Capability("get_incidents", READ, False, "Open incident records by severity (INCIDENT_RESPONSE)."),
    Capability("get_availability", READ, True, "Availability of one node over a period.", {"node": NODE_ARG}),
    Capability("search_adr", READ, False, "Search ADRs in the repository by text.",
               {"query": QUERY_ARG, "limit": LIMIT_ARG}),
    Capability("search_confluence", READ, False, "Search published Confluence pages. Not configured yet.",
               {"query": QUERY_ARG, "limit": LIMIT_ARG}),
    Capability("search_jira", READ, False, "Search Jira issues. Not configured yet.",
               {"query": QUERY_ARG, "limit": LIMIT_ARG}),
]

CAPABILITIES: Dict[str, Capability] = {c.name: c for c in _CAPS}


def get(name: str) -> Optional[Capability]:
    return CAPABILITIES.get(name)
