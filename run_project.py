"""
Main script to run the Smart City AI Industry Project
This script provides an easy way to set up and run the project
"""

import sys
from pathlib import Path
import subprocess

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pandas', 'numpy', 'networkx', 'haversine', 
        'flask', 'folium', 'cv2', 'torch', 'ultralytics'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False
    return True

def build_graph():
    """Build the road graph from CSV data."""
    print("Building road graph...")
    try:
        from graph import G
        print(f"✓ Graph built successfully: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return True
    except Exception as e:
        print(f"✗ Error building graph: {e}")
        return False

def run_web_app(enhanced=True):
    """Run the Flask web application."""
    if enhanced:
        app_file = "web_app/app_enhanced.py"
    else:
        app_file = "web_app/app.py"
    
    print(f"\nStarting web application: {app_file}")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, app_file])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"Error running web app: {e}")

def main():
    """Main entry point."""
    print("=" * 60)
    print("Smart City AI Industry Project - Setup & Run")
    print("=" * 60)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed")
    
    # Check if graph exists
    graph_path = Path("road_graph.pkl")
    if not graph_path.exists():
        print("\n2. Graph not found. Building graph...")
        if not build_graph():
            print("Failed to build graph. Please check your CSV file.")
            sys.exit(1)
    else:
        print("\n2. Graph file found ✓")
    
    # Ask user which app to run
    print("\n3. Starting web application...")
    print("Choose application:")
    print("  1. Enhanced app (Component 4 - Full features)")
    print("  2. Basic app (Simple routing)")
    
    choice = input("\nEnter choice (1 or 2, default=1): ").strip()
    enhanced = choice != "2"
    
    # Run the app
    run_web_app(enhanced=enhanced)

if __name__ == "__main__":
    main()

