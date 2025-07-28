import pytest
import json
from unittest.mock import patch, Mock


class TestCourseEndpoints:
    def test_new_course_issue_redirect(self, client):
        """Test that course form redirects when not configured."""
        response = client.get('/course/new')
        assert response.status_code == 302
        assert '/config' in response.location
    
    def test_new_course_issue_authenticated(self, authenticated_client):
        """Test course form loads when authenticated."""
        with patch('app.Config.BITCOIN_CONTENT_REPO_PATH', '/test/path'):
            response = authenticated_client.get('/course/new')
            assert response.status_code == 200
            assert b'Create Course Proofreading Issue' in response.data
    
    def test_api_courses(self, authenticated_client, temp_repo_path):
        """Test courses API endpoint."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_list.return_value = ['btc101', 'ln201']
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/courses')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'courses' in data
            assert 'btc101' in data['courses']
            assert 'ln201' in data['courses']
    
    def test_api_course_info(self, authenticated_client):
        """Test course info API endpoint."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_info.return_value = {
                'id': 'btc101',
                'uuid': '123-uuid',
                'title': 'Bitcoin Fundamentals',
                'title_slug': 'bitcoin-fundamentals'
            }
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/course/btc101')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['id'] == 'btc101'
            assert data['title'] == 'Bitcoin Fundamentals'
    
    def test_api_course_info_not_found(self, authenticated_client):
        """Test course info API with non-existent course."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_info.side_effect = FileNotFoundError("Course not found")
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/course/nonexistent')
            assert response.status_code == 404
            assert b'Course not found' in response.data
    
    def test_preview_course_issue(self, authenticated_client, sample_course_data):
        """Test course issue preview."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_info.return_value = {
                'id': 'btc101',
                'uuid': '123-uuid',
                'title': 'Bitcoin Fundamentals',
                'title_slug': 'bitcoin-fundamentals'
            }
            mock_manager.build_pbn_url.return_value = 'https://planb.network/es/courses/bitcoin-fundamentals-123-uuid'
            mock_manager.build_github_urls.return_value = [
                ('en', 'https://github.com/.../en.md'),
                ('es', 'https://github.com/.../es.md')
            ]
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.post(
                '/course/preview',
                json=sample_course_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['title'] == '[PROOFREADING] btc101 - es'
            assert 'en PBN version:' in data['body']
            assert 'content - course' in data['labels']
            assert data['project_fields']['Language'] == 'es'
    
    def test_create_course_issue(self, authenticated_client, sample_course_data, mock_github, mock_requests):
        """Test course issue creation."""
        with patch('app.get_github_integration') as mock_get_github:
            with patch('app.get_course_manager') as mock_get_manager:
                # Setup mocks
                mock_github_integration = Mock()
                mock_github_integration.create_issue.return_value = mock_github['issue']
                mock_github_integration.link_to_project.return_value = True
                mock_github_integration.get_issue_url.return_value = 'https://github.com/test/repo/issues/123'
                mock_get_github.return_value = mock_github_integration
                
                mock_manager = Mock()
                mock_manager.get_course_info.return_value = {
                    'id': 'btc101',
                    'uuid': '123-uuid',
                    'title': 'Bitcoin Fundamentals',
                    'title_slug': 'bitcoin-fundamentals'
                }
                mock_manager.build_pbn_url.return_value = 'https://planb.network/es/courses/bitcoin-fundamentals-123-uuid'
                mock_manager.build_github_urls.return_value = [
                    ('en', 'https://github.com/.../en.md'),
                    ('es', 'https://github.com/.../es.md')
                ]
                mock_get_manager.return_value = mock_manager
                
                response = authenticated_client.post(
                    '/course/create',
                    json=sample_course_data,
                    content_type='application/json'
                )
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['issue_number'] == 123
                assert 'github.com' in data['issue_url']
                
                # Verify issue was created with correct parameters
                mock_github_integration.create_issue.assert_called_once()
                call_args = mock_github_integration.create_issue.call_args
                assert '[PROOFREADING] btc101 - es' in call_args[0]
                assert 'content - course' in call_args[0][2]  # labels
    
    def test_video_course_preview(self, authenticated_client):
        """Test video course issue preview."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_info.return_value = {
                'id': 'btc101',
                'uuid': '123-uuid',
                'title': 'Bitcoin Fundamentals',
                'title_slug': 'bitcoin-fundamentals'
            }
            mock_get_manager.return_value = mock_manager
            
            data = {
                'course_id': 'btc101',
                'language': 'fr',
                'branch': 'dev',
                'iteration': '1st',
                'urgency': 'urgent'
            }
            
            response = authenticated_client.post(
                '/video-course/preview',
                json=data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            result = json.loads(response.data)
            assert result['title'] == '[VIDEO-PROOFREADING] btc101 - fr'
            assert 'video transcript' in result['labels']
            assert result['project_fields']['Content Type'] == 'Video Course'
    
    def test_image_course_preview(self, authenticated_client):
        """Test image course issue preview."""
        with patch('app.get_course_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_course_info.return_value = {
                'id': 'btc101',
                'uuid': '123-uuid',
                'title': 'Bitcoin Fundamentals',
                'title_slug': 'bitcoin-fundamentals'
            }
            mock_get_manager.return_value = mock_manager
            
            data = {
                'course_id': 'btc101',
                'language': 'de',
                'branch': 'main',
                'iteration': '2nd',
                'urgency': 'not urgent'
            }
            
            response = authenticated_client.post(
                '/image-course/preview',
                json=data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            result = json.loads(response.data)
            assert result['title'] == '[IMAGE-PROOFREADING] btc101 - de'
            assert 'content - images' in result['labels']
            assert result['project_fields']['Content Type'] == 'Image Course'