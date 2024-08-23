import os
from hooks.file_processor import FileProcessor
from hooks.api_client import APIClient

class PrecommitHook:
    def __init__(self, api_url):
        self.file_processor = FileProcessor()
        self.api_client = APIClient(api_url)
        self.supported_file_types = self.api_client.get_supported_file_types()

    def run(self):
        print("Running pre-commit docstring generation...")
        staged_files_with_changes = self.file_processor.get_staged_files_with_changes(self.supported_file_types)
        if staged_files_with_changes:
            self.process_files(staged_files_with_changes)
        else:
            print("No changes detected in staged files.")
        print("Pre-commit hook completed.")

    def process_files(self, files_with_changes):
        for file, line_numbers in files_with_changes.items():
            content = self.file_processor.read_file_content(file)
            modified_content = self.api_client.send_file_for_docstring_generation(file, content, line_numbers)
            self.file_processor.write_file_content(file, modified_content)
            print(f"Docstrings generated and applied to {file}")

if __name__ == "__main__":
    API_URL = "http://localhost:8000/api"  # Replace with your actual API URL
    hook = PrecommitHook(API_URL)
    hook.run()
