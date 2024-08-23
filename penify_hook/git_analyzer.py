import os
from git import Repo
from tqdm import tqdm
from .api_client import APIClient

class GitDocGenHook:
    def __init__(self, repo_path: str, api_client: APIClient):
        self.repo_path = repo_path
        self.api_client = api_client
        self.repo = Repo(repo_path)
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def get_modified_files_in_last_commit(self):
        """Get the list of files modified in the last commit.

        This function retrieves the files that were modified in the most recent
        commit of the repository. It accesses the last commit and iterates
        through the differences to compile a list of unique file paths that were
        changed. The function returns this list for further processing or
        analysis.

        Returns:
            list: A list of file paths that were modified in the last commit.
        """
        last_commit = self.repo.head.commit
        modified_files = []
        for diff in last_commit.diff('HEAD~1'):
            if diff.a_path not in modified_files:
                modified_files.append(diff.a_path)
        return modified_files

    def get_modified_lines(self, diff_text):
        """Extract modified line numbers from a diff text.

        This function processes a diff text to identify and extract the line
        numbers that have been modified. It distinguishes between added and
        deleted lines and keeps track of the current line number as it parses
        through the diff. The function handles hunk headers and ensures that any
        deletions at the end of the file are also captured.

        Args:
            diff_text (str): A string containing the diff text to be processed.

        Returns:
            list: A sorted list of unique line numbers that have been modified.
        """
        modified_lines = []
        current_line = 0
        deletion_start = None

        for line in diff_text.splitlines():
            if line.startswith('@@'):
                # Parse the hunk header
                _, old, new, _ = line.split(' ', 3)
                current_line = int(new.split(',')[0].strip('+'))
                deletion_start = None
            elif line.startswith('-'):
                # This is a deleted line
                if deletion_start is None:
                    deletion_start = current_line
            elif line.startswith('+'):
                # This is an added line
                modified_lines.append(current_line)
                current_line += 1
                if deletion_start is not None:
                    modified_lines.append(deletion_start)
                    deletion_start = None
            else:
                # This is an unchanged line
                current_line += 1
                if deletion_start is not None:
                    modified_lines.append(deletion_start)
                    deletion_start = None

        # Handle case where deletion is at the end of the file
        if deletion_start is not None:
            modified_lines.append(deletion_start)

        return sorted(set(modified_lines))  # Remove duplicates and sort

    def process_file(self, file_path):
        """Process a file by checking its type, reading its content, and sending it
        to an API.

        This method constructs the absolute path of the specified file and
        verifies whether the file has a valid extension. If the file type is
        supported, it reads the content of the file and retrieves the
        differences from the last commit in the repository. If changes are
        detected, it sends the file content along with the modified lines to an
        API for further processing. If the API response indicates no changes,
        the original file will not be overwritten.

        Args:
            file_path (str): The relative path to the file to be processed.

        Returns:
            bool: True if the file was successfully processed and updated, False
                otherwise.
        """
        file_abs_path = os.path.join(self.repo_path, file_path)
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

        # Get the diff of the file in the last commit
        last_commit = self.repo.head.commit
        prev_commit = last_commit.parents[0] if last_commit.parents else last_commit

        # Use git command to get the diff
        diff_text = self.repo.git.diff(prev_commit.hexsha, last_commit.hexsha, '--', file_path)

        if not diff_text:
            print(f"No changes detected for {file_path}")
            return False

        modified_lines = self.get_modified_lines(diff_text)
        # Send data to API
        response = self.api_client.send_file_for_docstring_generation(file_path, content, modified_lines)
        if response is None:
            return False
        
        if response == content:
            print(f"No changes detected for {file_path}")
            return False
        # If the response is successful, replace the file content
        with open(file_abs_path, 'w') as file:
            file.write(response)
        return True

    def run(self):
        """Run the post-commit hook.

        This method retrieves the list of modified files from the last commit
        and processes each file. It stages any files that have been modified
        during processing and creates an auto-commit if changes were made. A
        progress bar is displayed to indicate the processing status of each
        file.  This function is designed to automate the handling of files that
        have been modified in the most recent commit. It ensures that any
        necessary changes are staged and committed automatically, providing a
        seamless workflow for developers. The use of a progress bar enhances
        user experience by visually indicating the progress of file processing.
        """
        modified_files = self.get_modified_files_in_last_commit()
        changes_made = False
        total_files = len(modified_files)

        with tqdm(total=total_files, desc="Processing files", unit="file", ncols=80, ascii=True) as pbar:
            for file in modified_files:
                try:
                    if self.process_file(file):
                        # Stage the modified file
                        self.repo.git.add(file)
                        changes_made = True
                except Exception as file_error:
                    print(f"Error processing file [{file}]: {file_error}")
                pbar.update(1)  # Update the progress bar

        # If any file was modified, create a new commit
        if changes_made:
            # self.repo.git.commit('-m', 'Auto-commit: Updated files after doc_gen_hook processing.')
            print("Auto-commit created with changes.")
        else:
            print("doc_gen_hook complete. No changes made.")