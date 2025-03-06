import os
import sys
from ..folder_analyzer import FolderAnalyzerGenHook
from ..file_analyzer import FileAnalyzerGenHook
from ..git_analyzer import GitDocGenHook
from ..api_client import APIClient

def generate_doc(api_url, token, location=None):
    """
    Generates documentation based on the given parameters.
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
    if len(location.split('.')) > 1:
        try:
            analyzer = FileAnalyzerGenHook(location, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif complete_folder_path:
        try:
            analyzer = FolderAnalyzerGenHook(complete_folder_path, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        try:
            analyzer = GitDocGenHook(git_folder_path, api_client)
            analyzer.run()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
