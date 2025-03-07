import argparse
import sys
import time

def main():
    parser = argparse.ArgumentParser(
        description="""Penify CLI tool for:
1. AI commit message generation with JIRA integration to enhance commit messages.
2. Generating Code Documentation, it requires SignUp to Penify
3. For more information, visit https://docs.penify.dev/""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    
    # Add version flag
    parser.add_argument('--version', '-v', action='store_true', help='Show version information')

    subparsers = parser.add_subparsers(title="subcommands", dest="command")
    
    # Define subparsers without importing their modules yet
    commit_parser = subparsers.add_parser("commit", help="Generate smart commit messages using local-LLM(no login required).")
    config_parser = subparsers.add_parser("config", help="Configure local-LLM and JIRA.")
    login_parser = subparsers.add_parser("login", help="Log in to Penify to use advanced features like 'docgen' generation.")
    docgen_parser = subparsers.add_parser("docgen", help="[REQUIRES LOGIN] Generate code documentation for the Git diff, file or folder.")
    
    # Parse args without validation first to check for simple flags like --version
    if '--version' in sys.argv or '-v' in sys.argv:
        from importlib.metadata import version
        try:
            print(f"penifycli version {version('penifycli')}")
        except:
            print("penifycli version 0.2.2")
        return 0

    print("Welcome to Penify CLI!")
    
    # Parse the arguments to determine which command was requested
    args, unknown = parser.parse_known_args()
    # print(f"Unknown args: {unknown}")
    # print(f"Running command: {args.command}")
    print("Please run 'penifycli --help' to see the available commands.")
    
    
    # Import only the needed module based on the command
    if args.command == "commit":
        print("Please wait while we generate the commit message...")
        from .commit_command import setup_commit_parser, handle_commit
        setup_commit_parser(commit_parser)
        time.sleep(1)
        sys.exit(0) 
        return handle_commit(parser.parse_args())
    elif args.command == "config":
        from .config_command import setup_config_parser, handle_config
        setup_config_parser(config_parser)
        return handle_config(parser.parse_args())
    elif args.command == "login":
        from .login_command import setup_login_parser, handle_login
        setup_login_parser(login_parser)
        return handle_login(parser.parse_args())
    elif args.command == "docgen":
        from .docgen_command import setup_docgen_parser, handle_docgen
        setup_docgen_parser(docgen_parser)
        return handle_docgen(parser.parse_args())
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
