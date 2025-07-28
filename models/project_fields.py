from typing import Dict, List


class ProjectFieldMappings:
    """Centralized project field mappings and options."""
    
    STATUS_OPTIONS = ['Todo', 'In Progress', 'Done']
    ITERATION_OPTIONS = ['1st', '2nd', '3rd']
    URGENCY_OPTIONS = ['not urgent', 'urgent']
    CONTENT_TYPE_OPTIONS = [
        'Course',
        'Tutorial', 
        'Weblate',
        'Video Course',
        'Image Course'
    ]
    
    # Field name alternatives for GraphQL compatibility
    FIELD_ALTERNATIVES = {
        'Content Type': ['ContentType', 'Content type', 'content type', 'Type'],
        'Status': ['status', 'STATE', 'State'],
        'Language': ['language', 'Lang'],
        'Iteration': ['iteration'],
        'Urgency': ['urgency']
    }
    
    @classmethod
    def get_default_fields(cls, content_type: str, language: str, 
                          iteration: str, urgency: str) -> Dict[str, str]:
        """Get default project fields for an issue."""
        return {
            'Status': 'Todo',
            'Language': language,
            'Iteration': iteration,
            'Urgency': urgency,
            'Content Type': content_type
        }
    
    @classmethod
    def validate_field_value(cls, field_name: str, value: str) -> bool:
        """Validate if a field value is valid."""
        if field_name == 'Status':
            return value in cls.STATUS_OPTIONS
        elif field_name == 'Iteration':
            return value in cls.ITERATION_OPTIONS
        elif field_name == 'Urgency':
            return value in cls.URGENCY_OPTIONS
        elif field_name == 'Content Type':
            return value in cls.CONTENT_TYPE_OPTIONS
        return True  # No validation for other fields