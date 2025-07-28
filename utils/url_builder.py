import re
from typing import Tuple, List


class URLBuilder:
    """Centralized URL building utilities."""
    
    PLANB_BASE_URL = "https://planb.network"
    GITHUB_BASE_URL = "https://github.com/PlanB-Network/bitcoin-educational-content"
    WEBLATE_BASE_URL = "https://weblate.planb.network/projects/planb-network-website/website-elements"
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug."""
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    @classmethod
    def build_planb_course_url(cls, title: str, uuid: str, language: str = 'en') -> str:
        """Build PlanB Network URL for a course."""
        slug = cls.slugify(title)
        return f"{cls.PLANB_BASE_URL}/{language}/courses/{slug}-{uuid}"
    
    @classmethod
    def build_planb_tutorial_url(cls, category: str, name: str, title: str, 
                                uuid: str, language: str = 'en') -> str:
        """Build PlanB Network URL for a tutorial."""
        slug = cls.slugify(title)
        return f"{cls.PLANB_BASE_URL}/{language}/tutorials/{category}/{name}/{slug}-{uuid}"
    
    @classmethod
    def build_planb_tutorial_section_url(cls, section: str, language: str = 'en') -> str:
        """Build PlanB Network URL for a tutorial section."""
        return f"{cls.PLANB_BASE_URL}/{language}/tutorials/{section}"
    
    @classmethod
    def build_github_course_urls(cls, course_id: str, language: str, 
                                branch: str = 'dev') -> List[Tuple[str, str]]:
        """Build GitHub URLs for course (EN + selected language)."""
        base_url = f"{cls.GITHUB_BASE_URL}/blob/{branch}/courses/{course_id}"
        
        urls = [('en', f"{base_url}/en.md")]
        if language != 'en':
            urls.append((language, f"{base_url}/{language}.md"))
        
        return urls
    
    @classmethod
    def build_github_tutorial_urls(cls, category: str, name: str, language: str,
                                  branch: str = 'dev') -> List[Tuple[str, str]]:
        """Build GitHub URLs for tutorial (EN + selected language)."""
        base_url = f"{cls.GITHUB_BASE_URL}/blob/{branch}/tutorials/{category}/{name}"
        
        urls = [('en', f"{base_url}/en.md")]
        if language != 'en':
            urls.append((language, f"{base_url}/{language}.md"))
        
        return urls
    
    @classmethod
    def build_github_tutorial_section_url(cls, section: str, branch: str = 'dev') -> str:
        """Build GitHub URL for a tutorial section folder."""
        return f"{cls.GITHUB_BASE_URL}/blob/{branch}/tutorials/{section}"
    
    @classmethod
    def build_github_image_course_urls(cls, course_id: str, branch: str = 'dev') -> str:
        """Build GitHub URL for course images folder."""
        return f"{cls.GITHUB_BASE_URL}/blob/{branch}/courses/{course_id}/assets"
    
    @classmethod
    def build_weblate_url(cls, language: str) -> str:
        """Build Weblate URL for a language."""
        return f"{cls.WEBLATE_BASE_URL}/{language}/"