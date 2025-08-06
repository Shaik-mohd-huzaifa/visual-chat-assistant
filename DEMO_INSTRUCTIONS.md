# 🎬 Demo Instructions for Visual Understanding Chat Assistant

## Quick Start Guide

### Step 1: Setup Environment

1. Open a terminal in the project directory:
```bash
cd C:\Users\Admin\CascadeProjects\visual-chat-assistant
```

2. Run the setup script:
```bash
python setup.py
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Configure OpenAI API Key

1. Open the `.env` file
2. Replace `your_openai_api_key_here` with your actual OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Run the Application

```bash
python main.py
```

You should see:
```
INFO: Starting server on 0.0.0.0:8000
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Access the Web Interface

Open your browser and navigate to: **http://localhost:8000**

## 📹 Demo Scenarios

### Scenario 1: Traffic Video Analysis

1. **Upload a traffic scene video** (dashcam footage, intersection recording, etc.)
2. Click **"Analyze Video"**
3. The system will:
   - Identify vehicles, pedestrians, traffic lights
   - Detect violations (running red lights, jaywalking, etc.)
   - Generate a summary of traffic patterns

4. **Example chat queries:**
   - "What traffic violations were detected?"
   - "Describe the pedestrian activity at 30 seconds"
   - "Were there any dangerous situations?"
   - "How many vehicles ran the red light?"

### Scenario 2: Safety Compliance Video

1. **Upload a workplace or construction site video**
2. The system will identify:
   - PPE compliance (helmets, safety vests)
   - Unsafe behaviors
   - Equipment handling violations

3. **Example chat queries:**
   - "Are all workers wearing proper safety equipment?"
   - "What safety violations occurred?"
   - "Describe the events between 10-20 seconds"

### Scenario 3: General Activity Recognition

1. **Upload any video with human activities**
2. The system will:
   - Recognize various activities
   - Track object interactions
   - Create a timeline of events

3. **Example chat queries:**
   - "What are people doing in this video?"
   - "When did the main event occur?"
   - "Summarize all activities chronologically"

## 🎥 Recording Your Demo Video

### Recommended Demo Structure

1. **Introduction (30 seconds)**
   - Show the application interface
   - Briefly explain the purpose

2. **Video Upload & Analysis (1-2 minutes)**
   - Upload a sample video
   - Show the analysis process
   - Display the results (events, summary, guidelines)

3. **Multi-turn Conversation (2-3 minutes)**
   - Ask various questions about the video
   - Show context retention between queries
   - Demonstrate follow-up questions

4. **Feature Highlights (1 minute)**
   - Show the three tabs (Summary, Events, Guidelines)
   - Highlight timestamp precision
   - Show violation detection

### Recording Tools

**Windows:**
- OBS Studio (free, professional)
- Windows Game Bar (Win + G)
- ShareX

**macOS:**
- QuickTime Player
- OBS Studio
- ScreenFlow

**Cross-platform:**
- Loom
- Chrome extensions (Screencastify, Nimbus)

### Demo Video Tips

1. **Prepare your content:**
   - Have 2-3 sample videos ready (under 2 minutes each)
   - Plan your questions in advance
   - Test the application beforehand

2. **During recording:**
   - Speak clearly and explain what you're doing
   - Show both successful and edge cases
   - Highlight unique features

3. **Post-production:**
   - Keep total length under 5 minutes
   - Add captions for key features
   - Include timestamps in description

## 🧪 Test Videos

### Where to Find Test Videos

1. **Pexels** (https://www.pexels.com/videos/)
   - Free stock videos
   - Traffic, workplace, activity scenes

2. **Pixabay** (https://pixabay.com/videos/)
   - No attribution required
   - Various scenarios

3. **YouTube** (download with permission)
   - Traffic compilation videos
   - Safety training videos
   - Security camera footage

### Recommended Test Scenarios

1. **Traffic intersection** - Shows vehicles, pedestrians, traffic lights
2. **Construction site** - Safety compliance checking
3. **Retail store** - Customer behavior analysis
4. **Sports activity** - Event sequence detection
5. **Security footage** - Anomaly detection

## 🐛 Troubleshooting

### Common Issues

**1. "OpenAI API key not found"**
- Ensure `.env` file exists
- Check API key is correctly set
- Restart the application

**2. "Video processing failed"**
- Check video format (MP4, AVI, MOV, MKV, WEBM)
- Ensure video is under 2 minutes
- Try a smaller resolution video

**3. "Cannot connect to server"**
- Check if port 8000 is available
- Try running on a different port: `PORT=8080 python main.py`
- Check firewall settings

**4. "Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

## 📊 Performance Tips

1. **For faster processing:**
   - Use videos under 1 minute initially
   - Lower resolution videos (720p or less)
   - Ensure good internet connection (for API calls)

2. **For better results:**
   - Use clear, well-lit videos
   - Avoid shaky footage
   - Include relevant scenarios for guideline checking

## 📝 Demo Checklist

Before recording your demo:

- [ ] Application runs without errors
- [ ] OpenAI API key is configured
- [ ] Test videos are ready
- [ ] Browser console shows no errors
- [ ] All three tabs display data correctly
- [ ] Chat responds appropriately
- [ ] Session management works

## 🚀 Submission Ready

Once you've recorded your demo:

1. Upload demo video to YouTube/Vimeo/Google Drive
2. Add demo video link to README.md
3. Push code to GitHub
4. Add https://github.com/MantraHackathon as collaborator
5. Test the setup instructions on a clean environment

Good luck with your demo! 🎉
