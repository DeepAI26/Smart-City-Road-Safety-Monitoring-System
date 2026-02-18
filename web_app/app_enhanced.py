"""
Enhanced Flask Application for Component 4: Intelligent Navigation System
This application provides:
- Safe Path Algorithm (Dijkstra's, A*, custom weight function)
- Route Planning Interface with multiple route options
- Real-time Adaptation and Dynamic Re-routing
- User Notification System with alerts and alternative route suggestions
"""

from flask import Flask, render_template, request, jsonify
import pickle
import os
import json
import sys
from pathlib import Path
import networkx as nx

# Add parent directory to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from routing import dijkstra_route, astar_route

# Optional imports for model inference
try:
    from realtime_adaptation import RealTimeRouter
    from model_inference import RoadSafetyDetector, calculate_safety_score_from_condition
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Model inference not available: {e}")
    MODEL_AVAILABLE = False
    RealTimeRouter = None
    RoadSafetyDetector = None

app = Flask(__name__)

# Configuration
BASE_DIR = Path(__file__).parent.parent
# Try multiple possible graph paths
GRAPH_PATH = BASE_DIR / "road_graph.pkl"
if not GRAPH_PATH.exists():
    GRAPH_PATH = BASE_DIR.parent / "road_graph.pkl"
MODEL_PATH = BASE_DIR / "my_model" / "my_model.pt"
MAP_PATH = BASE_DIR / "web_app" / "static" / "map" / "road_map.html"

# Load pre-built graph
try:
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
except Exception as e:
    print(f"Error loading graph: {e}")
    G = None

# Initialize model detector (optional - only if model exists)
model_detector = None
if MODEL_AVAILABLE and MODEL_PATH.exists():
    try:
        model_detector = RoadSafetyDetector(str(MODEL_PATH))
        print("YOLO model loaded successfully")
    except Exception as e:
        print(f"Could not load YOLO model: {e}")

# Initialize real-time router
realtime_router = None
if G is not None and MODEL_AVAILABLE and RealTimeRouter:
    try:
        realtime_router = RealTimeRouter(G, model_detector)
    except Exception as e:
        print(f"Could not initialize real-time router: {e}")


def classify_route_safety(safety_score: float) -> dict:
    """
    Classify route safety based on probability thresholds.
    Returns classification with color and icon.
    """
    if safety_score < 0.3:
        return {
            'classification': 'Safe',
            'probability': safety_score,
            'color': 'green',
            'icon': '✓',
            'description': 'Route is safe to travel'
        }
    elif safety_score < 0.7:
        return {
            'classification': 'Possibly Hazardous',
            'probability': safety_score,
            'color': 'orange',
            'icon': '⚠',
            'description': 'Route may have some road issues'
        }
    else:
        return {
            'classification': 'Hazardous',
            'probability': safety_score,
            'color': 'red',
            'icon': '⚠',
            'description': 'Route contains hazardous conditions'
        }


