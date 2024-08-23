import sys
import os

from .api_client import APIClient
from .analyzer import DocGenHook
import argparse

def main():
    parser = argparse.ArgumentParser(description="A Git post-commit hook that generates docstrings for modified functions and classes in the latest commit.")

    # Add an argument for the API token, required for authentication. If not provided, fall back to the environment variable.
    parser.add_argument("-t", "--token", help="API token for authentication. If not provided, the environment variable 'API_TOKEN' will be used.", default=os.getenv('API_TOKEN'))

    # Add an argument for the folder path. If not provided, use the current folder.
    parser.add_argument("-f", "--folder_path", help="Path to the folder to scan for modified files. Defaults to the current folder.", default=os.getcwd())

    # Parse the arguments
    args = parser.parse_args()

    # Ensure the API token is available
    if not args.token:
        print("Error: API token must be provided either as an argument or via the 'API_TOKEN' environment variable.")
        sys.exit(1)

    # Use the provided arguments
    repo_path = args.folder_path
    api_token = args.token
    api_url = 'http://localhost:8000/api'
    api_client = APIClient(api_url, api_token)
    analyzer = DocGenHook(repo_path, api_client)
    analyzer.run()

if __name__ == "__main__":
    main()
