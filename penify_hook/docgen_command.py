import logging
import os



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
