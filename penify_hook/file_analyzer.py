import os
from git import Repo
from .api_client import APIClient

class FileAnalyzerGenHook:
    def __init__(self, file_path: str, api_client: APIClient):
        self.file_path = file_path
        self.api_client = api_client
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def process_file(self, file_path):
        """Process a file by reading its content and sending it to an API for
        processing.

        This function checks if the provided file has a supported extension. If
        the file is valid, it reads the content of the file and sends it to an
        API client for further processing. If the API responds successfully, the
        original file content is replaced with the response.

        Args:
            file_path (str): The relative path to the file that needs to be processed.

        Returns:
            bool: True if the file was processed successfully, False otherwise.
        """
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
        """Run the post-commit hook.

        This method executes the post-commit hook by processing a specified
        file. It attempts to process the file located at `self.file_path`. If an
        error occurs during the processing, it catches the exception and prints
        an error message indicating that the file was not processed.
        """
        try:
            self.process_file(self.file_path)
            # Stage the modified file
            
        except Exception as e:
            print(f"File [{self.file_path}] was not processed.")
        