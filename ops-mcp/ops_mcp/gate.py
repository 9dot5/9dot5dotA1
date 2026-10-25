"""Security gate: no node may be contacted until the governance conditions are met.

Three conditions, all required (ADR-0031 section "Gate"):
1. ADR-0029 to ADR-0033 have status Accepted. Read from the ADR files, not from configuration.
2. The threat model has been reviewed. Recorded by the owner in config/gate.json.
3. The permission matrix has been approved. Recorded by the owner in config/gate.json.

An agent cannot open the gate: the status comes from ADRs that only the owner accepts, and the two
review records are written by the owner into a file that agents may not edit (CLAUDE.md).
The gate is evaluated on every call, so closing it takes effect at once.

Capabilities that reach a node, or a monitoring source that reads from nodes, are gated.
Local capabilities (get_nodes, search_adr) and external knowledge sources are not.
"""

import json
import re
from pathlib import Path
from typing import Dict, Mapping

from .capabilities import Capability

REQUIRED_ADRS = ("ADR-0029", "ADR-0030", "ADR-0031", "ADR-0032", "ADR-0033")
GATED_WITHOUT_NODE = {"get_alerts", "get_incidents"}
ACCEPTED = re.compile(r"^-\s*\*\*Status:\*\*\s*Accepted\b", re.MULTILINE)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_gated(capability: Capability) -> bool:
    return capability.needs_node or capability.name in GATED_WITHOUT_NODE


class SecurityGate:
    def __init__(self, config: Mapping, adr_dir: Path):
        self._config = dict(config)
        self._adr_dir = Path(adr_dir)

    def _adr_accepted(self, adr: str) -> bool:
        matches = sorted(self._adr_dir.glob(f"{adr}-*.md"))
        if len(matches) != 1:
            return False
        text = matches[0].read_text(encoding="utf-8")[:1200]
        return ACCEPTED.search(text) is not None

    def status(self) -> Dict:
        adrs = {adr: self._adr_accepted(adr) for adr in REQUIRED_ADRS}
        threat_ok = bool(self._config.get("threat_model_reviewed_by")) and bool(
            DATE.match(str(self._config.get("threat_model_review_date", ""))))
        matrix_ok = bool(self._config.get("permission_matrix_approved_by")) and bool(
            DATE.match(str(self._config.get("permission_matrix_approved_date", ""))))
        missing = [adr for adr, ok in adrs.items() if not ok]
        if not threat_ok:
            missing.append("threat_model_review")
        if not matrix_ok:
            missing.append("permission_matrix_approval")
        return {"open": not missing, "missing": missing, "adrs": adrs,
                "threat_model_reviewed": threat_ok, "permission_matrix_approved": matrix_ok}

    def is_open(self) -> bool:
        return self.status()["open"]


class StaticGate:
    """For tests only. Never used by build_gateway."""

    def __init__(self, open_: bool):
        self._open = open_

    def is_open(self) -> bool:
        return self._open

    def status(self) -> Dict:
        return {"open": self._open, "missing": [] if self._open else ["test"]}
