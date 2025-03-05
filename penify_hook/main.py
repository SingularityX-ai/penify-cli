import os
import sys
import argparse
import logging

# Import command modules
from .commands.hook_commands import install_git_hook, uninstall_git_hook
from .commands.doc_commands import generate_doc
from .commands.commit_commands import commit_code
from .commands.auth_commands import login
from .commands.config_commands import (
    save_llm_config, save_jira_config, 
    config_llm_web, config_jira_web,
    get_llm_config, get_jira_config, get_token
)

# Try importing optional dependencies
try:
    from .jira_client import JiraClient
except ImportError:
    JiraClient = None

# Constants
API_URL = 'https://production-gateway.snorkell.ai/api'
DASHBOARD_URL = "https://dashboard.penify.dev/auth/localhost/login"
# API_URL = 'http://localhost:8000/api'

def main():
    """Main entry point for the Penify CLI tool.

    This function serves as the command-line interface for the Penify tool,
    allowing users to manage Git hooks, generate documentation, and
    configure settings for LLM and JIRA integrations. It sets up argument
    parsing for various subcommands, including installing and uninstalling
    Git hooks, generating documentation, committing changes, and configuring
    LLM and JIRA settings. The function also handles user authentication
    through an API token and manages the execution of the specified
    subcommands based on user input.
    """
    # Configure logging
    logging.basicConfig(level=logging.WARNING,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Penify CLI tool for managing Git hooks and generating documentation.")
    
    parser.add_argument("-t", "--token", help="API token for authentication.")

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # Subcommand: install-hook
    install_parser = subparsers.add_parser("install-hook", help="Install the Git post-commit hook.")
    install_parser.add_argument("-l", "--location", required=True, help="Location in which to install the Git hook.")

    # Subcommand: uninstall-hook
    uninstall_parser = subparsers.add_parser("uninstall-hook", help="Uninstall the Git post-commit hook.")
    uninstall_parser.add_argument("-l", "--location", required=True, help="Location from which to uninstall the Git hook.")

    # Subcommand: doc-gen
    doc_gen_parser = subparsers.add_parser("doc-gen", help="Generate documentation for specified files or folders.")
    doc_gen_parser.add_argument("-fl", "--file_path", help="Path of the file to generate documentation.")
    doc_gen_parser.add_argument("-cf", "--complete_folder_path", help="Generate documentation for the entire folder.")
    doc_gen_parser.add_argument("-gf", "--git_folder_path", help="Path to the folder with git to scan for modified files.", default=os.getcwd())

    # Subcommand: commit
    commit_parser = subparsers.add_parser("commit", help="Commit with a message.")
    commit_parser.add_argument("-gf", "--git_folder_path", help="Path to the folder with git.", default=os.getcwd())
    commit_parser.add_argument("-m", "--message", required=False, help="Commit message.", default="N/A")
    commit_parser.add_argument("-e", "--terminal", required=False, help="Open edit terminal", default="False")
    # Add LLM options
    commit_parser.add_argument("--llm", "--llm-model", dest="llm_model", help="LLM model to use")
    commit_parser.add_argument("--llm-api-base", help="API base URL for the LLM service")
    commit_parser.add_argument("--llm-api-key", help="API key for the LLM service")
    # Add JIRA options
    commit_parser.add_argument("--jira-url", help="JIRA base URL")
    commit_parser.add_argument("--jira-user", help="JIRA username or email")
    commit_parser.add_argument("--jira-api-token", help="JIRA API token")

    # Add a new subcommand: config-llm
    llm_config_parser = subparsers.add_parser("config-llm", help="Configure LLM settings")
    llm_config_parser.add_argument("--model", required=True, help="LLM model to use")
    llm_config_parser.add_argument("--api-base", help="API base URL for the LLM service")
    llm_config_parser.add_argument("--api-key", help="API key for the LLM service")

    # Add a new subcommand: config-llm-web
    subparsers.add_parser("config-llm-web", help="Configure LLM settings through a web interface")

    # Add a new subcommand: config-jira
    jira_config_parser = subparsers.add_parser("config-jira", help="Configure JIRA settings")
    jira_config_parser.add_argument("--url", required=True, help="JIRA base URL")
    jira_config_parser.add_argument("--username", required=True, help="JIRA username or email")
    jira_config_parser.add_argument("--api-token", required=True, help="JIRA API token")
    jira_config_parser.add_argument("--verify", action="store_true", help="Verify JIRA connection")

    # Add a new subcommand: config-jira-web
    subparsers.add_parser("config-jira-web", help="Configure JIRA settings through a web interface")

    # Subcommand: login
    subparsers.add_parser("login", help="Log in to Penify and obtain an API token.")

    args = parser.parse_args()

    # Get the token based on priority
    token = get_token(args.token)

    # Process commands
    if args.subcommand == "install-hook":
        if not token:
            print("Error: API token is required.")
            sys.exit(1)
        install_git_hook(args.location, token)
    
    elif args.subcommand == "uninstall-hook":
        uninstall_git_hook(args.location)
    
    elif args.subcommand == "doc-gen":
        if not token:
            print("Error: API token is required.")
            sys.exit(1)
        generate_doc(API_URL, token, args.file_path, args.complete_folder_path, args.git_folder_path)
    
    elif args.subcommand == "commit":
        if not token:
            print("Error: API token is required.")
            sys.exit(1)
        
        open_terminal = args.terminal.lower() == "true"
        
        # Get LLM configuration
        llm_model = args.llm_model
        llm_api_base = args.llm_api_base
        llm_api_key = args.llm_api_key
        
        if not llm_model:
            # Try to get from config
            llm_config = get_llm_config()
            llm_model = llm_config.get('model')
            llm_api_base = llm_config.get('api_base') if not llm_api_base else llm_api_base
            llm_api_key = llm_config.get('api_key') if not llm_api_key else llm_api_key
        
        # Get JIRA configuration
        jira_url = args.jira_url
        jira_user = args.jira_user
        jira_api_token = args.jira_api_token
        
        if not jira_url or not jira_user or not jira_api_token:
            # Try to get from config
            jira_config = get_jira_config()
            jira_url = jira_url or jira_config.get('url')
            jira_user = jira_user or jira_config.get('username')
            jira_api_token = jira_api_token or jira_config.get('api_token')
        
        commit_code(API_URL, args.git_folder_path, token, args.message, open_terminal,
                   llm_model, llm_api_base, llm_api_key,
                   jira_url, jira_user, jira_api_token)
    
    elif args.subcommand == "config-llm":
        save_llm_config(args.model, args.api_base, args.api_key)
        print(f"LLM configuration set: Model={args.model}, API Base={args.api_base or 'default'}")
    
    elif args.subcommand == "config-llm-web":
        config_llm_web()
    
    elif args.subcommand == "config-jira":
        save_jira_config(args.url, args.username, args.api_token)
        print(f"JIRA configuration set: URL={args.url}, Username={args.username}")
        
        # Verify connection if requested
        if args.verify:
            if JiraClient:
                jira_client = JiraClient(
                    jira_url=args.url,
                    jira_user=args.username,
                    jira_api_token=args.api_token
                )
                if jira_client.is_connected():
                    print("JIRA connection verified successfully!")
                else:
                    print("Failed to connect to JIRA. Please check your credentials.")
            else:
                print("JIRA package not installed. Cannot verify connection.")
    
    elif args.subcommand == "config-jira-web":
        config_jira_web()
    
    elif args.subcommand == "login":
        login(API_URL, DASHBOARD_URL)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
