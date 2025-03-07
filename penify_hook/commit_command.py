def setup_commit_parser(parser):
    parser.add_argument("--message", "-m", help="Specify commit message directly")
    # Add all other necessary arguments for commit command
    
def handle_commit(args):
    # Only import dependencies needed for commit functionality here
    from .commit import process_commit
    return process_commit(args)
