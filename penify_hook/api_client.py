import json
import os
import requests

class APIClient:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.AUTH_TOKEN = api_token

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
            repo_details (str?): Additional repository details, if applicable.

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
            print(f"Response: {response.status_code}")
            print(f"Error: {response.text}")
            return content
        
    def generate_commit_summary(self, git_diff, instruction: str = "", repo_details = None):
        """Send file content and modified lines to the API and return modified
        content.

        This function constructs a payload containing the git diff, any
        additional instructions, and optional repository details. It sends this
        payload to a specified API endpoint for processing. Upon receiving a
        response from the API, it checks the status code to determine if the
        request was successful. If the request is successful, it returns the
        modified content provided by the API. If the request fails, it logs the
        error details and returns None.

        Args:
            git_diff (str): The git diff information representing changes made.
            instruction (str?): Additional instructions for processing the diff.
                Defaults to an empty string.
            repo_details (optional): Details about the repository. Defaults to None.

        Returns:
            dict or None: The modified content returned by the API as a dictionary,
                or None if the request fails.
        """
        payload = {
            'git_diff': git_diff,
            'additional_instruction': instruction
        }
        if repo_details:
            payload['git_repo'] = repo_details

        url = self.api_url+"/v1/hook/commit/summary"
        response = requests.post(url, json=payload,headers={"api-key": f"{self.AUTH_TOKEN}"}, timeout=60*10)
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            print(f"Response: {response.status_code}")
            print(f"Error: {response.text}")
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
