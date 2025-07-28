import pytest
import json
from unittest.mock import patch, Mock


class TestAPIEndpoints:
    def test_api_branch_search(self, authenticated_client):
        """Test branch search API endpoint."""
        with patch('app.get_branch_selector') as mock_get_selector:
            mock_selector = Mock()
            mock_selector.fuzzy_search.return_value = ['dev', 'main', 'es-translation']
            mock_get_selector.return_value = mock_selector
            
            response = authenticated_client.get('/api/branches/search?q=es')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'branches' in data
            assert 'es-translation' in data['branches']
    
    def test_api_branch_search_with_language_context(self, authenticated_client):
        """Test branch search with language context."""
        with patch('app.get_branch_selector') as mock_get_selector:
            mock_selector = Mock()
            mock_selector.fuzzy_search.return_value = ['es-initial-upload', 'es-proofreading']
            mock_get_selector.return_value = mock_selector
            
            response = authenticated_client.get('/api/branches/search?q=&lang=es')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            # Verify context was passed to fuzzy_search
            call_args = mock_selector.fuzzy_search.call_args
            assert call_args[1]['context'] == {'language': 'es'}
    
    def test_api_validate_branch(self, authenticated_client):
        """Test branch validation API endpoint."""
        with patch('app.get_branch_selector') as mock_get_selector:
            mock_selector = Mock()
            mock_selector.branch_exists.return_value = True
            mock_get_selector.return_value = mock_selector
            
            response = authenticated_client.get('/api/branches/validate/dev')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['exists'] is True
    
    def test_api_language_search(self, authenticated_client):
        """Test language search API endpoint."""
        response = authenticated_client.get('/api/languages/search?q=span')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'languages' in data
        # Should find Spanish
        spanish = next((l for l in data['languages'] if l['code'] == 'es'), None)
        assert spanish is not None
        assert 'Spanish' in spanish['name']
    
    def test_api_language_search_by_code(self, authenticated_client):
        """Test language search by code."""
        response = authenticated_client.get('/api/languages/search?q=fr')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # French should be the top result
        assert data['languages'][0]['code'] == 'fr'
    
    def test_api_weblate_languages(self, authenticated_client):
        """Test Weblate languages API endpoint."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'results': [
                    {'code': 'es', 'name': 'Spanish'},
                    {'code': 'fr', 'name': 'French'},
                    {'code': 'de', 'name': 'German'}
                ]
            }
            mock_get.return_value = mock_response
            
            response = authenticated_client.get('/api/weblate/languages')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'languages' in data
            assert len(data['languages']) == 3
            assert data['languages'][0]['display'] == 'Spanish (es)'
    
    def test_api_weblate_languages_fallback(self, authenticated_client):
        """Test Weblate languages fallback on API error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            response = authenticated_client.get('/api/weblate/languages')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            # Should fallback to Config.LANGUAGES
            assert len(data['languages']) > 0
            assert any(l['code'] == 'en' for l in data['languages'])
    
    def test_api_weblate_language_search(self, authenticated_client):
        """Test Weblate language search."""
        # First populate cache
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'results': [
                    {'code': 'es', 'name': 'Spanish'},
                    {'code': 'es-AR', 'name': 'Spanish (Argentina)'},
                    {'code': 'fr', 'name': 'French'}
                ]
            }
            mock_get.return_value = mock_response
            
            response = authenticated_client.get('/api/weblate/languages/search?q=spa')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            # Should find both Spanish variants
            spanish_langs = [l for l in data['languages'] if 'Spanish' in l['name']]
            assert len(spanish_langs) >= 2
    
    def test_weblate_preview(self, authenticated_client):
        """Test Weblate issue preview."""
        data = {
            'language': 'it',
            'iteration': '2nd',
            'urgency': 'urgent'
        }
        
        response = authenticated_client.post(
            '/weblate/preview',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['title'] == '[PROOFREADING] weblate - it'
        assert 'Weblate Url:' in result['body']
        assert 'website translation' in result['labels']
        assert result['project_fields']['Content Type'] == 'Weblate'
    
    def test_weblate_create(self, authenticated_client, mock_github, mock_requests):
        """Test Weblate issue creation."""
        with patch('app.get_github_integration') as mock_get_github:
            mock_github_integration = Mock()
            mock_github_integration.create_issue.return_value = mock_github['issue']
            mock_github_integration.link_to_project.return_value = True
            mock_github_integration.get_issue_url.return_value = 'https://github.com/test/repo/issues/789'
            mock_get_github.return_value = mock_github_integration
            
            data = {
                'language': 'pl',
                'iteration': '1st',
                'urgency': 'not urgent'
            }
            
            response = authenticated_client.post(
                '/weblate/create',
                json=data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            result = json.loads(response.data)
            assert result['success'] is True
            
            # Verify issue was created with correct labels
            call_args = mock_github_integration.create_issue.call_args
            assert 'website translation' in call_args[0][2]
            assert 'language - pl' in call_args[0][2]
    
    def test_config_save(self, client):
        """Test configuration save endpoint."""
        with patch('app.Config.validate_repo_path') as mock_validate:
            with patch('app.Config.save_config') as mock_save:
                with patch('github_integration.GitHubIntegration') as mock_github:
                    mock_validate.return_value = (True, "Valid")
                    mock_instance = Mock()
                    mock_instance.validate_token.return_value = (True, "Valid token")
                    mock_github.return_value = mock_instance
                    
                    data = {
                        'repo_path': '/test/repo',
                        'github_token': 'test-token',
                        'default_branch': 'main'
                    }
                    
                    response = client.post(
                        '/config',
                        json=data,
                        content_type='application/json'
                    )
                    assert response.status_code == 200
                    
                    result = json.loads(response.data)
                    assert result['success'] is True
                    
                    # Verify save was called
                    mock_save.assert_called_once()
    
    def test_config_invalid_repo(self, client):
        """Test configuration with invalid repo path."""
        with patch('app.Config.validate_repo_path') as mock_validate:
            mock_validate.return_value = (False, "Invalid path")
            
            data = {
                'repo_path': '/invalid/path',
                'github_token': 'test-token'
            }
            
            response = client.post(
                '/config',
                json=data,
                content_type='application/json'
            )
            assert response.status_code == 400
            
            result = json.loads(response.data)
            assert result['success'] is False
            assert 'Invalid path' in result['message']