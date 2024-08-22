import os
import requests

class APIClient:
    def __init__(self, api_url):
        self.api_url = api_url
        self.AUTH_TOKEN = os.getenv("PENIFY_AUTH_TOKEN")

    def send_file_for_docstring_generation(self, file_name, content, line_numbers):
        """Send file content and modified lines to the API and return modified
        content.

        This function constructs a payload with the provided file name, content,
        and line numbers, and sends it to a specified API endpoint. If the API
        responds with a status code of 200, the function extracts and returns
        the modified content from the response. If the response indicates an
        error or a different status code, the original content is returned.

        Args:
            file_name (str): The name of the file being processed.
            content (str): The content of the file to be sent.
            line_numbers (list): A list of line numbers that have been modified.

        Returns:
            str: The modified content returned by the API, or the original content
            if the API call was unsuccessful.
        """
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
        """Retrieve supported file types from the API.

        This function sends a request to a specified API endpoint to retrieve
        the supported file types. If the request is successful (HTTP status code
        200), it returns the list of file types provided by the API. If the
        request fails, it returns a default list of commonly used file types.

        Returns:
            list[str]: A list of supported file types, either from the API or a default list.
        """

        url = self.api_url+"/v1/file/generate/diff/doc"

        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return ["py", "js", "ts", "java", "kt", "cs", "c"]
