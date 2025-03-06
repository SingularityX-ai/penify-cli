import os
import sys
from ..folder_analyzer import FolderAnalyzerGenHook
from ..file_analyzer import FileAnalyzerGenHook
from ..git_analyzer import GitDocGenHook
from ..api_client import APIClient

def generate_doc(api_url, token, location=None):
    """Generates documentation based on the given parameters.

    This function initializes an API client using the provided API URL and
    token. It then generates documentation by analyzing the specified
    location, which can be a folder, a file, or the current working
    directory if no location is provided. The function handles different
    types of analysis based on the input location and reports any errors
    encountered during the process.

    Args:
        api_url (str): The URL of the API to connect to for documentation generation.
        token (str): The authentication token for accessing the API.
        location (str?): The path to a specific file or folder to analyze.
            If not provided, the current working directory is used.
    """
    api_client = APIClient(api_url, token)
    if location is None:
        current_folder_path = os.getcwd()
        try:
            analyzer = GitDocGenHook(current_folder_path, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # if location is a file
    elif len(location.split('.')) > 1:
        try:
            analyzer = FileAnalyzerGenHook(location, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        try:
            analyzer = FolderAnalyzerGenHook(location, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)