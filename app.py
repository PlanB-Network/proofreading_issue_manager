from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from course_manager import CourseManager
from tutorial_manager import TutorialManager
from branch_selector import BranchSelector
from github_integration import GitHubIntegration
import os
from pathlib import Path
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Cache for Weblate languages
weblate_languages_cache = {
    'data': None,
    'last_updated': None,
    'ttl': timedelta(hours=24)  # Cache for 24 hours
}

def get_github_integration():
    """Get GitHub integration instance"""
    token = Config.GITHUB_TOKEN or session.get('github_token')
    if not token:
        return None
    return GitHubIntegration(token)

def get_branch_selector():
    """Get branch selector instance"""
    token = Config.GITHUB_TOKEN or session.get('github_token')
    if not token:
        return None
    repo_path = Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')
    return BranchSelector(token, repo_path)

def get_course_manager():
    """Get course manager instance"""
    repo_path = Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')
    if not repo_path:
        return None
    return CourseManager(repo_path)

def get_tutorial_manager():
    """Get tutorial manager instance"""
    repo_path = Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')
    if not repo_path:
        return None
    return TutorialManager(repo_path)

@app.route('/')
def index():
    """Landing page"""
    # Check if configuration is complete
    config_complete = bool(Config.GITHUB_TOKEN and Config.BITCOIN_CONTENT_REPO_PATH)
    return render_template('index.html', config_complete=config_complete)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate repo path
        repo_path = data.get('repo_path', '')
        is_valid, message = Config.validate_repo_path(repo_path)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # Validate GitHub token
        github_token = data.get('github_token', '')
        if github_token:
            try:
                github = GitHubIntegration(github_token)
                token_valid, token_message = github.validate_token()
                if not token_valid:
                    return jsonify({'success': False, 'message': f'Invalid GitHub token: {token_message}'}), 400
            except Exception as e:
                return jsonify({'success': False, 'message': f'GitHub token error: {str(e)}'}), 400
        
        # Save configuration
        config_data = {
            'repo_path': repo_path,
            'github_token': github_token,
            'default_branch': data.get('default_branch', 'dev')
        }
        
        # Save to session
        session['repo_path'] = repo_path
        session['github_token'] = github_token
        session['default_branch'] = data.get('default_branch', 'dev')
        
        # Optionally save to file
        Config.save_config(config_data)
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
    
    # Load existing configuration
    saved_config = Config.load_config()
    return render_template('config.html', config=saved_config)

