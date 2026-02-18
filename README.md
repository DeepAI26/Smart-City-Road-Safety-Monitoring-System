# Smart-City-Road-Safety-Monitoring-System

---

**@author:** Rishi Rakeshkumar Modi, Deep Patel, Aryan Parekh, Harshiv Patel  
**@course:** COSC 3P71  
**@project:** #1  
**@Student I'd:** 7606551, 7453921, 7646888, 7499700  
**@version:** 1.0  
**@since:** 23/12/2025 before 4:00 PM  

---

## DataSet
This folder contains the original raw dataset used in the project. It includes:

- All unprocessed road images collected during data acquisition  
- `metadata.csv`, which stores annotations such as timestamps, GPS coordinates, and road condition labels.  

This folder represents the initial data source before any labeling or model preparation.

---

## Merger
This is the post-annotation dataset folder, created after labeling the images.  
It includes:

- Images used for training and evaluation  
- responding YOLO label files for each image  
- `classes.txt`, which lists all hazard categories (e.g., potholes, cracks, traffic signs, etc.)  
- A JSON file containing structured annotation information  

This folder serves as the final formatted dataset used for YOLO model training.

---

## my_model
This folder contains the trained YOLO model and its outputs.  
It includes:

- `my_model.pt`: the final trained YOLO model  
- `train`: training artifacts such as confusion matrix, precision, recall, F1-score, box plots, and loss curves  
- `runs`: model predictions on validation and test datasets, including output images with bounding boxes  

This folder captures both model performance metrics and inference results.

---

## Web_app
This folder contains all components required for web deployment and visualization.  
It includes:

- Flask backend files for hosting the application  
- A Folium-based interactive map for visualizing image captures locations using GPS coordinates  
- `index.html`, which serves as the main frontend for the web application  

This folder demonstrates the deployment and visualization layer of the project.

---

## map.py
It creates a Folium map based on the GPS coordinates of the images in the dataset.  
It has segments rather than dots on the map for a particular coordinate.  
It is color-coded based on the road condition label.

- Red: Potholes (major)  
- Blue: Cracks (minor)  
- Green: Safe (none)  

---

## map_view.py
Builds a safety-aware road graph from GPS points (CSV) and visualizes it on an interactive Folium map with optional route drawing.  

- Reads and sorts GPS points by timestamp, then creates nodes/edges with distance and safety penalty weights  
- Saves the road network as either a pickle graph (`.pkl`) or a portable adjacency list (`.json`)  
- Renders points color-coded by safety (green/orange/red)  
- Supports click-to-select start/end or display a computed route  

Only used for `app.py`

---

## routing.py
This module computes safety-aware the shortest routes between two GPS locations using Dijkstra and A* search on a road network graph.

- Maps raw GPS coordinates to the nearest graph nodes using Haversine distance  
- Uses a custom edge cost function that penalizes unsafe road segments  
- Returns detailed route statistics including total distance, average safety, and travel time  

Only used for `app.py`

---

## graph.py
This script builds a safety-aware directed road network graph from GPS data for use in routing and navigation algorithms.

- Converts GPS/image locations into nodes and road segments into weighted edges  
- Accounts for one-way vs two-way roads and penalizes unsafe segments  
- Saves the graph as a reusable file for Dijkstra or A* pathfinding  

---

## graph_list.py
This script builds a safety-aware road graph from GPS data and exports it as a JSON adjacency list for easy routing and analysis.

---

## utils.py
Utility functions for path management, safety score calculation, and common operations used across the project.

---

## model_inference.py
YOLO model inference module for real-time road condition detection.  
Calculates safety scores from detected hazards.

---

## realtime_adaptation.py
Real-time routing adaptation system that handles dynamic graph updates and route recalculation when problems are detected.

---

## run_project.py
Main script to set up and run the project.  
Checks dependencies, builds graph if needed, and starts the web application.

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
