import os
import yaml
from pathlib import Path
import re
from fuzzywuzzy import fuzz, process

class TutorialManager:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.tutorials_path = self.repo_path / 'tutorials'
    
    def get_tutorial_categories(self):
        """Get list of all tutorial categories"""
        if not self.tutorials_path.exists():
            return []
        
        categories = []
        for category_dir in self.tutorials_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                categories.append(category_dir.name)
        
        return sorted(categories)
    
    def get_tutorials_list(self):
        """Get list of all tutorials with their category"""
        tutorials = []
        
        if not self.tutorials_path.exists():
            return tutorials
        
        for category_dir in self.tutorials_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                category = category_dir.name
                
                for tutorial_dir in category_dir.iterdir():
                    if tutorial_dir.is_dir() and not tutorial_dir.name.startswith('.'):
                        # Check if it has a tutorial.yml file
                        if (tutorial_dir / 'tutorial.yml').exists():
                            tutorials.append({
                                'category': category,
                                'name': tutorial_dir.name,
                                'path': f"{category}/{tutorial_dir.name}"
                            })
        
        return sorted(tutorials, key=lambda x: x['path'])
    
    def search_tutorials(self, query, limit=10):
        """Fuzzy search tutorials by name or category"""
        tutorials = self.get_tutorials_list()
        
        if not query:
            return tutorials[:limit]
        
        # Create searchable strings
        searchable_tutorials = []
        for tutorial in tutorials:
            # Create multiple search strings for better matching
            search_strings = [
                tutorial['path'],  # "wallet/alby"
                tutorial['name'],  # "alby"
                f"{tutorial['category']} {tutorial['name']}",  # "wallet alby"
            ]
            searchable_tutorials.append((tutorial, search_strings))
        
        # Perform fuzzy search
        results = []
        for tutorial, search_strings in searchable_tutorials:
            # Get the best match score from all search strings
            scores = [fuzz.partial_ratio(query.lower(), s.lower()) for s in search_strings]
            best_score = max(scores)
            
            if best_score > 50:  # Threshold for relevance
                results.append((tutorial, best_score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [result[0] for result in results[:limit]]
    
    def get_tutorial_info(self, category, tutorial_name):
        """Extract tutorial info from tutorial.yml and en.md"""
        tutorial_path = self.tutorials_path / category / tutorial_name
        tutorial_yml_path = tutorial_path / 'tutorial.yml'
        en_md_path = tutorial_path / 'en.md'
        
        if not tutorial_yml_path.exists():
            raise FileNotFoundError(f"Tutorial config not found: {tutorial_yml_path}")
        
        if not en_md_path.exists():
            raise FileNotFoundError(f"English markdown file not found: {en_md_path}")
        
        # Get ID from tutorial.yml
        with open(tutorial_yml_path, 'r', encoding='utf-8') as f:
            tutorial_data = yaml.safe_load(f)
        
        tutorial_id = tutorial_data.get('id', '')
        if not tutorial_id:
            raise ValueError(f"Missing id in tutorial.yml for {category}/{tutorial_name}")
        
        # Get title from en.md header
        with open(en_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from the first H1 header
        title_match = re.match(r'^---[\s\S]*?---\s*#+\s+(.+)$', content.strip(), re.MULTILINE)
        if not title_match:
            # Try without frontmatter
            title_match = re.match(r'^#+\s+(.+)$', content.strip(), re.MULTILINE)
        
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Fallback to tutorial name
            title = tutorial_name.replace('-', ' ').title()
        
        return {
            'category': category,
            'name': tutorial_name,
            'id': tutorial_id,
            'title': title
        }
    
    def build_pbn_url(self, category, tutorial_name, title, uuid, lang='en'):
        """Build PlanB Network URL for tutorial"""
        # Clean and format the title
        clean_title = title.lower()
        
        # Replace special characters and spaces with hyphens
        clean_title = re.sub(r'[^\w\s-]', '', clean_title)
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        clean_title = clean_title.strip('-')
        
        # Build URL: /tutorials/{category}/{tutorial_name}/{title-slug}-{uuid}
        return f"https://planb.network/{lang}/tutorials/{category}/{tutorial_name}/{clean_title}-{uuid}"
    
    def build_github_urls(self, category, tutorial_name, lang, branch='dev'):
        """Build GitHub URLs (EN + selected language if different)"""
        base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/tutorials/{category}/{tutorial_name}"
        
        urls = []
        # Always include EN version
        en_url = f"{base_url}/en.md"
        urls.append(('en', en_url))
        
        # Add selected language if not EN
        if lang != 'en':
            lang_url = f"{base_url}/{lang}.md"
            urls.append((lang, lang_url))
        
        return urls
    
    def check_language_file_exists(self, category, tutorial_name, lang):
        """Check if a language file exists for the tutorial"""
        lang_file = self.tutorials_path / category / tutorial_name / f"{lang}.md"
        return lang_file.exists()
    
    def validate_tutorial_structure(self, category, tutorial_name):
        """Validate that tutorial has proper structure"""
        tutorial_path = self.tutorials_path / category / tutorial_name
        
        if not tutorial_path.exists():
            return False, "Tutorial directory does not exist"
        
        tutorial_yml = tutorial_path / 'tutorial.yml'
        if not tutorial_yml.exists():
            return False, "tutorial.yml file not found"
        
        en_md = tutorial_path / 'en.md'
        if not en_md.exists():
            return False, "English markdown file (en.md) not found"
        
        return True, "Tutorial structure is valid"
    
    def get_tutorial_sections(self):
        """Get all main tutorial category sections (wallet, node, mining, etc.)"""
        if not self.tutorials_path.exists():
            return []
        
        sections = []
        for category_dir in self.tutorials_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                # Check if it has any tutorials inside
                has_tutorials = False
                try:
                    for subdir in category_dir.iterdir():
                        if subdir.is_dir() and (subdir / 'tutorial.yml').exists():
                            has_tutorials = True
                            break
                except:
                    # Handle permission errors or other issues
                    pass
                
                if has_tutorials:
                    sections.append({
                        'name': category_dir.name,
                        'path': category_dir.name
                    })
        
        return sorted(sections, key=lambda x: x['name'])