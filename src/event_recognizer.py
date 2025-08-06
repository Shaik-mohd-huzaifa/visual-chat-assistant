"""
Event Recognition Module
Uses Vision Language Models to detect and analyze events in video frames
"""

import os
import base64
from typing import List, Dict, Tuple, Any
import json
from datetime import datetime
import io
from PIL import Image
import logging
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class EventRecognizer:
    """Handles event recognition in video frames using AI vision models"""
    
    def __init__(self):
        # Use Nebius AI Studio with OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=os.getenv("NEBIUS_API_KEY")
        )
        # Use Qwen2-VL-72B for vision tasks (multimodal model)
        self.model = "Qwen/Qwen2-VL-72B-Instruct"
        # Use Google Gemma-3-27B for chat/summarization tasks
        self.chat_model = "google/gemma-3-27b-it"
        
        # Define common guideline types for different scenarios
        self.guidelines = {
            "traffic": [
                "Traffic light compliance",
                "Speed limit adherence", 
                "Pedestrian right of way",
                "Lane discipline",
                "Stop sign compliance"
            ],
            "safety": [
                "PPE usage",
                "Hazard awareness",
                "Emergency procedures",
                "Equipment handling",
                "Restricted area access"
            ],
            "general": [
                "Activity detection",
                "Object tracking",
                "Anomaly detection",
                "Pattern recognition"
            ]
        }
    
    def detect_events(self, frames: List[dict]) -> List[dict]:
        """
        Detect events in video frames using Vision Language Model
        
        Args:
            frames: List of frame data with base64 images
            
        Returns:
            List of detected events with timestamps
        """
        events = []
        
        try:
            # Analyze frames in batches for efficiency
            batch_size = 5
            for i in range(0, len(frames), batch_size):
                batch = frames[i:i+batch_size]
                batch_events = self._analyze_frame_batch(batch)
                events.extend(batch_events)
            
            # Sort events by timestamp
            events.sort(key=lambda x: x['timestamp'])
            
            logger.info(f"Detected {len(events)} events in video")
            return events
            
        except Exception as e:
            logger.error(f"Error detecting events: {str(e)}")
            return []
    
    def _analyze_frame_batch(self, frames: List[dict]) -> List[dict]:
        """
        Analyze a batch of frames for events
        
        Args:
            frames: Batch of frame data
            
        Returns:
            List of events detected in the batch
        """
        events = []
        
        try:
            # Prepare messages for GPT-4 Vision
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert video analyst with specialized knowledge in traffic laws, safety regulations, and behavioral analysis. 
                    
                    THOROUGHLY analyze these video frames for:
                    
                    1. TRAFFIC & VEHICLE ANALYSIS:
                       - Traffic light status (red, yellow, green)
                       - Vehicle movements and positions
                       - Lane changes, turns, stops
                       - Speed estimation (normal, fast, slow)
                       - Following distance
                       - Use of indicators/signals
                       - Parking violations
                       - Running red lights or stop signs
                    
                    2. PEDESTRIAN & CYCLIST ACTIVITY:
                       - Pedestrian crossings (jaywalking, crossing at signals)
                       - Pedestrian signal compliance
                       - Cyclist behavior and lane usage
                       - Near-miss incidents
                       - Right of way violations
                    
                    3. ENVIRONMENTAL CONTEXT:
                       - Road conditions (wet, dry, construction)
                       - Weather conditions
                       - Time of day/lighting conditions
                       - Road signs and markings
                       - Traffic control devices
                    
                    4. SAFETY & COMPLIANCE:
                       - Seatbelt usage (if visible)
                       - Phone usage while driving
                       - Aggressive driving behaviors
                       - Emergency vehicle interactions
                       - Construction zone compliance
                       - School zone violations
                    
                    5. GENERAL OBSERVATIONS:
                       - Unusual or noteworthy events
                       - Potential hazards
                       - Good driving practices observed
                       - Traffic flow patterns
                    
                    BE SPECIFIC: Instead of "traffic at intersection", describe "vehicle approaching red light at 15mph" or "pedestrians waiting at crosswalk with walk signal"
                    
                    Return a JSON array where EACH detected element gets its own entry:
                    {
                        "timestamp": float,
                        "event_type": "traffic_signal|vehicle_movement|pedestrian_activity|violation|hazard|environmental|other",
                        "description": "Detailed description of what is happening",
                        "objects": ["car", "pedestrian", "traffic_light", "crosswalk", etc.],
                        "location_in_frame": "top-left|top-center|top-right|center-left|center|center-right|bottom-left|bottom-center|bottom-right",
                        "severity": "info|low|medium|high|critical",
                        "guideline_violation": boolean,
                        "violation_details": "Specific law or guideline violated if applicable",
                        "confidence": 0.0-1.0
                    }"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze these {len(frames)} frames from a video. The timestamps are: " + 
                                   ", ".join([f"{f['timestamp']:.1f}s" for f in frames])
                        }
                    ]
                }
            ]
            
            # Add frame images to the message
            for frame in frames:
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame['image']}"
                    }
                })
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                # Find JSON array in response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    detected_events = json.loads(json_str)
                    
                    # Add frame information to events
                    for event in detected_events:
                        event['frame_number'] = self._find_closest_frame(
                            event.get('timestamp', 0), frames
                        )
                    
                    events.extend(detected_events)
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON from response, using fallback")
                # Fallback: create a general event
                for frame in frames:
                    events.append({
                        "timestamp": frame['timestamp'],
                        "frame_number": frame['frame_number'],
                        "event_type": "scene",
                        "description": "Scene captured",
                        "objects": [],
                        "severity": "low",
                        "guideline_violation": False,
                        "violation_details": None
                    })
            
            return events
            
        except Exception as e:
            logger.error(f"Error analyzing frame batch: {str(e)}")
            return []
    
    def _find_closest_frame(self, timestamp: float, frames: List[dict]) -> int:
        """
        Find the frame number closest to a given timestamp
        """
        closest_frame = frames[0]['frame_number']
        min_diff = abs(frames[0]['timestamp'] - timestamp)
        
        for frame in frames[1:]:
            diff = abs(frame['timestamp'] - timestamp)
            if diff < min_diff:
                min_diff = diff
                closest_frame = frame['frame_number']
        
        return closest_frame
    
    def generate_summary(self, events: List[dict]) -> tuple[str, dict]:
        """
        Generate a comprehensive summary of events and guideline adherence
        
        Args:
            events: List of detected events
            
        Returns:
            tuple of (summary_text, guideline_adherence_dict)
        """
        try:
            if not events:
                return "No significant events detected in the video.", {}
            
            # Analyze guideline violations
            violations = [e for e in events if e.get('guideline_violation', False)]
            high_severity = [e for e in events if e.get('severity') == 'high']
            medium_severity = [e for e in events if e.get('severity') == 'medium']
            
            # Build summary using Nebius AI
            messages = [
                {
                    "role": "system",
                    "content": """You are a video analysis expert. Create a DETAILED and COMPREHENSIVE summary of the video based on detected events.
                    
                    Your summary MUST include:
                    
                    1. SCENE OVERVIEW:
                       - Location type (intersection, highway, parking lot, etc.)
                       - Environmental conditions (weather, lighting, road conditions)
                       - Time of day and visibility
                    
                    2. TRAFFIC ELEMENTS:
                       - Traffic signal states and changes
                       - Traffic signs visible
                       - Road markings and lanes
                    
                    3. VEHICLE ACTIVITY:
                       - Number and types of vehicles
                       - Vehicle movements (turns, stops, lane changes)
                       - Speed and following distance
                       - Signal usage
                    
                    4. PEDESTRIAN/CYCLIST ACTIVITY:
                       - Number of pedestrians/cyclists
                       - Crossing behavior
                       - Signal compliance
                       - Interactions with vehicles
                    
                    5. VIOLATIONS & SAFETY CONCERNS:
                       - Traffic law violations (be specific: "ran red light at 5.2s", "failed to stop at crosswalk")
                       - Near-miss incidents
                       - Unsafe behaviors
                       - Right-of-way violations
                    
                    6. POSITIVE OBSERVATIONS:
                       - Proper signal compliance
                       - Safe driving practices
                       - Courteous behaviors
                    
                    7. TEMPORAL FLOW:
                       - How events unfold chronologically
                       - Cause-and-effect relationships
                    
                    Be SPECIFIC with timestamps and descriptions. Don't just say "traffic violation" - explain exactly what happened.
                    
                    Length: 250-400 words for thoroughness."""
                },
                {
                    "role": "user",
                    "content": f"Events detected in video:\n{json.dumps(events, indent=2)}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.chat_model,  # Uses google/gemma-3-27b-it
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            # Compile guideline adherence report
            guideline_adherence = {
                "total_events": len(events),
                "violations_count": len(violations),
                "high_severity_count": len(high_severity),
                "medium_severity_count": len(medium_severity),
                "violation_rate": len(violations) / len(events) if events else 0,
                "violations": [
                    {
                        "timestamp": v['timestamp'],
                        "description": v.get('violation_details', v['description']),
                        "severity": v['severity']
                    }
                    for v in violations
                ],
                "compliance_status": "Good" if len(violations) == 0 else 
                                   "Needs Attention" if len(violations) <= 2 else "Poor"
            }
            
            return summary, guideline_adherence
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Error generating summary", {}
    
    def analyze_specific_guidelines(self, events: List[dict], guideline_type: str = "general") -> dict:
        """
        Analyze events against specific guidelines
        
        Args:
            events: List of detected events
            guideline_type: Type of guidelines to check (traffic, safety, general)
            
        Returns:
            Detailed guideline analysis
        """
        guidelines = self.guidelines.get(guideline_type, self.guidelines["general"])
        
        analysis = {
            "guideline_type": guideline_type,
            "checked_guidelines": guidelines,
            "results": {}
        }
        
        for guideline in guidelines:
            # Check if any events relate to this guideline
            related_events = [
                e for e in events 
                if guideline.lower() in e.get('description', '').lower() or 
                   guideline.lower() in e.get('violation_details', '').lower()
            ]
            
            analysis["results"][guideline] = {
                "related_events": len(related_events),
                "violations": len([e for e in related_events if e.get('guideline_violation', False)]),
                "status": "Pass" if not any(e.get('guideline_violation', False) for e in related_events) else "Fail"
            }
        
        return analysis
