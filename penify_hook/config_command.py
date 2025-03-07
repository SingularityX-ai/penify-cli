def setup_config_parser(parser):
    parser.add_argument("--llm", help="Set the LLM provider (local or penify)")
    # Add all other necessary arguments for config command
    
def handle_config(args):
    # Only import dependencies needed for config functionality here
    from .config import process_config
    return process_config(args)
