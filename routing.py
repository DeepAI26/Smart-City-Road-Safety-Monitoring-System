import networkx as nx
from haversine import haversine

def find_nearest_node(G, gps):
    """Find the nearest node to a GPS coordinate."""
    return min(
        G.nodes,
        key=lambda n: haversine(
            gps, 
            (G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)),
             G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)))
        )
    )

def edge_cost(distance_km: float, safety: float, alpha: float = 2.0) -> float:
    # safety in [0,1]; lower safety => higher cost
    safety = max(0.0, min(1.0, float(safety)))
    return float(distance_km) * (1.0 + alpha * (1.0 - safety))

def recompute_all_edge_weights(G, alpha: float = 2.0):
    for u, v, data in G.edges(data=True):
        dist = float(data.get("distance", 0.0))
        safety = float(data.get("safety", 1.0))
        data["weight"] = edge_cost(dist, safety, alpha=alpha)

def route_stats(G, path):
    total_distance = 0.0
    total_safety = 0.0
    for i in range(len(path) - 1):
        e = G[path[i]][path[i+1]]
        total_distance += float(e["distance"])
        total_safety += float(e["safety"])
    edges = max(1, len(path) - 1)
    avg_safety = total_safety / edges
    travel_time = (total_distance / 50.0) * 60.0  # minutes at 50 km/h
    return {
        "path": path,
        "distance": total_distance,
        "avg_safety": avg_safety,
        "travel_time": travel_time
    }

def dijkstra_route(G, start_gps, end_gps, weight_key="weight"):
    s = find_nearest_node(G, start_gps)
    t = find_nearest_node(G, end_gps)
    path = nx.dijkstra_path(G, s, t, weight=weight_key)
    return route_stats(G, path)

def astar_route(G, start_gps, end_gps, weight_key="weight"):
    s = find_nearest_node(G, start_gps)
    t = find_nearest_node(G, end_gps)

    def h(n1, n2):
        return haversine(
            (G.nodes[n1].get("latitude", G.nodes[n1].get("lat", 0)),
             G.nodes[n1].get("longitude", G.nodes[n1].get("lon", 0))),
            (G.nodes[n2].get("latitude", G.nodes[n2].get("lat", 0)),
             G.nodes[n2].get("longitude", G.nodes[n2].get("lon", 0)))
        )

    path = nx.astar_path(G, s, t, heuristic=lambda n, _: h(n, t), weight=weight_key)
    return route_stats(G, path)
