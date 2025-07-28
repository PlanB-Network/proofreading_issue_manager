import os
import yaml
from pathlib import Path
import re

class CourseManager:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.courses_path = self.repo_path / 'courses'
    
    def get_course_list(self):
        """Get list of all available courses"""
        if not self.courses_path.exists():
            return []
        
        courses = []
        for course_dir in self.courses_path.iterdir():
            if course_dir.is_dir() and not course_dir.name.startswith('.'):
                course_yml = course_dir / 'course.yml'
                if course_yml.exists():
                    courses.append(course_dir.name)
        
        return sorted(courses)
    
    def get_course_info(self, course_id):
        """Extract course title from en.md and UUID from course.yml"""
        course_yml_path = self.courses_path / course_id / 'course.yml'
        en_md_path = self.courses_path / course_id / 'en.md'
        
        if not course_yml_path.exists():
            raise FileNotFoundError(f"Course file not found: {course_yml_path}")
        
        if not en_md_path.exists():
            raise FileNotFoundError(f"English markdown file not found: {en_md_path}")
        
        # Get UUID from course.yml
        with open(course_yml_path, 'r', encoding='utf-8') as f:
            course_data = yaml.safe_load(f)
        
        # The id field in course.yml is the UUID
        uuid = course_data.get('id', '')
        if not uuid:
            raise ValueError(f"Missing id (UUID) in course.yml for {course_id}")
        
        # Get title from en.md header
        with open(en_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from the first H1 header
        title_match = re.match(r'^#+\s+(.+)$', content.strip(), re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Fallback to name from course.yml if no header found
            title = course_data.get('name', course_id)
        
        # Generate title slug for URL
        title_slug = title.lower()
        title_slug = re.sub(r'[^\w\s-]', '', title_slug)
        title_slug = re.sub(r'[-\s]+', '-', title_slug)
        title_slug = title_slug.strip('-')
        
        return {
            'id': course_id,
            'uuid': uuid,
            'title': title,
            'title_slug': title_slug
        }
    
    def build_pbn_url(self, course_title, uuid, lang='en'):
        """Build PlanB Network URL"""
        # Clean and format the title
        clean_title = course_title.lower()
        
        # Replace special characters and spaces with hyphens
        clean_title = re.sub(r'[^\w\s-]', '', clean_title)
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        clean_title = clean_title.strip('-')
        
        return f"https://planb.network/{lang}/courses/{clean_title}-{uuid}"
    
    def build_github_urls(self, course_id, lang, branch='dev'):
        """Build GitHub URLs (EN + selected language if different)"""
        base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/courses/{course_id}"
        
        urls = []
        # Always include EN version
        en_url = f"{base_url}/en.md"
        urls.append(('en', en_url))
        
        # Add selected language if not EN
        if lang != 'en':
            lang_url = f"{base_url}/{lang}.md"
            urls.append((lang, lang_url))
        
        return urls
    
    def check_language_file_exists(self, course_id, lang):
        """Check if a language file exists for the course"""
        lang_file = self.courses_path / course_id / f"{lang}.md"
        return lang_file.exists()
    
    def get_course_size(self, course_id, lang='en'):
        """Estimate course size based on content"""
        lang_file = self.courses_path / course_id / f"{lang}.md"
        
        if not lang_file.exists():
            # Try English as fallback
            lang_file = self.courses_path / course_id / "en.md"
        
        if not lang_file.exists():
            return "medium"  # Default size
        
        with open(lang_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estimate based on character count
        char_count = len(content)
        
        if char_count < 10000:
            return "small"
        elif char_count < 50000:
            return "medium"
        else:
            return "large"
    
    def validate_course_structure(self, course_id):
        """Validate that course has proper structure"""
        course_path = self.courses_path / course_id
        
        if not course_path.exists():
            return False, "Course directory does not exist"
        
        course_yml = course_path / 'course.yml'
        if not course_yml.exists():
            return False, "course.yml file not found"
        
        en_md = course_path / 'en.md'
        if not en_md.exists():
            return False, "English markdown file (en.md) not found"
        
        return True, "Course structure is valid"