import cv2
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
import json

from ultralytics import YOLO
from shapely.geometry import Point, Polygon


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float = 1.0
    
    @property
    def bottom_center(self) -> Tuple[float, float]:
        """Bottom-center point - represents player's ground position"""
        return ((self.x1 + self.x2) / 2, self.y2)
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1


# ============================================================================
# COURT DETECTION
# ============================================================================

class CourtDetector:
    """Handles court boundary detection/annotation"""
    
    def __init__(self):
        self.court_polygon = None
    
    def annotate_court_manual(self, frame: np.ndarray) -> Polygon:
        """Manual court annotation via mouse clicks - 50% size display"""
        points = []
        
        # Resize frame to 50% of original size
        display_frame = frame.copy()
        height, width = frame.shape[:2]
        
        # Set to 50% of screen size
        scale = 0.5
        new_width = int(width * scale)
        new_height = int(height * scale)
        display_frame = cv2.resize(display_frame, (new_width, new_height))
        print(f"Display scaled to {new_width}x{new_height} (50% of original)")
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convert back to original coordinates
                original_x = int(x / scale)
                original_y = int(y / scale)
                points.append((original_x, original_y))
                
                # Draw on display
                cv2.circle(display_frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(display_frame, f"{len(points)}", (x+10, y+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Court Annotation', display_frame)
                
                if len(points) == 4:
                    scaled_points = [(int(p[0]*scale), int(p[1]*scale)) for p in points]
                    pts = np.array(scaled_points, np.int32)
                    cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                    cv2.imshow('Court Annotation', display_frame)
        
        cv2.namedWindow('Court Annotation', cv2.WINDOW_NORMAL)
        cv2.imshow('Court Annotation', display_frame)
        cv2.setMouseCallback('Court Annotation', mouse_callback)
        
        print("\n" + "="*60)
        print("COURT ANNOTATION (50% Screen Size)")
        print("="*60)
        print("Click 4 corners in this order:")
        print("  1. Top-Left")
        print("  2. Top-Right")
        print("  3. Bottom-Right")
        print("  4. Bottom-Left")
        print("\nPress any key when done")
        print("="*60 + "\n")
        
        while len(points) < 4:
            key = cv2.waitKey(1) & 0xFF
            if key != 255:  # Any key pressed
                break
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        if len(points) == 4:
            self.court_polygon = Polygon(points)
            print(f"✓ Court corners saved: {points}")
            return self.court_polygon
        
        raise ValueError("Need exactly 4 points for court annotation")
    
    def load_court(self, court_points: List[Tuple[float, float]]) -> Polygon:
        """Load court from predefined points"""
        self.court_polygon = Polygon(court_points)
        return self.court_polygon
    
    def is_in_court(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside court"""
        if self.court_polygon is None:
            return True
        return self.court_polygon.contains(Point(point))


# ============================================================================
# DETECTION
# ============================================================================

class PersonDetector:
    """YOLO11-based person detection"""
    
    def __init__(self, model_name: str = 'yolo11x.pt'):
        """
        Use YOLO11 for detection
        Options: yolo11n.pt (fast), yolo11s.pt, yolo11m.pt, yolo11l.pt, yolo11x.pt (accurate)
        """
        print(f"Loading {model_name}...")
        self.model = YOLO(model_name)
        print("✓ Model loaded")
    
    def detect(self, frame: np.ndarray, conf_thresh: float = 0.4) -> List[BBox]:
        """Detect all persons in frame"""
        results = self.model(frame, classes=[0], conf=conf_thresh, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                detections.append(BBox(x1, y1, x2, y2, conf))
        
        return detections


class DetectionFilter:
    """Filter detections based on court boundaries"""
    
    def __init__(
        self,
        court_detector: CourtDetector,
        min_height: float = 60,
        min_conf: float = 0.4
    ):
        self.court_detector = court_detector
        self.min_height = min_height
        self.min_conf = min_conf
    
    def filter(self, detections: List[BBox]) -> List[BBox]:
        """Apply filters to keep only valid detections"""
        filtered = []
        
        for det in detections:
            if det.conf < self.min_conf:
                continue
            
            if not self.court_detector.is_in_court(det.bottom_center):
                continue
            
            if det.height < self.min_height:
                continue
            
            filtered.append(det)
        
        return filtered


# ============================================================================
# MAIN PIPELINE
# ============================================================================

class BadmintonPlayerDetector:
    """Simple player detection pipeline - returns bottom-center coordinates"""
    
    def __init__(
        self,
        video_path: str,
        court_points: Optional[List[Tuple[float, float]]] = None,
        output_dir: str = 'output',
        model_name: str = 'yolo11x.pt',
        save_video: bool = True
    ):
        self.video_path = video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.model_name = model_name
        self.save_video = save_video
        
        # Initialize components
        self.court_detector = CourtDetector()
        if court_points:
            self.court_detector.load_court(court_points)
        
        self.detector = PersonDetector(model_name)
        self.filter = DetectionFilter(self.court_detector)
        
        # Storage
        self.detection_data = []
    
    def run(self, annotate_court: bool = False):
        """Run detection pipeline"""
        print("=" * 60)
        print("BADMINTON PLAYER DETECTION")
        print(f"Model: {self.model_name}")
        print("=" * 60)
        
        if annotate_court or self.court_detector.court_polygon is None:
            print("\n[1/3] Court Annotation (50% Screen Size)")
            self._annotate_court()
        else:
            print("\n[1/3] Court Loaded")
        
        print("\n[2/3] Player Detection")
        self._detect_players()
        
        print("\n[3/3] Saving Results")
        self._save_results()
        
        if self.save_video:
            print("\n[BONUS] Creating Detection Video")
            self._create_detection_video()
        
        print("\n" + "=" * 60)
        print("DETECTION COMPLETE!")
        print(f"Results saved to: {self.output_dir}")
        print("=" * 60)
    
    def _annotate_court(self):
        """Annotate court boundaries"""
        cap = cv2.VideoCapture(self.video_path)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError("Could not read video")
        
        self.court_detector.annotate_court_manual(frame.copy())
    
    def _detect_players(self):
        """Detect players in all frames"""
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect persons
            detections = self.detector.detect(frame, conf_thresh=0.4)
            
            # Filter based on court boundaries
            filtered = self.filter.filter(detections)
            
            # Store detections for this frame
            frame_detections = {
                'frame': frame_idx,
                'players': []
            }
            
            for i, det in enumerate(filtered):
                bottom_center = det.bottom_center
                frame_detections['players'].append({
                    'player_id': i,
                    'x': float(bottom_center[0]),
                    'y': float(bottom_center[1]),
                    'bbox': {
                        'x1': float(det.x1),
                        'y1': float(det.y1),
                        'x2': float(det.x2),
                        'y2': float(det.y2)
                    },
                    'confidence': float(det.conf)
                })
            
            self.detection_data.append(frame_detections)
            
            if frame_idx % 100 == 0:
                print(f"  Processed {frame_idx}/{total_frames} frames", end='\r')
            
            frame_idx += 1
        
        cap.release()
        print(f"  Processed {frame_idx}/{total_frames} frames")
    
    def _save_results(self):
        """Save results to CSV and JSON"""
        # Create CSV data with up to 2 players per frame
        csv_data = []
        for item in self.detection_data:
            row = {
                'frame_no': item['frame'],
                'player_1_x': None,
                'player_1_y': None,
                'player_1_conf': None,
                'player_2_x': None,
                'player_2_y': None,
                'player_2_conf': None
            }
            
            players = item['players']
            if len(players) >= 1:
                row['player_1_x'] = players[0]['x']
                row['player_1_y'] = players[0]['y']
                row['player_1_conf'] = players[0]['confidence']
            
            if len(players) >= 2:
                row['player_2_x'] = players[1]['x']
                row['player_2_y'] = players[1]['y']
                row['player_2_conf'] = players[1]['confidence']
            
            csv_data.append(row)
        
        # Save to CSV
        df = pd.DataFrame(csv_data)
        csv_file = self.output_dir / 'player_detections.csv'
        df.to_csv(csv_file, index=False)
        print(f"  ✓ CSV saved to: {csv_file}")
        
        # Save JSON with full details
        json_file = self.output_dir / 'player_detections.json'
        output_data = {
            'video': str(self.video_path),
            'detection_method': 'yolo11_simple',
            'model': self.model_name,
            'detection_data': self.detection_data
        }
        
        with open(json_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"  ✓ JSON saved to: {json_file}")
    
    def _create_detection_video(self):
        """Create annotated video with detection visualizations"""
        cap = cv2.VideoCapture(self.video_path)
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Output video
        output_video = self.output_dir / 'detection_output.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_video), fourcc, fps, (width, height))
        
        # Draw court polygon once
        court_pts = None
        if self.court_detector.court_polygon:
            coords = list(self.court_detector.court_polygon.exterior.coords)
            court_pts = np.array(coords, dtype=np.int32)
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Draw court
            if court_pts is not None:
                cv2.polylines(frame, [court_pts], True, (255, 255, 0), 2)
            
            # Get detections for this frame
            detections = self.detection_data[frame_idx]
            
            # Draw each detected player
            colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255)]
            for i, player in enumerate(detections['players']):
                x = int(player['x'])
                y = int(player['y'])
                
                # Draw bounding box
                bbox = player['bbox']
                x1, y1 = int(bbox['x1']), int(bbox['y1'])
                x2, y2 = int(bbox['x2']), int(bbox['y2'])
                
                color = colors[i % len(colors)]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw bottom-center point
                cv2.circle(frame, (x, y), 8, color, -1)
                
                # Draw label
                label = f"P{i+1} ({player['confidence']:.2f})"
                cv2.putText(frame, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add frame counter
            cv2.putText(frame, f"Frame: {frame_idx}/{total_frames}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Players: {len(detections['players'])}", (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
            
            if frame_idx % 100 == 0:
                print(f"  Video: {frame_idx}/{total_frames} frames", end='\r')
            
            frame_idx += 1
        
        cap.release()
        out.release()
        print(f"\n  ✓ Detection video saved to: {output_video}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Option 1: With court annotation
    # detector = BadmintonPlayerDetector(
    #     video_path='F2.mp4',
    #     output_dir='output3',
    #     model_name='yolo11x.pt',  # Use yolo11s.pt for faster processing
    #     save_video=True
    # )
    # detector.run(annotate_court=True)
    
    #Option 2: Reuse court coordinates
    court_points = [
        (380, 280), 
        (902, 290), 
        (1094, 710), 
        (210, 700)
    ]

    detector = BadmintonPlayerDetector(
        video_path='video_fixed/output.mp4',
        court_points=court_points,
        output_dir='output',
        model_name='yolo11x.pt',
        save_video=True
    )
    detector.run()
