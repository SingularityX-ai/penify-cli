import os
from hooks.file_processor import FileProcessor
from hooks.api_client import APIClient

class PrecommitHook:
    def __init__(self, api_url):
        self.file_processor = FileProcessor()
        self.api_client = APIClient(api_url)
        self.supported_file_types = self.api_client.get_supported_file_types()

    def run(self):
        """Execute the pre-commit hook for docstring generation.

        This method checks for staged files with changes and processes them if
        any are found. It utilizes the file processor to retrieve the relevant
        files based on supported file types. If no changes are detected, a
        message is printed to inform the user.
        """

        print("Running pre-commit docstring generation...")
        staged_files_with_changes = self.file_processor.get_staged_files_with_changes(self.supported_file_types)
        if staged_files_with_changes:
            self.process_files(staged_files_with_changes)
        else:
            print("No changes detected in staged files.")
        print("Pre-commit hook completed.")

    def process_files(self, files_with_changes):
        """Process files to generate and apply docstrings.

        This function iterates over a dictionary of files with their
        corresponding line numbers that require docstring generation. For each
        file, it reads the content, sends it to an API client for docstring
        generation, and then writes the modified content back to the file. It
        also prints a confirmation message for each processed file.

        Args:
            files_with_changes (dict): A dictionary where keys are file names (str) and values are
                lists of line numbers (list) that need docstring generation.
        """

        for file, line_numbers in files_with_changes.items():
            content = self.file_processor.read_file_content(file)
            modified_content = self.api_client.send_file_for_docstring_generation(file, content, line_numbers)
            self.file_processor.write_file_content(file, modified_content)
            print(f"Docstrings generated and applied to {file}")

if __name__ == "__main__":
    API_URL = "http://localhost:8000/api"  # Replace with your actual API URL
    hook = PrecommitHook(API_URL)
    hook.run()
