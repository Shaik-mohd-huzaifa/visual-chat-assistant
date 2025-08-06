// Visual Understanding Chat Assistant - Frontend JavaScript

let sessionId = null;
let currentVideo = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');
const videoPreview = document.getElementById('videoPreview');
const videoPlayer = document.getElementById('videoPlayer');
const analyzeBtn = document.getElementById('analyzeBtn');
const analysisResults = document.getElementById('analysisResults');
const chatSection = document.getElementById('chatSection');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const clearChat = document.getElementById('clearChat');

// Tab Elements
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// Initialize Event Listeners
function initializeEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => videoInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Video input change
    videoInput.addEventListener('change', handleFileSelect);
    
    // Analyze button
    analyzeBtn.addEventListener('click', analyzeVideo);
    
    // Chat events
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    clearChat.addEventListener('click', clearChatHistory);
    
    // Tab navigation
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Analyze Another Video button
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
    if (analyzeAnotherBtn) {
        analyzeAnotherBtn.addEventListener('click', resetForNewVideo);
    }
}

// File Handling Functions
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragging');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragging');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragging');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleVideoFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleVideoFile(file);
    }
}

function handleVideoFile(file) {
    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv|webm)$/i)) {
        showNotification('Please upload a valid video file (MP4, AVI, MOV, MKV, WEBM)', 'error');
        return;
    }
    
    // Check file size (optional, e.g., max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
        showNotification('Video file is too large. Maximum size is 100MB', 'error');
        return;
    }
    
    currentVideo = file;
    
    // Preview video
    const url = URL.createObjectURL(file);
    videoPlayer.src = url;
    uploadArea.style.display = 'none';
    videoPreview.style.display = 'block';
}

