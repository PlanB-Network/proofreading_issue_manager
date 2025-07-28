import pytest
from pathlib import Path
from tutorial_manager import TutorialManager


class TestTutorialManager:
    def test_init(self, temp_repo_path):
        """Test TutorialManager initialization."""
        manager = TutorialManager(temp_repo_path)
        assert manager.repo_path == Path(temp_repo_path)
        assert manager.tutorials_path == Path(temp_repo_path) / 'tutorials'
    
    def test_get_tutorial_categories(self, temp_repo_path):
        """Test getting tutorial categories."""
        manager = TutorialManager(temp_repo_path)
        categories = manager.get_tutorial_categories()
        assert 'wallet' in categories
        assert len(categories) == 1
    
    def test_get_tutorials_list(self, temp_repo_path):
        """Test getting list of all tutorials."""
        manager = TutorialManager(temp_repo_path)
        tutorials = manager.get_tutorials_list()
        
        assert len(tutorials) == 1
        assert tutorials[0]['category'] == 'wallet'
        assert tutorials[0]['name'] == 'electrum'
        assert tutorials[0]['path'] == 'wallet/electrum'
    
    def test_search_tutorials(self, temp_repo_path):
        """Test tutorial search functionality."""
        manager = TutorialManager(temp_repo_path)
        
        # Search by name
        results = manager.search_tutorials('electrum')
        assert len(results) == 1
        assert results[0]['name'] == 'electrum'
        
        # Search by category
        results = manager.search_tutorials('wallet')
        assert len(results) == 1
        assert results[0]['category'] == 'wallet'
        
        # Empty search
        results = manager.search_tutorials('')
        assert len(results) == 1
        
        # No matches
        results = manager.search_tutorials('nonexistent')
        assert len(results) == 0
    
    def test_get_tutorial_info(self, temp_repo_path):
        """Test getting tutorial information."""
        manager = TutorialManager(temp_repo_path)
        info = manager.get_tutorial_info('wallet', 'electrum')
        
        assert info['category'] == 'wallet'
        assert info['name'] == 'electrum'
        assert info['id'] == '987f6543-e21b-12d3-a456-426614174000'
        assert info['title'] == 'Electrum Wallet Tutorial'
    
    def test_get_tutorial_info_not_found(self, temp_repo_path):
        """Test getting info for non-existent tutorial."""
        manager = TutorialManager(temp_repo_path)
        with pytest.raises(FileNotFoundError):
            manager.get_tutorial_info('wallet', 'nonexistent')
    
    def test_build_pbn_url(self, temp_repo_path):
        """Test PlanB Network URL generation for tutorials."""
        manager = TutorialManager(temp_repo_path)
        
        url = manager.build_pbn_url('wallet', 'electrum', 'Electrum Wallet Tutorial', '123-uuid', 'en')
        expected = 'https://planb.network/en/tutorials/wallet/electrum/electrum-wallet-tutorial-123-uuid'
        assert url == expected
        
        # Test with special characters
        url = manager.build_pbn_url('exchange', 'kraken', 'Kraken: Buy & Sell', '456-uuid', 'fr')
        expected = 'https://planb.network/fr/tutorials/exchange/kraken/kraken-buy-sell-456-uuid'
        assert url == expected
    
    def test_build_github_urls(self, temp_repo_path):
        """Test GitHub URL generation for tutorials."""
        manager = TutorialManager(temp_repo_path)
        
        # English only
        urls = manager.build_github_urls('wallet', 'electrum', 'en', 'main')
        assert len(urls) == 1
        base = 'https://github.com/PlanB-Network/bitcoin-educational-content/blob/main/tutorials/wallet/electrum'
        assert urls[0] == ('en', f'{base}/en.md')
        
        # Multiple languages
        urls = manager.build_github_urls('wallet', 'electrum', 'es', 'dev')
        assert len(urls) == 2
        base = 'https://github.com/PlanB-Network/bitcoin-educational-content/blob/dev/tutorials/wallet/electrum'
        assert urls[0] == ('en', f'{base}/en.md')
        assert urls[1] == ('es', f'{base}/es.md')
    
    def test_check_language_file_exists(self, temp_repo_path):
        """Test checking if language file exists for tutorial."""
        manager = TutorialManager(temp_repo_path)
        
        # English exists
        assert manager.check_language_file_exists('wallet', 'electrum', 'en') is True
        
        # Spanish doesn't exist
        assert manager.check_language_file_exists('wallet', 'electrum', 'es') is False
    
    def test_validate_tutorial_structure(self, temp_repo_path):
        """Test tutorial structure validation."""
        manager = TutorialManager(temp_repo_path)
        
        # Valid tutorial
        is_valid, message = manager.validate_tutorial_structure('wallet', 'electrum')
        assert is_valid is True
        assert message == 'Tutorial structure is valid'
        
        # Non-existent tutorial
        is_valid, message = manager.validate_tutorial_structure('wallet', 'nonexistent')
        assert is_valid is False
        assert 'does not exist' in message
    
    def test_get_tutorial_sections(self, temp_repo_path):
        """Test getting tutorial sections."""
        manager = TutorialManager(temp_repo_path)
        sections = manager.get_tutorial_sections()
        
        assert len(sections) == 1
        assert sections[0]['name'] == 'wallet'
        assert sections[0]['path'] == 'wallet'