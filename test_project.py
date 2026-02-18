"""
Test script for Smart City AI Industry Project
Tests all components and functionality
"""

import sys
from pathlib import Path

def test_imports():
    """Test if required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Checking Dependencies")
    print("=" * 60)
    
    required_modules = {
        'pandas': 'pandas',
        'networkx': 'networkx',
        'folium': 'folium',
        'haversine': 'haversine',
        'flask': 'flask',
        'cv2': 'opencv-python',
        'torch': 'torch',
        'ultralytics': 'ultralytics'
    }
    
    missing = []
    available = []
    
    for module_name, package_name in required_modules.items():
        try:
            if module_name == 'cv2':
                __import__('cv2')
            else:
                __import__(module_name)
            available.append(package_name)
            print(f"✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"✗ {package_name} - NOT INSTALLED")
    
    print(f"\nAvailable: {len(available)}/{len(required_modules)}")
    if missing:
        print(f"Missing: {', '.join(missing)}")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        return False
    return True

def test_files():
    """Test if required files exist."""
    print("\n" + "=" * 60)
    print("TEST 2: Checking Required Files")
    print("=" * 60)
    
    required_files = {
        'DataSet/metadata_auto.csv': 'Dataset CSV file',
        'road_graph.pkl': 'Graph file (will be created if missing)',
        'graph.py': 'Graph construction script',
        'routing.py': 'Routing algorithms',
        'web_app/app_enhanced.py': 'Enhanced web application',
        'utils.py': 'Utility functions'
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        path = Path(file_path)
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path:40s} - {description}")
        if not exists and file_path != 'road_graph.pkl':
            all_exist = False
    
    return all_exist

def test_utils():
    """Test utility functions."""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Utility Functions")
    print("=" * 60)
    
    try:
        from utils import get_csv_path, calculate_safety_score, get_project_root
        
        # Test path functions
        root = get_project_root()
        csv_path = get_csv_path()
        print(f"✓ Project root: {root}")
        print(f"✓ CSV path: {csv_path}")
        print(f"✓ CSV exists: {csv_path.exists()}")
        
        # Test safety score calculation
        scores = {
            ('safe', 'none'): calculate_safety_score('safe', 'none'),
            ('minor_issue', 'crack'): calculate_safety_score('minor_issue', 'crack'),
            ('major_problem', 'pothole'): calculate_safety_score('major_problem', 'pothole')
        }
        
        print("\nSafety Score Calculations:")
        for (condition, problem), score in scores.items():
            print(f"  {condition}/{problem}: {score:.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing utils: {e}")
        return False

def test_graph_construction():
    """Test graph construction."""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Graph Construction")
    print("=" * 60)
    
    try:
        import pandas as pd
        from utils import get_csv_path, calculate_safety_score
        
        csv_path = get_csv_path()
        if not csv_path.exists():
            print("✗ CSV file not found")
            return False
        
        # Load and check CSV
        df = pd.read_csv(csv_path)
        print(f"✓ CSV loaded: {len(df)} rows")
        print(f"✓ Columns: {list(df.columns)}")
        
        # Check if safety_score exists or needs calculation
        if 'safety_score' not in df.columns:
            print("  → Safety scores will be calculated automatically")
            df['safety_score'] = df.apply(
                lambda row: calculate_safety_score(
                    str(row.get("road_condition", "safe")),
                    str(row.get("problem_type", "none"))
                ),
                axis=1
            )
            print(f"✓ Safety scores calculated: {df['safety_score'].min():.2f} - {df['safety_score'].max():.2f}")
        
        # Check graph file
        graph_path = Path('road_graph.pkl')
        if graph_path.exists():
            import pickle
            with open(graph_path, 'rb') as f:
                G = pickle.load(f)
            print(f"✓ Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
            return True
        else:
            print("  → Graph file not found (run 'python graph.py' to create)")
            return False
            
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Install with: pip install pandas")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_routing():
    """Test routing algorithms."""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Routing Algorithms")
    print("=" * 60)
    
    try:
        import pickle
        from routing import dijkstra_route, astar_route, find_nearest_node
        
        graph_path = Path('road_graph.pkl')
        if not graph_path.exists():
            print("✗ Graph file not found (run 'python graph.py' first)")
            return False
        
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
        
        print(f"✓ Graph loaded: {G.number_of_nodes()} nodes")
        
        # Get sample coordinates from graph
        nodes = list(G.nodes())[:5]
        if len(nodes) < 2:
            print("✗ Not enough nodes in graph")
            return False
        
        # Get coordinates from first and last node
        node1_data = G.nodes[nodes[0]]
        node2_data = G.nodes[nodes[-1]]
        
        start = (
            node1_data.get("latitude", node1_data.get("lat", 0)),
            node1_data.get("longitude", node1_data.get("lon", 0))
        )
        end = (
            node2_data.get("latitude", node2_data.get("lat", 0)),
            node2_data.get("longitude", node2_data.get("lon", 0))
        )
        
        print(f"✓ Test route: {start} → {end}")
        
        # Test Dijkstra
        try:
            route = dijkstra_route(G, start, end, weight_key="weight")
            print(f"✓ Dijkstra route: {len(route['path'])} nodes, {route['distance']:.3f} km")
        except Exception as e:
            print(f"✗ Dijkstra error: {e}")
            return False
        
        # Test A*
        try:
            route = astar_route(G, start, end)
            print(f"✓ A* route: {len(route['path'])} nodes, {route['distance']:.3f} km")
        except Exception as e:
            print(f"✗ A* error: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app():
    """Test web application files."""
    print("\n" + "=" * 60)
    print("TEST 6: Testing Web Application")
    print("=" * 60)
    
    try:
        app_path = Path('web_app/app_enhanced.py')
        template_path = Path('web_app/templates/index_enhanced.html')
        
        if not app_path.exists():
            print("✗ Enhanced app not found")
            return False
        
        print(f"✓ App file exists: {app_path}")
        print(f"✓ Template exists: {template_path.exists()}")
        
        # Try to import (without running)
        import sys
        sys.path.insert(0, str(Path.cwd()))
        
        # Check if imports would work
        try:
            from routing import dijkstra_route, astar_route
            from realtime_adaptation import RealTimeRouter
            from model_inference import RoadSafetyDetector
            print("✓ All imports successful")
            return True
        except ImportError as e:
            print(f"✗ Import error: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SMART CITY AI PROJECT - TEST SUITE")
    print("=" * 60)
    
    results = {
        'Dependencies': test_imports(),
        'Files': test_files(),
        'Utils': test_utils(),
        'Graph': test_graph_construction(),
        'Routing': test_routing(),
        'Web App': test_web_app()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name:20s} - {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Project is ready!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - See details above")
        print("\nTo fix issues:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Build graph: python graph.py")
        print("3. Run tests again: python test_project.py")

if __name__ == "__main__":
    main()

