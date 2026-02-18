# Component 4: Intelligent Navigation System - Complete Solution

## Overview

This document provides a complete implementation guide for **Component 4: Intelligent Navigation System** as specified in the Smart City AI Industry Project assignment. The solution includes all required features:

1. **Safe Path Algorithm** - Dijkstra's, A*, and custom weight functions
2. **Route Planning Interface** - User interface with multiple route options
3. **Real-time Adaptation** - Dynamic re-routing based on detected problems
4. **User Notification System** - Alerts and alternative route suggestions

## Files Created/Modified

### New Files

1. **`model_inference.py`** - YOLO model inference for real-time road condition detection
2. **`realtime_adaptation.py`** - Real-time routing adaptation and dynamic re-routing
3. **`web_app/app_enhanced.py`** - Enhanced Flask application with all Component 4 features
4. **`web_app/templates/index_enhanced.html`** - Modern web interface with notifications

### Modified Files

1. **`routing.py`** - Fixed node attribute access (latitude/longitude compatibility)
2. **`map_view.py`** - Updated to handle both latitude/lat and longitude/lon attributes

## Component 4 Features Implementation

### 1. Safe Path Algorithm

**Location:** `routing.py`, `dijkstra.py`, `astar.py`

**Features:**
- ✅ **Dijkstra's Algorithm** - Finds shortest path using distance or safety-weighted edges
- ✅ **A* Algorithm** - Optimized pathfinding with heuristic function
- ✅ **Custom Weight Function** - Combines distance and safety scores:
  ```python
  weight = distance * (1 + alpha * (1 - safety))
  ```

**Usage:**
```python
from routing import dijkstra_route, astar_route

# Shortest route (distance only)
shortest = dijkstra_route(G, start_gps, end_gps, weight_key="distance")

# Safest route (safety-weighted)
safest = dijkstra_route(G, start_gps, end_gps, weight_key="weight")

# Optimized route (A*)
optimized = astar_route(G, start_gps, end_gps)
```

### 2. Route Planning Interface

**Location:** `web_app/app_enhanced.py`, `web_app/templates/index_enhanced.html`

**Features:**
- ✅ **Interactive Map** - Click to select start and end points
- ✅ **Multiple Route Options** - Displays shortest, safest, and optimized routes
- ✅ **Safety Classifications** - Color-coded routes based on safety probability:
  - 🟢 **Safe** (p < 0.3)
  - 🟠 **Possibly Hazardous** (0.3 ≤ p < 0.7)
  - 🔴 **Hazardous** (p ≥ 0.7)
- ✅ **Route Statistics** - Shows distance, travel time, and safety score for each route
- ✅ **Visual Comparison** - Side-by-side route visualization with safety legend

**Route Display:**
- Distance in kilometers
- Estimated travel time in minutes
- Average safety score as percentage
- Safety classification badge

### 3. Real-time Adaptation

**Location:** `realtime_adaptation.py`

**Features:**
- ✅ **Real-time Problem Detection** - Uses YOLO model to detect hazards in images
- ✅ **Dynamic Graph Updates** - Updates edge weights when problems are detected
- ✅ **Dynamic Re-routing** - Automatically recalculates routes when conditions change
- ✅ **Alternative Route Suggestions** - Provides multiple route options when problems are detected

**Key Functions:**

```python
from realtime_adaptation import RealTimeRouter

# Initialize router
router = RealTimeRouter(graph, model_detector)

# Detect and update from image
result = router.detect_and_update(image_path, gps_coords)

# Simulate problem detection (for testing)
router.simulate_problem_detection(gps_coords, "major_problem", "pothole")

# Get alternative routes
alternatives = router.get_alternative_routes(start_gps, end_gps, current_route)

# Check route for problems
problems = router.check_route_for_problems(route_path)
```

**How It Works:**
1. When a problem is detected (via model or simulation), the safety score of the affected node is updated
2. All edges connected to that node are recalculated with new weights
3. Routes are automatically recomputed using updated graph weights
4. Alternative routes are suggested if the current route has problems

### 4. User Notification System

**Location:** `realtime_adaptation.py`, `web_app/templates/index_enhanced.html`

**Features:**
- ✅ **Route Alerts** - Warns users about hazardous conditions on selected route
- ✅ **Problem Notifications** - Alerts for specific hazards (potholes, flooding, etc.)
- ✅ **Alternative Route Suggestions** - Recommends safer routes with explanations
- ✅ **Time/Distance Comparisons** - Shows time savings or delays for alternative routes
- ✅ **Safety Improvements** - Displays safety score improvements for alternatives

**Notification Types:**
- 🚨 **Critical Alerts** - High severity hazards detected
- ⚠️ **Warnings** - Medium severity issues
- 💡 **Suggestions** - Alternative route recommendations

**Example Notification:**
```
⚠️ Route may have some road issues
🚨 Detected pothole on route
💡 Alternative route available: +2.3 min, +0.15 km (Safety improvement: +0.25)
```