def create_enhanced_map(G, routes_dict, selected_route_type='safest'):
    """
    Create an enhanced Folium map with route visualization and safety classifications.
    """
    try:
        import folium
        from folium import Element
    except ImportError:
        raise ImportError("folium is required for map generation")
    
    # Calculate center
    lats = [G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)) for n in G.nodes]
    lons = [G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)) for n in G.nodes]
    center_lat = sum(lats) / len(lats) if lats else 43.125
    center_lon = sum(lons) / len(lons) if lons else -79.22
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
    
    # Draw road nodes with safety coloring
    for node, data in G.nodes(data=True):
        safety = float(data.get("safety", 1.0))
        lat = data.get("latitude", data.get("lat", 0))
        lon = data.get("longitude", data.get("lon", 0))
        
        if safety >= 0.7:
            color = "green"
        elif safety >= 0.4:
            color = "orange"
        else:
            color = "red"
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"Safety: {safety:.2f}<br>Condition: {data.get('condition', 'unknown')}"
        ).add_to(m)
    
    # Draw routes with different colors
    route_colors = {
        'shortest': 'blue',
        'safest': 'green',
        'optimized': 'purple'
    }
    
    if routes_dict:
        for route_type, route_data in routes_dict.items():
            if route_data and 'path' in route_data:
                route_coords = []
                for node in route_data['path']:
                    node_data = G.nodes[node]
                    lat = node_data.get("latitude", node_data.get("lat", 0))
                    lon = node_data.get("longitude", node_data.get("lon", 0))
                    route_coords.append([lat, lon])
                
                color = route_colors.get(route_type, 'gray')
                weight = 6 if route_type == selected_route_type else 4
                opacity = 0.9 if route_type == selected_route_type else 0.5
                
                folium.PolyLine(
                    route_coords,
                    color=color,
                    weight=weight,
                    opacity=opacity,
                    popup=f"{route_type.title()} Route"
                ).add_to(m)
        
        # Add start and end markers
        if 'safest' in routes_dict and routes_dict['safest']:
            start_node = routes_dict['safest']['path'][0]
            end_node = routes_dict['safest']['path'][-1]
            
            start_data = G.nodes[start_node]
            end_data = G.nodes[end_node]
            
            folium.Marker(
                [start_data.get("latitude", start_data.get("lat", 0)),
                 start_data.get("longitude", start_data.get("lon", 0))],
                popup="Start Point",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
            
            folium.Marker(
                [end_data.get("latitude", end_data.get("lat", 0)),
                 end_data.get("longitude", end_data.get("lon", 0))],
                popup="End Point",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)
    
    # Add safety legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: 120px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
    <h4>Safety Legend</h4>
    <p><span style="color:green">●</span> Safe (p < 0.3)</p>
    <p><span style="color:orange">●</span> Possibly Hazardous (0.3 ≤ p < 0.7)</p>
    <p><span style="color:red">●</span> Hazardous (p ≥ 0.7)</p>
    </div>
    '''
    m.get_root().html.add_child(Element(legend_html))
    
    return m


@app.route("/")
def index():
    """Main page with route planning interface."""
    # Generate initial map with click handlers for point selection
    if G is not None:
        try:
            import folium
            from folium import Element
            # Create map directly here to ensure it has click handlers
            lats = [G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)) for n in G.nodes]
            lons = [G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)) for n in G.nodes]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
            
            # Add road nodes
            for node, data in G.nodes(data=True):
                safety = float(data.get("safety", 1.0))
                if safety >= 0.7:
                    color = "green"
                elif safety >= 0.4:
                    color = "orange"
                else:
                    color = "red"
                lat = data.get("latitude", data.get("lat", 0))
                lon = data.get("longitude", data.get("lon", 0))
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color=color,
                    fill=True,
                    fill_opacity=0.8,
                    popup=f"Safety: {safety:.2f}"
                ).add_to(m)
            
            # Add click handler - attach to all Leaflet maps
            click_js = """
            <script>
            (function() {
                let clickCount = 0;
                let markers = [];
                let mapObj = null;

                function findMap() {
                    // Method 1: Look for all Leaflet map instances
                    if (typeof L !== 'undefined') {
                        // Get the map container
                        const mapDiv = document.querySelector('.folium-map');
                        if (mapDiv) {
                            // Leaflet stores map instances, try to find it
                            const mapId = mapDiv.id;
                            // Check if there's a global variable with the map
                            for (let key in window) {
                                try {
                                    if (window[key] && 
                                        window[key]._container && 
                                        window[key]._container.id === mapId &&
                                        window[key].on) {
                                        return window[key];
                                    }
                                } catch(e) {}
                            }
                        }
                    }
                    return null;
                }

                function attachClickHandler() {
                    if (!mapObj) {
                        mapObj = findMap();
                    }
                    
                    if (mapObj && typeof mapObj.on === 'function') {
                        // Remove any existing click handler first
                        mapObj.off('click');
                        
                        mapObj.on('click', function(e) {
                            const lat = parseFloat(e.latlng.lat.toFixed(6));
                            const lng = parseFloat(e.latlng.lng.toFixed(6));
                            
                            console.log('Map clicked:', lat, lng);
                            
                            // Send message to parent window
                            if (window.parent && window.parent !== window) {
                                window.parent.postMessage({lat: lat, lng: lng}, "*");
                                console.log('Message sent to parent window');
                            } else {
                                console.log('No parent window found');
                            }
                            
                            // Add marker
                            if (clickCount === 0) {
                                // Clear previous markers
                                markers.forEach(function(m) { 
                                    try { mapObj.removeLayer(m); } catch(e) {}
                                });
                                markers = [];
                                
                                const marker = L.marker([lat, lng]).addTo(mapObj);
                                marker.bindPopup("Start Point").openPopup();
                                markers.push(marker);
                                clickCount++;
                            } else {
                                const marker = L.marker([lat, lng]).addTo(mapObj);
                                marker.bindPopup("End Point").openPopup();
                                markers.push(marker);
                                clickCount = 0;
                            }
                        });
                        console.log('Click handler attached successfully to map');
                        return true;
                    } else {
                        console.log('Map object not found yet, mapObj:', mapObj);
                    }
                    return false;
                }
                
                function tryAttach() {
                    if (!attachClickHandler()) {
                        setTimeout(tryAttach, 300);
                    }
                }
                
                // Wait for Leaflet to load, then try to attach
                if (typeof L !== 'undefined' && typeof L.map !== 'undefined') {
                    setTimeout(tryAttach, 1000);
                } else {
                    window.addEventListener('load', function() {
                        setTimeout(tryAttach, 1500);
                    });
                }
            })();
            </script>
            """
            m.get_root().html.add_child(Element(click_js))
            
            MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
            m.save(str(MAP_PATH))
            print("✓ Initial map generated with click handlers")
        except Exception as e:
            print(f"⚠ Error generating initial map: {e}")
            import traceback
            traceback.print_exc()
    
    return render_template("index_enhanced.html")


@app.route("/api/route", methods=["POST"])
def compute_routes():
    """API endpoint to compute routes between two points."""
    if G is None:
        return jsonify({"error": "Graph not loaded"}), 500
    
    data = request.json
    start = (float(data["start_lat"]), float(data["start_lon"]))
    end = (float(data["end_lat"]), float(data["end_lon"]))
    
    try:
        # Compute different route options
        routes = {}
        
        # Shortest route (distance only)
        try:
            shortest = dijkstra_route(G, start, end, weight_key="distance")
            routes['shortest'] = shortest
        except Exception as e:
            print(f"Error computing shortest route: {e}")
        
        # Safest route (safety-weighted)
        try:
            safest = dijkstra_route(G, start, end, weight_key="weight")
            routes['safest'] = safest
        except Exception as e:
            print(f"Error computing safest route: {e}")
        
        # Optimized route (A*)
        try:
            optimized = astar_route(G, start, end)
            routes['optimized'] = optimized
        except Exception as e:
            print(f"Error computing optimized route: {e}")
        
        # Add safety classifications
        for route_type, route_data in routes.items():
            if route_data:
                safety_class = classify_route_safety(1.0 - route_data['avg_safety'])
                route_data['safety_classification'] = safety_class
        
        # Get notifications and alternatives
        notifications = {}
        if realtime_router and routes.get('safest'):
            alternatives = realtime_router.get_alternative_routes(start, end, routes['safest']['path'])
            notifications = realtime_router.get_route_notification(routes['safest'], alternatives)
            routes['alternatives'] = [alt['route'] for alt in alternatives]
        
        # Create map (optional - only if folium is available)
        try:
            m = create_enhanced_map(G, routes, 'safest')
            MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
            m.save(str(MAP_PATH))
            map_file = "static/map/road_map.html"
        except Exception as e:
            print(f"Warning: Could not create map: {e}")
            map_file = "static/map/road_map.html"  # Use existing map
        
        return jsonify({
            "success": True,
            "routes": routes,
            "notifications": notifications,
            "map_file": map_file
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/simulate-problem", methods=["POST"])
def simulate_problem():
    """Simulate real-time problem detection at a location."""
    if realtime_router is None:
        return jsonify({"error": "Real-time router not initialized"}), 500
    
    data = request.json
    gps = (float(data["lat"]), float(data["lon"]))
    condition = data.get("condition", "major_problem")
    problem_type = data.get("problem_type", "pothole")
    
    result = realtime_router.simulate_problem_detection(gps, condition, problem_type)
    
    return jsonify({
        "success": True,
        "result": result,
        "message": f"Simulated {problem_type} at location"
    })


@app.route("/api/recompute-routes", methods=["POST"])
def recompute_routes():
    """Recompute routes after real-time updates."""
    if realtime_router is None:
        return jsonify({"error": "Real-time router not initialized"}), 500
    
    data = request.json
    start = (float(data["start_lat"]), float(data["start_lon"]))
    end = (float(data["end_lat"]), float(data["end_lon"]))
    
    # Get updated routes
    routes = {}
    try:
        routes['shortest'] = dijkstra_route(realtime_router.graph, start, end, weight_key="distance")
        routes['safest'] = dijkstra_route(realtime_router.graph, start, end, weight_key="weight")
        routes['optimized'] = astar_route(realtime_router.graph, start, end)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Add safety classifications
    for route_type, route_data in routes.items():
        if route_data:
            safety_class = classify_route_safety(1.0 - route_data['avg_safety'])
            route_data['safety_classification'] = safety_class
    
    # Get notifications
    notifications = {}
    if routes.get('safest'):
        alternatives = realtime_router.get_alternative_routes(start, end, routes['safest']['path'])
        notifications = realtime_router.get_route_notification(routes['safest'], alternatives)
    
    # Update map (optional)
    try:
        m = create_enhanced_map(realtime_router.graph, routes, 'safest')
        m.save(str(MAP_PATH))
    except Exception as e:
        print(f"Warning: Could not update map: {e}")
    
    return jsonify({
        "success": True,
        "routes": routes,
        "notifications": notifications,
        "message": "Routes recomputed with updated road conditions"
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

