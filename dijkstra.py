import networkx as nx
from haversine import haversine

def find_nearest_node(G, gps):
    """
    Given a GPS coordinate, find the closest node in the graph.
    This is used to map real-world locations to graph nodes.
    """
    return min(
        G.nodes,
        key=lambda n: haversine(
            gps,
            (G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)),
             G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)))
        )
    )

def dijkstra_path(G, start_gps, end_gps):
    """
    Compute the safest path between two GPS locations using Dijkstra’s algorithm.
    Safety is encoded in the edge weights.
    """

    # Snap start and end GPS points to the nearest graph nodes
    start_node = find_nearest_node(G, start_gps)
    end_node = find_nearest_node(G, end_gps)

    # Run Dijkstra using the custom edge weight (distance + safety penalty)
    path = nx.dijkstra_path(G, start_node, end_node, weight="weight")

    total_distance = 0
    total_safety = 0

    # Accumulate distance and safety values along the selected path
    for i in range(len(path) - 1):
        edge = G[path[i]][path[i + 1]]
        total_distance += edge["distance"]
        total_safety += edge["safety"]

    # Return useful metrics for analysis and visualization
    return {
        "path": path,
        "total_distance": total_distance,
        "average_safety": total_safety / (len(path) - 1),
        "travel_time": (total_distance / 50) * 60  # assume ~50 km/h, output in minutes
    }
