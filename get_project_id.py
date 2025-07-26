#!/usr/bin/env python3
"""
Script to get GitHub Project ID for PlanB-Network organization
"""

import requests
import json
from config import Config

def get_project_id(token):
    """Get all projects from PlanB-Network organization"""
    
    query = """
    query {
      organization(login: "PlanB-Network") {
        projectsV2(first: 20) {
          nodes {
            id
            title
            number
            url
            closed
          }
        }
      }
    }
    """
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    if 'errors' in data:
        print("GraphQL Errors:")
        for error in data['errors']:
            print(f"  - {error['message']}")
        return
    
    projects = data['data']['organization']['projectsV2']['nodes']
    
    print("\nPlanB-Network Projects:")
    print("-" * 80)
    
    for project in projects:
        status = "✓ Open" if not project['closed'] else "✗ Closed"
        print(f"\nTitle: {project['title']}")
        print(f"Number: #{project['number']}")
        print(f"ID: {project['id']}")
        print(f"URL: {project['url']}")
        print(f"Status: {status}")
        print("-" * 40)
    
    # Look for proofreading project
    print("\n🔍 Looking for Proofreading project...")
    for project in projects:
        if 'proofreading' in project['title'].lower():
            print(f"\n✅ Found Proofreading Project!")
            print(f"   Title: {project['title']}")
            print(f"   ID: {project['id']}")
            print(f"\n   Add this to your .env file:")
            print(f"   GITHUB_PROJECT_ID={project['id']}")
            return project['id']
    
    print("\n⚠️  No project with 'Proofreading' in the title found.")
    print("   Please check the project list above and manually select the correct ID.")

if __name__ == "__main__":
    # Try to get token from environment or config
    token = Config.GITHUB_TOKEN
    
    if not token:
        print("Please enter your GitHub Personal Access Token:")
        print("(The token needs 'repo' and 'project' permissions)")
        token = input("Token: ").strip()
    
    if not token:
        print("Error: No token provided")
        exit(1)
    
    get_project_id(token)