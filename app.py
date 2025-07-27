from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from course_manager import CourseManager
from branch_selector import BranchSelector
from github_integration import GitHubIntegration
import os
from pathlib import Path

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
        title = f"[PROOFREADING] {data['course_id']} - [{data['language']}]"
        
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
