from github import Github, GithubException
import requests
from config import Config

class GitHubIntegration:
    def __init__(self, token):
        self.github = Github(token)
        self.token = token
        self.repo = None
        self._init_repo()
    
    def _init_repo(self):
        """Initialize repository object"""
        try:
            self.repo = self.github.get_repo(f"{Config.GITHUB_OWNER}/{Config.GITHUB_REPO}")
        except Exception as e:
            print(f"Error initializing repository: {e}")
    
    def create_issue(self, title, body, labels):
        """Create a new issue in the repository"""
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            return issue
        except GithubException as e:
            raise Exception(f"Failed to create issue: {e.data}")
    
    def link_to_project(self, issue, project_id, fields):
        """Link issue to project and set custom fields"""
        # GraphQL query to add issue to project
        add_to_project_mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item {
              id
            }
          }
        }
        """
        
        # Execute mutation to add issue to project
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        
        # Get the node_id from the issue
        # PyGithub v2+ uses node_id as a direct attribute
        node_id = None
        
        # Try different methods to get node_id
        if hasattr(issue, 'node_id'):
            node_id = issue.node_id
        elif hasattr(issue, '_rawData') and 'node_id' in issue._rawData:
            node_id = issue._rawData['node_id']
        elif hasattr(issue, 'raw_data') and 'node_id' in issue.raw_data:
            node_id = issue.raw_data['node_id']
        else:
            # As a last resort, make a REST API call to get the issue with node_id
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            api_url = f"https://api.github.com/repos/{Config.GITHUB_OWNER}/{Config.GITHUB_REPO}/issues/{issue.number}"
            resp = requests.get(api_url, headers=headers)
            if resp.status_code == 200:
                issue_data = resp.json()
                node_id = issue_data.get('node_id')
        
        if not node_id:
            raise Exception(f"Unable to get node_id from issue #{issue.number}")
        
        variables = {
            'projectId': project_id,
            'contentId': node_id
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': add_to_project_mutation, 'variables': variables},
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to add issue to project: {response.text}")
        
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        # Get the project item ID
        item_id = result['data']['addProjectV2ItemById']['item']['id']
        
        # Now set the custom fields
        self._set_project_fields(item_id, project_id, fields)
        
        return True
    
    def _set_project_fields(self, item_id, project_id, fields):
        """Set custom fields on a project item"""
        # First, get the project fields
        get_fields_query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 20) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': get_fields_query, 'variables': {'projectId': project_id}},
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get project fields: {response.text}")
        
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        # Parse fields
        field_map = {}
        for field in result['data']['node']['fields']['nodes']:
            field_name = field['name']
            field_id = field['id']
            
            if 'options' in field:
                # It's a single select field
                options = {opt['name']: opt['id'] for opt in field['options']}
                field_map[field_name] = {'id': field_id, 'options': options}
            else:
                field_map[field_name] = {'id': field_id}
        
        # Update each field
        update_field_mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: $value
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """
        
        for field_name, field_value in fields.items():
            # Try alternative field names if the exact match isn't found
            actual_field_name = field_name
            if field_name not in field_map:
                # Try some common alternatives
                alternatives = {
                    'Content Type': ['ContentType', 'Content type', 'content type', 'Type'],
                    'Status': ['status', 'STATE', 'State']
                }
                
                found = False
                if field_name in alternatives:
                    for alt in alternatives[field_name]:
                        if alt in field_map:
                            actual_field_name = alt
                            found = True
                            print(f"Using alternative field name '{alt}' for '{field_name}'")
                            break
                
                if not found:
                    print(f"Warning: Field '{field_name}' not found in project")
                    continue
            
            field_info = field_map[actual_field_name]
            field_id = field_info['id']
            
            # Prepare the value based on field type
            if 'options' in field_info:
                # Single select field
                if field_value in field_info['options']:
                    value = {'singleSelectOptionId': field_info['options'][field_value]}
                else:
                    print(f"Warning: Option '{field_value}' not found for field '{field_name}'")
                    continue
            else:
                # Text field
                value = {'text': str(field_value)}
            
            variables = {
                'projectId': project_id,
                'itemId': item_id,
                'fieldId': field_id,
                'value': value
            }
            
            response = requests.post(
                'https://api.github.com/graphql',
                json={'query': update_field_mutation, 'variables': variables},
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Failed to update field '{field_name}': {response.text}")
    
    def get_issue_url(self, issue):
        """Get the HTML URL of an issue"""
        return issue.html_url
    
    def validate_token(self):
        """Validate that the GitHub token is valid and has necessary permissions"""
        try:
            user = self.github.get_user()
            # Try to access the repo to check permissions
            self.repo.get_issues(state='open', per_page=1)
            return True, f"Authenticated as {user.login}"
        except Exception as e:
            return False, str(e)