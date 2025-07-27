@echo off
echo ==================================
echo Proofreading Issue Manager Launcher
echo ==================================
echo.

REM Check if app.py exists
if not exist "app.py" (
    echo [ERROR] app.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment is active
if defined VIRTUAL_ENV (
    echo [PIM] Virtual environment is already active: %VIRTUAL_ENV%
) else (
    REM Check if env directory exists
    if exist "env\Scripts\activate.bat" (
        echo [PIM] Activating existing virtual environment...
        call env\Scripts\activate.bat
    ) else (
        echo [PIM] Virtual environment not found. Creating new one...
        python -m venv env
        if errorlevel 1 (
            echo [ERROR] Failed to create virtual environment
            pause
            exit /b 1
        )
        echo [PIM] Virtual environment created successfully
        call env\Scripts\activate.bat
    )
)

REM Upgrade pip
echo [PIM] Ensuring pip is up to date...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo [PIM] Checking requirements...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)
echo [PIM] All requirements satisfied

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo [WARNING] Please edit .env file with your GitHub token and repository path
        echo [WARNING] Opening .env file for editing...
        notepad .env
    ) else (
        echo [ERROR] .env.example not found. Please create a .env file manually.
        pause
        exit /b 1
    )
)

REM Start the Flask app
echo [PIM] Starting Proofreading Issue Manager...
echo [PIM] Server will be available at http://localhost:5000
echo.

REM Open browser after a delay
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

REM Run the Flask app
python app.py