import pandas as pd
import networkx as nx
from haversine import haversine
import pickle
from pathlib import Path
from utils import get_csv_path, calculate_safety_score

# Input CSV containing GPS points and road metadata
CSV_PATH = get_csv_path()

# Output file where the constructed graph will be stored
OUT_GRAPH = Path(__file__).parent / "road_graph.pkl"

# Maximum allowed distance between two consecutive points
# Helps prevent connecting unrelated road segments
MAX_SEGMENT_KM = 0.08     # ~80 meters

# Controls how much safety affects the edge weight
# Higher ALPHA = more penalty for unsafe roads
ALPHA = 1.0

# Used to estimate travel time along road segments
AVG_SPEED_KMH = 50


# Load CSV file
if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Sort by timestamp so edges follow the actual traversal order
if "timestamp" in df.columns:
    df = df.sort_values("timestamp")

# Calculate safety_score if it doesn't exist
if "safety_score" not in df.columns:
    print("Calculating safety scores from road conditions...")
    df["safety_score"] = df.apply(
        lambda row: calculate_safety_score(
            str(row.get("road_condition", "safe")),
            str(row.get("problem_type", "none"))
        ),
        axis=1
    )
    print("Safety scores calculated.")

# Directed graph allows modeling one-way streets
G = nx.DiGraph()

# ---- Add nodes ----
# Each node represents a GPS point / image location
# Node attributes store metadata useful for routing and visualization
for _, row in df.iterrows():
    G.add_node(
        row["image_name"],
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        condition=row.get("road_condition", "safe"),
        problem=row.get("problem_type", "none"),
        safety=float(row.get("safety_score", 1.0)),
        image=row.get("image_name")
    )

# ---- Add edges ----
# Convert rows to dictionaries for easier sequential processing
points = df.to_dict("records")

for i in range(len(points) - 1):
    p1 = points[i]
    p2 = points[i + 1]

    u = p1["image_name"]
    v = p2["image_name"]

    # Compute geographic distance between consecutive GPS points
    dist = haversine(
        (p1["latitude"], p1["longitude"]),
        (p2["latitude"], p2["longitude"])
    )

    # Ignore connections that are unrealistically far apart
    if dist > MAX_SEGMENT_KM:
        continue

    # Safety-aware edge weight
    # Lower safety scores increase traversal cost
    safety = float(p2.get("safety_score", 1.0))
    weight = dist * (1 + ALPHA * (1 - safety))

    # Approximate travel time in minutes
    travel_time = (dist / AVG_SPEED_KMH) * 60

    # Determine if the road segment is one-way
    # Default behavior assumes two-way roads
    one_way = str(p2.get("one_way", "false")).lower() == "true"

    # ---- Forward edge ----
    G.add_edge(
        u,
        v,
        distance=dist,
        safety=safety,
        weight=weight,
        travel_time=travel_time
    )

    # ---- Reverse edge (only if road is not one-way) ----
    if not one_way:
        G.add_edge(
            v,
            u,
            distance=dist,
            safety=safety,
            weight=weight,
            travel_time=travel_time
        )

# Persist the graph so it can be reused for routing algorithms
with open(OUT_GRAPH, "wb") as f:
    pickle.dump(G, f)

print(f"Graph saved to: {OUT_GRAPH}")

print("Directed road graph built with bidirectional edges")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Print sample entries for quick verification
print("Sample node:", next(iter(G.nodes(data=True))))
print("Sample edge:", next(iter(G.edges(data=True))))
