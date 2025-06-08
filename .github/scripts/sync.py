#!/usr/bin/env python3
import os
import sys
import yaml
import requests

def load_yaml(file_path):
    """Load YAML file and return data."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def github_api_request(method, url, data=None):
    """Make GitHub API request."""
    headers = {
        'Authorization': f'token {os.environ["GITHUB_TOKEN"]}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    
    return response

def get_org():
    """Get organization name from repository."""
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    return repo.split('/')[0] if '/' in repo else 'yorkie-team'

def sync_team(team_name, members):
    """Sync GitHub team with members list."""
    org = get_org()
    base_url = f'https://api.github.com/orgs/{org}'
    
    print(f"Syncing team: {team_name} with {len(members)} members")
    
    # Create team if it doesn't exist
    team_data = {'name': team_name, 'privacy': 'closed'}
    create_response = github_api_request('POST', f'{base_url}/teams', team_data)
    
    if create_response.status_code == 422:
        # Team already exists, get team info
        teams_response = github_api_request('GET', f'{base_url}/teams')
        if teams_response.status_code == 200:
            teams = teams_response.json()
            team_slug = None
            for team in teams:
                if team['name'] == team_name:
                    team_slug = team['slug']
                    break
        else:
            print(f"Failed to get teams: {teams_response.status_code}")
            return
    elif create_response.status_code == 201:
        team_slug = create_response.json()['slug']
    else:
        print(f"Failed to create team {team_name}: {create_response.status_code}")
        return
    
    if not team_slug:
        team_slug = team_name.lower().replace(' ', '-')
    
    # Get current team members
    current_members_response = github_api_request('GET', f'{base_url}/teams/{team_slug}/members')
    current_members = []
    if current_members_response.status_code == 200:
        current_members = [member['login'] for member in current_members_response.json()]
    
    # Add new members
    for member in members:
        if member not in current_members:
            add_response = github_api_request('PUT', f'{base_url}/teams/{team_slug}/memberships/{member}')
            if add_response.status_code in [200, 201]:
                print(f"  Added {member}")
            else:
                print(f"  Failed to add {member}: {add_response.status_code}")
    
    # Remove old members
    for member in current_members:
        if member not in members:
            remove_response = github_api_request('DELETE', f'{base_url}/teams/{team_slug}/memberships/{member}')
            if remove_response.status_code in [204, 404]:
                print(f"  Removed {member}")
            else:
                print(f"  Failed to remove {member}: {remove_response.status_code}")

def main():
    """Main sync function."""
    print("Starting team synchronization...")
    
    # Sync members
    members_data = load_yaml('teams/members.yaml')
    sync_team('members', members_data['members'])
    
    # Sync mentors (latest year only)
    mentors_data = load_yaml('teams/mentors.yaml')
    latest_mentor_year = max(mentors_data['mentors'].keys())
    mentor_members = mentors_data['mentors'][latest_mentor_year]
    sync_team('mentors', mentor_members)
    
    # Sync OSSCA (latest year only)
    ossca_data = load_yaml('teams/ossca.yaml')
    latest_ossca_year = max(ossca_data['ossca'].keys())
    ossca_members = ossca_data['ossca'][latest_ossca_year]
    sync_team('ossca', ossca_members)
    
    print("Team synchronization completed!")

if __name__ == '__main__':
    main()
