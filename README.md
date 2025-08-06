# 🎥 Visual Understanding Chat Assistant

An AI-powered video analysis system that detects events, identifies guideline violations, and enables intelligent multi-turn conversations about video content.

## 📋 Project Overview

The Visual Understanding Chat Assistant is an advanced AI system that processes video input to:
- **Detect and recognize events** in video streams
- **Identify guideline violations** (traffic rules, safety protocols, etc.)
- **Generate comprehensive summaries** of video content
- **Enable natural conversations** about the analyzed video with context retention
- **Provide temporal analysis** of events with precise timestamps

This solution leverages state-of-the-art Vision Language Models (VLMs) to understand visual content and maintain coherent, context-aware conversations about video analysis results.

## 🎬 Demo Video

Watch the Visual Understanding Chat Assistant in action:

Demo video link: https://www.loom.com/share/8fb0074375bb4a428776fd3d1f12e701?sid=df5e3fe6-80d6-4db9-a2f7-363d84c6b5fb

The demo showcases:
- Video upload and processing
- Real-time event detection with detailed analysis
- Traffic violation identification (red lights, pedestrian crossings)
- Interactive chat functionality
- Video playback with analysis results
- "Analyze Another Video" feature for seamless workflow

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (HTML/CSS/JavaScript)                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Endpoints                          │   │
│  │  • /api/upload-video  • /api/chat                       │   │
│  │  • /api/session/{id}  • /api/session/{id}/delete        │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬─────────────┬────────────┐
        ▼                         ▼             ▼            ▼
┌──────────────┐      ┌──────────────┐  ┌──────────┐  ┌──────────┐
│Video         │      │Event         │  │Chat      │  │Session   │
│Processor     │      │Recognizer    │  │Handler   │  │Manager   │
├──────────────┤      ├──────────────┤  ├──────────┤  ├──────────┤
│• Frame       │      │• GPT-4       │  │• Context │  │• History │
│  Extraction  │      │  Vision      │  │  Aware   │  │  Storage │
│• Validation  │      │• Event       │  │• Multi-  │  │• Context │
│• Preprocessing│     │  Detection   │  │  turn    │  │  Mgmt    │
└──────────────┘      │• Guideline   │  └──────────┘  └──────────┘
                      │  Analysis     │
                      └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  OpenAI APIs     │
                    │ • GPT-4 Vision   │
                    │ • GPT-4 Turbo    │
                    └──────────────────┘
```

### Component Description

1. **Video Processor**: Handles video input, validates duration limits, extracts frames at optimal intervals
2. **Event Recognizer**: Uses GPT-4 Vision to detect events, analyze scenes, and identify guideline violations
3. **Conversation Manager**: Maintains session state, conversation history, and video analysis context
4. **Chat Handler**: Processes natural language queries with context awareness and multi-turn capability
5. **FastAPI Backend**: RESTful API server handling all client requests
6. **Web Interface**: Modern, responsive UI for video upload and chat interaction

## 💻 Tech Stack Justification

### Backend Framework: **FastAPI**
- **Why FastAPI?**
  - Async support for handling concurrent video processing
  - Built-in data validation with Pydantic
  - Automatic API documentation
  - High performance for ML workloads
  - WebSocket support for real-time features

### AI/ML Models: **OpenAI GPT-4 Vision & GPT-4 Turbo**
- **Why GPT-4 Vision?**
  - State-of-the-art visual understanding capabilities
  - Can analyze multiple frames simultaneously
  - Excellent at detecting complex events and violations
  - Natural language output for summaries
- **Why GPT-4 Turbo?**
  - Superior context retention for multi-turn conversations
  - Advanced reasoning about video events
  - Consistent and coherent responses

### Video Processing: **OpenCV + Pillow**
- **Why this combination?**
  - OpenCV: Industry standard for video processing
  - Pillow: Efficient image manipulation and compression
  - Optimal frame extraction algorithms
  - Wide format support

### Data Management: **In-Memory Session Storage**
- **Why in-memory?**
  - Fast access for real-time chat
  - Simplified deployment for prototype
  - Adequate for session-based interactions
  - Easy to scale with Redis later

## 🚀 Setup and Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- 4GB+ RAM recommended
- Modern web browser

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/visual-chat-assistant.git
cd visual-chat-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
python main.py
```

