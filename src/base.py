from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol


@dataclass
class PlacementResult:
    # Mapping from service/component id -> host node id
    mapping: Dict[int, int]
    # Optional diagnostics (e.g., path info, resource usage)
    meta: Dict[str, Any]


class PlacementStrategy(Protocol):
    def place(self, service_graph, network_graph) -> PlacementResult:
        ...
