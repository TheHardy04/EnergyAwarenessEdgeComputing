from src.base import PlacementResult
from src.serviceGraph import *
from src.networkGraph import *
from src.utils import *
import copy

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
        routing = final_placement.meta.get('routing', {})

        reconstructed = copy.deepcopy(network_graph)

        # Add back allocations so reconstructed represents pre-allocation state
        for (u, v), info in routing.items():
            path = info.get('path', [])
            bw_req = service_graph.G[u][v].get('bandwidth', 0)
            # increment each edge along the path by bw_req
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                if not reconstructed.G.has_edge(a, b):
                    # should not happen if routing is valid, but guard anyway
                    continue
                data = reconstructed.G[a][b]
                cur = int(data.get('bandwidth') or 0)
                data['bandwidth'] = cur + int(bw_req)

        # Now validate each routed edge against the reconstructed graph
        for (u, v), info in routing.items():
            src_host = final_placement.mapping[u]
            dst_host = final_placement.mapping[v]
            bw_req = service_graph.G[u][v].get('bandwidth', 0)
            lat_limit = service_graph.G[u][v].get('latency', 10**9)

            path = info.get('path', [])
            assert path, f"No path recorded for service edge {u}->{v}"
            assert path[0] == src_host, f"Route for edge {u}->{v} does not start at source host {src_host}"
            assert path[-1] == dst_host, f"Route for edge {u}->{v} does not end at destination host {dst_host}"

            ok, info2 = edge_capacity_ok(reconstructed, path, bw_req, lat_limit)
            assert ok, f"Edge {u}->{v} routing failed constraints: {info2}"
        print("All edge routing constraint tests passed.")

        print("All Mapping Unit Tests Passed!")