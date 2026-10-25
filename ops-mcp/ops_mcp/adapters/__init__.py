"""Adapters execute a capability against one node type or one data source.

An adapter never receives a credential in its arguments. Node credentials come from the secret broker
(ADR-0014) and are not present in version 0.1.
"""

from typing import Dict, Optional, Protocol


class Adapter(Protocol):
    def execute(self, capability: str, node: Optional[str], args: Dict) -> Dict:
        ...
