"""
Conversation Manager Module
Manages conversation sessions and context retention
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, max_history: int = 10, session_timeout_minutes: int = 30):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of messages to retain per session
            session_timeout_minutes: Session timeout in minutes
        """
        self.sessions: Dict[str, Dict] = {}
        self.max_history = max_history
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(self) -> str:
        """
        Create a new conversation session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'conversation_history': [],
            'video_analysis': None,
            'context': {}
        }
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session has expired
            if datetime.now() - session['last_activity'] > self.session_timeout:
                logger.info(f"Session {session_id} has expired")
                self.clear_session(session_id)
                return None
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
        return session
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """
        Add a message to conversation history
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Additional metadata
        """
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found")
            return
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        session['conversation_history'].append(message)
        
        # Trim history if it exceeds max limit
        if len(session['conversation_history']) > self.max_history * 2:
            # Keep system messages and recent history
            system_messages = [
                m for m in session['conversation_history'] 
                if m['role'] == 'system'
            ]
            recent_messages = session['conversation_history'][-(self.max_history * 2):]
            
            # Combine, removing duplicates
            session['conversation_history'] = system_messages + [
                m for m in recent_messages if m not in system_messages
            ]
        
        logger.debug(f"Added {role} message to session {session_id}")
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        session = self.get_session(session_id)
        
        if not session:
            return []
        
        history = session['conversation_history']
        
        if limit:
            return history[-limit:]
        
        return history
    
    def store_video_analysis(self, session_id: str, events: List[Dict], 
                            summary: str, guidelines: Dict):
        """
        Store video analysis results in session
        
        Args:
            session_id: Session identifier
            events: Detected events
            summary: Video summary
            guidelines: Guideline adherence information
        """
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session {session_id} not found")
            return
        
        session['video_analysis'] = {
            'events': events,
            'summary': summary,
            'guidelines': guidelines,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Add system message about video analysis
        self.add_message(
            session_id,
            'system',
            f"Video analyzed. Found {len(events)} events. Summary: {summary[:200]}...",
            {'type': 'video_analysis'}
        )
        
        logger.info(f"Stored video analysis for session {session_id}")
    
    def get_video_analysis(self, session_id: str) -> Optional[Dict]:
        """
        Get video analysis results for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Video analysis data or None
        """
        session = self.get_session(session_id)
        
        if session:
            return session.get('video_analysis')
        
        return None
    
    def update_context(self, session_id: str, context_key: str, context_value: Any):
        """
        Update session context
        
        Args:
            session_id: Session identifier
            context_key: Context key
            context_value: Context value
        """
        session = self.get_session(session_id)
        
        if session:
            session['context'][context_key] = context_value
            logger.debug(f"Updated context '{context_key}' for session {session_id}")
    
    def get_context(self, session_id: str) -> Dict:
        """
        Get session context
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session context dictionary
        """
        session = self.get_session(session_id)
        
        if session:
            return session.get('context', {})
        
        return {}
    
    def clear_session(self, session_id: str):
        """
        Clear a conversation session
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def clear_expired_sessions(self):
        """
        Clear all expired sessions
        """
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleared {len(expired_sessions)} expired sessions")
    
    def get_active_sessions_count(self) -> int:
        """
        Get count of active sessions
        
        Returns:
            Number of active sessions
        """
        self.clear_expired_sessions()
        return len(self.sessions)
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export session data as JSON
        
        Args:
            session_id: Session identifier
            
        Returns:
            JSON string or None
        """
        session = self.get_session(session_id)
        
        if session:
            # Convert datetime objects to strings
            export_data = {
                'id': session['id'],
                'created_at': session['created_at'].isoformat(),
                'last_activity': session['last_activity'].isoformat(),
                'conversation_history': session['conversation_history'],
                'video_analysis': session['video_analysis'],
                'context': session['context']
            }
            
            return json.dumps(export_data, indent=2)
        
        return None
