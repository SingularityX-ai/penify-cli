import json
import os
import requests

class APIClient:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.AUTH_TOKEN = api_token

    def send_file_for_docstring_generation(self, file_name, content, line_numbers):
        """Send file content and modified lines to the API and return modified
        content.

        This function constructs a payload containing the file path, content,
        and modified line numbers, then sends this payload to a specified API
        endpoint for processing. It handles the API response and returns the
        modified content if the request is successful. If the request fails, it
        returns the original content.

        Args:
            file_name (str): The name of the file to be processed.
            content (str): The content of the file to be sent.
            line_numbers (list): A list of line numbers that have been modified.

        Returns:
            str: The modified content returned by the API, or the original
            content if the request was unsuccessful.
        """
        payload = {
            'file_path': file_name,
            'content': content,
            'modified_lines': line_numbers
        }
        print(f"Sending file {file_name} to API for processing.")
        url = self.api_url+"/v1/file/generate/diff/doc"
        response = requests.post(url, json=payload,headers={"api-key": f"{self.AUTH_TOKEN}"}, timeout=60*10)
        print("status_code",response.status_code)
        if response.status_code == 200:
            response = response.json()
            print(f"is Modified: {not response.get('status')}")
            return response.get('modified_content')
        else:
            return content

    def get_supported_file_types(self) -> list[str]:
        """Send file content and modified lines to the API and return modified content."""

        url = self.api_url+"/v1/file/supported_languages"
        print(f"Sending request to {url}")
        response = requests.get(url)
        
        print("status_code",response.status_code)
        print("response",response)

        if response.status_code == 200:
            response = response.json()
            print(f"supported languages: {response}")
            return response
        else:
            return ["py", "js", "ts", "java", "kt", "cs", "c"]
