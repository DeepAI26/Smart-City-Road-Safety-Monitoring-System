import pandas as pd
import networkx as nx
from haversine import haversine
import json
from pathlib import Path
from utils import get_csv_path, calculate_safety_score

# Input CSV containing GPS points and road condition metadata
CSV_PATH = get_csv_path()

# Output file for the adjacency list representation
OUTPUT_PATH = Path(__file__).parent / "adjacency_list.json"


# Load CSV file
if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Sort by timestamp so edges follow the real traversal order of the road
if "timestamp" in df.columns:
    df = df.sort_values("timestamp")


# BUILD GRAPH STRUCTURE
G = nx.Graph()

# Add nodes representing GPS points / captured images
for _, row in df.iterrows():
    G.add_node(
        row["image_name"],
        pos=(row["latitude"], row["longitude"]),
        condition=row["road_condition"]
    )

# Map road condition to a safety penalty
# Unsafe roads increase traversal cost
penalty = {
    "safe": 0.0,
    "minor_issue": 0.3,
    "major_problem": 0.7
}

# Add edges between consecutive GPS points
points = df.to_dict("records")

for i in range(len(points) - 1):
    p1 = points[i]
    p2 = points[i + 1]

    # Geographic distance between consecutive points
    dist = haversine(
        (p1["latitude"], p1["longitude"]),
        (p2["latitude"], p2["longitude"])
    )

    # Combine distance with safety penalty for routing weight
    weight = dist * (1 + penalty[p2["road_condition"]])

    G.add_edge(
        p1["image_name"],
        p2["image_name"],
        weight=weight,
        distance=dist,
        safety=p2["road_condition"]
    )

# Quick sanity check
print("Graph constructed")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Convert the NetworkX graph into a plain adjacency list
# This makes the structure easier to inspect and serialize
adjacency_list = {}

for node in G.nodes():
    adjacency_list[node] = []

    for neighbor, data in G[node].items():
        adjacency_list[node].append({
            "neighbor": neighbor,
            "weight": data["weight"],
            "distance": data["distance"],
            "safety": data["safety"]
        })


# PRINT SAMPLE OUTPUT (FOR VERIFICATION)
print("\nSample adjacency list (first 3 nodes):")
for node, edges in list(adjacency_list.items())[:3]:
    print(node, "→", edges)

# Saving as JSON allows reuse in other components or languages
with open(OUTPUT_PATH, "w") as f:
    json.dump(adjacency_list, f, indent=2)

print(f"\nAdjacency list saved to {OUTPUT_PATH}")
