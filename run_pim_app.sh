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
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your GitHub token and repository path"
        print_warning "Opening .env file for editing..."
        ${EDITOR:-nano} .env
    else
        print_error ".env.example not found. Please create a .env file manually."
        exit 1
    fi
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