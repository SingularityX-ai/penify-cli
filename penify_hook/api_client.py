import json
import os
import requests

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

        This function constructs a payload containing the file path, content,
        and modified line numbers, and sends it to a specified API endpoint for
        processing. It handles the response from the API, returning the modified
        content if the request is successful. If the request fails, it logs the
        error details and returns the original content.

        Args:
            file_name (str): The path to the file being sent.
            content (str): The content of the file to be processed.
            line_numbers (list): A list of line numbers that have been modified.

        Returns:
            str: The modified content returned by the API, or the original content if the
                request fails.
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
        
    def generate_commit_summary(self, git_diff, instruction: str = "", repo_details = None):
        """
        Generates a commit summary by sending a POST request to the API endpoint.

        Args:
            git_diff (str): The git diff of the commit.
            instruction (str, optional): Additional instruction for the commit. Defaults to "".
            repo_details (dict, optional): Details of the git repository. Defaults to None.

        Returns:
            dict: The response from the API if the request is successful, None otherwise.
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

        