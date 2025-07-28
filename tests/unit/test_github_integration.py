import pytest
from unittest.mock import Mock, patch, call
from github_integration import GitHubIntegration
from github import GithubException


class TestGitHubIntegration:
    def test_init(self, mock_github):
        """Test GitHubIntegration initialization."""
        github = GitHubIntegration('test-token')
        assert github.token == 'test-token'
        assert github.github is not None
        assert github.repo is not None
    
    def test_create_issue_success(self, mock_github):
        """Test successful issue creation."""
        github = GitHubIntegration('test-token')
        
        title = "Test Issue"
        body = "Test body"
        labels = ["test-label"]
        
        issue = github.create_issue(title, body, labels)
        
        assert issue.number == 123
        assert issue.html_url == 'https://github.com/test/repo/issues/123'
        
        # Verify the mock was called correctly
        mock_github['repo'].create_issue.assert_called_once_with(
            title=title,
            body=body,
            labels=labels
        )
    
    def test_create_issue_failure(self, mock_github):
        """Test issue creation failure."""
        github = GitHubIntegration('test-token')
        
        # Setup mock to raise exception
        mock_github['repo'].create_issue.side_effect = GithubException(
            status=403,
            data={'message': 'Forbidden'}
        )
        
        with pytest.raises(Exception) as exc_info:
            github.create_issue("Test", "Body", ["label"])
        
        assert "Failed to create issue" in str(exc_info.value)
    
    def test_link_to_project(self, mock_github, mock_requests):
        """Test linking issue to project."""
        github = GitHubIntegration('test-token')
        
        fields = {
            'Status': 'Todo',
            'Language': 'es',
            'Iteration': '1st',
            'Urgency': 'urgent'
        }
        
        result = github.link_to_project(mock_github['issue'], 'PROJECT_ID', fields)
        assert result is True
        
        # Verify GraphQL calls were made
        assert mock_requests.call_count >= 2  # At least add to project and get fields
    
    def test_link_to_project_with_node_id_fallback(self, mock_github, mock_requests):
        """Test link to project when node_id needs to be fetched."""
        github = GitHubIntegration('test-token')
        
        # Create issue without node_id attribute
        issue = Mock()
        issue.number = 456
        issue.html_url = 'https://github.com/test/repo/issues/456'
        # Remove node_id attribute
        delattr(issue, 'node_id')
        
        # Mock the REST API call to get node_id
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'node_id': 'MDU6SXNzdWU0NTY='}
            mock_get.return_value = mock_response
            
            result = github.link_to_project(issue, 'PROJECT_ID', {'Status': 'Todo'})
            assert result is True
            
            # Verify REST API was called
            mock_get.assert_called_once()
    
    def test_get_issue_url(self, mock_github):
        """Test getting issue URL."""
        github = GitHubIntegration('test-token')
        url = github.get_issue_url(mock_github['issue'])
        assert url == 'https://github.com/test/repo/issues/123'
    
    def test_validate_token_success(self, mock_github):
        """Test successful token validation."""
        with patch('github_integration.Github') as mock_github_class:
            mock_instance = Mock()
            mock_user = Mock()
            mock_user.login = 'testuser'
            mock_repo = Mock()
            
            mock_github_class.return_value = mock_instance
            mock_instance.get_user.return_value = mock_user
            mock_instance.get_repo.return_value = mock_repo
            
            github = GitHubIntegration('test-token')
            is_valid, message = github.validate_token()
            
            assert is_valid is True
            assert 'testuser' in message
    
    def test_validate_token_failure(self, mock_github):
        """Test token validation failure."""
        with patch('github_integration.Github') as mock_github_class:
            mock_instance = Mock()
            mock_instance.get_user.side_effect = Exception("Invalid token")
            mock_github_class.return_value = mock_instance
            
            github = GitHubIntegration('test-token')
            is_valid, message = github.validate_token()
            
            assert is_valid is False
            assert 'Invalid token' in message
    
    def test_set_project_fields_with_alternatives(self, mock_github, mock_requests):
        """Test setting project fields with alternative field names."""
        github = GitHubIntegration('test-token')
        
        # Mock response with different field names
        mock_requests.return_value.json.return_value = {
            'data': {
                'node': {
                    'fields': {
                        'nodes': [
                            {
                                'id': 'PVTF_status',
                                'name': 'status',  # lowercase
                                'options': [
                                    {'id': 'PVTFO_todo', 'name': 'Todo'}
                                ]
                            },
                            {
                                'id': 'PVTF_type',
                                'name': 'Type',  # Different from 'Content Type'
                                'options': [
                                    {'id': 'PVTFO_course', 'name': 'Course'}
                                ]
                            }
                        ]
                    }
                }
            }
        }
        
        github._set_project_fields('ITEM_ID', 'PROJECT_ID', {
            'Status': 'Todo',
            'Content Type': 'Course'
        })
        
        # Should make at least 3 calls: get fields + 2 updates
        assert mock_requests.call_count >= 3