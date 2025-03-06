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
    """Main entry point for the Penify CLI tool."""
    # Configure logging
    logging.basicConfig(level=logging.WARNING,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Multi-line description using triple quotes
    description = """Penify CLI tool for:
1. AI commit message generation
2. Using JIRA descriptions to enhance commit messages
3. Generating code documentation for code files
4. Installing Git hooks for automatic documentation generation
5. For more information, visit https://docs.penify.dev/
"""

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # Create subparsers for the main commands
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    
    # Group commands logically
    basic_title = "Basic Commands (No login required)"
    advanced_title = "Advanced Commands (Login required)"
    
    # Create grouped subparsers (visually separated in help output)
    parser.add_argument_group(basic_title)
    parser.add_argument_group(advanced_title)
    
    # ===== BASIC COMMANDS (No login required) =====
    
    # Subcommand: commit
    commit_parser = subparsers.add_parser("commit", help="Generate smart commit messages (no login required).")
    commit_parser.add_argument("-gf", "--git_folder_path", help="Path to the folder with git.", default=os.getcwd())
    commit_parser.add_argument("-m", "--message", required=False, help="Commit with contextual commit message.", default="N/A")
    commit_parser.add_argument("-e", "--terminal", required=False, help="Open edit terminal", default="False")
    # Add LLM options
    commit_parser.add_argument("--llm", "--llm-model", dest="llm_model", help="LLM model to use")
    commit_parser.add_argument("--llm-api-base", help="API base URL for the LLM service")
    commit_parser.add_argument("--llm-api-key", help="API key for the LLM service")
    # Add JIRA options
    commit_parser.add_argument("--jira-url", help="JIRA base URL")
    commit_parser.add_argument("--jira-user", help="JIRA username or email")
    commit_parser.add_argument("--jira-api-token", help="JIRA API token")

    # Subcommand: config
    config_parser = subparsers.add_parser("config", help="Configure local settings (no login required).")
    config_subparsers = config_parser.add_subparsers(title="config_type", dest="config_type")
    
    # Config subcommand: llm
    llm_config_parser = config_subparsers.add_parser("llm", help="Configure LLM settings.")
    llm_config_parser.add_argument("--model", required=True, help="LLM model to use")
    llm_config_parser.add_argument("--api-base", help="API base URL for the LLM service")
    llm_config_parser.add_argument("--api-key", help="API key for the LLM service")
    
    # Config subcommand: llm-web
    config_subparsers.add_parser("llm-web", help="Configure LLM settings through a web interface")
    
    # Config subcommand: jira
    jira_config_parser = config_subparsers.add_parser("jira", help="Configure JIRA settings.")
    jira_config_parser.add_argument("--url", required=True, help="JIRA base URL")
    jira_config_parser.add_argument("--username", required=True, help="JIRA username or email")
    jira_config_parser.add_argument("--api-token", required=True, help="JIRA API token")
    jira_config_parser.add_argument("--verify", action="store_true", help="Verify JIRA connection")
    
    # Config subcommand: jira-web
    config_subparsers.add_parser("jira-web", help="Configure JIRA settings through a web interface")
    
    # ===== ADVANCED COMMANDS (Login required) =====
    
    # Subcommand: login (bridge between basic and advanced)
    login_parser = subparsers.add_parser("login", help="Log in to Penify to use advanced features like documentation generation.")
    
    # Advanced Subcommand: docgen
    docgen_parser = subparsers.add_parser("docgen", help="[REQUIRES LOGIN] Generate documentation and manage Git hooks.")
    docgen_subparsers = docgen_parser.add_subparsers(title="docgen_subcommand", dest="docgen_subcommand")
    
    # Docgen main options (for direct documentation generation)
    docgen_parser.add_argument("-fl", "--file_path", help="Path of the file to generate documentation.")
    docgen_parser.add_argument("-l", "--git_folder_path", help="Path to the folder with git to scan for modified files.", default=os.getcwd())
    
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

    args = parser.parse_args()

    # Get the token based on priority
    token = get_token()

    # Process commands
    if args.subcommand == "docgen":
        # Check for login for all advanced commands
        if not token:
            print("Error: This command requires login. Please run 'penifycli login' first.")
            sys.exit(1)
            
        if args.docgen_subcommand == "install-hook":
            install_git_hook(args.location, token)
        
        elif args.docgen_subcommand == "uninstall-hook":
            uninstall_git_hook(args.location)
        
        else:  # Direct documentation generation
            generate_doc(API_URL, token, args.file_path, args.complete_folder_path, args.git_folder_path)
    
    elif args.subcommand == "commit":
        # For commit, token is now optional - some functionality may be limited without it
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
    
    elif args.subcommand == "config":
        # Config doesn't require token
        if args.config_type == "llm":
            save_llm_config(args.model, args.api_base, args.api_key)
            print(f"LLM configuration set: Model={args.model}, API Base={args.api_base or 'default'}")
        
        elif args.config_type == "llm-web":
            config_llm_web()
        
        elif args.config_type == "jira":
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
        
        elif args.config_type == "jira-web":
            config_jira_web()
        
        else:
            config_parser.print_help()
    
    elif args.subcommand == "login":
        login(API_URL, DASHBOARD_URL)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
