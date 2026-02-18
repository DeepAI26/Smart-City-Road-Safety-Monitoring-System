"""
Real-time Adaptation Module for Dynamic Re-routing
This module handles real-time problem detection, graph weight updates,
and dynamic route recalculation.
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from haversine import haversine
from routing import find_nearest_node, edge_cost, recompute_all_edge_weights

# Handle optional imports
try:
    from model_inference import RoadSafetyDetector, calculate_safety_score_from_condition
    MODEL_INFERENCE_AVAILABLE = True
except Exception as e:
    RoadSafetyDetector = None
    calculate_safety_score_from_condition = None
    MODEL_INFERENCE_AVAILABLE = False

from utils import get_node_coords


class RealTimeRouter:
    """
    Manages real-time route adaptation based on newly detected road conditions.
    """
    
    def __init__(self, graph: nx.DiGraph, model_detector: Optional[RoadSafetyDetector] = None):
        """
        Initialize the real-time router.
        
        Args:
            graph: The road network graph
            model_detector: Optional YOLO model detector for real-time inference
        """
        self.graph = graph.copy()  # Work with a copy to preserve original
        self.model_detector = model_detector
        self.original_weights = {}  # Store original edge weights
        self.detected_problems = {}  # Track detected problems by node
        
        # Store original weights
        for u, v, data in self.graph.edges(data=True):
            self.original_weights[(u, v)] = data.get("weight", data.get("distance", 1.0))
    
    def update_node_safety(self, node: str, safety_score: float, 
                          road_condition: str, problem_type: str = "none"):
        """
        Update the safety score of a specific node in the graph.
        
        Args:
            node: Node identifier
            safety_score: New safety score (0-1)
            road_condition: Road condition classification
            problem_type: Type of problem detected
        """
        if node not in self.graph.nodes:
            return False
        
        # Update node attributes
        self.graph.nodes[node]['safety'] = safety_score
        self.graph.nodes[node]['condition'] = road_condition
        self.graph.nodes[node]['problem'] = problem_type
        
        # Store detected problem
        self.detected_problems[node] = {
            'safety': safety_score,
            'condition': road_condition,
            'problem': problem_type
        }
        
        # Update all edges connected to this node
        self._update_connected_edges(node, safety_score)
        
        return True
    
    def _update_connected_edges(self, node: str, safety_score: float):
        """
        Update edge weights for all edges connected to a node.
        
        Args:
            node: Node identifier
            safety_score: Safety score to use for edge weight calculation
        """
        alpha = 2.0  # Safety penalty factor
        
        # Update outgoing edges
        for successor in self.graph.successors(node):
            edge_data = self.graph[node][successor]
            distance = edge_data.get("distance", 0.0)
            # Use the node's safety score for the edge
            edge_data["safety"] = safety_score
            edge_data["weight"] = edge_cost(distance, safety_score, alpha=alpha)
        
        # Update incoming edges
        for predecessor in self.graph.predecessors(node):
            edge_data = self.graph[predecessor][node]
            distance = edge_data.get("distance", 0.0)
            edge_data["safety"] = safety_score
            edge_data["weight"] = edge_cost(distance, safety_score, alpha=alpha)
    
    def detect_and_update(self, image_path: str, gps_coords: Tuple[float, float]) -> Dict:
        """
        Detect road problems from an image and update the graph.
        
        Args:
            image_path: Path to the image file
            gps_coords: GPS coordinates (lat, lon) of the image location
            
        Returns:
            Dictionary with detection results and update status
        """
        if not self.model_detector:
            return {
                'success': False,
                'message': 'Model detector not available'
            }
        
        # Find nearest node to GPS coordinates
        nearest_node = find_nearest_node(self.graph, gps_coords)
        
        # Run detection
        detection_result = self.model_detector.detect_hazards(image_path)
        
        # Update graph with new safety information
        self.update_node_safety(
            nearest_node,
            detection_result['safety_score'],
            detection_result['road_condition'],
            detection_result['problem_type']
        )
        
        return {
            'success': True,
            'node': nearest_node,
            'detection': detection_result,
            'message': f"Updated node {nearest_node} with safety score {detection_result['safety_score']:.2f}"
        }
    
    def simulate_problem_detection(self, gps_coords: Tuple[float, float], 
                                  road_condition: str, problem_type: str = "none"):
        """
        Simulate problem detection without using the model (for testing).
        
        Args:
            gps_coords: GPS coordinates (lat, lon)
            road_condition: "safe", "minor_issue", or "major_problem"
            problem_type: Type of problem
        """
        nearest_node = find_nearest_node(self.graph, gps_coords)
        safety_score = calculate_safety_score_from_condition(road_condition, problem_type)
        
        self.update_node_safety(nearest_node, safety_score, road_condition, problem_type)
        
        return {
            'success': True,
            'node': nearest_node,
            'safety_score': safety_score,
            'condition': road_condition,
            'problem': problem_type
        }
    
    def get_alternative_routes(self, start_gps: Tuple[float, float], 
                              end_gps: Tuple[float, float], 
                              current_route: List[str],
                              num_alternatives: int = 3) -> List[Dict]:
        """
        Find alternative routes when problems are detected on the current route.
        
        Args:
            start_gps: Start GPS coordinates
            end_gps: End GPS coordinates
            current_route: List of nodes in the current route
            num_alternatives: Number of alternative routes to find
            
        Returns:
            List of alternative route dictionaries
        """
        from routing import dijkstra_route, astar_route
        
        alternatives = []
        
        # Find routes using different algorithms and weight functions
        try:
            # Safest route (using updated weights)
            safest = dijkstra_route(self.graph, start_gps, end_gps, weight_key="weight")
            if safest['path'] != current_route:
                alternatives.append({
                    'type': 'safest',
                    'route': safest,
                    'algorithm': 'Dijkstra (safety-weighted)'
                })
        except:
            pass
        
        try:
            # Shortest route (ignoring safety)
            shortest = dijkstra_route(self.graph, start_gps, end_gps, weight_key="distance")
            if shortest['path'] != current_route:
                alternatives.append({
                    'type': 'shortest',
                    'route': shortest,
                    'algorithm': 'Dijkstra (distance-only)'
                })
        except:
            pass
        
        try:
            # A* optimized route
            optimized = astar_route(self.graph, start_gps, end_gps)
            if optimized['path'] != current_route:
                alternatives.append({
                    'type': 'optimized',
                    'route': optimized,
                    'algorithm': 'A* (heuristic)'
                })
        except:
            pass
        
        # Sort by safety score (descending)
        alternatives.sort(key=lambda x: x['route']['avg_safety'], reverse=True)
        
        return alternatives[:num_alternatives]
    
    def check_route_for_problems(self, route: List[str]) -> Dict:
        """
        Check if the current route has any detected problems.
        
        Args:
            route: List of nodes in the route
            
        Returns:
            Dictionary with problem information
        """
        problems = []
        
        for node in route:
            if node in self.detected_problems:
                problem_info = self.detected_problems[node]
                if problem_info['safety'] < 0.7:  # Threshold for problems
                    problems.append({
                        'node': node,
                        'safety': problem_info['safety'],
                        'condition': problem_info['condition'],
                        'problem': problem_info['problem'],
                        'location': (
                            self.graph.nodes[node]['latitude'],
                            self.graph.nodes[node]['longitude']
                        )
                    })
        
        return {
            'has_problems': len(problems) > 0,
            'problem_count': len(problems),
            'problems': problems,
            'route_safety': min([p['safety'] for p in problems]) if problems else 1.0
        }
    
    def reset_to_original(self):
        """Reset all edge weights to their original values."""
        for (u, v), original_weight in self.original_weights.items():
            if self.graph.has_edge(u, v):
                self.graph[u][v]['weight'] = original_weight
        self.detected_problems.clear()
    
    def get_route_notification(self, route: Dict, alternatives: List[Dict]) -> Dict:
        """
        Generate user notification information for a route.
        
        Args:
            route: Current route dictionary
            alternatives: List of alternative routes
            
        Returns:
            Notification dictionary with alerts and suggestions
        """
        route_problems = self.check_route_for_problems(route['path'])
        
        notifications = []
        alerts = []
        
        # Check route safety
        if route['avg_safety'] < 0.3:
            alerts.append({
                'type': 'critical',
                'message': 'Route contains hazardous road conditions!',
                'severity': 'high'
            })
        elif route['avg_safety'] < 0.7:
            alerts.append({
                'type': 'warning',
                'message': 'Route may have some road issues',
                'severity': 'medium'
            })
        
        # Check for specific problems
        if route_problems['has_problems']:
            for problem in route_problems['problems']:
                alerts.append({
                    'type': 'hazard',
                    'message': f"Detected {problem['problem']} on route",
                    'severity': 'high' if problem['safety'] < 0.4 else 'medium',
                    'location': problem['location']
                })
        
        # Compare with alternatives
        if alternatives:
            best_alternative = alternatives[0]
            time_diff = best_alternative['route']['travel_time'] - route['travel_time']
            distance_diff = best_alternative['route']['distance'] - route['distance']
            
            if best_alternative['route']['avg_safety'] > route['avg_safety'] + 0.1:
                notifications.append({
                    'type': 'suggestion',
                    'message': f"Alternative route available: {time_diff:+.1f} min, {distance_diff:+.2f} km",
                    'safety_improvement': best_alternative['route']['avg_safety'] - route['avg_safety'],
                    'alternative': best_alternative
                })
        
        return {
            'alerts': alerts,
            'notifications': notifications,
            'route_safety': route['avg_safety'],
            'has_problems': route_problems['has_problems'],
            'problem_count': route_problems['problem_count']
        }

