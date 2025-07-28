import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from branch_selector import BranchSelector


class TestBranchSelector:
    def test_init(self):
        """Test BranchSelector initialization."""
        selector = BranchSelector('test-token', '/test/path')
        assert selector.github is not None
        assert selector.local_repo_path.as_posix() == '/test/path'
        assert selector._branches_cache is None
    
    def test_get_branches_from_cache(self, mock_github):
        """Test getting branches from cache."""
        selector = BranchSelector('test-token')
        
        # Set up cache
        selector._branches_cache = ['main', 'dev', 'feature-1']
        selector._cache_time = datetime.now()
        
        branches = selector.get_branches()
        assert branches == ['main', 'dev', 'feature-1']
        
        # Verify no API call was made
        assert not hasattr(selector, 'repo') or selector.repo is None
    
    def test_get_branches_expired_cache(self, mock_github):
        """Test getting branches with expired cache."""
        selector = BranchSelector('test-token')
        
        # Set up expired cache
        selector._branches_cache = ['old-branch']
        selector._cache_time = datetime.now() - timedelta(minutes=10)
        
        # Mock repo branches
        branch1 = Mock()
        branch1.name = 'main'
        branch2 = Mock()
        branch2.name = 'dev'
        
        mock_repo = Mock()
        mock_repo.get_branches.return_value = [branch1, branch2]
        
        with patch.object(selector, '_get_repo', return_value=mock_repo):
            branches = selector.get_branches()
        
        assert 'main' in branches
        assert 'dev' in branches
        assert 'old-branch' not in branches
    
    def test_get_local_branches(self):
        """Test getting branches from local repository."""
        selector = BranchSelector('test-token', '/test/path')
        
        # Mock subprocess run
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = """
  main
* dev
  remotes/origin/main
  remotes/origin/dev
  remotes/origin/feature-branch
  remotes/origin/HEAD
"""
            mock_run.return_value = mock_result
            
            branches = selector.get_local_branches()
            
            assert 'main' in branches
            assert 'dev' in branches
            assert 'feature-branch' in branches
            assert 'HEAD' not in branches  # HEAD should be filtered out
    
    def test_fuzzy_search_empty_query(self):
        """Test fuzzy search with empty query."""
        selector = BranchSelector('test-token')
        selector._branches_cache = ['main', 'dev', 'es-translation', 'fr-proofreading']
        selector._cache_time = datetime.now()
        
        results = selector.fuzzy_search('', limit=3)
        assert len(results) <= 3
        assert 'dev' in results  # Common branches should be prioritized
    
    def test_fuzzy_search_with_language_context(self):
        """Test fuzzy search with language context."""
        selector = BranchSelector('test-token')
        selector._branches_cache = [
            'main', 'dev', 'es-initial-upload', 'fr-translation',
            'es-proofreading', 'feature-xyz'
        ]
        selector._cache_time = datetime.now()
        
        context = {'language': 'es'}
        results = selector.fuzzy_search('', limit=5, context=context)
        
        # Spanish-related branches should be prioritized
        es_branches = [b for b in results if 'es' in b]
        assert len(es_branches) >= 2
        assert results.index('es-initial-upload') < results.index('feature-xyz')
    
    def test_fuzzy_search_exact_match(self):
        """Test fuzzy search with exact match."""
        selector = BranchSelector('test-token')
        selector._branches_cache = ['main', 'dev', 'feature-1', 'feature-2']
        selector._cache_time = datetime.now()
        
        results = selector.fuzzy_search('dev')
        assert results[0] == 'dev'  # Exact match should be first
    
    def test_fuzzy_search_prefix_match(self):
        """Test fuzzy search with prefix matching."""
        selector = BranchSelector('test-token')
        selector._branches_cache = ['main', 'develop', 'dev-feature', 'feature-dev']
        selector._cache_time = datetime.now()
        
        results = selector.fuzzy_search('dev')
        
        # Prefix matches should come before contains matches
        assert results.index('develop') < results.index('feature-dev')
        assert results.index('dev-feature') < results.index('feature-dev')
    
    def test_branch_exists(self):
        """Test checking if branch exists."""
        selector = BranchSelector('test-token')
        selector._branches_cache = ['main', 'dev', 'feature-1']
        selector._cache_time = datetime.now()
        
        assert selector.branch_exists('main') is True
        assert selector.branch_exists('dev') is True
        assert selector.branch_exists('nonexistent') is False
    
    def test_get_default_branch(self, mock_github):
        """Test getting default branch."""
        selector = BranchSelector('test-token')
        
        mock_repo = Mock()
        mock_repo.default_branch = 'main'
        
        with patch.object(selector, '_get_repo', return_value=mock_repo):
            default = selector.get_default_branch()
        
        assert default == 'main'
    
    def test_get_default_branch_fallback(self):
        """Test default branch fallback on error."""
        selector = BranchSelector('test-token')
        
        with patch.object(selector, '_get_repo', side_effect=Exception("API Error")):
            default = selector.get_default_branch()
        
        assert default == 'dev'  # Fallback value
    
    def test_get_language_branches(self):
        """Test getting language-specific branches."""
        selector = BranchSelector('test-token')
        selector._branches_cache = [
            'main', 'dev', 'es-translation', 'proofreading-es',
            'ES-update', 'test-es', 'feature-spanish'
        ]
        selector._cache_time = datetime.now()
        
        es_branches = selector.get_language_branches('es')
        
        assert 'es-translation' in es_branches
        assert 'proofreading-es' in es_branches
        assert 'ES-update' in es_branches
        assert 'test-es' in es_branches
        assert 'main' not in es_branches
        assert 'dev' not in es_branches