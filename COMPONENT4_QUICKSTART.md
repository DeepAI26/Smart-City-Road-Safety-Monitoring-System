# Component 4 Quick Start Guide

## Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install flask networkx folium haversine ultralytics torch torchvision opencv-python pandas numpy
```

### Step 2: Ensure Graph Exists
If `road_graph.pkl` doesn't exist, run:
```bash
python graph.py
```

### Step 3: Start the Application
```bash
cd web_app
python app_enhanced.py
```

### Step 4: Open Browser
Navigate to: `http://localhost:5000`

## Basic Usage

1. **Select Start Point**: Click anywhere on the map
2. **Select End Point**: Click again on the map
3. **Find Routes**: Click the "Find Routes" button
4. **View Results**: See three route options with safety classifications

## Testing Real-time Features

1. **Compute a route first** (follow steps above)
2. **Simulate Problem**: 
   - Select a problem type (pothole, flooding, etc.)
   - Select severity (major/minor)
   - Click "Simulate Problem Detection"
3. **Recompute Routes**: Click "Recompute Routes" to see updated paths
4. **View Notifications**: Check the "Alerts & Notifications" section

## Route Types Explained

- **Shortest Route**: Minimizes distance only
- **Safest Route (AI)**: Prioritizes safety using weighted algorithm
- **Optimized Route (A*)**: Balanced approach using A* heuristic

## Safety Classifications

- 🟢 **Safe** (p < 0.3): Route is safe to travel
- 🟠 **Possibly Hazardous** (0.3 ≤ p < 0.7): Route may have issues
- 🔴 **Hazardous** (p ≥ 0.7): Route contains hazardous conditions

## Troubleshooting

**Graph not found?**
- Run `python graph.py` from the IndustryProject01 directory

**Model not loading?**
- The app works without the model (uses simulation mode)
- Ensure `my_model/my_model.pt` exists if you want real detection

**Routes not computing?**
- Make sure start and end points are within the map area
- Check that the graph has nodes in that region

## Next Steps

For detailed documentation, see `COMPONENT4_DOCUMENTATION.md`

