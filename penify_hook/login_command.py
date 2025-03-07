def setup_login_parser(parser):
    parser.add_argument("--token", help="Specify API token directly")
    # Add all other necessary arguments for login command
    
def handle_login(args):
    from penify_hook.constants import API_URL, DASHBOARD_URL
    from penify_hook.commands.auth_commands import login


    # Only import dependencies needed for login functionality here
    return login(API_URL, DASHBOARD_URL)
