from typing import Dict, Any, List, Tuple

import networkx as nx

from src.base import PlacementResult
from src.utils import host_resources_snapshot, can_host, allocate_on_host, edge_capacity_ok


class GreedyFirstFit:
    """A simple baseline placement:
    - Iterate components in order (0..n-1)
    - For each, pick the first host with enough CPU/RAM
    - After mapping all nodes, validate each service edge by finding a path that meets BW/latency
      using shortest path (by latency) and checking capacities.
    - Returns mapping and per-edge routing meta.
    """

    def place(self, service_graph, network_graph, start_host: int = None) -> PlacementResult:
        SG, NG = service_graph.G, network_graph.G

        # Track host resources
        res = host_resources_snapshot(network_graph)

        # 1) Place components
        mapping: Dict[int, int] = {}
        # Prepare host iteration order. If start_host is provided and exists in
        # the infra graph, begin the search from that node and wrap around.
        hosts_list = list(NG.nodes())
        if start_host is not None and start_host in hosts_list:
            # rotate so start_host is first
            idx = hosts_list.index(start_host)
            hosts_list = hosts_list[idx:] + hosts_list[:idx]

        for comp, d in SG.nodes(data=True):
            cpu_req = int(d.get('cpu') or 0)
            ram_req = int(d.get('ram') or 0)
            placed = False
            for host in hosts_list:
                if can_host(res, host, cpu_req, ram_req):
                    allocate_on_host(res, host, cpu_req, ram_req)
                    mapping[comp] = host
                    placed = True
                    break
            if not placed:
                return PlacementResult(mapping=mapping, meta={'status': 'failed', 'reason': f'no_host_for_component_{comp}'})

        # 2) Route edges with constraints
        # Build a latency-weighted graph for shortest paths
        H = nx.DiGraph()
        for u, v, d in NG.edges(data=True):
            lat = float(d.get('latency') or 0.0)
            H.add_edge(u, v, weight=lat)

        routing: Dict[Tuple[int, int], Dict[str, Any]] = {}
        for u, v, d in SG.edges(data=True):
            src_host = mapping[u]
            dst_host = mapping[v]
            bw_req = int(d.get('bandwidth') or 0)
            lat_limit = int(d.get('latency') or 10**9)  # large if not provided

            try:
                path = nx.shortest_path(H, source=src_host, target=dst_host, weight='weight')
            except nx.NetworkXNoPath:
                return PlacementResult(mapping=mapping, meta={'status': 'failed', 'reason': f'no_path_{u}_{v}'})

            ok, info = edge_capacity_ok(network_graph, path, bw_req, lat_limit)
            if not ok:
                return PlacementResult(mapping=mapping, meta={'status': 'failed', 'reason': f'constraints_{u}_{v}', 'detail': info})
            routing[(u, v)] = {'path': path, **info}

        return PlacementResult(mapping=mapping, meta={'status': 'ok', 'routing': routing})