// Video Analysis
async function analyzeVideo() {
    if (!currentVideo) {
        showNotification('Please select a video first', 'error');
        return;
    }
    
    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.querySelector('.btn-text').textContent = 'Analyzing...';
    analyzeBtn.querySelector('.spinner').style.display = 'inline-block';
    
    try {
        const formData = new FormData();
        formData.append('file', currentVideo);
        if (sessionId) {
            formData.append('session_id', sessionId);
        }
        
        const response = await fetch('/api/upload-video', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store session ID
        sessionId = data.session_id;
        
        // Display results
        displayAnalysisResults(data);
        
        // Show chat section
        chatSection.style.display = 'block';
        
        showNotification('Video analyzed successfully!', 'success');
        
    } catch (error) {
        console.error('Error analyzing video:', error);
        showNotification('Failed to analyze video. Please try again.', 'error');
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        analyzeBtn.querySelector('.btn-text').textContent = 'Analyze Video';
        analyzeBtn.querySelector('.spinner').style.display = 'none';
    }
}

// Display Analysis Results
function displayAnalysisResults(data) {
    analysisResults.style.display = 'block';
    
    // Set up video players with the uploaded video
    const resultVideoPlayer = document.getElementById('resultVideoPlayer');
    const tabVideoPlayer = document.getElementById('tabVideoPlayer');
    
    if (currentVideo) {
        const videoURL = URL.createObjectURL(currentVideo);
        resultVideoPlayer.src = videoURL;
        tabVideoPlayer.src = videoURL;
    }
    
    // Display summary
    document.getElementById('videoSummary').textContent = data.summary;
    
    // Display events
    const eventsList = document.getElementById('eventsList');
    eventsList.innerHTML = '';
    
    if (data.events && data.events.length > 0) {
        data.events.forEach(event => {
            const eventItem = createEventElement(event);
            eventsList.appendChild(eventItem);
        });
    } else {
        eventsList.innerHTML = '<p>No events detected</p>';
    }
    
    // Display guidelines
    const guidelines = data.guideline_adherence;
    
    // Update compliance status
    const complianceStatus = document.getElementById('complianceStatus');
    complianceStatus.textContent = guidelines.compliance_status || 'Unknown';
    complianceStatus.className = 'status-badge';
    
    if (guidelines.compliance_status === 'Good') {
        complianceStatus.classList.add('status-good');
    } else if (guidelines.compliance_status === 'Needs Attention') {
        complianceStatus.classList.add('status-attention');
    } else {
        complianceStatus.classList.add('status-poor');
    }
    
    // Update statistics
    document.getElementById('totalEvents').textContent = guidelines.total_events || 0;
    document.getElementById('violationsCount').textContent = guidelines.violations_count || 0;
    document.getElementById('highSeverity').textContent = guidelines.high_severity_count || 0;
    
    // Display violations
    const violationsList = document.getElementById('violationsList');
    violationsList.innerHTML = '';
    
    if (guidelines.violations && guidelines.violations.length > 0) {
        const violationsTitle = document.createElement('h4');
        violationsTitle.textContent = 'Detected Violations:';
        violationsList.appendChild(violationsTitle);
        
        guidelines.violations.forEach(violation => {
            const violationItem = createViolationElement(violation);
            violationsList.appendChild(violationItem);
        });
    }
}

function createEventElement(event) {
    const div = document.createElement('div');
    div.className = 'event-item';
    
    const timestamp = document.createElement('div');
    timestamp.className = 'event-timestamp';
    timestamp.textContent = `${event.timestamp.toFixed(1)}s`;
    
    const content = document.createElement('div');
    content.className = 'event-content';
    
    const type = document.createElement('span');
    type.className = 'event-type';
    type.textContent = event.event_type || 'Event';
    
    const description = document.createElement('div');
    description.className = 'event-description';
    description.textContent = event.description;
    
    const severity = document.createElement('span');
    severity.className = `event-severity severity-${event.severity || 'low'}`;
    severity.textContent = event.severity || 'Low';
    
    content.appendChild(type);
    content.appendChild(description);
    content.appendChild(severity);
    
    div.appendChild(timestamp);
    div.appendChild(content);
    
    return div;
}

function createViolationElement(violation) {
    const div = document.createElement('div');
    div.className = 'violation-item';
    
    const timestamp = document.createElement('strong');
    timestamp.textContent = `[${violation.timestamp.toFixed(1)}s] `;
    
    const description = document.createElement('span');
    description.textContent = violation.description;
    
    const severity = document.createElement('span');
    severity.className = `event-severity severity-${violation.severity}`;
    severity.textContent = ` (${violation.severity})`;
    severity.style.marginLeft = '0.5rem';
    
    div.appendChild(timestamp);
    div.appendChild(description);
    div.appendChild(severity);
    
    return div;
}

// Tab Navigation
function switchTab(tabName) {
    // Update tab buttons
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update tab panes
    tabPanes.forEach(pane => {
        if (pane.id === `${tabName}Tab`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// Chat Functions
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    chatInput.value = '';
    
    // Disable input while processing
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID if needed
        if (data.session_id) {
            sessionId = data.session_id;
        }
        
        // Add assistant response to chat
        addMessageToChat('assistant', data.response);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('assistant', 'Sorry, I encountered an error processing your message. Please try again.');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function clearChatHistory() {
    if (sessionId) {
        try {
            await fetch(`/api/session/${sessionId}`, {
                method: 'DELETE'
            });
            
            // Clear chat messages except the initial assistant message
            chatMessages.innerHTML = `
                <div class="message assistant">
                    <div class="message-content">
                        Hello! I've analyzed your video. Feel free to ask me any questions about the events, violations, or anything you'd like to know about the video content.
                    </div>
                </div>
            `;
            
            showNotification('Chat history cleared', 'success');
            
        } catch (error) {
            console.error('Error clearing chat:', error);
            showNotification('Failed to clear chat history', 'error');
        }
    }
}

// Reset interface for new video analysis
function resetForNewVideo() {
    // Hide analysis results and chat sections
    analysisResults.style.display = 'none';
    chatSection.style.display = 'none';
    
    // Show upload section
    uploadSection.style.display = 'block';
    
    // Reset video preview
    videoPreview.style.display = 'none';
    videoPlayer.src = '';
    
    // Reset video players in results
    const resultVideoPlayer = document.getElementById('resultVideoPlayer');
    const tabVideoPlayer = document.getElementById('tabVideoPlayer');
    if (resultVideoPlayer) resultVideoPlayer.src = '';
    if (tabVideoPlayer) tabVideoPlayer.src = '';
    
    // Clear file input
    videoInput.value = '';
    currentVideo = null;
    
    // Clear session
    sessionId = null;
    
    // Clear chat messages
    chatMessages.innerHTML = '';
    
    // Reset analyze button
    analyzeBtn.disabled = false;
    analyzeBtn.querySelector('.btn-text').textContent = 'Analyze Video';
    analyzeBtn.querySelector('.spinner').style.display = 'none';
    
    // Reset to first tab
    switchTab('summary');
    
    // Clear any previous analysis data
    document.getElementById('videoSummary').textContent = '';
    document.getElementById('eventsList').innerHTML = '';
    document.getElementById('violationsList').innerHTML = '';
    
    showNotification('Ready to analyze a new video!', 'success');
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeEventListeners);
