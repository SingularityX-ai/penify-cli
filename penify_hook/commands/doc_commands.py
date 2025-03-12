
import argparse
import logging
import os

def generate_doc(api_url, token, location=None):
    import os
    import sys
    from ..folder_analyzer import FolderAnalyzerGenHook
    from ..file_analyzer import FileAnalyzerGenHook
    from ..git_analyzer import GitDocGenHook
    from ..api_client import APIClient
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


# Define the docgen description text
docgen_description = """Generate code documentation using Penify.

This command requires you to be logged in to your Penify account.
You can generate documentation for:
- Current Git diff (default)
- Specific file
- Specific folder
"""

def setup_docgen_parser(parser):
    # We don't need to create a new docgen_parser since it's passed as a parameter
    docgen_parser_description = """
It generates Documentation for the Git diff, file or folder.
1. By default, it will git diff documentation - visit https://penify.wiki/dcdc for more details.
2. If file is provided, it will generate documentation for that file - visit https://penify.wiki/dfdc
3. If folder is provided, it will generate documentation for that folder - visit https://penify.wiki/drdc
4. Commit Hooks will automatically generate documentation for the Git diff on commit - https://penify.wiki/dpchc
5. You need to be logged in to your Penify account to use these commands.
"""

    parser.description = docgen_parser_description
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    docgen_subparsers = parser.add_subparsers(title="docgen_subcommand", dest="docgen_subcommand")

    # Docgen main options (for direct documentation generation)
    parser.add_argument("-l", "--location", help="[Optional] Path to the folder or file to Generate Documentation. By default it will pick the root directory.", default=None)

    # Subcommand: install-hook (as part of docgen)
    install_hook_parser = docgen_subparsers.add_parser("install-hook", help="Install the Git post-commit hook.")
    install_hook_parser.add_argument("-l", "--location", required=False, 
                                    help="Location in which to install the Git hook. Defaults to current directory.",
                                    default=os.getcwd())

    # Subcommand: uninstall-hook (as part of docgen)
    uninstall_hook_parser = docgen_subparsers.add_parser("uninstall-hook", help="Uninstall the Git post-commit hook.")
    uninstall_hook_parser.add_argument("-l", "--location", required=False, 
                                      help="Location from which to uninstall the Git hook. Defaults to current directory.", 
                                      default=os.getcwd())

def handle_docgen(args):
    # Only import dependencies needed for docgen functionality here
    from penify_hook.commands.config_commands import get_token
    import sys
    from penify_hook.commands.doc_commands import generate_doc
    from penify_hook.commands.hook_commands import install_git_hook, uninstall_git_hook
    from penify_hook.constants import API_URL

    token = get_token()
    if not token:
        logging.error("Error: Unable to authenticate. Please run 'penifycli login'.")
        sys.exit(1)

    if args.docgen_subcommand == "install-hook":
        install_git_hook(args.location, token)

    elif args.docgen_subcommand == "uninstall-hook":
        uninstall_git_hook(args.location)

    else:  # Direct documentation generation
        generate_doc(API_URL, token, args.location)