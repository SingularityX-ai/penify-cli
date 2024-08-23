import json
import os
import requests

class APIClient:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.AUTH_TOKEN = api_token

    def send_file_for_docstring_generation(self, file_name, content, line_numbers):
        """Send file content and modified lines to the API and return modified content."""
        payload = {
            'file_path': file_name,
            'content': content,
            'modified_lines': line_numbers
        }
        url = self.api_url+"/v1/file/generate/diff/doc"
        response = requests.post(url, json=payload,headers={"api-key": f"{self.AUTH_TOKEN}"}, timeout=60*10)
        if response.status_code == 200:
            response = response.json()
            return response.get('modified_content')
        else:
            print(f"Response: {response.status_code}")
            print(f"Error: {response.text}")
            return content

    def get_supported_file_types(self) -> list[str]:
        """Send file content and modified lines to the API and return modified content."""

        url = self.api_url+"/v1/file/supported_languages"
        response = requests.get(url)
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return ["py", "js", "ts", "java", "kt", "cs", "c"]
