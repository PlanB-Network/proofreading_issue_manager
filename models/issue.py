from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class IssueData:
    """Base data class for GitHub issues."""
    title: str
    body: str
    labels: List[str]
    project_fields: Dict[str, str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'body': self.body,
            'labels': self.labels,
            'project_fields': self.project_fields
        }


@dataclass
class CourseIssueData(IssueData):
    """Data class for course proofreading issues."""
    course_id: str
    language: str
    branch: str
    iteration: str
    urgency: str
    course_uuid: Optional[str] = None
    course_title: Optional[str] = None
    
    @classmethod
    def from_request(cls, data: dict, course_info: dict) -> 'CourseIssueData':
        """Create from request data and course info."""
        title = f"[PROOFREADING] {data['course_id']} - {data['language']}"
        labels = [
            "content - course",
            "content proofreading",
            f"language - {data['language']}"
        ]
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Course'
        }
        
        return cls(
            title=title,
            body="",  # Will be set by issue creator
            labels=labels,
            project_fields=project_fields,
            course_id=data['course_id'],
            language=data['language'],
            branch=data['branch'],
            iteration=data['iteration'],
            urgency=data['urgency'],
            course_uuid=course_info.get('uuid'),
            course_title=course_info.get('title')
        )


@dataclass
class TutorialIssueData(IssueData):
    """Data class for tutorial proofreading issues."""
    category: str
    name: str
    language: str
    branch: str
    iteration: str
    urgency: str
    tutorial_id: Optional[str] = None
    tutorial_title: Optional[str] = None
    
    @classmethod
    def from_request(cls, data: dict, tutorial_info: dict) -> 'TutorialIssueData':
        """Create from request data and tutorial info."""
        category, name = data['tutorial_path'].split('/', 1)
        title = f"[PROOFREADING] {category}/{name} - {data['language']}"
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Tutorial'
        }
        
        return cls(
            title=title,
            body="",  # Will be set by issue creator
            labels=labels,
            project_fields=project_fields,
            category=category,
            name=name,
            language=data['language'],
            branch=data['branch'],
            iteration=data['iteration'],
            urgency=data['urgency'],
            tutorial_id=tutorial_info.get('id'),
            tutorial_title=tutorial_info.get('title')
        )


@dataclass
class WeblateIssueData(IssueData):
    """Data class for Weblate proofreading issues."""
    language: str
    iteration: str
    urgency: str
    
    @classmethod
    def from_request(cls, data: dict) -> 'WeblateIssueData':
        """Create from request data."""
        title = f"[PROOFREADING] weblate - {data['language']}"
        labels = [
            "website translation",
            f"language - {data['language']}"
        ]
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Weblate'
        }
        
        return cls(
            title=title,
            body="",  # Will be set by issue creator
            labels=labels,
            project_fields=project_fields,
            language=data['language'],
            iteration=data['iteration'],
            urgency=data['urgency']
        )


@dataclass
class VideoCourseIssueData(CourseIssueData):
    """Data class for video course proofreading issues."""
    
    @classmethod
    def from_request(cls, data: dict, course_info: dict) -> 'VideoCourseIssueData':
        """Create from request data and course info."""
        base = super().from_request(data, course_info)
        base.title = f"[VIDEO-PROOFREADING] {data['course_id']} - {data['language']}"
        base.labels.append("video transcript")
        base.project_fields['Content Type'] = 'Video Course'
        return base


@dataclass
class ImageCourseIssueData(CourseIssueData):
    """Data class for image course proofreading issues."""
    
    @classmethod
    def from_request(cls, data: dict, course_info: dict) -> 'ImageCourseIssueData':
        """Create from request data and course info."""
        base = super().from_request(data, course_info)
        base.title = f"[IMAGE-PROOFREADING] {data['course_id']} - {data['language']}"
        base.labels = [
            "content - course",
            "content - images",
            f"language - [{data['language']}]"  # Note: brackets in label
        ]
        base.project_fields['Content Type'] = 'Image Course'
        return base


@dataclass  
class TutorialSectionIssueData(IssueData):
    """Data class for tutorial section proofreading issues."""
    section: str
    language: str
    branch: str
    iteration: str
    urgency: str
    
    @classmethod
    def from_request(cls, data: dict) -> 'TutorialSectionIssueData':
        """Create from request data."""
        title = f"[PROOFREADING] {data['section']}_section - {data['language']}"
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Tutorial'
        }
        
        return cls(
            title=title,
            body="",  # Will be set by issue creator
            labels=labels,
            project_fields=project_fields,
            section=data['section'],
            language=data['language'],
            branch=data['branch'],
            iteration=data['iteration'],
            urgency=data['urgency']
        )