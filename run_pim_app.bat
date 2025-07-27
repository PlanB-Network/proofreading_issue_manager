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
    echo [WARNING] .env file not found. Let's set it up!
    echo.
    
    echo [PIM] Configuration Setup
    echo ===================
    echo.
    
    REM GitHub Token
    echo 1. GitHub Personal Access Token
    echo    You need a token with 'repo' and 'project' permissions.
    echo    Create one at: https://github.com/settings/tokens/new
    echo.
    set /p github_token="Enter your GitHub token: "
    if "%github_token%"=="" (
        echo [ERROR] GitHub token is required!
        pause
        exit /b 1
    )
    echo.
    
    REM Repository Path
    echo 2. Bitcoin Educational Content Repository Path
    echo    This should be the absolute path to your local clone of:
    echo    https://github.com/PlanB-Network/bitcoin-educational-content
    echo.
    
    REM Try to find the repo automatically
    set found_path=
    for %%i in (
        "%USERPROFILE%\bitcoin-educational-content"
        "%USERPROFILE%\Documents\bitcoin-educational-content"
        "%USERPROFILE%\Projects\bitcoin-educational-content"
        "%USERPROFILE%\repos\bitcoin-educational-content"
        "%USERPROFILE%\github\bitcoin-educational-content"
        "..\bitcoin-educational-content"
    ) do (
        if exist "%%~i\courses" (
            set found_path=%%~i
            goto :found
        )
    )
    :found
    
    if not "%found_path%"=="" (
        set /p repo_path="Enter the repository path [%found_path%]: "
        if "%repo_path%"=="" set repo_path=%found_path%
    ) else (
        set /p repo_path="Enter the repository path: "
    )
    
    :validate_path
    if not exist "%repo_path%\courses" (
        echo [ERROR] Invalid path! The directory must contain a 'courses' folder.
        set /p repo_path="Enter the repository path: "
        goto :validate_path
    )
    echo.
    
    REM Project ID
    echo 3. GitHub Project ID (optional)
    echo    Leave empty to use the default PlanB Network project.
    echo.
    set /p project_id="Enter GitHub Project ID [PVT_kwDOCbV58s4AlOvb]: "
    if "%project_id%"=="" set project_id=PVT_kwDOCbV58s4AlOvb
    echo.
    
    REM Default Branch
    echo 4. Default Git Branch
    echo.
    set /p default_branch="Enter default branch [dev]: "
    if "%default_branch%"=="" set default_branch=dev
    echo.
    
    REM Generate secret key
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set secret_key=%%i
    
    REM Create .env file
    (
        echo # GitHub Configuration
        echo GITHUB_TOKEN=%github_token%
        echo GITHUB_PROJECT_ID=%project_id%
        echo.
        echo # Local Repository Path
        echo BITCOIN_CONTENT_REPO_PATH=%repo_path%
        echo.
        echo # Default Branch
        echo DEFAULT_BRANCH=%default_branch%
        echo.
        echo # Flask Configuration
        echo SECRET_KEY=%secret_key%
    ) > .env
    
    echo [PIM] .env file created successfully!
    echo.
)

REM Start the Flask app
echo [PIM] Starting Proofreading Issue Manager...
echo [PIM] Server will be available at http://localhost:5000
echo.

REM Open browser after a delay
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

REM Run the Flask app
python app.py