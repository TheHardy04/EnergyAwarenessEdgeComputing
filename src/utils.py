from typing import Dict, Any, Tuple, List


def host_resources_snapshot(network_graph) -> Dict[int, Dict[str, Any]]:
    """
    Create a snapshot of host resources (cpu, ram) from the network graph.
    """
    resources: Dict[int, Dict[str, Any]] = {}
    for n, d in network_graph.G.nodes(data=True):
        resources[n] = {
            'cpu_total': int(d.get('cpu') or 0),
            'ram_total': int(d.get('ram') or 0),
            'cpu_used': 0,
            'ram_used': 0,
        }
    return resources


def can_host(resources: Dict[int, Dict[str, Any]], node: int, cpu: int, ram: int) -> bool:
    r = resources[node]
    return r['cpu_used'] + cpu <= r['cpu_total'] and r['ram_used'] + ram <= r['ram_total']


def allocate_on_host(resources: Dict[int, Dict[str, Any]], node: int, cpu: int, ram: int) -> None:
    resources[node]['cpu_used'] += cpu
    resources[node]['ram_used'] += ram


def edge_capacity_ok(network_graph, path: List[int], bandwidth: int, latency_limit: int) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if the given path can support the bandwidth and latency constraints.
    """
    total_latency = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if not network_graph.G.has_edge(u, v):
            return False, {'reason': 'missing_edge', 'u': u, 'v': v}
        data = network_graph.G[u][v]
        bw = int(data.get('bandwidth') or 0)
        lat = int(data.get('latency') or 0)
        if bw < bandwidth:
            return False, {'reason': 'bandwidth', 'u': u, 'v': v, 'bw': bw, 'required': bandwidth}
        total_latency += lat
    if total_latency > latency_limit:
        return False, {'reason': 'latency', 'total_latency': total_latency, 'limit': latency_limit}
    return True, {'total_latency': total_latency}


def allocate_on_path(network_graph, path: List[int], bandwidth: int) -> None:
    """Consume bandwidth on each link along the given path.

    This mutates the network_graph in place by subtracting `bandwidth` from
    each edge's 'bandwidth' attribute. It assumes a prior check (e.g.
    edge_capacity_ok) ensured links had sufficient capacity.
    """
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        data = network_graph.G[u][v]
        cur = int(data.get('bandwidth') or 0)
        data['bandwidth'] = cur - int(bandwidth)
