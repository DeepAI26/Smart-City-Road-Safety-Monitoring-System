"""
Model Inference Module for Real-time Road Condition Detection
This module provides functionality to run YOLO model inference on images
and calculate safety scores based on detected hazards.
"""

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except Exception as e:
    YOLO = None
    ULTRALYTICS_AVAILABLE = False

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class RoadSafetyDetector:
    """
    A class for detecting road hazards using a trained YOLO model.
    Calculates safety scores and classifies road conditions in real-time.
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.25):
        """
        Initialize the road safety detector.
        
        Args:
            model_path: Path to the trained YOLO model (.pt file)
            confidence_threshold: Minimum confidence for detections
        """
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("ultralytics package is required for RoadSafetyDetector. Install it with: pip install ultralytics")
        
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        if TORCH_AVAILABLE:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = 'cpu'
        
        # Hazard categories and their severity weights
        # Higher weight = more dangerous
        self.hazard_weights = {
            'pothole': 0.9,      # Very dangerous
            'flooding': 0.95,    # Very dangerous
            'construction': 0.7,  # Moderate danger
            'debris': 0.6,       # Moderate danger
            'cracks': 0.4        # Minor issue
        }
    def detect_hazards(self, image_path: str) -> Dict:
        """
        Detect hazards in a road image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing detection results, safety score, and classification
        """
        # Run inference
        results = self.model(image_path, conf=self.confidence_threshold, device=self.device)
        
        detections = []
        total_risk = 0.0
        
        # Process detections
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    # Get class name and confidence
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Calculate risk contribution
                    hazard_weight = self.hazard_weights.get(class_name.lower(), 0.5)
                    risk_contribution = confidence * hazard_weight
                    total_risk += risk_contribution
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'risk': risk_contribution
                    })
        
        # Calculate safety score (0-1 scale, where 1 is safest)
        # Normalize risk to safety score
        # More detections and higher confidence = lower safety
        max_possible_risk = len(detections) * 1.0  # Assuming max confidence and weight
        if max_possible_risk > 0:
            normalized_risk = min(total_risk / max_possible_risk, 1.0)
        else:
            normalized_risk = 0.0
        
        safety_score = 1.0 - normalized_risk
        
        # Classify road condition based on safety score
        if safety_score >= 0.7:
            condition = "safe"
            problem_type = "none"
        elif safety_score >= 0.4:
            condition = "minor_issue"
            # Determine most common problem type
            if detections:
                problem_type = max(set([d['class'] for d in detections]), 
                                 key=[d['class'] for d in detections].count)
            else:
                problem_type = "unknown"
        else:
            condition = "major_problem"
            if detections:
                problem_type = max(set([d['class'] for d in detections]), 
                                 key=[d['class'] for d in detections].count)
            else:
                problem_type = "unknown"
        
        return {
            'detections': detections,
            'safety_score': float(safety_score),
            'road_condition': condition,
            'problem_type': problem_type,
            'num_hazards': len(detections),
            'total_risk': float(total_risk)
        }
    
    def detect_from_array(self, image_array: np.ndarray) -> Dict:
        """
        Detect hazards from a numpy image array (for real-time processing).
        
        Args:
            image_array: NumPy array representing the image (BGR format)
            
        Returns:
            Dictionary containing detection results
        """
        # Run inference on array
        results = self.model(image_array, conf=self.confidence_threshold, device=self.device)
        
        detections = []
        total_risk = 0.0
        
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    hazard_weight = self.hazard_weights.get(class_name.lower(), 0.5)
                    risk_contribution = confidence * hazard_weight
                    total_risk += risk_contribution
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'risk': risk_contribution
                    })
        
        # Calculate safety score
        max_possible_risk = len(detections) * 1.0 if detections else 1.0
        normalized_risk = min(total_risk / max_possible_risk, 1.0) if max_possible_risk > 0 else 0.0
        safety_score = 1.0 - normalized_risk
        
        # Classify condition
        if safety_score >= 0.7:
            condition = "safe"
            problem_type = "none"
        elif safety_score >= 0.4:
            condition = "minor_issue"
            problem_type = max(set([d['class'] for d in detections]), 
                             key=[d['class'] for d in detections].count) if detections else "unknown"
        else:
            condition = "major_problem"
            problem_type = max(set([d['class'] for d in detections]), 
                             key=[d['class'] for d in detections].count) if detections else "unknown"
        
        return {
            'detections': detections,
            'safety_score': float(safety_score),
            'road_condition': condition,
            'problem_type': problem_type,
            'num_hazards': len(detections),
            'total_risk': float(total_risk)
        }


def calculate_safety_score_from_condition(road_condition: str, problem_type: str = "none") -> float:
    """
    Calculate safety score from road condition and problem type.
    Used when model inference is not available.
    
    Args:
        road_condition: "safe", "minor_issue", or "major_problem"
        problem_type: Type of problem detected
        
    Returns:
        Safety score between 0.0 and 1.0
    """
    if road_condition == "safe":
        return 0.9
    elif road_condition == "minor_issue":
        # Adjust based on problem type
        if problem_type in ["cracks"]:
            return 0.5
        elif problem_type in ["debris", "construction"]:
            return 0.4
        else:
            return 0.45
    else:  # major_problem
        if problem_type in ["pothole", "flooding"]:
            return 0.2
        elif problem_type in ["construction"]:
            return 0.3
        else:
            return 0.25

