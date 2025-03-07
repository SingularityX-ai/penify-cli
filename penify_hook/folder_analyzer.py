import os
from git import Repo

from penify_hook.base_analyzer import BaseAnalyzer
from .api_client import APIClient
from .file_analyzer import FileAnalyzerGenHook
from tqdm import tqdm

class FolderAnalyzerGenHook(BaseAnalyzer):
    def __init__(self, dir_path: str, api_client: APIClient):
        self.dir_path = dir_path
        super().__init__(dir_path, api_client)

    def list_all_files_in_dir(self, dir_path: str):
        """List all files in a directory and its subdirectories."""

        files = []
        for dirpath, dirnames, filenames in os.walk(dir_path):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for filename in filenames:
                # Construct the full file path
                full_path = os.path.join(dirpath, filename)
                files.append(full_path)
        return files

    def run(self):
        """Run the post-commit hook."""
        try:
            file_list = self.list_all_files_in_dir(self.dir_path)
            total_files = len(file_list)
            print(f"Processing {total_files} files in folder [{self.dir_path}]")
            
            with tqdm(total=total_files, desc="Processing files", unit="file", ncols=80, ascii=True) as pbar:
                for file_path in file_list:
                    try:
                        analyzer = FileAnalyzerGenHook(file_path, self.api_client)
                        analyzer.run()
                    except Exception as file_error:
                        print(f"Error processing file [{file_path}]: {file_error}")
                    pbar.update(1)  # Even if there is an error, move the progress bar forward
        except Exception as e:
            print(f"File [{self.dir_path}] was not processed due to error: {e}")
