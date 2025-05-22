import sys
import requests
import argparse
import time
import json
import csv
from datetime import datetime

# Standard global variables
base_url = None
tenant_name = None
auth_url = None
iam_base_url = None
api_key = None
auth_token = None
token_expiration = 0  # initialize so we have to authenticate
debug = False

def generate_auth_url():
    global iam_base_url
    
    try:
        if debug:
            print("Generating authentication URL...")
        
        if iam_base_url is None:
            iam_base_url = base_url.replace("ast.checkmarx.net", "iam.checkmarx.net")
            if debug:
                print(f"Generated IAM base URL: {iam_base_url}")
        
        temp_auth_url = f"{iam_base_url}/auth/realms/{tenant_name}/protocol/openid-connect/token"
        
        if debug:
            print(f"Generated authentication URL: {temp_auth_url}")
        
        return temp_auth_url
    except AttributeError:
        print("Error: Invalid base_url provided.")
        sys.exit(1)

def authenticate():
    global auth_token, token_expiration

    # if the token hasn't expired then we don't need to authenticate
    if time.time() < token_expiration - 60:
        if debug:
            print("Token still valid.")
        return
    
    if debug:
        print("Authenticating with API key...")
        
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'refresh_token',
        'client_id': 'ast-app',
        'refresh_token': api_key
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        
        json_response = response.json()
        auth_token = json_response.get('access_token')
        if not auth_token:
            print("Error: Access token not found in the response.")
            sys.exit(1)
        
        expires_in = json_response.get('expires_in')
        
        if not expires_in:
            expires_in = 600

        token_expiration = time.time() + expires_in

        if debug:
            print("Authenticated successfully.")
      
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during authentication: {e}")
        sys.exit(1)

def get_client_id():
    """Get the client ID for ast-app."""
    if debug:
        print("Getting client ID for ast-app...")
    
    authenticate()
    
    try:
        url = f"{iam_base_url}/auth/admin/realms/{tenant_name}/clients?clientId=ast-app"
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        clients = response.json()
        if not clients:
            print("Error: No clients found with clientId=ast-app")
            sys.exit(1)
            
        client_id = clients[0].get('id')
        if not client_id:
            print("Error: Client ID not found in response")
            sys.exit(1)
            
        if debug:
            print(f"Found client ID: {client_id}")
            
        return client_id
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while getting client ID: {e}")
        sys.exit(1)

def get_api_keys(client_id):
    """Get all API keys for the specified client."""
    if debug:
        print("Getting API keys...")
    
    authenticate()
    
    try:
        url = f"{iam_base_url}/auth/admin/realms/{tenant_name}/clients/{client_id}/offline-sessions"
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        api_keys = response.json()
        if debug:
            print(f"Found {len(api_keys)} API keys")
            
        return api_keys
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while getting API keys: {e}")
        sys.exit(1)

def convert_timestamp(timestamp):
    """Convert Unix timestamp to human readable format."""
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

def output_to_csv(api_keys, output_file):
    """Output API key information to CSV file."""
    if debug:
        print(f"Writing API key information to {output_file}...")
    
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Username', 'User ID', 'Created', 'Last Access']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for key in api_keys:
                writer.writerow({
                    'Username': key['username'],
                    'User ID': key['userId'],
                    'Created': convert_timestamp(key['start']),
                    'Last Access': convert_timestamp(key['lastAccess'])
                })
                
        if debug:
            print("Successfully wrote API key information to CSV")
            
    except Exception as e:
        print(f"An error occurred while writing to CSV: {e}")
        sys.exit(1)

def main():
    global base_url, tenant_name, auth_url, api_key, debug
    
    parser = argparse.ArgumentParser(description='Audit API keys in Checkmarx One')
    parser.add_argument('--base-url', required=True, help='Base URL for Checkmarx One (e.g., https://ast.checkmarx.net)')
    parser.add_argument('--tenant', required=True, help='Tenant name')
    parser.add_argument('--api-key', required=True, help='API key for authentication')
    parser.add_argument('--output', default='api_keys.csv', help='Output CSV file (default: api_keys.csv)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    base_url = args.base_url
    tenant_name = args.tenant
    api_key = args.api_key
    debug = args.debug
    
    auth_url = generate_auth_url()
    
    print("Getting client ID...")
    client_id = get_client_id()
    
    print("Getting API keys...")
    api_keys = get_api_keys(client_id)
    
    print(f"Writing {len(api_keys)} API keys to {args.output}...")
    output_to_csv(api_keys, args.output)
    
    print("Done!")

if __name__ == "__main__":
    main() 