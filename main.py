
import json

from src.infraProperties import InfraProperties
from src.networkGraph import NetworkGraph
from src.appProperties import AppProperties
from src.serviceGraph import ServiceGraph


if __name__ == '__main__':
    # backwards-compatible CLI: parse the default properties file and print JSON
    infra = InfraProperties.from_file()
    print(infra.to_json(indent=2, ensure_ascii=False))

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
    G.draw()

    app = AppProperties.from_file(r'properties\\Appli_4comps.properties')
    print("\nApp Properties:")
    print(app.to_json(indent=2, ensure_ascii=False))

    service_G = ServiceGraph.from_app_dict(app.to_dict())
    print("\nService Graph Summary:")
    service_G.print_summary()
    print("\nService Graph Nodes:")
    service_G.print_nodes()
    print("\nService Graph Edges:")
    service_G.print_edges()
    print("\nService Graph Degree stats:")
    print(json.dumps(service_G.degree_stats(), indent=2))
    print("\nService Graph Connectivity:")
    print(json.dumps(service_G.connectivity_info(), indent=2))
    service_G.draw()
