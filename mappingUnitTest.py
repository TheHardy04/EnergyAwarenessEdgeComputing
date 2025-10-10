from src.base import PlacementResult
from src.serviceGraph import *
from src.networkGraph import *
from src.utils import *

class MappingUnitTest:
    @staticmethod
    def run_tests(network_graph : NetworkGraph, service_graph : ServiceGraph, final_placement : PlacementResult):
        print("Running Mapping Unit Tests...")
        # Test 1: Validate the network graph structure
        assert network_graph.G.number_of_nodes() > 0, "Network graph is empty"
        assert network_graph.G.number_of_edges() > 0, "Network graph has no edges"

        # Test 2: Validate the service graph structure
        assert service_graph.G.number_of_nodes() > 0, "Service graph is empty"
        assert service_graph.G.number_of_edges() > 0, "Service graph has no edges"

        # Test 3: Validate the final placement
        for comp, host in final_placement.mapping.items():
            assert host in network_graph.G.nodes(), f"Component {comp} placed on invalid host {host}"
            assert comp in service_graph.G.nodes(), f"Invalid component {comp} in placement mapping"
        print("All basic structure tests passed.")
        
        # Test 4: Validate host resource constraints
        host_resources = {n: {'cpu': d.get('cpu'), 'ram': d.get('ram')} for n, d in network_graph.G.nodes(data=True)}
        used_resources = {n: {'cpu': 0, 'ram': 0} for n in network_graph.G.nodes()}
        for comp, host in final_placement.mapping.items():
            comp_data = service_graph.G.nodes[comp]
            used_resources[host]['cpu'] += comp_data.get('cpu', 0)
            used_resources[host]['ram'] += comp_data.get('ram', 0)

        for host, used in used_resources.items():
            total = host_resources.get(host, {'cpu': 0, 'ram': 0})
            assert used['cpu'] <= total['cpu'], f"Host {host} CPU overcommit: {used['cpu']} > {total['cpu']}"
            assert used['ram'] <= total['ram'], f"Host {host} RAM overcommit: {used['ram']} > {total['ram']}"
        print("All resource constraint tests passed.")

        # Test 5: Validate edge routing constraints
        for (u, v), route_info in final_placement.mapping.items():
            src_host = final_placement.mapping[u]
            dst_host = final_placement.mapping[v]
            bw_req = service_graph.G[u][v].get('bandwidth', 0)
            lat_limit = service_graph.G[u][v].get('latency', 10**9)

            path = route_info.get('path', [])
            assert path[0] == src_host, f"Route for edge {u}->{v} does not start at source host {src_host}"
            assert path[-1] == dst_host, f"Route for edge {u}->{v} does not end at destination host {dst_host}"

            ok, info = edge_capacity_ok(network_graph, path, bw_req, lat_limit)
            assert ok, f"Edge {u}->{v} routing failed constraints: {info}"

        print("All Mapping Unit Tests Passed!")