The application will start on `http://localhost:8000`

## 📖 Usage Instructions

### 1. Upload a Video
- Open your browser and navigate to `http://localhost:8000`
- Click the upload area or drag and drop a video file
- Supported formats: MP4, AVI, MOV, MKV, WEBM
- Maximum duration: 2 minutes

### 2. Analyze the Video
- After uploading, click "Analyze Video"
- The system will:
  - Extract key frames from the video
  - Detect events and activities
  - Identify any guideline violations
  - Generate a comprehensive summary

### 3. View Analysis Results
- **Summary Tab**: Overall video summary and key findings
- **Events Tab**: Timeline of detected events with timestamps
- **Guidelines Tab**: Compliance report and violation details

### 4. Chat About the Video
- Ask questions about specific events
- Inquire about violations or safety concerns
- Request details about particular timestamps
- Get clarifications on the analysis

### Example Queries
```
"What happened at 15 seconds?"
"Were there any traffic violations?"
"Describe the pedestrian activities in the video"
"What safety concerns were identified?"
"Give me a timeline of all high-severity events"
```

## 🎯 Features

### Core Features Implemented

✅ **Video Event Recognition**
- Automatic detection of activities and interactions
- Object identification and tracking
- Temporal event sequencing

✅ **Guideline Adherence Analysis**
- Traffic rule compliance checking
- Safety protocol violation detection
- Severity classification (Low/Medium/High)

✅ **Video Summarization**
- Concise content summaries
- Key event highlighting
- Chronological event ordering

✅ **Multi-Turn Conversations**
- Context retention across queries
- Reference to previous discussions
- Intelligent follow-up handling

✅ **Agentic Workflow**
- Autonomous video analysis pipeline
- Smart frame selection
- Adaptive response generation

## 📊 API Documentation

### POST `/api/upload-video`
Upload and analyze a video file
```json
Request:
  - file: Video file (multipart/form-data)
  - session_id: Optional session ID

Response:
{
  "session_id": "uuid",
  "events": [...],
  "summary": "string",
  "guideline_adherence": {...}
}
```

### POST `/api/chat`
Send a chat message about the analyzed video
```json
Request:
{
  "message": "string",
  "session_id": "uuid"
}

Response:
{
  "response": "string",
  "session_id": "uuid",
  "context_retained": true
}
```

### GET `/api/session/{session_id}`
Retrieve session information

### DELETE `/api/session/{session_id}`
Clear a conversation session

## 🔧 Configuration

Edit `.env` file to customize:
```env
# API Keys
OPENAI_API_KEY=your_key_here

# Server Settings
HOST=0.0.0.0
PORT=8000

# Video Processing
MAX_VIDEO_DURATION_SECONDS=120
MAX_FRAMES_TO_ANALYZE=30

# Chat Settings
MAX_CONVERSATION_HISTORY=10
```

## 📈 Performance Considerations

- **Video Processing**: Optimized frame extraction (30 frames max)
- **API Calls**: Batch processing for efficiency
- **Memory Usage**: Automatic session cleanup after 30 minutes
- **Response Time**: Typical analysis completes in 10-30 seconds

## 🛠️ Development

### Project Structure
```
visual-chat-assistant/
├── src/
│   ├── video_processor.py      # Video handling logic
│   ├── event_recognizer.py     # Event detection with VLM
│   ├── conversation_manager.py # Session management
│   └── chat_handler.py         # Chat processing
├── static/
│   ├── index.html              # Web interface
│   ├── style.css               # Styling
│   └── app.js                  # Frontend logic
├── main.py                     # FastAPI application
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
└── README.md                  # Documentation
```

## 🚦 Future Enhancements

- [ ] Real-time video streaming support
- [ ] Multiple video comparison
- [ ] Custom guideline configuration
- [ ] Export analysis reports (PDF/JSON)
- [ ] Multi-language support
- [ ] GPU acceleration for video processing
- [ ] Persistent storage with database
- [ ] User authentication and authorization

## 📝 License

This project is developed for the Mantra Hackathon 2024.

## 👥 Contributors

- Your Name - Lead Developer

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision and GPT-4 Turbo APIs
- FastAPI community for the excellent framework
- OpenCV contributors for video processing capabilities

---

Built with ❤️ for the Mantra Hackathon
