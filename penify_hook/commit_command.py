import argparse



def setup_commit_parser(parser):
    commit_parser_description = """
It generates smart commit messages. By default, it will just generate just the Title of the commit message.
1. If you have not configured LLM, it will give an error. You either need to configure LLM or use the API key.
2. If you have not configured JIRA. It will not enhance the commit message with JIRA issue details.
3. For more information, visit https://docs.penify.dev/
"""
    parser.help = "Generate smart commit messages using local-LLM(no login required)."
    parser.description = commit_parser_description
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    
    # Add the message argument with better help
    parser.add_argument("-m", "--message", required=False, help="Commit with contextual commit message.", default="N/A")
    parser.add_argument("-e", "--terminal", action="store_true", help="Open edit terminal before committing.")
    parser.add_argument("-d", "--description", action="store_false", help="It will generate commit message with title and description.", default=False)
    
def handle_commit(args):
    from penify_hook.commands.commit_commands import commit_code
    from penify_hook.commands.config_commands import get_jira_config, get_llm_config, get_token
    from penify_hook.constants import API_URL

    # Only import dependencies needed for commit functionality here
    open_terminal = args.terminal
    generate_description = args.description
    print(f"Generate Description: {generate_description}")        
    # Try to get from config
    llm_config = get_llm_config()
    llm_model = llm_config.get('model')
    llm_api_base = llm_config.get('api_base') 
    llm_api_key = llm_config.get('api_key')
    token = get_token()



    # Try to get from config
    jira_config = get_jira_config()
    jira_url = jira_config.get('url')
    jira_user = jira_config.get('username')
    jira_api_token = jira_config.get('api_token')


    commit_code(API_URL, token, args.message, open_terminal, generate_description,
                llm_model, llm_api_base, llm_api_key,
                jira_url, jira_user, jira_api_token)
