@echo off
echo Installing Visual Chat Assistant Dependencies...
echo ================================================

REM Upgrade pip first
echo.
echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

REM Install setuptools and wheel first
echo.
echo Step 2: Installing build tools...
pip install setuptools==69.0.3 wheel==0.42.0

REM Install core dependencies one by one
echo.
echo Step 3: Installing core dependencies...
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6
pip install pydantic==2.5.0

REM Install OpenAI
echo.
echo Step 4: Installing OpenAI...
pip install openai==1.6.1

REM Install video processing
echo.
echo Step 5: Installing video processing libraries...
pip install opencv-python==4.8.1.78
pip install pillow==10.1.0
pip install imageio==2.33.0
pip install imageio-ffmpeg==0.4.9

REM Install other dependencies
echo.
echo Step 6: Installing other dependencies...
pip install aiofiles==23.2.1
pip install websockets==12.0
pip install httpx==0.25.2
pip install python-dotenv==1.0.0
pip install numpy==1.24.3
pip install tqdm==4.66.1
pip install tiktoken==0.5.2

REM Install jose
echo.
echo Step 7: Installing JWT libraries...
pip install python-jose[cryptography]==3.3.0

echo.
echo ================================================
echo Installation complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your OpenAI API key to .env
echo 3. Run: python main.py
echo.
pause
