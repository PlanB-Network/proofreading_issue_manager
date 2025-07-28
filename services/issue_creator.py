from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.issue import IssueData
from github_integration import GitHubIntegration
from config import Config


class BaseIssueCreator(ABC):
    """Abstract base class for issue creators."""
    
    def __init__(self, github_integration: GitHubIntegration):
        self.github = github_integration
    
    @abstractmethod
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create issue data from request data."""
        pass
    
    @abstractmethod
    def build_issue_body(self, issue_data: IssueData) -> str:
        """Build the issue body content."""
        pass
    
    def preview_issue(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preview the issue before creation."""
        issue_data = self.create_issue_data(request_data)
        issue_data.body = self.build_issue_body(issue_data)
        return issue_data.to_dict()
    
    def create_issue(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create the issue on GitHub."""
        # Create issue data
        issue_data = self.create_issue_data(request_data)
        issue_data.body = self.build_issue_body(issue_data)
        
        # Create issue on GitHub
        issue = self.github.create_issue(
            issue_data.title,
            issue_data.body,
            issue_data.labels
        )
        
        # Link to project
        self.github.link_to_project(
            issue,
            Config.GITHUB_PROJECT_ID,
            issue_data.project_fields
        )
        
        return {
            'success': True,
            'issue_url': self.github.get_issue_url(issue),
            'issue_number': issue.number
        }


class CourseIssueCreator(BaseIssueCreator):
    """Issue creator for course proofreading."""
    
    def __init__(self, github_integration: GitHubIntegration, course_manager):
        super().__init__(github_integration)
        self.course_manager = course_manager
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create course issue data."""
        from models.issue import CourseIssueData
        course_info = self.course_manager.get_course_info(request_data['course_id'])
        return CourseIssueData.from_request(request_data, course_info)
    
    def build_issue_body(self, issue_data: 'CourseIssueData') -> str:
        """Build course issue body."""
        from utils.url_builder import URLBuilder
        
        # Build URLs
        pbn_url = URLBuilder.build_planb_course_url(
            issue_data.course_title,
            issue_data.course_uuid,
            issue_data.language
        )
        github_urls = URLBuilder.build_github_course_urls(
            issue_data.course_id,
            issue_data.language,
            issue_data.branch
        )
        
        # Build body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        return '\n'.join(body_lines)


class TutorialIssueCreator(BaseIssueCreator):
    """Issue creator for tutorial proofreading."""
    
    def __init__(self, github_integration: GitHubIntegration, tutorial_manager):
        super().__init__(github_integration)
        self.tutorial_manager = tutorial_manager
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create tutorial issue data."""
        from models.issue import TutorialIssueData
        category, name = request_data['tutorial_path'].split('/', 1)
        tutorial_info = self.tutorial_manager.get_tutorial_info(category, name)
        return TutorialIssueData.from_request(request_data, tutorial_info)
    
    def build_issue_body(self, issue_data: 'TutorialIssueData') -> str:
        """Build tutorial issue body."""
        from utils.url_builder import URLBuilder
        
        # Build URLs
        pbn_url = URLBuilder.build_planb_tutorial_url(
            issue_data.category,
            issue_data.name,
            issue_data.tutorial_title,
            issue_data.tutorial_id,
            issue_data.language
        )
        github_urls = URLBuilder.build_github_tutorial_urls(
            issue_data.category,
            issue_data.name,
            issue_data.language,
            issue_data.branch
        )
        
        # Build body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        return '\n'.join(body_lines)


class TutorialSectionIssueCreator(BaseIssueCreator):
    """Issue creator for tutorial section proofreading."""
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create tutorial section issue data."""
        from models.issue import TutorialSectionIssueData
        return TutorialSectionIssueData.from_request(request_data)
    
    def build_issue_body(self, issue_data: 'TutorialSectionIssueData') -> str:
        """Build tutorial section issue body."""
        from utils.url_builder import URLBuilder
        
        pbn_url = URLBuilder.build_planb_tutorial_section_url(
            issue_data.section,
            issue_data.language
        )
        github_url = URLBuilder.build_github_tutorial_section_url(
            issue_data.section,
            issue_data.branch
        )
        
        body_lines = [
            f"English PBN Version: {URLBuilder.build_planb_tutorial_section_url(issue_data.section, 'en')}",
            f"Folder GitHub Version: {github_url}"
        ]
        
        return '\n'.join(body_lines)


class WeblateIssueCreator(BaseIssueCreator):
    """Issue creator for Weblate proofreading."""
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create Weblate issue data."""
        from models.issue import WeblateIssueData
        return WeblateIssueData.from_request(request_data)
    
    def build_issue_body(self, issue_data: 'WeblateIssueData') -> str:
        """Build Weblate issue body."""
        from utils.url_builder import URLBuilder
        weblate_url = URLBuilder.build_weblate_url(issue_data.language)
        return f"Weblate Url: {weblate_url}"


class VideoCourseIssueCreator(CourseIssueCreator):
    """Issue creator for video course proofreading."""
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create video course issue data."""
        from models.issue import VideoCourseIssueData
        course_info = self.course_manager.get_course_info(request_data['course_id'])
        return VideoCourseIssueData.from_request(request_data, course_info)
    
    def build_issue_body(self, issue_data: 'VideoCourseIssueData') -> str:
        """Build video course issue body."""
        from utils.url_builder import URLBuilder
        
        # Build URLs
        planb_en_url = URLBuilder.build_planb_course_url(
            issue_data.course_title,
            issue_data.course_uuid,
            'en'
        )
        github_base_url = f"{URLBuilder.GITHUB_BASE_URL}/blob/{issue_data.branch}/courses/{issue_data.course_id}"
        
        body_lines = [
            f"English PBN Version: {planb_en_url}",
            f"EN GitHub Version: {github_base_url}/en.md",
            f"{issue_data.language} GitHub Version: {github_base_url}/{issue_data.language}.md",
            "Workspace link shared privately"
        ]
        
        return '\n'.join(body_lines)


class ImageCourseIssueCreator(CourseIssueCreator):
    """Issue creator for image course proofreading."""
    
    def create_issue_data(self, request_data: Dict[str, Any]) -> IssueData:
        """Create image course issue data."""
        from models.issue import ImageCourseIssueData
        course_info = self.course_manager.get_course_info(request_data['course_id'])
        return ImageCourseIssueData.from_request(request_data, course_info)
    
    def build_issue_body(self, issue_data: 'ImageCourseIssueData') -> str:
        """Build image course issue body."""
        from utils.url_builder import URLBuilder
        
        # Build URLs
        planb_url = URLBuilder.build_planb_course_url(
            issue_data.course_title,
            issue_data.course_uuid,
            issue_data.language
        )
        github_assets_url = URLBuilder.build_github_image_course_urls(
            issue_data.course_id,
            issue_data.branch
        )
        
        body_lines = [
            f"English PBN Version: {planb_url}",
            f"EN GitHub Version: {github_assets_url}/en/",
            "Workspace link shared privately"
        ]
        
        return '\n'.join(body_lines)