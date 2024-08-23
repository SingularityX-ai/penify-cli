import os
import requests

class APIClient:
    def __init__(self, api_url):
        self.api_url = api_url
        self.AUTH_TOKEN = os.getenv("PENIFY_AUTH_TOKEN")

    def send_file_for_docstring_generation(self, file_name, content, line_numbers):
        """Send file content and modified lines to the API and return modified content."""
        payload = {
            'file_name': file_name,
            'content': content,
            'line_numbers': line_numbers
        }

        response = requests.post(self.api_url, json=payload)

        if response.status_code == 200:
            return response.json().get('modified_content')
        else:
            return content

    def get_supported_file_types(self) -> list[str]:
        """Send file content and modified lines to the API and return modified content."""

        url = self.api_url+"/v1/file/generate/diff/doc"

        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return ["py", "js", "ts", "java", "kt", "cs", "c"]
