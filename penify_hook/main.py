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

    This function serves as the main interface for the Penify command-line
    tool, which provides various functionalities including AI commit message
    generation, JIRA integration for enhancing commit messages, code
    documentation generation, and Git hook installation for automatic
    documentation generation.  It sets up the command-line argument parser
    with subcommands for basic and advanced operations. Basic commands do
    not require user login, while advanced commands do. The function also
    handles the parsing of arguments and the execution of the corresponding
    commands based on user input.  For more information about the tool and
    its capabilities, please visit https://docs.penify.dev/.
    """
    # Configure logging
    logging.basicConfig(level=logging.WARNING,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Multi-line description using triple quotes
    description = """Penify CLI tool for:
1. AI commit message generation with JIRA integration to enhance commit messages. By default, it uses local-LLM but can be configured to use Penify's LLM. 
2. Generating Code Documentation, it requires SignUp to Penify
3. For more information, visit https://docs.penify.dev/
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

    
    commit_parser_description = """
It generates smart commit messages. By default, it will just generate just the Title of the commit message.

1. If you have not configured LLM, it will give an error. You either need to configure LLM or use the API key.
2. If you have not configured JIRA. It will not enhance the commit message with JIRA issue details.
3. For more information, visit https://docs.penify.dev/
"""
    
    # Subcommand: commit
    commit_parser = subparsers.add_parser("commit", help="Generate smart commit messages using local-LLM(no login required).", description=commit_parser_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    commit_parser.add_argument("-m", "--message", required=False, help="Commit with contextual commit message.", default="N/A")
    commit_parser.add_argument("-e", "--terminal", action="store_true", help="Open edit terminal before committing.")
    commit_parser.add_argument("-d", "--description", action="store_false", help="It will generate commit message with title and description.", default=False)

    # Subcommand: config
    config_parser = subparsers.add_parser("config", help="Configure local-LLM and JIRA.")
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
    login_parser = subparsers.add_parser("login", help="Log in to Penify to use advanced features like 'docgen' generation.")

    docgen_description="""By default, 'docgen' generates documentation for the latest Git commit diff. Use the -l flag to document a specific file or folder.

The 'install-hook' command sets up a Git post-commit hook to auto-generate documentation after each commit.
"""
    
    # Advanced Subcommand: docgen
    docgen_parser = subparsers.add_parser("docgen", help="[REQUIRES LOGIN] Generate code documentation for the Git diff, file or folder.", description=docgen_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    docgen_subparsers = docgen_parser.add_subparsers(title="docgen_subcommand", dest="docgen_subcommand")
    
    # Docgen main options (for direct documentation generation)
    docgen_parser.add_argument("-l", "--location", help="[Optional] Path to the folder or file to Generate Documentation. By default it will pick the root directory.", default=None)
    
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
            logging.error("Error: Unable to authenticate. Please run 'penifycli login'.")
            sys.exit(1)
            
        if args.docgen_subcommand == "install-hook":
            install_git_hook(args.location, token)
        
        elif args.docgen_subcommand == "uninstall-hook":
            uninstall_git_hook(args.location)
        
        else:  # Direct documentation generation
            generate_doc(API_URL, token, args.location)
    
    elif args.subcommand == "commit":
        # For commit, token is now optional - some functionality may be limited without it
        open_terminal = args.terminal
        generate_description = args.description
        print(f"Generate Description: {generate_description}")        
        # Try to get from config
        llm_config = get_llm_config()
        llm_model = llm_config.get('model')
        llm_api_base = llm_config.get('api_base') 
        llm_api_key = llm_config.get('api_key')
        
        
       
        # Try to get from config
        jira_config = get_jira_config()
        jira_url = jira_config.get('url')
        jira_user = jira_config.get('username')
        jira_api_token = jira_config.get('api_token')

    
        commit_code(API_URL, token, args.message, open_terminal, generate_description,
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