## Installation and Setup

### Prerequisites

```bash
pip install flask networkx folium haversine ultralytics torch torchvision opencv-python pandas numpy
```

### Running the Application

1. **Ensure graph is built:**
   ```bash
   python graph.py
   ```

2. **Start the enhanced web application:**
   ```bash
   cd web_app
   python app_enhanced.py
   ```

3. **Access the application:**
   - Open browser to `http://localhost:5000`
   - Click on map to set start and end points
   - Click "Find Routes" to get AI-powered route suggestions

## API Endpoints

### POST `/api/route`
Compute routes between two GPS coordinates.

**Request:**
```json
{
  "start_lat": 43.124,
  "start_lon": -79.222,
  "end_lat": 43.125,
  "end_lon": -79.220
}
```

**Response:**
```json
{
  "success": true,
  "routes": {
    "shortest": {...},
    "safest": {...},
    "optimized": {...}
  },
  "notifications": {...},
  "map_file": "static/map/road_map.html"
}
```

### POST `/api/simulate-problem`
Simulate real-time problem detection at a location.

**Request:**
```json
{
  "lat": 43.124,
  "lon": -79.222,
  "condition": "major_problem",
  "problem_type": "pothole"
}
```

### POST `/api/recompute-routes`
Recompute routes after real-time updates.

**Request:**
```json
{
  "start_lat": 43.124,
  "start_lon": -79.222,
  "end_lat": 43.125,
  "end_lon": -79.220
}
```

## Safety Score Calculation

Safety scores are calculated based on:
1. **Model Inference** - YOLO model detects hazards and calculates risk
2. **Hazard Weights** - Different hazards have different severity:
   - Pothole: 0.9 (very dangerous)
   - Flooding: 0.95 (very dangerous)
   - Construction: 0.7 (moderate)
   - Debris: 0.6 (moderate)
   - Cracks: 0.4 (minor)

3. **Safety Score Formula:**
   ```
   safety_score = 1.0 - normalized_risk
   normalized_risk = total_risk / max_possible_risk
   ```

## Route Classification

Routes are classified based on average safety score:

| Safety Score | Classification | Color | Icon |
|-------------|----------------|-------|------|
| p < 0.3 | Safe | Green | ✓ |
| 0.3 ≤ p < 0.7 | Possibly Hazardous | Orange | ⚠ |
| p ≥ 0.7 | Hazardous | Red | ⚠ |

## Testing the System

### 1. Basic Route Planning
1. Open the web application
2. Click on map to set start point
3. Click again to set end point
4. Click "Find Routes"
5. View three route options with safety classifications

### 2. Real-time Adaptation
1. Compute a route first
2. Use "Simulate Problem Detection" to add a hazard
3. Click "Recompute Routes" to see updated routes
4. Observe how routes change to avoid the hazard

### 3. Notifications
1. Select a route with known problems
2. View alerts in the "Alerts & Notifications" section
3. See alternative route suggestions with comparisons

## Deliverables Checklist

✅ **Navigation System Implementation**
- Dijkstra's algorithm for shortest safe path
- A* algorithm for optimized pathfinding
- Custom weight function combining distance and safety

✅ **User Interface**
- Web-based application (Flask)
- Interactive map for route selection
- Multiple route display with safety ratings
- Travel time and distance estimates

✅ **Real-time Detection and Re-routing**
- Simulate real-time problem detection
- Dynamic re-routing when new problems detected
- Graph weight updates based on new information
- Alternative route suggestions

✅ **System Architecture Documentation**
- This documentation file
- Code comments and docstrings
- API documentation

## File Structure

```
IndustryProject01/
├── model_inference.py          # YOLO model inference
├── realtime_adaptation.py      # Real-time routing adaptation
├── routing.py                  # Core routing algorithms
├── dijkstra.py                 # Dijkstra implementation
├── astar.py                    # A* implementation
├── graph.py                    # Graph construction
├── map_view.py                 # Map visualization
├── web_app/
│   ├── app_enhanced.py         # Enhanced Flask app
│   ├── templates/
│   │   └── index_enhanced.html # Enhanced UI
│   └── static/
│       └── map/
│           └── road_map.html    # Generated map
└── COMPONENT4_DOCUMENTATION.md # This file
```

## Future Enhancements

Potential improvements for the system:
1. Real-time GPS tracking integration
2. Mobile app version
3. Historical data analysis
4. Machine learning for route prediction
5. Integration with traffic data APIs
6. Multi-user collaborative problem reporting

## Troubleshooting

### Graph not loading
- Ensure `road_graph.pkl` exists
- Run `graph.py` to generate the graph

### Model not loading
- Check if `my_model/my_model.pt` exists
- System will work without model (uses simulation mode)

### Routes not computing
- Verify GPS coordinates are within graph bounds
- Check that start and end points are connected in graph

## Contact

For questions or issues, refer to the project README or contact the development team.

