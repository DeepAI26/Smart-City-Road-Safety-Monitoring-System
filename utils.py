"""
Utility functions for the Smart City AI Project
Common functions used across multiple modules
"""

from pathlib import Path
from typing import Tuple, Dict


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent


def get_data_path() -> Path:
    """Get the path to the DataSet directory."""
    return get_project_root() / "DataSet"


def get_csv_path() -> Path:
    """Get the path to metadata_auto.csv."""
    return get_data_path() / "metadata_auto.csv"


def calculate_safety_score(road_condition: str, problem_type: str = "none") -> float:
    """
    Calculate safety score from road condition and problem type.
    
    Args:
        road_condition: "safe", "minor_issue", or "major_problem"
        problem_type: Type of problem (pothole, flooding, crack, etc.)
        
    Returns:
        Safety score between 0.0 (unsafe) and 1.0 (safe)
    """
    # Base safety scores by condition
    if road_condition == "safe":
        return 0.9
    elif road_condition == "minor_issue":
        # Adjust based on problem type
        if problem_type in ["crack", "cracks"]:
            return 0.5
        elif problem_type in ["debris", "construction"]:
            return 0.4
        else:
            return 0.45
    else:  # major_problem
        if problem_type in ["pothole", "potholes"]:
            return 0.2
        elif problem_type in ["flooding", "flood"]:
            return 0.15
        elif problem_type in ["construction"]:
            return 0.3
        else:
            return 0.25


def get_node_coords(G, node) -> Tuple[float, float]:
    """
    Get coordinates from a node, handling both 'latitude'/'longitude' and 'lat'/'lon' attributes.
    
    Args:
        G: NetworkX graph
        node: Node identifier
        
    Returns:
        Tuple of (latitude, longitude)
    """
    node_data = G.nodes[node]
    lat = node_data.get("latitude", node_data.get("lat", 0.0))
    lon = node_data.get("longitude", node_data.get("lon", 0.0))
    return (float(lat), float(lon))

