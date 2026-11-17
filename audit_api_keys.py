import sys
import requests
import argparse
import time
import json
import csv
import os
from datetime import datetime

from dotenv import load_dotenv

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

FIELDNAMES = ['Username', 'User ID', 'Created', 'Last Access']
EXTENSIONS = {'csv': 'csv', 'json': 'json', 'table': 'txt'}

def build_rows(api_keys):
    """Convert raw API key records into display rows."""
    return [{
        'Username': key['username'],
        'User ID': key['userId'],
        'Created': convert_timestamp(key['start']),
        'Last Access': convert_timestamp(key['lastAccess']),
    } for key in api_keys]

def write_output(rows, fmt, stream):
    """Write rows to an open text stream in the requested format."""
    if fmt == 'csv':
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    elif fmt == 'json':
        json.dump(rows, stream, indent=2)
        stream.write('\n')
    else:  # table
        widths = {f: max([len(f)] + [len(str(r[f])) for r in rows]) for f in FIELDNAMES}
        line = lambda vals: '  '.join(str(vals[f]).ljust(widths[f]) for f in FIELDNAMES).rstrip()
        stream.write(line({f: f for f in FIELDNAMES}) + '\n')
        stream.write('  '.join('-' * widths[f] for f in FIELDNAMES) + '\n')
        for r in rows:
            stream.write(line(r) + '\n')

def emit(rows, fmt, to_screen, output_file, screen):
    """Send output to the screen and/or a file."""
    try:
        if output_file:
            # csv module needs newline='' on files; harmless for json/table
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                write_output(rows, fmt, f)
            print(f"Wrote {len(rows)} API keys to {output_file}")
        if to_screen:
            write_output(rows, fmt, screen)
    except Exception as e:
        print(f"An error occurred while writing output: {e}")
        sys.exit(1)

class Config:
    def __init__(self):
        self.base_url = None
        self.tenant_name = None
        self.api_key = None
        self.iam_base_url = None
        self.output = None
        self.format = None
        self.stdout = False
        self.debug = False

    @classmethod
    def from_env(cls, env_file=".env"):
        load_dotenv(env_file)  # a missing file is fine; existing env vars are not overwritten
        config = cls()
        config.base_url = os.getenv("CXONE_BASE_URL")
        config.tenant_name = os.getenv("CXONE_TENANT")
        config.api_key = os.getenv("CXONE_API_KEY")
        config.iam_base_url = os.getenv("CXONE_IAM_BASE_URL")
        config.output = os.getenv("CXONE_OUTPUT")
        config.format = (os.getenv("CXONE_FORMAT") or "").lower() or None
        config.stdout = os.getenv("CXONE_STDOUT", "").lower() == "true"
        config.debug = os.getenv("CXONE_DEBUG", "").lower() == "true"
        return config

    def validate(self):
        if not self.base_url:
            return False, "Base URL is required (set CXONE_BASE_URL in .env or use --base-url)."
        if not self.tenant_name:
            return False, "Tenant name is required (set CXONE_TENANT in .env or use --tenant-name)."
        if not self.api_key:
            return False, "API key is required (set CXONE_API_KEY in .env or use --api-key)."
        if self.format and self.format not in EXTENSIONS:
            return False, f"Format must be one of {', '.join(EXTENSIONS)} (got '{self.format}')."
        return True, None

def main():
    global base_url, tenant_name, auth_url, iam_base_url, api_key, debug

    parser = argparse.ArgumentParser(description='Audit API keys in Checkmarx One')
    parser.add_argument('--env-file', default='.env', help='Path to environment file (default: .env)')
    parser.add_argument('--base-url', help='Region base URL (e.g. https://ast.checkmarx.net)')
    parser.add_argument('--tenant-name', '--tenant', dest='tenant_name', help='Tenant name')
    parser.add_argument('--api-key', help='API key')
    parser.add_argument('--format', choices=list(EXTENSIONS), help='Output format: csv, json, or table (default: table)')
    parser.add_argument('--output', help='Write output to this file (default: api_keys.<format> unless output goes to screen only)')
    parser.add_argument('--stdout', action='store_true', help='Display output on screen instead of (or in addition to, with --output) writing a file')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    config = Config.from_env(args.env_file)
    if args.base_url:
        config.base_url = args.base_url
    if args.tenant_name:
        config.tenant_name = args.tenant_name
    if args.api_key:
        config.api_key = args.api_key
    if args.output:
        config.output = args.output
    if args.format:
        config.format = args.format
    if args.stdout:
        config.stdout = True
    if args.debug:
        config.debug = True

    ok, err = config.validate()
    if not ok:
        print("Configuration error:", err)
        sys.exit(1)

    base_url = config.base_url.rstrip("/")
    tenant_name = config.tenant_name
    api_key = config.api_key
    iam_base_url = (config.iam_base_url or "").rstrip("/") or None
    debug = config.debug
    fmt = config.format or 'table'
    # table is meant for the screen; csv/json write a file unless --stdout is used
    to_screen = config.stdout or fmt == 'table'
    output_file = config.output or (None if to_screen else f"api_keys.{EXTENSIONS[fmt]}")

    # Keep stdout clean for data: send status/debug messages to stderr when printing csv/json
    screen = sys.stdout
    if to_screen and fmt != 'table':
        sys.stdout = sys.stderr

    print(f"Tenant: {tenant_name} | Base URL: {base_url}")

    auth_url = generate_auth_url()

    print("Getting client ID...")
    client_id = get_client_id()

    print("Getting API keys...")
    api_keys = get_api_keys(client_id)

    print(f"Found {len(api_keys)} API keys")
    emit(build_rows(api_keys), fmt, to_screen, output_file, screen)

    print("Done!")

if __name__ == "__main__":
    main()
