from flask import Flask, render_template, request, redirect, url_for
import pickle
import sys
from pathlib import Path

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from routing import dijkstra_route, astar_route
from map_view import create_map

# This Flask app loads a pre-built road graph and lets users select start/end points on a map.
# It computes the shortest, safest, and optimized routes using Dijkstra and A* algorithms.
# The selected route is rendered and saved as an interactive HTML map for display.
app = Flask(__name__)

# Use relative paths
GRAPH_PATH = BASE_DIR / "road_graph.pkl"
if not GRAPH_PATH.exists():
    GRAPH_PATH = BASE_DIR.parent / "road_graph.pkl"

MAP_PATH = BASE_DIR / "web_app" / "static" / "map" / "road_map.html"
MAP_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load pre-built graph
try:
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
except FileNotFoundError:
    print(f"Error: Graph file not found at {GRAPH_PATH}")
    print("Please run 'python graph.py' first to generate the graph.")
    G = None
except Exception as e:
    print(f"Error loading graph: {e}")
    G = None

@app.route("/", methods=["GET", "POST"])
def index():
    routes = None
    error = None

    if request.method == "POST":
        if G is None:
            error = "Graph not loaded. Please run 'python graph.py' first."
        else:
            try:
                # Coordinates come from hidden inputs (set by pin clicks)
                start = (
                    float(request.form["start_lat"]),
                    float(request.form["start_lon"])
                )
                end = (
                    float(request.form["end_lat"]),
                    float(request.form["end_lon"])
                )

                # Compute routes
                shortest = dijkstra_route(G, start, end, weight_key="distance")
                safest = dijkstra_route(G, start, end, weight_key="weight")
                optimized = astar_route(G, start, end)

                routes = {
                    "shortest": shortest,
                    "safest": safest,
                    "optimized": optimized
                }

                # Create map (show safest route)
                m = create_map(G, safest["path"])
                m.save(str(MAP_PATH))
            except Exception as e:
                error = f"Error computing routes: {str(e)}"

    return render_template(
        "index.html",
        routes=routes,
        map_file="static/map/road_map.html" if routes else None,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)

