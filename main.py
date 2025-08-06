"""
Visual Understanding Chat Assistant
Main application server with FastAPI
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from src.video_processor import VideoProcessor
from src.event_recognizer import EventRecognizer
from src.chat_handler import ChatHandler
from src.conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Visual Understanding Chat Assistant",
    description="An AI-powered assistant for video analysis and conversation",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
video_processor = VideoProcessor()
event_recognizer = EventRecognizer()
conversation_manager = ConversationManager()
chat_handler = ChatHandler(conversation_manager)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class VideoAnalysisResponse(BaseModel):
    session_id: str
    events: list
    summary: str
    guideline_adherence: dict

class ChatResponse(BaseModel):
    response: str
    session_id: str
    context_retained: bool

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/api/upload-video", response_model=VideoAnalysisResponse)
async def upload_video(
    file: UploadFile = File(...),
    session_id: Optional[str] = None
):
    """
    Upload and analyze a video file
    """
    try:
        # Validate video file
        if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            raise HTTPException(status_code=400, detail="Invalid video format")
        
        # Save uploaded video temporarily
        temp_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process video
        logger.info(f"Processing video: {file.filename}")
        frames = video_processor.extract_frames(temp_path)
        
        # Recognize events
        events = event_recognizer.detect_events(frames)
        
        # Generate summary and check guideline adherence
        summary, guidelines = event_recognizer.generate_summary(events)
        
        # Create or update session
        if not session_id:
            session_id = conversation_manager.create_session()
        
        # Store video analysis in session
        conversation_manager.store_video_analysis(
            session_id, events, summary, guidelines
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return VideoAnalysisResponse(
            session_id=session_id,
            events=events,
            summary=summary,
            guideline_adherence=guidelines
        )
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Handle chat messages with context retention
    """
    try:
        # Get or create session
        session_id = message.session_id or conversation_manager.create_session()
        
        # Process message with context
        response = await chat_handler.process_message(
            session_id=session_id,
            message=message.message
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            context_retained=True
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve session information
    """
    try:
        session_data = conversation_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_data
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session
    """
    try:
        conversation_manager.clear_session(session_id)
        return {"message": "Session cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)
