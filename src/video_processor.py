"""
Video Processing Module
Handles video input, frame extraction, and preprocessing
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging
import os
from PIL import Image
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, max_frames: int = 30, max_duration: int = 120):
        """
        Initialize video processor
        
        Args:
            max_frames: Maximum number of frames to extract
            max_duration: Maximum video duration in seconds
        """
        self.max_frames = max_frames
        self.max_duration = max_duration
    
    def extract_frames(self, video_path: str) -> List[dict]:
        """
        Extract frames from video at regular intervals
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of frame data with timestamps
        """
        frames_data = []
        
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Validate duration
            if duration > self.max_duration:
                logger.warning(f"Video duration ({duration}s) exceeds maximum ({self.max_duration}s)")
                duration = self.max_duration
                total_frames = int(fps * self.max_duration)
            
            # Calculate frame interval
            frame_interval = max(1, total_frames // self.max_frames)
            
            logger.info(f"Processing video: {duration:.1f}s, {total_frames} frames, extracting every {frame_interval} frames")
            
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < self.max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Extract frame at interval
                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps if fps > 0 else 0
                    
                    # Convert frame to base64 for processing
                    frame_base64 = self._frame_to_base64(frame)
                    
                    frames_data.append({
                        'frame_number': frame_count,
                        'timestamp': timestamp,
                        'image': frame_base64,
                        'width': frame.shape[1],
                        'height': frame.shape[0]
                    })
                    
                    extracted_count += 1
                
                frame_count += 1
                
                # Stop if we've processed enough of the video
                if frame_count >= total_frames:
                    break
            
            cap.release()
            
            logger.info(f"Extracted {len(frames_data)} frames from video")
            return frames_data
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            raise
    
    def _frame_to_base64(self, frame: np.ndarray) -> str:
        """
        Convert OpenCV frame to base64 string
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            Base64 encoded image string
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Resize if too large (for API limits)
        max_size = (1024, 1024)
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_base64
    
    def validate_video(self, video_path: str) -> tuple[bool, str]:
        """
        Validate video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(video_path):
                return False, "Video file not found"
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return False, "Cannot open video file"
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return False, "Video has no frames"
            
            duration = total_frames / fps if fps > 0 else 0
            
            if duration > self.max_duration:
                return False, f"Video duration ({duration:.1f}s) exceeds maximum ({self.max_duration}s)"
            
            cap.release()
            return True, "Video is valid"
            
        except Exception as e:
            return False, f"Error validating video: {str(e)}"
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            info = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration': 0
            }
            
            if info['fps'] > 0:
                info['duration'] = info['frame_count'] / info['fps']
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}
