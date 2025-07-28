from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from course_manager import CourseManager
from tutorial_manager import TutorialManager
from branch_selector import BranchSelector
from github_integration import GitHubIntegration
from services.issue_creator import (
    CourseIssueCreator, TutorialIssueCreator, TutorialSectionIssueCreator,
    WeblateIssueCreator, VideoCourseIssueCreator, ImageCourseIssueCreator
)
from services.cache_service import cache
import os
from pathlib import Path
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

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
    config_complete = bool(Config.GITHUB_TOKEN and Config.BITCOIN_CONTENT_REPO_PATH)
    return render_template('index.html', config_complete=config_complete)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page"""
    if request.method == 'POST':
        data = request.get_json()
        
        repo_path = data.get('repo_path', '')
        is_valid, message = Config.validate_repo_path(repo_path)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        github_token = data.get('github_token', '')
        if github_token:
            try:
                github = GitHubIntegration(github_token)
                token_valid, token_message = github.validate_token()
                if not token_valid:
                    return jsonify({'success': False, 'message': f'Invalid GitHub token: {token_message}'}), 400
            except Exception as e:
                return jsonify({'success': False, 'message': f'GitHub token error: {str(e)}'}), 400
        
        config_data = {
            'repo_path': repo_path,
            'github_token': github_token,
            'default_branch': data.get('default_branch', 'dev')
        }
        
        session['repo_path'] = repo_path
        session['github_token'] = github_token
        session['default_branch'] = data.get('default_branch', 'dev')
        
        Config.save_config(config_data)
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
    
    saved_config = Config.load_config()
    return render_template('config.html', config=saved_config)

# Course routes
@app.route('/course/new')
def new_course_issue():
    """Course issue creation form"""
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

@app.route('/course/preview', methods=['POST'])
def preview_course_issue():
    """Preview the issue before creation"""
    data = request.get_json()
    
    manager = get_course_manager()
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = CourseIssueCreator(github, manager)
        preview = creator.preview_issue(data)
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/course/create', methods=['POST'])
def create_course_issue():
    """Create the course issue"""
    data = request.get_json()
    
    github = get_github_integration()
    manager = get_course_manager()
    
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        creator = CourseIssueCreator(github, manager)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tutorial routes
@app.route('/tutorial/new')
def new_tutorial_issue():
    """Tutorial issue creation form"""
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
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = TutorialIssueCreator(github, manager)
        preview = creator.preview_issue(data)
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tutorial/create', methods=['POST'])
def create_tutorial_issue():
    """Create the tutorial issue"""
    data = request.get_json()
    
    github = get_github_integration()
    manager = get_tutorial_manager()
    
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    
    try:
        creator = TutorialIssueCreator(github, manager)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tutorial Section routes
@app.route('/tutorial-section/new')
def new_tutorial_section_issue():
    """Tutorial section issue creation form"""
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
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = TutorialSectionIssueCreator(github)
        preview = creator.preview_issue(data)
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
        creator = TutorialSectionIssueCreator(github)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Weblate routes
@app.route('/weblate/new')
def new_weblate_issue():
    """Weblate issue creation form"""
    if not (Config.GITHUB_TOKEN or session.get('github_token')):
        return redirect(url_for('config'))
    
    return render_template('weblate_form.html', 
                         languages=Config.LANGUAGES,
                         default_branch=Config.DEFAULT_BRANCH or session.get('default_branch', 'dev'))

@app.route('/api/weblate/languages')
def api_weblate_languages():
    """API endpoint for Weblate languages with caching"""
    # Check cache first
    cached_languages = cache.get('weblate_languages')
    if cached_languages is not None:
        return jsonify({'languages': cached_languages})
    
    try:
        response = requests.get('https://weblate.planb.network/api/languages/', timeout=10)
        response.raise_for_status()
        
        weblate_data = response.json()
        languages = []
        
        results = weblate_data.get('results', [])
        for lang in results:
            languages.append({
                'code': lang.get('code', ''),
                'name': lang.get('name', ''),
                'display': f"{lang.get('name', '')} ({lang.get('code', '')})",
                'searchText': f"{lang.get('name', '').lower()} {lang.get('code', '').lower()}"
            })
        
        # Update cache with 24 hour TTL
        cache.set('weblate_languages', languages, ttl_seconds=86400)
        
        return jsonify({'languages': languages})
    except Exception as e:
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
    
    response = api_weblate_languages()
    all_languages = response.get_json()['languages']
    
    if not query:
        return jsonify({'languages': all_languages[:10]})
    
    results = []
    for lang in all_languages:
        if query in lang['searchText']:
            score = 0
            if lang['code'].lower() == query:
                score = 100
            elif lang['code'].lower().startswith(query):
                score = 90
            elif lang['name'].lower().startswith(query):
                score = 80
            elif query in lang['name'].lower():
                score = 70
            else:
                score = 60
            
            results.append((lang, score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify({'languages': [r[0] for r in results[:10]]})

@app.route('/weblate/preview', methods=['POST'])
def preview_weblate_issue():
    """Preview the weblate issue before creation"""
    data = request.get_json()
    
    github = get_github_integration()
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = WeblateIssueCreator(github)
        preview = creator.preview_issue(data)
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
        creator = WeblateIssueCreator(github)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Video Course routes
@app.route('/video-course/new')
def new_video_course_issue():
    """Video course issue creation form"""
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
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = VideoCourseIssueCreator(github, manager)
        preview = creator.preview_issue(data)
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video-course/create', methods=['POST'])
def create_video_course_issue():
    """Create the video course issue"""
    data = request.get_json()
    
    manager = get_course_manager()
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = VideoCourseIssueCreator(github, manager)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Image Course routes
@app.route('/image-course/new')
def new_image_course_issue():
    """Image course issue creation form"""
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
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = ImageCourseIssueCreator(github, manager)
        preview = creator.preview_issue(data)
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image-course/create', methods=['POST'])
def create_image_course_issue():
    """Create the image course issue"""
    data = request.get_json()
    
    manager = get_course_manager()
    github = get_github_integration()
    
    if not manager:
        return jsonify({'error': 'Repository path not configured'}), 400
    if not github:
        return jsonify({'error': 'GitHub token not configured'}), 400
    
    try:
        creator = ImageCourseIssueCreator(github, manager)
        result = creator.create_issue(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API routes
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
    
    languages = []
    for code, name in Config.LANGUAGES.items():
        languages.append({
            'code': code,
            'name': name,
            'display': f"{name} ({code})",
            'searchText': f"{name.lower()} {code.lower()}"
        })
    
    if not query:
        return jsonify({'languages': languages[:10]})
    
    results = []
    for lang in languages:
        if query in lang['searchText']:
            score = 0
            if lang['code'].lower() == query:
                score = 100
            elif lang['code'].lower().startswith(query):
                score = 90
            elif lang['name'].lower().startswith(query):
                score = 80
            elif query in lang['name'].lower():
                score = 70
            else:
                score = 60
            
            results.append((lang, score))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify({'languages': [r[0] for r in results[:10]]})

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
    
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*50)
        print("🚀 Proofreading Issue Manager (Modular)")
        print("="*50)
        print("\n📍 Server starting at: http://localhost:5000")
        print("📝 Press Ctrl+C to stop the server\n")
        
        def open_browser():
            webbrowser.open('http://localhost:5000')
        
        Timer(1.5, open_browser).start()
    
    app.run(debug=True, port=5000, host='127.0.0.1')