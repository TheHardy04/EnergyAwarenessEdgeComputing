from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol


@dataclass
class PlacementResult:
    # Mapping from service/component id -> host node id
    mapping: Dict[int, int]
    # diagnostics (e.g., path info, resource usage)
    meta: Dict[str, Any]


class PlacementStrategy(Protocol):
    # Optional start_host allows callers to indicate which infra node should be
    # considered first when placing components. Implementations may ignore it.
    def place(self, service_graph, network_graph, start_host: Optional[int] = None) -> PlacementResult:
        ...
