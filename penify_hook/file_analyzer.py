import os
from git import Repo
from .api_client import APIClient

class FileAnalyzerGenHook:
    def __init__(self, file_path: str, api_client: APIClient):
        self.file_path = file_path
        self.api_client = api_client
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def process_file(self, file_path):
        """Read the file, check if it's supported, and send it to the API."""
        file_abs_path = os.path.join(os.getcwd(), file_path)
        file_extension = os.path.splitext(file_path)[1].lower()

        if not file_extension:
            print(f"File {file_path} has no extension. Skipping.")
            return False
        
        file_extension = file_extension[1:]  # Remove the leading dot

        if file_extension not in self.supported_file_types:
            print(f"File type {file_extension} is not supported. Skipping {file_path}.")
            return False

        with open(file_abs_path, 'r') as file:
            content = file.read()

        modified_lines = [i for i in  range(len(content.splitlines()))]
        
        # Send data to API
        response = self.api_client.send_file_for_docstring_generation(file_path, content, modified_lines)
        
        # If the response is successful, replace the file content
        with open(file_abs_path, 'w') as file:
            file.write(response)
        print(f"File [{self.file_path}] processed successfully.")


    def run(self):
        """Run the post-commit hook."""
        try:
            self.process_file(self.file_path)
            # Stage the modified file
            
        except Exception as e:
            print(f"File [{self.file_path}] was not processed.")
        