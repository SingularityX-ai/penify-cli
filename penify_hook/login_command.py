def setup_login_parser(parser):
    parser.add_argument("--token", help="Specify API token directly")
    # Add all other necessary arguments for login command
    
def handle_login(args):
    # Only import dependencies needed for login functionality here
    from .login import process_login
    return process_login(args)
