from github import Github
from fuzzywuzzy import fuzz, process
import time
from datetime import datetime, timedelta
import subprocess
from pathlib import Path
import re

class BranchSelector:
    def __init__(self, github_token, local_repo_path=None):
        self.github = Github(github_token)
        self.repo = None
        self.local_repo_path = Path(local_repo_path) if local_repo_path else None
        self._branches_cache = None
        self._cache_time = None
        self._cache_duration = timedelta(minutes=5)
        self._local_branches_cache = None
        self._local_cache_time = None
    
    def _get_repo(self):
        """Lazy load repository"""
        if self.repo is None:
            self.repo = self.github.get_repo("PlanB-Network/bitcoin-educational-content")
        return self.repo
    
    def get_local_branches(self):
        """Get branches from local repository"""
        if not self.local_repo_path or not self.local_repo_path.exists():
            return []
        
        now = datetime.now()
        
        # Check if local cache is valid (1 minute cache)
        if (self._local_branches_cache is not None and 
            self._local_cache_time is not None and 
            now - self._local_cache_time < timedelta(minutes=1)):
            return self._local_branches_cache
        
        try:
            # Run git command to get all branches (local and remote)
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = []
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('*'):
                    line = line[2:]  # Remove current branch marker
                
                # Extract branch name
                if line.startswith('remotes/origin/'):
                    branch = line.replace('remotes/origin/', '')
                    if branch != 'HEAD':
                        branches.append(branch)
                else:
                    branches.append(line)
            
            # Remove duplicates and sort
            branches = sorted(list(set(branches)))
            
            # Update cache
            self._local_branches_cache = branches
            self._local_cache_time = now
            
            return branches
        except Exception as e:
            print(f"Error getting local branches: {e}")
            return []
    
    def get_branches(self, force_refresh=False):
        """Fetch all branches from repository with caching"""
        # Try local first for better performance
        local_branches = self.get_local_branches()
        if local_branches:
            return local_branches
        
        # Fallback to GitHub API
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
    
    def fuzzy_search(self, query, limit=10, context=None):
        """Fuzzy search branches with intelligent suggestions"""
        branches = self.get_branches()
        
        if not query:
            # Smart default suggestions based on context
            suggestions = []
            
            # Always include common branches
            common_branches = ['dev', 'main', 'master']
            for branch in common_branches:
                if branch in branches:
                    suggestions.append(branch)
            
            # If we have language context, suggest language-specific branches
            if context and 'language' in context:
                lang = context['language']
                language_patterns = [
                    f"{lang}-initial-upload",
                    f"{lang}-proofreading",
                    f"{lang}-translation",
                    f"proofreading-{lang}",
                    f"translation-{lang}"
                ]
                
                for pattern in language_patterns:
                    for branch in branches:
                        if pattern in branch.lower() and branch not in suggestions:
                            suggestions.append(branch)
            
            # Add other branches
            other_branches = [b for b in branches if b not in suggestions]
            suggestions.extend(other_branches[:limit-len(suggestions)])
            
            return suggestions[:limit]
        
        # If exact match exists, prioritize it
        if query in branches:
            return [query] + [b for b in branches if b != query][:limit-1]
        
        # Smart matching with different strategies
        results = []
        
        # 1. Exact prefix match
        prefix_matches = [b for b in branches if b.lower().startswith(query.lower())]
        results.extend(prefix_matches)
        
        # 2. Contains match
        contains_matches = [b for b in branches if query.lower() in b.lower() and b not in results]
        results.extend(contains_matches)
        
        # 3. Fuzzy matching for remaining slots
        if len(results) < limit:
            remaining_branches = [b for b in branches if b not in results]
            fuzzy_matches = process.extract(query, remaining_branches, scorer=fuzz.token_sort_ratio, limit=limit-len(results))
            results.extend([match[0] for match in fuzzy_matches if match[1] > 40])
        
        return results[:limit]
    
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