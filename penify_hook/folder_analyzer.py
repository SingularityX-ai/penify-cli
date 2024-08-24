import os
from git import Repo
from .api_client import APIClient
from .file_analyzer import FileAnalyzerGenHook
from tqdm import tqdm

class FolderAnalyzerGenHook:
    def __init__(self, dir_path: str, api_client: APIClient):
        self.dir_path = dir_path
        self.api_client = api_client

    def list_all_files_in_dir(self, dir_path: str):
        """List all files in a directory and its subdirectories.

        This function traverses the specified directory and its subdirectories,
        collecting the full paths of all files found. It ignores any directories
        that start with a dot (.), which are typically hidden directories in
        Unix-like operating systems. The resulting list contains the full paths
        of the files, making it useful for file management tasks.

        Args:
            dir_path (str): The path to the directory to search for files.

        Returns:
            list: A list of full file paths found in the specified directory and its
            subdirectories.
        """

        files = []
        for dirpath, dirnames, filenames in os.walk(dir_path):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for filename in filenames:
                # Construct the full file path
                full_path = os.path.join(dirpath, filename)
                files.append(full_path)
        return files

    def run(self):
        """Run the post-commit hook.

        This method processes all files in the specified directory by listing
        them and running a file analyzer on each one. It provides feedback on
        the number of files being processed and handles any errors that occur
        during the analysis of individual files, ensuring that the progress bar
        updates appropriately even in the event of an error.  It first retrieves
        a list of all files in the specified directory and prints the total
        number of files to be processed. Then, it initializes a progress bar to
        visually indicate the processing status. For each file, it attempts to
        create an instance of `FileAnalyzerGenHook` and run its analysis method.
        If an error occurs while processing a file, it catches the exception,
        prints an error message, and continues with the next file, ensuring that
        the progress bar reflects the ongoing processing.
        """
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
