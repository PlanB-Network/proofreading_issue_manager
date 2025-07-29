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
    
    # Language mapping - loaded from supported_languages.json
    @staticmethod
    def _load_languages_from_file():
        """Load languages from the bitcoin-educational-content repo"""
        languages = {}
        
        # Try to load from the configured repo path
        bitcoin_path = os.environ.get('BITCOIN_CONTENT_REPO_PATH', '')
        if bitcoin_path:
            json_path = Path(bitcoin_path) / 'scripts' / 'auto-translate' / 'translation_logic' / 'supported_languages.json'
            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for lang in data.get('languages', []):
                            code = lang.get('code', '')
                            name = lang.get('name', '')
                            if code and name:
                                languages[code] = name
                    return languages
                except Exception as e:
                    print(f"Error loading languages from {json_path}: {e}")
        
        # Fallback to hardcoded languages if file not found
        return {
            'cs': 'Czech',
            'de': 'German',
            'en': 'English',
            'es': 'Spanish',
            'et': 'Estonian',
            'fa': 'Farsi',
            'fi': 'Finnish',
            'fr': 'French',
            'hi': 'Hindi',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'nb-NO': 'Norwegian',
            'nl': 'Dutch',
            'pl': 'Polish',
            'pt': 'Portuguese',
            'rn': 'Rundi',
            'ro': 'Romanian',
            'ru': 'Russian',
            'si': 'Sinhala',
            'sr-Latn': 'Serbian',
            'sv': 'Swedish',
            'sw': 'Swahili',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'zh-Hans': 'Chinese Simplified',
            'zh-Hant': 'Chinese Traditional'
        }
    
    # Initialize languages
    LANGUAGES = _load_languages_from_file()
    
    @classmethod
    def reload_languages(cls):
        """Reload languages from file - useful when the repo path changes"""
        cls.LANGUAGES = cls._load_languages_from_file()
        return cls.LANGUAGES
    
    # Project field mappings
    PROJECT_FIELDS = {
        'status_options': ['To Do', 'In Progress', 'Done'],
        'iteration_options': ['1st', '2nd', '3rd'],
        'urgency_options': ['not urgent', 'urgent'],
        'content_type_options': ['course', 'tutorial', 'tutorial_section', 'Weblate', 'Video Course', 'Image Course']
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