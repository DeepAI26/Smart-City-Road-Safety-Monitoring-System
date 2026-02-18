# Complete Setup Guide - Smart City AI Industry Project

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Build the Graph
```bash
python graph.py
```

### 3. Run the Application
```bash
# Option 1: Use the run script (recommended)
python run_project.py

# Option 2: Run directly
cd web_app
python app_enhanced.py
```

## Project Structure

```
IndustryProject01/
├── DataSet/                    # Raw dataset with images and metadata
│   ├── images/                 # Road images
│   └── metadata_auto.csv      # GPS coordinates and road conditions
├── Merger/                     # Annotated dataset for YOLO training
│   ├── images/                 # Training images
│   ├── labels/                 # YOLO format labels
│   └── classes.txt             # Hazard categories
├── my_model/                   # Trained YOLO model
│   └── my_model.pt             # Model weights
├── web_app/                    # Web application
│   ├── app.py                  # Basic Flask app
│   ├── app_enhanced.py         # Enhanced app with Component 4 features
│   ├── templates/              # HTML templates
│   └── static/                 # Static files (maps, etc.)
├── graph.py                    # Graph construction script
├── routing.py                  # Core routing algorithms
├── model_inference.py          # YOLO model inference
├── realtime_adaptation.py      # Real-time routing adaptation
├── utils.py                    # Utility functions
└── requirements.txt            # Python dependencies
```

## Component Overview

### Component 1: Data Collection and Annotation
- **Location**: `DataSet/` folder
- **Files**: Images and `metadata_auto.csv`
- **Status**: ✓ Complete

### Component 2: Geospatial Mapping and Graph Construction
- **Scripts**: `graph.py`, `grap_list.py`, `map.py`
- **Output**: `road_graph.pkl`, `adjacency_list.json`
- **Status**: ✓ Complete

### Component 3: AI Model Development
- **Location**: `my_model/` folder
- **Model**: `my_model.pt` (YOLO)
- **Status**: ✓ Complete

### Component 4: Intelligent Navigation System
- **Files**: 
  - `routing.py` - Core algorithms
  - `realtime_adaptation.py` - Dynamic routing
  - `model_inference.py` - Real-time detection
  - `web_app/app_enhanced.py` - Web interface
- **Status**: ✓ Complete

## Running Individual Components

### Build Graph
```bash
python graph.py
```

### Generate Adjacency List
```bash
python grap_list.py
```

### Create Visualization Map
```bash
python map.py
```

### Run Basic Web App
```bash
cd web_app
python app.py
```

### Run Enhanced Web App (Component 4)
```bash
cd web_app
python app_enhanced.py
```

## Troubleshooting

### Graph file not found
**Solution**: Run `python graph.py` to generate the graph

### CSV file not found
**Solution**: Ensure `DataSet/metadata_auto.csv` exists

### Import errors
**Solution**: 
1. Install all dependencies: `pip install -r requirements.txt`
2. Make sure you're in the correct directory
3. Check that all Python files are in the project root

### Model not loading
**Solution**: The app works without the model (uses simulation mode). 
If you want real detection, ensure `my_model/my_model.pt` exists.

### Port already in use
**Solution**: Change the port in the Flask app:
```python
app.run(debug=True, port=5001)
```

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB (16GB recommended for model training)
- **Storage**: 50GB free space
- **GPU**: Optional but recommended for model inference

## Features

### Basic Features
- Graph construction from GPS data
- Route planning with Dijkstra and A*
- Interactive map visualization
- Safety-aware routing

### Enhanced Features (Component 4)
- Real-time problem detection
- Dynamic route recalculation
- Multiple route options
- User notifications and alerts
- Safety classifications
- Alternative route suggestions

## API Endpoints (Enhanced App)

- `GET /` - Main web interface
- `POST /api/route` - Compute routes
- `POST /api/simulate-problem` - Simulate problem detection
- `POST /api/recompute-routes` - Recompute routes after updates

## Next Steps

1. Review the documentation files:
   - `COMPONENT4_DOCUMENTATION.md` - Detailed Component 4 docs
   - `COMPONENT4_QUICKSTART.md` - Quick start guide
   - `README.md` - Project overview

2. Test the system:
   - Build the graph
   - Run the web app
   - Test route planning
   - Try real-time simulation

3. Customize:
   - Adjust safety weights in `graph.py`
   - Modify UI in `templates/index_enhanced.html`
   - Add new features to `app_enhanced.py`

## Support

For issues or questions, refer to:
- Component 4 documentation
- Code comments in source files
- README.md for project overview

