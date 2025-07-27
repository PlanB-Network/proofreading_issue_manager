import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_PROJECT_ID = os.environ.get('GITHUB_PROJECT_ID', 'PVT_kwDOCbV58s4AlOvb')  # Content Translation & Proofreading Dashboard
    
    # Local repository path
    BITCOIN_CONTENT_REPO_PATH = os.environ.get('BITCOIN_CONTENT_REPO_PATH', '')
    
    # Default branch
    DEFAULT_BRANCH = os.environ.get('DEFAULT_BRANCH', 'dev')
    
    # GitHub repository details
    GITHUB_OWNER = 'PlanB-Network'
    GITHUB_REPO = 'bitcoin-educational-content'
    
    # Language mapping
    LANGUAGES = {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'fa': 'Persian',
        'pl': 'Polish',
        'ru': 'Russian',
        'nl': 'Dutch',
        'tr': 'Turkish',
        'vi': 'Vietnamese',
        'hi': 'Hindi',
        'cs': 'Czech',
        'fi': 'Finnish',
        'el': 'Greek',
        'he': 'Hebrew',
        'hu': 'Hungarian',
        'id': 'Indonesian',
        'nb': 'Norwegian',
        'ro': 'Romanian',
        'sv': 'Swedish',
        'th': 'Thai',
        'uk': 'Ukrainian'
    }
    
    # Project field mappings
    PROJECT_FIELDS = {
        'status_options': ['To Do', 'In Progress', 'Done'],
        'iteration_options': ['1st', '2nd', '3rd'],
        'urgency_options': ['not urgent', 'urgent'],
        'content_type_options': ['course', 'tutorial', 'tutorial_section', 'Weblate']
    }
    
    # Weblate configuration
    WEBLATE_BASE_URL = 'https://weblate.planb.network/projects/planb-network-website/website-elements'
    
    @classmethod
    def save_config(cls, config_data):
        """Save configuration to a JSON file"""
        config_file = Path('user_config.json')
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @classmethod
    def load_config(cls):
        """Load configuration from JSON file"""
        config_file = Path('user_config.json')
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    @classmethod
    def validate_repo_path(cls, path):
        """Validate that the path contains a bitcoin-educational-content repo"""
        if not path:
            return False, "Path cannot be empty"
        
        path_obj = Path(path)
        if not path_obj.exists():
            return False, "Path does not exist"
        
        # Check for courses directory
        courses_path = path_obj / 'courses'
        if not courses_path.exists():
            return False, "No 'courses' directory found in the specified path"
        
        return True, "Valid bitcoin-educational-content repository"