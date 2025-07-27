#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[PIM]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[PIM]${NC} $1"
}

print_error() {
    echo -e "${RED}[PIM]${NC} $1"
}

# Banner
echo "=================================="
echo "Proofreading Issue Manager Launcher"
echo "=================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    print_error "Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Virtual environment is already active: $VIRTUAL_ENV"
else
    # Check if env directory exists
    if [ -d "env" ]; then
        print_status "Activating existing virtual environment..."
        source env/bin/activate
    else
        print_warning "Virtual environment not found. Creating new one..."
        python3 -m venv env
        if [ $? -eq 0 ]; then
            print_status "Virtual environment created successfully"
            source env/bin/activate
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
    fi
fi

# Upgrade pip quietly
print_status "Ensuring pip is up to date..."
pip install --upgrade pip --quiet

# Check if requirements need to be installed/updated
print_status "Checking requirements..."
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    print_status "All requirements satisfied"
else
    print_error "Failed to install requirements"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Let's set it up!"
    echo ""
    
    # Function to prompt for input with a default value
    prompt_with_default() {
        local prompt="$1"
        local default="$2"
        local varname="$3"
        
        if [ -n "$default" ]; then
            read -p "$prompt [$default]: " value
            value="${value:-$default}"
        else
            read -p "$prompt: " value
            while [ -z "$value" ]; do
                print_error "This field is required!"
                read -p "$prompt: " value
            done
        fi
        
        eval "$varname='$value'"
    }
    
    print_status "Configuration Setup"
    echo "==================="
    echo ""
    
    # GitHub Token
    echo "1. GitHub Personal Access Token"
    echo "   You need a token with 'repo' and 'project' permissions."
    echo "   Create one at: https://github.com/settings/tokens/new"
    echo ""
    prompt_with_default "Enter your GitHub token" "" "github_token"
    echo ""
    
    # Repository Path
    echo "2. Bitcoin Educational Content Repository Path"
    echo "   This should be the absolute path to your local clone of:"
    echo "   https://github.com/PlanB-Network/bitcoin-educational-content"
    echo ""
    
    # Try to find the repo automatically
    possible_paths=(
        "$HOME/bitcoin-educational-content"
        "$HOME/Documents/bitcoin-educational-content"
        "$HOME/Projects/bitcoin-educational-content"
        "$HOME/repos/bitcoin-educational-content"
        "$HOME/github/bitcoin-educational-content"
        "../bitcoin-educational-content"
    )
    
    found_path=""
    for path in "${possible_paths[@]}"; do
        if [ -d "$path/courses" ]; then
            found_path=$(realpath "$path")
            break
        fi
    done
    
    if [ -n "$found_path" ]; then
        prompt_with_default "Enter the repository path" "$found_path" "repo_path"
    else
        prompt_with_default "Enter the repository path" "" "repo_path"
    fi
    
    # Validate the path
    while [ ! -d "$repo_path/courses" ]; do
        print_error "Invalid path! The directory must contain a 'courses' folder."
        prompt_with_default "Enter the repository path" "" "repo_path"
    done
    echo ""
    
    # Project ID
    echo "3. GitHub Project ID (optional)"
    echo "   Leave empty to use the default PlanB Network project."
    echo ""
    prompt_with_default "Enter GitHub Project ID" "PVT_kwDOCbV58s4AlOvb" "project_id"
    echo ""
    
    # Default Branch
    echo "4. Default Git Branch"
    echo ""
    prompt_with_default "Enter default branch" "dev" "default_branch"
    echo ""
    
    # Secret Key
    secret_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Create .env file
    cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=$github_token
GITHUB_PROJECT_ID=$project_id

# Local Repository Path
BITCOIN_CONTENT_REPO_PATH=$repo_path

# Default Branch
DEFAULT_BRANCH=$default_branch

# Flask Configuration
SECRET_KEY=$secret_key
EOF
    
    print_status ".env file created successfully!"
    echo ""
fi

# Function to open browser
open_browser() {
    url="$1"
    print_status "Opening browser at $url"
    
    # Try different commands based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open "$url" 2>/dev/null &
        elif command -v gnome-open &> /dev/null; then
            gnome-open "$url" 2>/dev/null &
        elif command -v firefox &> /dev/null; then
            firefox "$url" 2>/dev/null &
        elif command -v google-chrome &> /dev/null; then
            google-chrome "$url" 2>/dev/null &
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "$url" 2>/dev/null &
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start "$url" 2>/dev/null &
    fi
}

# Start the Flask app
print_status "Starting Proofreading Issue Manager..."
print_status "Server will be available at http://localhost:5000"
echo ""

# Wait a moment for the server to start, then open browser
(sleep 2 && open_browser "http://localhost:5000") &

# Run the Flask app
python3 app.py