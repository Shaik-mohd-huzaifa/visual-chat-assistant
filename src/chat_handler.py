"""
Chat Handler Module
Handles multi-turn conversations with context retention
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
import json

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles multi-turn conversations using Nebius AI models"""
    
    def __init__(self, conversation_manager):
        """
        Initialize chat handler with Nebius AI Gemma-3-27B
        
        Args:
            conversation_manager: ConversationManager instance
        """
        self.conversation_manager = conversation_manager
        
        # Use Nebius AI Studio with OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=os.getenv("NEBIUS_API_KEY")
        )
        
        # Use Google Gemma-3-27B for chat interactions
        self.model = "google/gemma-3-27b-it"
        
        # System prompt for the assistant
        self.system_prompt = """You are an intelligent visual understanding assistant specializing in video analysis. 
        You have access to video analysis results including detected events, summaries, and guideline adherence information.
        
        Your capabilities include:
        1. Answering questions about analyzed videos
        2. Providing detailed explanations of events
        3. Discussing guideline violations and safety concerns
        4. Maintaining context across multiple conversation turns
        5. Helping users understand temporal relationships between events
        
        Be informative, precise, and helpful. When discussing events, reference specific timestamps when available.
        If asked about something not in the video analysis, clearly state that information is not available."""
    
    async def process_message(self, session_id: str, message: str) -> str:
        """
        Process a user message and generate response
        
        Args:
            session_id: Session identifier
            message: User message
            
        Returns:
            Assistant response
        """
        try:
            # Add user message to history
            self.conversation_manager.add_message(session_id, 'user', message)
            
            # Get conversation context
            history = self.conversation_manager.get_conversation_history(session_id, limit=10)
            video_analysis = self.conversation_manager.get_video_analysis(session_id)
            context = self.conversation_manager.get_context(session_id)
            
            # Build messages for LLM
            messages = self._build_messages(history, video_analysis, context, message)
            
            # Generate response
            response = await self._generate_response(messages)
            
            # Add assistant response to history
            self.conversation_manager.add_message(session_id, 'assistant', response)
            
            # Update context if needed
            self._update_context_from_conversation(session_id, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your message. Please try again."
    
    def _build_messages(self, history: List[Dict], video_analysis: Optional[Dict], 
                       context: Dict, current_message: str) -> List[Dict]:
        """
        Build messages array for LLM
        
        Args:
            history: Conversation history
            video_analysis: Video analysis data
            context: Session context
            current_message: Current user message
            
        Returns:
            Messages array for LLM
        """
        messages = []
        
        # Add system prompt
        system_content = self.system_prompt
        
        # Add video analysis context if available
        if video_analysis:
            system_content += f"\n\nVideo Analysis Available:\n"
            system_content += f"Summary: {video_analysis.get('summary', 'No summary available')}\n"
            system_content += f"Total Events: {len(video_analysis.get('events', []))}\n"
            
            guidelines = video_analysis.get('guidelines', {})
            system_content += f"Guideline Compliance: {guidelines.get('compliance_status', 'Unknown')}\n"
            system_content += f"Violations: {guidelines.get('violations_count', 0)}\n"
            
            # Add recent events for context
            events = video_analysis.get('events', [])[:5]  # First 5 events
            if events:
                system_content += "\nSample Events:\n"
                for event in events:
                    system_content += f"- [{event.get('timestamp', 0):.1f}s] {event.get('description', 'No description')}\n"
        
        messages.append({"role": "system", "content": system_content})
        
        # Add conversation history (excluding current message)
        for msg in history[:-1]:  # Exclude the just-added user message
            if msg['role'] in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    async def _generate_response(self, messages: List[Dict]) -> str:
        """
        Generate response using LLM
        
        Args:
            messages: Messages array for LLM
            
        Returns:
            Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _update_context_from_conversation(self, session_id: str, message: str, response: str):
        """
        Update session context based on conversation
        
        Args:
            session_id: Session identifier
            message: User message
            response: Assistant response
        """
        # Detect if user is asking about specific topics
        topics = []
        
        keywords = {
            'traffic': ['traffic', 'vehicle', 'car', 'pedestrian', 'light', 'road'],
            'safety': ['safety', 'violation', 'danger', 'hazard', 'risk'],
            'timeline': ['when', 'time', 'timestamp', 'sequence', 'order'],
            'summary': ['summary', 'overview', 'summarize', 'brief']
        }
        
        message_lower = message.lower()
        for topic, words in keywords.items():
            if any(word in message_lower for word in words):
                topics.append(topic)
        
        if topics:
            self.conversation_manager.update_context(session_id, 'current_topics', topics)
    
    async def answer_specific_query(self, session_id: str, query_type: str, 
                                   parameters: Dict) -> str:
        """
        Answer specific types of queries about the video
        
        Args:
            session_id: Session identifier
            query_type: Type of query (e.g., 'event_at_time', 'violation_details')
            parameters: Query parameters
            
        Returns:
            Specific answer
        """
        video_analysis = self.conversation_manager.get_video_analysis(session_id)
        
        if not video_analysis:
            return "No video has been analyzed yet. Please upload a video first."
        
        events = video_analysis.get('events', [])
        guidelines = video_analysis.get('guidelines', {})
        
        if query_type == 'event_at_time':
            timestamp = parameters.get('timestamp', 0)
            # Find events near this timestamp
            nearby_events = [
                e for e in events 
                if abs(e.get('timestamp', 0) - timestamp) < 2.0
            ]
            
            if nearby_events:
                response = f"Events around {timestamp}s:\n"
                for event in nearby_events:
                    response += f"- [{event.get('timestamp', 0):.1f}s] {event.get('description', 'No description')}\n"
                return response
            else:
                return f"No events found around {timestamp}s"
        
        elif query_type == 'violation_details':
            violations = guidelines.get('violations', [])
            if violations:
                response = "Detected violations:\n"
                for v in violations:
                    response += f"- [{v.get('timestamp', 0):.1f}s] {v.get('description', 'No description')} (Severity: {v.get('severity', 'unknown')})\n"
                return response
            else:
                return "No violations detected in the video."
        
        elif query_type == 'event_summary':
            event_type = parameters.get('event_type', '')
            filtered_events = [
                e for e in events 
                if event_type.lower() in e.get('event_type', '').lower()
            ]
            
            if filtered_events:
                response = f"Found {len(filtered_events)} {event_type} events:\n"
                for event in filtered_events[:5]:  # Limit to 5
                    response += f"- [{event.get('timestamp', 0):.1f}s] {event.get('description', 'No description')}\n"
                return response
            else:
                return f"No {event_type} events found in the video."
        
        return "Query type not recognized."
    
    def get_conversation_summary(self, session_id: str) -> str:
        """
        Generate a summary of the conversation
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation summary
        """
        history = self.conversation_manager.get_conversation_history(session_id)
        
        if not history:
            return "No conversation history available."
        
        # Extract key points from conversation
        user_questions = [msg['content'] for msg in history if msg['role'] == 'user']
        
        summary = f"Conversation Summary:\n"
        summary += f"Total exchanges: {len([m for m in history if m['role'] == 'user'])}\n"
        summary += f"Topics discussed: "
        
        # Identify topics
        topics = set()
        for q in user_questions:
            q_lower = q.lower()
            if 'event' in q_lower:
                topics.add('events')
            if 'violation' in q_lower or 'guideline' in q_lower:
                topics.add('violations')
            if 'summary' in q_lower:
                topics.add('summary')
            if 'time' in q_lower or 'when' in q_lower:
                topics.add('timeline')
        
        summary += ", ".join(topics) if topics else "general"
        
        return summary
