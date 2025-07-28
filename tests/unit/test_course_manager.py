import pytest
from pathlib import Path
from course_manager import CourseManager


class TestCourseManager:
    def test_init(self, temp_repo_path):
        """Test CourseManager initialization."""
        manager = CourseManager(temp_repo_path)
        assert manager.repo_path == Path(temp_repo_path)
        assert manager.courses_path == Path(temp_repo_path) / 'courses'
    
    def test_get_course_list(self, temp_repo_path):
        """Test getting list of courses."""
        manager = CourseManager(temp_repo_path)
        courses = manager.get_course_list()
        assert 'btc101' in courses
        assert len(courses) == 1
    
    def test_get_course_info(self, temp_repo_path):
        """Test getting course information."""
        manager = CourseManager(temp_repo_path)
        info = manager.get_course_info('btc101')
        
        assert info['id'] == 'btc101'
        assert info['uuid'] == '123e4567-e89b-12d3-a456-426614174000'
        assert info['title'] == 'Bitcoin Fundamentals'
        assert info['title_slug'] == 'bitcoin-fundamentals'
    
    def test_get_course_info_not_found(self, temp_repo_path):
        """Test getting info for non-existent course."""
        manager = CourseManager(temp_repo_path)
        with pytest.raises(FileNotFoundError):
            manager.get_course_info('nonexistent')
    
    def test_build_pbn_url(self, temp_repo_path):
        """Test PlanB Network URL generation."""
        manager = CourseManager(temp_repo_path)
        
        # Test English URL
        url = manager.build_pbn_url('Bitcoin Fundamentals', '123-uuid', 'en')
        assert url == 'https://planb.network/en/courses/bitcoin-fundamentals-123-uuid'
        
        # Test other language
        url = manager.build_pbn_url('Bitcoin Fundamentals', '123-uuid', 'es')
        assert url == 'https://planb.network/es/courses/bitcoin-fundamentals-123-uuid'
        
        # Test title with special characters
        url = manager.build_pbn_url('Bitcoin & Lightning: Advanced!', '456-uuid', 'fr')
        assert url == 'https://planb.network/fr/courses/bitcoin-lightning-advanced-456-uuid'
    
    def test_build_github_urls(self, temp_repo_path):
        """Test GitHub URL generation."""
        manager = CourseManager(temp_repo_path)
        
        # Test English only
        urls = manager.build_github_urls('btc101', 'en', 'main')
        assert len(urls) == 1
        assert urls[0] == ('en', 'https://github.com/PlanB-Network/bitcoin-educational-content/blob/main/courses/btc101/en.md')
        
        # Test with different language
        urls = manager.build_github_urls('btc101', 'es', 'dev')
        assert len(urls) == 2
        assert urls[0] == ('en', 'https://github.com/PlanB-Network/bitcoin-educational-content/blob/dev/courses/btc101/en.md')
        assert urls[1] == ('es', 'https://github.com/PlanB-Network/bitcoin-educational-content/blob/dev/courses/btc101/es.md')
    
    def test_check_language_file_exists(self, temp_repo_path):
        """Test checking if language file exists."""
        manager = CourseManager(temp_repo_path)
        
        # English file exists
        assert manager.check_language_file_exists('btc101', 'en') is True
        
        # Spanish file doesn't exist
        assert manager.check_language_file_exists('btc101', 'es') is False
    
    def test_get_course_size(self, temp_repo_path):
        """Test course size estimation."""
        manager = CourseManager(temp_repo_path)
        
        # Small course (our test file has minimal content)
        size = manager.get_course_size('btc101', 'en')
        assert size == 'small'
        
        # Test with non-existent language (should fallback to English)
        size = manager.get_course_size('btc101', 'es')
        assert size == 'small'
    
    def test_validate_course_structure(self, temp_repo_path):
        """Test course structure validation."""
        manager = CourseManager(temp_repo_path)
        
        # Valid course
        is_valid, message = manager.validate_course_structure('btc101')
        assert is_valid is True
        assert message == 'Course structure is valid'
        
        # Non-existent course
        is_valid, message = manager.validate_course_structure('nonexistent')
        assert is_valid is False
        assert 'does not exist' in message