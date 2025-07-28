import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from app import app
from config import Config


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def authenticated_client(client):
    """Create a test client with session data."""
    with client.session_transaction() as sess:
        sess['github_token'] = 'test-token'
        sess['repo_path'] = '/test/repo/path'
        sess['default_branch'] = 'dev'
    return client


@pytest.fixture
def temp_repo_path():
    """Create a temporary repository structure for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Create basic structure
    (repo_path / 'courses').mkdir(parents=True)
    (repo_path / 'tutorials').mkdir(parents=True)
    
    # Create sample course
    course_dir = repo_path / 'courses' / 'btc101'
    course_dir.mkdir()
    
    # Create course.yml
    course_yml = course_dir / 'course.yml'
    course_yml.write_text("""id: 123e4567-e89b-12d3-a456-426614174000
name: Bitcoin Basics
description: Introduction to Bitcoin
""")
    
    # Create en.md
    en_md = course_dir / 'en.md'
    en_md.write_text("""# Bitcoin Fundamentals

This is a basic course about Bitcoin.
""")
    
    # Create sample tutorial
    tutorial_cat = repo_path / 'tutorials' / 'wallet'
    tutorial_cat.mkdir()
    tutorial_dir = tutorial_cat / 'electrum'
    tutorial_dir.mkdir()
    
    # Create tutorial.yml
    tutorial_yml = tutorial_dir / 'tutorial.yml'
    tutorial_yml.write_text("""id: 987f6543-e21b-12d3-a456-426614174000
name: Electrum Wallet
description: How to use Electrum
""")
    
    # Create en.md
    tutorial_md = tutorial_dir / 'en.md'
    tutorial_md.write_text("""# Electrum Wallet Tutorial

Learn how to use Electrum wallet.
""")
    
    yield str(repo_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_github():
    """Mock GitHub integration."""
    with patch('github_integration.Github') as mock_github_class:
        mock_instance = Mock()
        mock_repo = Mock()
        
        # Setup mock returns
        mock_github_class.return_value = mock_instance
        mock_instance.get_repo.return_value = mock_repo
        
        # Mock issue creation
        mock_issue = Mock()
        mock_issue.number = 123
        mock_issue.html_url = 'https://github.com/test/repo/issues/123'
        mock_issue.node_id = 'MDU6SXNzdWUxMjM='
        mock_repo.create_issue.return_value = mock_issue
        
        yield {
            'github_class': mock_github_class,
            'instance': mock_instance,
            'repo': mock_repo,
            'issue': mock_issue
        }


@pytest.fixture
def mock_requests():
    """Mock requests for GraphQL calls."""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'addProjectV2ItemById': {
                    'item': {'id': 'PVI_123'}
                },
                'node': {
                    'fields': {
                        'nodes': [
                            {
                                'id': 'PVTF_status',
                                'name': 'Status',
                                'options': [
                                    {'id': 'PVTFO_todo', 'name': 'Todo'},
                                    {'id': 'PVTFO_done', 'name': 'Done'}
                                ]
                            },
                            {
                                'id': 'PVTF_lang',
                                'name': 'Language'
                            }
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def sample_course_data():
    """Sample course data for testing."""
    return {
        'course_id': 'btc101',
        'language': 'es',
        'branch': 'dev',
        'iteration': '1st',
        'urgency': 'not urgent'
    }


@pytest.fixture
def sample_tutorial_data():
    """Sample tutorial data for testing."""
    return {
        'tutorial_path': 'wallet/electrum',
        'language': 'fr',
        'branch': 'dev',
        'iteration': '2nd',
        'urgency': 'urgent'
    }