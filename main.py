import os
import sys
import json
from src.InfraProperties import InfraProperties
from src.networkGraph import NetworkGraph

if __name__ == '__main__':
    # backwards-compatible CLI: parse the default properties file and print JSON
    infra = InfraProperties.from_file()
    print(infra.to_json(indent=2, ensure_ascii=False))

    # Ensure project root is on sys.path so we can import the root-level module
    root_dir = os.path.dirname(os.path.dirname(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    infra = InfraProperties.from_file(r'properties\\Infra_8nodes.properties')
    G = NetworkGraph.from_infra_dict(infra.to_dict())
    print("Summary:")
    G.print_summary()
    print("\nNodes:")
    G.print_nodes()
    print("\nEdges:")
    G.print_edges()
    print("\nDegree stats:")
    print(json.dumps(G.degree_stats(), indent=2))
    print("\nConnectivity:")
    print(json.dumps(G.connectivity_info(), indent=2))
    # Uncomment to visualize
    G.draw()