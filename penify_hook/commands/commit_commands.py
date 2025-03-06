import os
import sys

from penify_hook.utils import recursive_search_git_folder
from ..commit_analyzer import CommitDocGenHook
from ..api_client import APIClient

# Try importing optional dependencies
try:
    from ..llm_client import LLMClient
except ImportError:
    LLMClient = None

try:
    from ..jira_client import JiraClient
except ImportError:
    JiraClient = None

def commit_code(api_url, token, message, open_terminal, 
               llm_model=None, llm_api_base=None, llm_api_key=None,
               jira_url=None, jira_user=None, jira_api_token=None):
    """
    Enhance Git commits with AI-powered commit messages.
    """
    # Create API client
    api_client = APIClient(api_url, token)
    
    # Initialize LLM client if LLM parameters are provided and LLMClient is available
    llm_client = None
    if LLMClient is not None and llm_model:
        try:
            llm_client = LLMClient(
                model=llm_model,
                api_base=llm_api_base,
                api_key=llm_api_key
            )
            print(f"Using LLM model: {llm_model}")
        except Exception as e:
            print(f"Error initializing LLM client: {e}")
            print("Falling back to API for commit summary generation")
    
    # Initialize JIRA client if parameters are provided and JiraClient is available
    jira_client = None
    if JiraClient is not None and jira_url and jira_user and jira_api_token:
        try:
            jira_client = JiraClient(
                jira_url=jira_url,
                jira_user=jira_user,
                jira_api_token=jira_api_token
            )
            if jira_client.is_connected():
                print(f"Connected to JIRA: {jira_url}")
            else:
                print(f"Failed to connect to JIRA: {jira_url}")
                jira_client = None
        except Exception as e:
            print(f"Error initializing JIRA client: {e}")
            jira_client = None
    
    try:
        # Pass the LLM client and JIRA client to CommitDocGenHook
        gf_path = recursive_search_git_folder(os.getcwd())
        analyzer = CommitDocGenHook(gf_path, api_client, llm_client, jira_client)
        analyzer.run(message, open_terminal)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
