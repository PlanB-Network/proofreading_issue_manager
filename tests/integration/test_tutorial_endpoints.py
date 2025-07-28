import pytest
import json
from unittest.mock import patch, Mock


class TestTutorialEndpoints:
    def test_new_tutorial_issue_redirect(self, client):
        """Test that tutorial form redirects when not configured."""
        response = client.get('/tutorial/new')
        assert response.status_code == 302
        assert '/config' in response.location
    
    def test_new_tutorial_issue_authenticated(self, authenticated_client):
        """Test tutorial form loads when authenticated."""
        with patch('app.Config.BITCOIN_CONTENT_REPO_PATH', '/test/path'):
            response = authenticated_client.get('/tutorial/new')
            assert response.status_code == 200
            assert b'Create Tutorial Proofreading Issue' in response.data
    
    def test_api_tutorials(self, authenticated_client):
        """Test tutorials API endpoint."""
        with patch('app.get_tutorial_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_tutorials_list.return_value = [
                {'category': 'wallet', 'name': 'electrum', 'path': 'wallet/electrum'},
                {'category': 'node', 'name': 'bitcoin-core', 'path': 'node/bitcoin-core'}
            ]
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/tutorials')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'tutorials' in data
            assert len(data['tutorials']) == 2
            assert data['tutorials'][0]['path'] == 'wallet/electrum'
    
    def test_api_tutorials_search(self, authenticated_client):
        """Test tutorials search API endpoint."""
        with patch('app.get_tutorial_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.search_tutorials.return_value = [
                {'category': 'wallet', 'name': 'electrum', 'path': 'wallet/electrum'}
            ]
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/tutorials/search?q=electrum')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data['tutorials']) == 1
            assert data['tutorials'][0]['name'] == 'electrum'
    
    def test_api_tutorial_info(self, authenticated_client):
        """Test tutorial info API endpoint."""
        with patch('app.get_tutorial_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_tutorial_info.return_value = {
                'category': 'wallet',
                'name': 'electrum',
                'id': '987-uuid',
                'title': 'Electrum Wallet Tutorial'
            }
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/tutorial/wallet/electrum')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['name'] == 'electrum'
            assert data['title'] == 'Electrum Wallet Tutorial'
    
    def test_preview_tutorial_issue(self, authenticated_client, sample_tutorial_data):
        """Test tutorial issue preview."""
        with patch('app.get_tutorial_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_tutorial_info.return_value = {
                'category': 'wallet',
                'name': 'electrum',
                'id': '987-uuid',
                'title': 'Electrum Wallet Tutorial'
            }
            mock_manager.build_pbn_url.return_value = 'https://planb.network/fr/tutorials/wallet/electrum/...'
            mock_manager.build_github_urls.return_value = [
                ('en', 'https://github.com/.../en.md'),
                ('fr', 'https://github.com/.../fr.md')
            ]
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.post(
                '/tutorial/preview',
                json=sample_tutorial_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['title'] == '[PROOFREADING] wallet/electrum - fr'
            assert 'content - tutorial' in data['labels']
            assert data['project_fields']['Content Type'] == 'Tutorial'
    
    def test_create_tutorial_issue(self, authenticated_client, sample_tutorial_data, mock_github, mock_requests):
        """Test tutorial issue creation."""
        with patch('app.get_github_integration') as mock_get_github:
            with patch('app.get_tutorial_manager') as mock_get_manager:
                # Setup mocks
                mock_github_integration = Mock()
                mock_github_integration.create_issue.return_value = mock_github['issue']
                mock_github_integration.link_to_project.return_value = True
                mock_github_integration.get_issue_url.return_value = 'https://github.com/test/repo/issues/123'
                mock_get_github.return_value = mock_github_integration
                
                mock_manager = Mock()
                mock_manager.get_tutorial_info.return_value = {
                    'category': 'wallet',
                    'name': 'electrum',
                    'id': '987-uuid',
                    'title': 'Electrum Wallet Tutorial'
                }
                mock_manager.build_pbn_url.return_value = 'https://planb.network/fr/tutorials/...'
                mock_manager.build_github_urls.return_value = [
                    ('en', 'https://github.com/.../en.md'),
                    ('fr', 'https://github.com/.../fr.md')
                ]
                mock_get_manager.return_value = mock_manager
                
                response = authenticated_client.post(
                    '/tutorial/create',
                    json=sample_tutorial_data,
                    content_type='application/json'
                )
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['issue_number'] == 123
    
    def test_api_tutorial_sections(self, authenticated_client):
        """Test tutorial sections API endpoint."""
        with patch('app.get_tutorial_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_tutorial_sections.return_value = [
                {'name': 'wallet', 'path': 'wallet'},
                {'name': 'node', 'path': 'node'},
                {'name': 'mining', 'path': 'mining'}
            ]
            mock_get_manager.return_value = mock_manager
            
            response = authenticated_client.get('/api/tutorial-sections')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'sections' in data
            assert len(data['sections']) == 3
            assert any(s['name'] == 'wallet' for s in data['sections'])
    
    def test_preview_tutorial_section_issue(self, authenticated_client):
        """Test tutorial section issue preview."""
        data = {
            'section': 'wallet',
            'language': 'es',
            'branch': 'main',
            'iteration': '3rd',
            'urgency': 'urgent'
        }
        
        response = authenticated_client.post(
            '/tutorial-section/preview',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['title'] == '[PROOFREADING] wallet_section - es'
        assert 'English PBN Version:' in result['body']
        assert 'Folder GitHub Version:' in result['body']
        assert result['project_fields']['Iteration'] == '3rd'
    
    def test_create_tutorial_section_issue(self, authenticated_client, mock_github, mock_requests):
        """Test tutorial section issue creation."""
        with patch('app.get_github_integration') as mock_get_github:
            mock_github_integration = Mock()
            mock_github_integration.create_issue.return_value = mock_github['issue']
            mock_github_integration.link_to_project.return_value = True
            mock_github_integration.get_issue_url.return_value = 'https://github.com/test/repo/issues/456'
            mock_get_github.return_value = mock_github_integration
            
            data = {
                'section': 'node',
                'language': 'ja',
                'branch': 'dev',
                'iteration': '1st',
                'urgency': 'not urgent'
            }
            
            response = authenticated_client.post(
                '/tutorial-section/create',
                json=data,
                content_type='application/json'
            )
            assert response.status_code == 200
            
            result = json.loads(response.data)
            assert result['success'] is True
            assert result['issue_number'] == 123  # From mock
            
            # Verify correct title was used
            call_args = mock_github_integration.create_issue.call_args
            assert '[PROOFREADING] node_section - ja' in call_args[0]