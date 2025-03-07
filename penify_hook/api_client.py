import json
import os
import requests
from .llm_client import LLMClient

class APIClient:
    def __init__(self, api_url, api_token: str = None, bearer_token: str = None):
        self.api_url = api_url
        self.AUTH_TOKEN = api_token
        self.BEARER_TOKEN = bearer_token

    def send_file_for_docstring_generation(self, file_name, content, line_numbers, repo_details = None):
        """Send file content and modified lines to the API and return modified
        content.

        This function constructs a payload containing the file path, content,
        and modified line numbers, and sends it to a specified API endpoint for
        processing. It handles the response from the API, returning the modified
        content if the request is successful. If the request fails, it logs the
        error details and returns the original content.

        Args:
            file_name (str): The path to the file being sent.
            content (str): The content of the file to be processed.
            line_numbers (list): A list of line numbers that have been modified.
            repo_details (str?): Additional repository details if applicable.

        Returns:
            str: The modified content returned by the API, or the original content if the
                request fails.
        """
        payload = {
            'file_path': file_name,
            'content': content,
            'modified_lines': line_numbers
        }
        if repo_details:
            payload['git_repo'] = repo_details
        url = self.api_url+"/v1/hook/file/generate/doc"
        response = requests.post(url, json=payload,headers={"api-key": f"{self.AUTH_TOKEN}"}, timeout=60*10)
        if response.status_code == 200:
            response = response.json()
            return response.get('modified_content')
        else:
            error_message = response.json().get('detail')
            if not error_message:
                error_message = response.text

            raise Exception(f"API Error: {error_message}")
        
    def generate_commit_summary(self, git_diff, instruction: str = "", repo_details = None, jira_context: dict = None):
        """Generate a commit summary by sending a POST request to the API endpoint.

        This function constructs a payload containing the git diff and any
        additional instructions provided. It then sends this payload to a
        specified API endpoint to generate a summary of the commit. If the
        request is successful, it returns the response from the API; otherwise,
        it returns None.

        Args:
            git_diff (str): The git diff of the commit.
            instruction (str?): Additional instruction for the commit. Defaults to "".
            repo_details (dict?): Details of the git repository. Defaults to None.
            jira_context (dict?): JIRA issue details to enhance the commit summary. Defaults to None.

        Returns:
            dict: The response from the API if the request is successful, None otherwise.
        """
        payload = {
            'git_diff': git_diff,
            'additional_instruction': instruction
        }
        if repo_details:
            payload['git_repo'] = repo_details
            
        # Add JIRA context if available
        if jira_context:
            payload['jira_context'] = jira_context

        url = self.api_url+"/v1/hook/commit/summary"
        try:
            response = requests.post(url, json=payload, headers
            ={"api-key": f"{self.AUTH_TOKEN}"}, timeout=60*10)
            if response.status_code == 200:
                response = response.json()
                return response
            else:
                # print(f"Response: {response.status_code}")
                # print(f"Error: {response.text}")
                raise Exception(f"API Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_supported_file_types(self) -> list[str]:
        """Retrieve the supported file types from the API.

        This function sends a request to the API to obtain a list of supported
        file types. If the API responds successfully, it returns the list of
        supported file types. If the API call fails, it returns a default list
        of common file types.

        Returns:
            list[str]: A list of supported file types, either from the API or a default set.
        """

        url = self.api_url+"/v1/file/supported_languages"
        response = requests.get(url)
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return ["py", "js", "ts", "java", "kt", "cs", "c"]

    def generate_commit_summary_with_llm(self, diff, message, generate_description: bool, repo_details, llm_client : LLMClient, jira_context=None):
        """
        Generate a commit summary using a local LLM client instead of the API.
        
        Args:
            diff: Git diff of changes
            message: User-provided commit message or instructions
            repo_details: Details about the repository
            llm_client: Instance of LLMClient
            jira_context: Optional JIRA issue context to enhance the summary
            
        Returns:
            Dict with title and description for the commit
        """
        try:
            return llm_client.generate_commit_summary(diff, message, generate_description, repo_details, jira_context)
        except Exception as e:
            print(f"Error using local LLM: {e}")
            # Fall back to API for commit summary
            return self.generate_commit_summary(diff, message, repo_details, jira_context)

    def get_api_key(self):

        url = self.api_url+"/v1/apiToken/get"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.BEARER_TOKEN}"}, timeout=60*10)
        if response.status_code == 200:
            response = response.json()
            return response.get('key')
        else:
            print(f"Response: {response.status_code}")
            print(f"Error: {response.text}")
            return None

