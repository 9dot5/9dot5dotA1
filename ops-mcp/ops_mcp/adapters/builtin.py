"""Built-in adapters for version 0.1.

- NotConfiguredAdapter: answers every infrastructure capability with "not_configured". Real node
  adapters are added in later versions, one per node type, after ADR-0030 is accepted.
- NodesAdapter: returns the node registry from config (no credentials, no network access).
- RepoKnowledgeAdapter: searches ADR files in the repository (read only, adr/ folder only).
"""

import re
from pathlib import Path
from typing import Dict, Mapping, Optional

ADR_NAME = re.compile(r"^ADR-(\d{4})-.+\.md$")
STATUS_LINE = re.compile(r"^-\s*\*\*Status:\*\*\s*(.+)$")


class NotConfiguredAdapter:
    def execute(self, capability: str, node: Optional[str], args: Dict) -> Dict:
        return {"status": "not_configured", "capability": capability, "node": node,
                "detail": "no adapter is configured for this capability (ADR-0029 phase 1)"}


class NodesAdapter:
    def __init__(self, nodes: Mapping[str, Mapping]):
        self._nodes = nodes

    def execute(self, capability: str, node: Optional[str], args: Dict) -> Dict:
        listing = [
            {"id": nid, "name": spec.get("name", nid), "enabled": bool(spec.get("enabled", False)),
             "manual_only": bool(spec.get("manual_only", False)), "zone": spec.get("zone", "")}
            for nid, spec in sorted(self._nodes.items())
        ]
        return {"nodes": listing}


class RepoKnowledgeAdapter:
    def __init__(self, adr_dir: Path):
        self._dir = Path(adr_dir)

    def execute(self, capability: str, node: Optional[str], args: Dict) -> Dict:
        query = args["query"].strip().lower()
        limit = int(args.get("limit", 10))
        hits = []
        for path in sorted(self._dir.glob("ADR-*.md")):
            match = ADR_NAME.match(path.name)
            if not match:
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            title = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), path.stem)
            status = ""
            for ln in lines[:12]:
                found = STATUS_LINE.match(ln.strip())
                if found:
                    status = found.group(1).strip()
                    break
            text = "\n".join(lines)
            if query in text.lower() or query in title.lower():
                snippet = next((ln.strip() for ln in lines if query in ln.lower()), title)
                hits.append({"adr": f"ADR-{match.group(1)}", "title": title, "status": status,
                             "path": f"adr/{path.name}", "snippet": snippet[:200]})
            if len(hits) >= limit:
                break
        return {"query": args["query"], "count": len(hits), "results": hits}