@app.route('/course/new')
def new_course_issue():
    """Course issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    if not (Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')):
        return redirect(url_for('config'))
    
    return render_template('course_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/api/courses')
def api_courses():
    """API endpoint to get list of courses"""
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        courses = manager.get_course_list()
        return jsonify({'courses': courses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/course/<course_id>')
def api_course_info(course_id):
    """API endpoint to get course information"""
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        course_info = manager.get_course_info(course_id)
        return jsonify(course_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/branches/search')
def api_branch_search():
    """API endpoint for branch fuzzy search"""
    query = request.args.get('q', '')
    language = request.args.get('lang', '')
    
    selector = get_branch_selector()
    if not selector:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        context = {'language': language} if language else None
        branches = selector.fuzzy_search(query, context=context)
        return jsonify({'branches': branches})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/branches/validate/<branch_name>')
def api_validate_branch(branch_name):
    """API endpoint to validate if a branch exists"""
    selector = get_branch_selector()
    if not selector:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        exists = selector.branch_exists(branch_name)
        return jsonify({'exists': exists})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages/search')
def api_language_search():
    """API endpoint for language fuzzy search"""
    query = request.args.get('q', '').lower()
    
    # Convert language dict to searchable format
    languages = []
    for code, name in Config.LANGUAGES.items():
        languages.append({
            'code': code,
            'name': name,
            'display': f"{name} ({code})",
            'searchText': f"{name.lower()} {code.lower()}"
        })
    
    if not query:
        return jsonify({'languages': languages[:10]})  # Return first 10 if no query
    
    # Simple fuzzy matching
    results = []
    for lang in languages:
        # Check if query matches in name or code
        if query in lang['searchText']:
            # Calculate a simple relevance score
            score = 0
            if lang['code'].lower() == query:
                score = 100  # Exact code match
            elif lang['code'].lower().startswith(query):
                score = 90   # Code starts with query
            elif lang['name'].lower().startswith(query):
                score = 80   # Name starts with query
            elif query in lang['name'].lower():
                score = 70   # Query in name
            else:
                score = 60   # Query in code
            
            results.append((lang, score))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify({'languages': [r[0] for r in results[:10]]})

@app.route('/api/weblate/languages')
def api_weblate_languages():
    """API endpoint for Weblate languages with caching"""
    global weblate_languages_cache
    
    # Check if cache is still valid
    if (weblate_languages_cache['data'] is not None and 
        weblate_languages_cache['last_updated'] is not None and
        datetime.now() - weblate_languages_cache['last_updated'] < weblate_languages_cache['ttl']):
        return jsonify({'languages': weblate_languages_cache['data']})
    
    try:
        # Fetch languages from Weblate API
        response = requests.get('https://weblate.planb.network/api/languages/', timeout=10)
        response.raise_for_status()
        
        weblate_data = response.json()
        languages = []
        
        # Process the results
        results = weblate_data.get('results', [])
        for lang in results:
            # Extract language info
            languages.append({
                'code': lang.get('code', ''),
                'name': lang.get('name', ''),
                'display': f"{lang.get('name', '')} ({lang.get('code', '')})",
                'searchText': f"{lang.get('name', '').lower()} {lang.get('code', '').lower()}"
            })
        
        # Update cache
        weblate_languages_cache['data'] = languages
        weblate_languages_cache['last_updated'] = datetime.now()
        
        return jsonify({'languages': languages})
    except Exception as e:
        # Fallback to config languages if Weblate API fails
        print(f"Error fetching Weblate languages: {e}")
        languages = []
        for code, name in Config.LANGUAGES.items():
            languages.append({
                'code': code,
                'name': name,
                'display': f"{name} ({code})",
                'searchText': f"{name.lower()} {code.lower()}"
            })
        return jsonify({'languages': languages})

@app.route('/api/weblate/languages/search')
def api_weblate_language_search():
    """API endpoint for Weblate language fuzzy search"""
    query = request.args.get('q', '').lower()
    
    # First get all languages (from cache or API)
    response = api_weblate_languages()
    all_languages = response.get_json()['languages']
    
    if not query:
        return jsonify({'languages': all_languages[:10]})  # Return first 10 if no query
    
    # Simple fuzzy matching
    results = []
    for lang in all_languages:
        # Check if query matches in name or code
        if query in lang['searchText']:
            # Calculate a simple relevance score
            score = 0
            if lang['code'].lower() == query:
                score = 100  # Exact code match
            elif lang['code'].lower().startswith(query):
                score = 90   # Code starts with query
            elif lang['name'].lower().startswith(query):
                score = 80   # Name starts with query
            elif query in lang['name'].lower():
                score = 70   # Query in name
            else:
                score = 60   # Query in code
            
            results.append((lang, score))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify({'languages': [r[0] for r in results[:10]]})

@app.route('/course/preview', methods=['POST'])
def preview_course_issue():
    """Preview the issue before creation"""
    data = request.get_json()
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build URLs
        pbn_url = manager.build_pbn_url(course_info['title'], course_info['uuid'], data['language'])
        github_urls = manager.build_github_urls(data['course_id'], data['language'], data['branch'])
        
        # Build issue title
        title = f"[PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build issue body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',  # Changed from 'To Do' to 'Todo'
                'Language': data['language'],  # Show language code in preview
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Course'  # Changed from 'course' to 'Course'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/course/create', methods=['POST'])
def create_course_issue():
    """Create the course issue"""
    data = request.get_json()
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build URLs
        pbn_url = manager.build_pbn_url(course_info['title'], course_info['uuid'], data['language'])
        github_urls = manager.build_github_urls(data['course_id'], data['language'], data['branch'])
        
        # Build issue title
        title = f"[PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build issue body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        # Use language code instead of full name
        project_fields = {
            'Status': 'Todo',  # Changed from 'To Do' to 'Todo'
            'Language': data['language'],  # Use language code (e.g., 'it', 'es')
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Course'  # Changed from 'course' to 'Course'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tutorial routes
@app.route('/tutorial/new')
def new_tutorial_issue():
    """Tutorial issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    if not (Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')):
        return redirect(url_for('config'))
    
    return render_template('tutorial_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/api/tutorials')
def api_tutorials():
    """API endpoint to get list of tutorials"""
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        tutorials = manager.get_tutorials_list()
        return jsonify({'tutorials': tutorials})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tutorials/search')
def api_tutorials_search():
    """API endpoint for tutorial fuzzy search"""
    query = request.args.get('q', '')
    
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        tutorials = manager.search_tutorials(query)
        return jsonify({'tutorials': tutorials})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tutorial/<category>/<name>')
def api_tutorial_info(category, name):
    """API endpoint to get tutorial information"""
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        tutorial_info = manager.get_tutorial_info(category, name)
        return jsonify(tutorial_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/tutorial/preview', methods=['POST'])
def preview_tutorial_issue():
    """Preview the tutorial issue before creation"""
    data = request.get_json()
    
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Parse category and name from the selection
        tutorial_path = data['tutorial_path']
        category, name = tutorial_path.split('/', 1)
        
        # Get tutorial info
        tutorial_info = manager.get_tutorial_info(category, name)
        
        # Build URLs
        pbn_url = manager.build_pbn_url(category, name, tutorial_info['title'], tutorial_info['id'], data['language'])
        github_urls = manager.build_github_urls(category, name, data['language'], data['branch'])
        
        # Build issue title (no brackets around language)
        title = f"[PROOFREADING] {category}/{name} - {data['language']}"
        
        # Build issue body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',
                'Language': data['language'],
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Tutorial'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tutorial/create', methods=['POST'])
def create_tutorial_issue():
    """Create the tutorial issue"""
    data = request.get_json()
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Parse category and name from the selection
        tutorial_path = data['tutorial_path']
        category, name = tutorial_path.split('/', 1)
        
        # Get tutorial info
        tutorial_info = manager.get_tutorial_info(category, name)
        
        # Build URLs
        pbn_url = manager.build_pbn_url(category, name, tutorial_info['title'], tutorial_info['id'], data['language'])
        github_urls = manager.build_github_urls(category, name, data['language'], data['branch'])
        
        # Build issue title (no brackets around language)
        title = f"[PROOFREADING] {category}/{name} - {data['language']}"
        
        # Build issue body
        body_lines = [f"en PBN version: {pbn_url}"]
        for lang, url in github_urls:
            if lang == 'en':
                body_lines.append(f"en github version: {url}")
            else:
                body_lines.append(f"{lang} github version: {url}")
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Tutorial'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tutorial Section routes
@app.route('/tutorial-section/new')
def new_tutorial_section_issue():
    """Tutorial section issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    if not (Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')):
        return redirect(url_for('config'))
    
    return render_template('tutorial_section_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/api/tutorial-sections')
def api_tutorial_sections():
    """API endpoint to get all tutorial category sections"""
    manager = get_tutorial_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        sections = manager.get_tutorial_sections()
        return jsonify({'sections': sections})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tutorial-section/preview', methods=['POST'])
def preview_tutorial_section_issue():
    """Preview the tutorial section issue before creation"""
    data = request.get_json()
    
    try:
        # Get the section name
        section = data['section']
        
        # Build issue title
        title = f"[PROOFREADING] {section}_section - {data['language']}"
        
        # Build URLs
        pbn_url = f"https://planb.network/{data['language']}/tutorials/{section}"
        github_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/tutorials/{section}"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: https://planb.network/en/tutorials/{section}",
            f"Folder GitHub Version: {github_url}"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',
                'Language': data['language'],
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Tutorial'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tutorial-section/create', methods=['POST'])
def create_tutorial_section_issue():
    """Create the tutorial section issue"""
    data = request.get_json()
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        # Get the section name
        section = data['section']
        
        # Build issue title
        title = f"[PROOFREADING] {section}_section - {data['language']}"
        
        # Build URLs
        pbn_url = f"https://planb.network/{data['language']}/tutorials/{section}"
        github_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/tutorials/{section}"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: https://planb.network/en/tutorials/{section}",
            f"Folder GitHub Version: {github_url}"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - tutorial",
            "content proofreading",
            f"language - {data['language']}"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Tutorial'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Weblate routes
@app.route('/weblate/new')
def new_weblate_issue():
    """Weblate issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    return render_template('weblate_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/weblate/preview', methods=['POST'])
def preview_weblate_issue():
    """Preview the weblate issue before creation"""
    data = request.get_json()
    
    try:
        # Build issue title
        title = f"[PROOFREADING] weblate - {data['language']}"
        
        # Build Weblate URL
        weblate_url = f"{Config.WEBLATE_BASE_URL}/{data['language']}/"
        
        # Build issue body
        body = f"Weblate Url: {weblate_url}"
        
        # Labels
        labels = [
            "website translation",
            f"language - {data['language']}"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',
                'Language': data['language'],
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Weblate'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weblate/create', methods=['POST'])
def create_weblate_issue():
    """Create the weblate issue"""
    data = request.get_json()
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        # Build issue title
        title = f"[PROOFREADING] weblate - {data['language']}"
        
        # Build Weblate URL
        weblate_url = f"{Config.WEBLATE_BASE_URL}/{data['language']}/"
        
        # Build issue body
        body = f"Weblate Url: {weblate_url}"
        
        # Labels
        labels = [
            "website translation",
            f"language - {data['language']}"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Weblate'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Video Course routes
@app.route('/video-course/new')
def new_video_course_issue():
    """Video course issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    if not (Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')):
        return redirect(url_for('config'))
    
    return render_template('video_course_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/video-course/preview', methods=['POST'])
def preview_video_course_issue():
    """Preview the video course issue before creation"""
    data = request.get_json()
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build issue title
        title = f"[VIDEO-PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build URLs
        planb_url = f"https://planb.network/{data['language']}/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}"
        github_base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/courses/{data['course_id']}"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: https://planb.network/en/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}",
            f"EN GitHub Version: {github_base_url}/en.md",
            f"{data['language']} GitHub Version: {github_base_url}/{data['language']}.md",
            f"Workspace link shared privately"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content proofreading",
            f"language - {data['language']}",
            "video transcript"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',
                'Language': data['language'],
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Video Course'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video-course/create', methods=['POST'])
def create_video_course_issue():
    """Create the video course issue"""
    data = request.get_json()
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build issue title
        title = f"[VIDEO-PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build URLs
        planb_url = f"https://planb.network/{data['language']}/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}"
        github_base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/courses/{data['course_id']}"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: https://planb.network/en/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}",
            f"EN GitHub Version: {github_base_url}/en.md",
            f"{data['language']} GitHub Version: {github_base_url}/{data['language']}.md",
            f"Workspace link shared privately"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content proofreading",
            f"language - {data['language']}",
            "video transcript"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Video Course'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Image Course routes
@app.route('/image-course/new')
def new_image_course_issue():
    """Image course issue creation form"""
    # Check configuration
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    if not (Config.BITCOIN_CONTENT_REPO_PATH or session.get('repo_path')):
        return redirect(url_for('config'))
    
    return render_template('image_course_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/image-course/preview', methods=['POST'])
def preview_image_course_issue():
    """Preview the image course issue before creation"""
    data = request.get_json()
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build issue title
        title = f"[IMAGE-PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build URLs
        planb_url = f"https://planb.network/{data['language']}/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}"
        github_base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/courses/{data['course_id']}/assets"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: [{planb_url}]",
            f"EN GitHub Version: [{github_base_url}/en/]",
            f"Workspace link shared privately"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content - images",
            f"language - [{data['language']}]"
        ]
        
        preview = {
            'title': title,
            'body': body,
            'labels': labels,
            'project_fields': {
                'Status': 'Todo',
                'Language': data['language'],
                'Iteration': data['iteration'],
                'Urgency': data['urgency'],
                'Content Type': 'Image Course'
            }
        }
        
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image-course/create', methods=['POST'])
def create_image_course_issue():
    """Create the image course issue"""
    data = request.get_json()
    
    manager = get_course_manager()
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        # Get course info
        course_info = manager.get_course_info(data['course_id'])
        
        # Build issue title
        title = f"[IMAGE-PROOFREADING] {data['course_id']} - {data['language']}"
        
        # Build URLs
        planb_url = f"https://planb.network/{data['language']}/courses/{data['course_id']}/{course_info['title_slug']}-{course_info['uuid']}"
        github_base_url = f"https://github.com/PlanB-Network/bitcoin-educational-content/blob/{data['branch']}/courses/{data['course_id']}/assets"
        
        # Build issue body
        body_lines = [
            f"English PBN Version: {planb_url}",
            f"EN GitHub Version: {github_base_url}/en/",
            f"Workspace link shared privately"
        ]
        
        body = '\n'.join(body_lines)
        
        # Labels
        labels = [
            "content - course",
            "content - images",
            f"language - [{data['language']}]"
        ]
        
        # Create issue
        issue = github.create_issue(title, body, labels)
        
        # Link to project with fields
        project_fields = {
            'Status': 'Todo',
            'Language': data['language'],
            'Iteration': data['iteration'],
            'Urgency': data['urgency'],
            'Content Type': 'Image Course'
        }
        
        github.link_to_project(issue, Config.GITHUB_PROJECT_ID, project_fields)
        
        return jsonify({
            'success': True,
            'issue_url': github.get_issue_url(issue),
            'issue_number': issue.number
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/success')
def success():
    """Success page after issue creation"""
    issue_url = request.args.get('url')
    issue_number = request.args.get('number')
    return render_template('success.html', issue_url=issue_url, issue_number=issue_number)

if __name__ == '__main__':
    import os
    import webbrowser
    from threading import Timer
    
    # Only open browser on the first run, not on reloader
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*50)
        print("🚀 Proofreading Issue Manager")
        print("="*50)
        print("\n📍 Server starting at: http://localhost:5000")
        print("📝 Press Ctrl+C to stop the server\n")
        
        # Open browser after a short delay
        def open_browser():
            webbrowser.open('http://localhost:5000')
        
        Timer(1.5, open_browser).start()
    
    app.run(debug=True, port=5000, host='127.0.0.1')
