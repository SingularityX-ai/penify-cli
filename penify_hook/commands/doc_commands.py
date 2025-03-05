import sys
from ..folder_analyzer import FolderAnalyzerGenHook
from ..file_analyzer import FileAnalyzerGenHook
from ..git_analyzer import GitDocGenHook
from ..api_client import APIClient

def generate_doc(api_url, token, file_path=None, complete_folder_path=None, git_folder_path=None):
    """Generate documentation based on the provided parameters.

    This function generates documentation by utilizing different analyzers
    depending on the input parameters. It can analyze a specific file, a
    complete folder, or a Git repository. The function initializes an API
    client with the given API URL and token, and then it attempts to run the
    appropriate analyzer based on the provided arguments. If an error occurs
    during the analysis, it prints the error message and exits the program.

    Args:
        api_url (str): The URL of the API to connect to.
        token (str): The authentication token for the API.
        file_path (str?): The path to a specific file to analyze.
        complete_folder_path (str?): The path to a complete folder to analyze.
        git_folder_path (str?): The path to a Git repository to analyze.
    """
    api_client = APIClient(api_url, token)

    if file_path:
        try:
            analyzer = FileAnalyzerGenHook(file_path, api_client)
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
