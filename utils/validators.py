from pathlib import Path
from typing import Tuple, Optional


class Validators:
    """Common validation functions."""
    
    @staticmethod
    def validate_repo_path(path: str) -> Tuple[bool, str]:
        """Validate that the path contains a bitcoin-educational-content repo."""
        if not path:
            return False, "Path cannot be empty"
        
        path_obj = Path(path)
        if not path_obj.exists():
            return False, "Path does not exist"
        
        # Check for courses directory
        courses_path = path_obj / 'courses'
        if not courses_path.exists():
            return False, "No 'courses' directory found in the specified path"
        
        # Check for tutorials directory
        tutorials_path = path_obj / 'tutorials'
        if not tutorials_path.exists():
            return False, "No 'tutorials' directory found in the specified path"
        
        return True, "Valid bitcoin-educational-content repository"
    
    @staticmethod
    def validate_course_id(course_id: str) -> bool:
        """Validate course ID format."""
        if not course_id:
            return False
        # Course IDs should be alphanumeric with possible hyphens
        return course_id.replace('-', '').replace('_', '').isalnum()
    
    @staticmethod
    def validate_language_code(code: str) -> bool:
        """Validate language code format."""
        if not code:
            return False
        # Language codes are typically 2-3 lowercase letters
        return len(code) in [2, 3] and code.islower() and code.isalpha()
    
    @staticmethod
    def validate_branch_name(branch: str) -> bool:
        """Validate git branch name."""
        if not branch:
            return False
        # Basic validation - no spaces, not starting with dash
        return ' ' not in branch and not branch.startswith('-')
    
    @staticmethod
    def validate_iteration(iteration: str) -> bool:
        """Validate iteration value."""
        return iteration in ['1st', '2nd', '3rd']
    
    @staticmethod
    def validate_urgency(urgency: str) -> bool:
        """Validate urgency value."""
        return urgency in ['urgent', 'not urgent']
    
    @staticmethod
    def validate_tutorial_path(path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate and parse tutorial path."""
        if not path or '/' not in path:
            return False, None, None
        
        parts = path.split('/', 1)
        if len(parts) != 2:
            return False, None, None
        
        category, name = parts
        if not category or not name:
            return False, None, None
        
        return True, category, name