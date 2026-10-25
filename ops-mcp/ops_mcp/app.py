"""Build a Gateway from configuration files. No network, no credentials."""

import json
from pathlib import Path
from typing import Dict

from .adapters.builtin import NodesAdapter, NotConfiguredAdapter, RepoKnowledgeAdapter
from .approval import ApprovalStore
from .audit import AuditLog
from .gate import SecurityGate
from .gateway import Gateway
from .identity import TokenVerifier
from .policy import PolicyEngine, load_roles

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_gateway(key: bytes, audit_path: Path, config_dir: Path = None, adr_dir: Path = None) -> Gateway:
    config_dir = config_dir or (PACKAGE_ROOT / "config")
    adr_dir = adr_dir or (REPO_ROOT / "adr")
    nodes = load_json(config_dir / "nodes.json")
    policy = load_json(config_dir / "policy.json")
    gate_config = load_json(config_dir / "gate.json")
    engine = PolicyEngine(load_roles(policy["roles"]), nodes)

    adapters = {name: NotConfiguredAdapter() for name in (
        "get_inventory", "get_system_status", "get_vm_status", "get_storage_status",
        "get_network_status", "get_gpu_status", "get_openwebui_status", "get_ollama_status",
        "get_qdrant_status", "get_models", "start_service", "stop_service", "restart_service",
        "deploy_service", "get_alerts", "get_incidents", "get_availability",
        "search_confluence", "search_jira",
    )}
    adapters["get_nodes"] = NodesAdapter(nodes)
    adapters["search_adr"] = RepoKnowledgeAdapter(adr_dir)

    audit = AuditLog(audit_path)
    return Gateway(
        verifier=TokenVerifier(key),
        policy=engine,
        approvals=ApprovalStore(journal=audit_path.parent / "approvals.jsonl"),
        audit=audit,
        adapters=adapters,
        nodes=nodes,
        gate=SecurityGate(gate_config, adr_dir),
    )
