from github import Github
from fuzzywuzzy import fuzz, process
import time
from datetime import datetime, timedelta

class BranchSelector:
    def __init__(self, github_token):
        self.github = Github(github_token)
        self.repo = None
        self._branches_cache = None
        self._cache_time = None
        self._cache_duration = timedelta(minutes=5)
    
    def _get_repo(self):
        """Lazy load repository"""
        if self.repo is None:
            self.repo = self.github.get_repo("PlanB-Network/bitcoin-educational-content")
        return self.repo
    
    def get_branches(self, force_refresh=False):
        """Fetch all branches from repository with caching"""
        now = datetime.now()
        
        # Check if cache is valid
        if (not force_refresh and 
            self._branches_cache is not None and 
            self._cache_time is not None and 
            now - self._cache_time < self._cache_duration):
            return self._branches_cache
        
        try:
            # Fetch branches from GitHub
            repo = self._get_repo()
            branches = [branch.name for branch in repo.get_branches()]
            
            # Update cache
            self._branches_cache = branches
            self._cache_time = now
            
            return branches
        except Exception as e:
            print(f"Error fetching branches: {e}")
            # Return cached data if available, otherwise return default
            if self._branches_cache:
                return self._branches_cache
            return ['dev', 'main']
    
    def fuzzy_search(self, query, limit=10):
        """Fuzzy search branches"""
        if not query:
            branches = self.get_branches()
            # Return most common branches first
            common_branches = ['dev', 'main', 'master']
            other_branches = [b for b in branches if b not in common_branches]
            return common_branches + other_branches[:limit-len(common_branches)]
        
        branches = self.get_branches()
        
        # If exact match exists, prioritize it
        if query in branches:
            return [query] + [b for b in branches if b != query][:limit-1]
        
        # Use fuzzy matching
        matches = process.extract(query, branches, scorer=fuzz.token_sort_ratio, limit=limit)
        return [match[0] for match in matches if match[1] > 30]  # Only return matches with >30% similarity
    
    def branch_exists(self, branch_name):
        """Check if a branch exists"""
        branches = self.get_branches()
        return branch_name in branches
    
    def get_default_branch(self):
        """Get the default branch of the repository"""
        try:
            repo = self._get_repo()
            return repo.default_branch
        except:
            return 'dev'
    
    def get_language_branches(self, language_code):
        """Get branches that might be related to a specific language"""
        branches = self.get_branches()
        language_branches = []
        
        # Common patterns for language branches
        patterns = [
            f"{language_code}-",
            f"-{language_code}-",
            f"-{language_code}",
            f"{language_code}_",
            language_code.upper(),
        ]
        
        for branch in branches:
            for pattern in patterns:
                if pattern in branch:
                    language_branches.append(branch)
                    break
        
        return language_branches