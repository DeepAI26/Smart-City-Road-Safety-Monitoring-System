import networkx as nx
from haversine import haversine

def astar_path(G, start_gps, end_gps):
    """
    Compute a safe path between two GPS locations using the A* algorithm.
    The heuristic is based on straight-line (geographic) distance.
    """

    # Map the start GPS coordinate to the nearest node in the graph
    start_node = min(
        G.nodes,
        key=lambda n: haversine(
            start_gps,
            (G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)),
             G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)))
        )
    )

    # Map the end GPS coordinate to the nearest node in the graph
    end_node = min(
        G.nodes,
        key=lambda n: haversine(
            end_gps,
            (G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)),
             G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)))
        )
    )

    # Heuristic function: estimates remaining cost using straight-line distance
    # This helps guide the search toward the destination efficiently
    def heuristic(n1, n2):
        return haversine(
            (G.nodes[n1].get("latitude", G.nodes[n1].get("lat", 0)),
             G.nodes[n1].get("longitude", G.nodes[n1].get("lon", 0))),
            (G.nodes[n2].get("latitude", G.nodes[n2].get("lat", 0)),
             G.nodes[n2].get("longitude", G.nodes[n2].get("lon", 0)))
        )

    # Run A* search using safety-aware edge weights
    path = nx.astar_path(
        G,
        start_node,
        end_node,
        heuristic=lambda n, _: heuristic(n, end_node),
        weight="weight"
    )

    return path
