@echo off
setlocal

echo ================================================
echo    🚀 Starting Gate.io Crypto Trading Bot
echo ================================================

:: Step 1: Check and Setup Python Environment
echo.
echo [1/3] Setting up Python Backend Environment...
cd backend

IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE (
    echo Error: Could not find virtual environment activation script.
    pause
    exit /b 1
)

:: Install dependencies with trusted host flags to bypass SSL issues
echo Installing dependencies...
python -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -q

:: Step 2: Start the FastAPI Backend Server
echo.
echo [2/3] Starting Backend Server on port 8000...

:: Run uvicorn in the background using start
start "Trading Bot Backend" cmd /c "python -m uvicorn main:app --reload"

:: Step 3: Start the Frontend UI Server
echo.
echo [3/3] Starting Frontend UI on port 3000...
cd ..\frontend

:: Run a simple Python HTTP server in the background using start
start "Trading Bot Frontend" cmd /c "python -m http.server 3000"

echo ================================================
echo ✅ All services are starting up!
echo 👉 Opening your browser to: http://localhost:3000
echo ================================================

:: Wait 3 seconds for servers to start, then open the browser
timeout /t 3 /nobreak >nul
start http://localhost:3000/index.html?v=%RANDOM%

echo.
echo Press any key to stop both servers...
pause >nul

:: Kill the specific command prompt windows by their title
taskkill /fi "WINDOWTITLE eq Trading Bot Backend*" /T /F >nul 2>&1
taskkill /fi "WINDOWTITLE eq Trading Bot Frontend*" /T /F >nul 2>&1

echo.
echo Servers stopped. Goodbye!
endlocal
