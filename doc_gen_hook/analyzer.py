import os
from git import Repo
from .api_client import APIClient

class DocGenHook:
    def __init__(self, repo_path: str, api_url: str):
        self.repo_path = repo_path
        self.api_client = APIClient(api_url)
        self.repo = Repo(repo_path)

    def get_modified_files_in_last_commit(self):
        """Get the list of files modified in the last commit.

        This function retrieves the files that were modified in the most recent
        commit of the repository. It accesses the last commit and iterates
        through the differences between the last commit and its parent. The
        function collects the paths of modified files and returns them as a
        list.

        Returns:
            list: A list of file paths that were modified in the last commit.
        """
        last_commit = self.repo.head.commit
        modified_files = []
        for diff in last_commit.diff('HEAD~1'):
            if diff.a_path not in modified_files:
                modified_files.append(diff.a_path)
        return modified_files

    def get_modified_lines(self, diff):
        """Extract modified line numbers from a diff object.

        This function iterates through the hunks of a diff object and extracts
        the line numbers that have been modified. It identifies modified lines
        by checking for lines that start with a '+' character, excluding lines
        that indicate the addition of a new file (which start with '+++'). The
        resulting list contains all modified lines from the diff.

        Args:
            diff (Diff): A diff object containing hunks of changes.

        Returns:
            list: A list of strings representing the modified lines.
        """
        modified_lines = []
        for hunk in diff.hunks:
            for line in hunk:
                if line.startswith('+') and not line.startswith('+++'):
                    modified_lines.append(line)
        return modified_lines

    def process_file(self, file_path):
        """Process a file by reading its content, checking its support status, and
        sending it to an API.

        This function takes a file path, verifies if the file type is supported
        by the API client, reads the file content, retrieves the modified lines
        from the last commit, and sends the data to the API. If the API responds
        with a success status, it updates the file with the response content.

        Args:
            file_path (str): The relative path to the file to be processed.

        Returns:
            bool: True if the file was successfully processed and updated, False
                otherwise.
        """
        file_abs_path = os.path.join(self.repo_path, file_path)
        file_extension = os.path.splitext(file_path)[1].lower()

        if not self.api_client.is_file_supported(file_extension):
            print(f"File type {file_extension} is not supported. Skipping {file_path}.")
            return False

        with open(file_abs_path, 'r') as file:
            content = file.read()

        # Get the diff of the file in the last commit
        last_commit = self.repo.head.commit
        diffs = last_commit.diff('HEAD~1', paths=file_path)

        modified_lines = []
        for diff in diffs:
            modified_lines.extend(self.get_modified_lines(diff))

        # Send data to API
        response = self.api_client.send_to_api(file_path, content, modified_lines)
        
        # If the response is successful, replace the file content
        if response.status_code == 200:
            with open(file_abs_path, 'w') as file:
                file.write(response.text)
            return True

        return False

    def run(self):
        """Run the post-commit hook to process modified files.

        This method retrieves the list of files that were modified in the last
        commit and processes each file. If any file is modified during
        processing, it stages the file and creates a new commit with a
        predefined message. The method also provides feedback on whether any
        changes were made during the execution.
        """
        modified_files = self.get_modified_files_in_last_commit()
        changes_made = False

        for file in modified_files:
            if self.process_file(file):
                # Stage the modified file
                self.repo.git.add(file)
                changes_made = True

        # If any file was modified, create a new commit
        if changes_made:
            self.repo.git.commit('-m', 'Auto-commit: Updated files after doc_gen_hook processing.')
            print("Auto-commit created with changes.")

        print("doc_gen_hook complete. No changes made." if not changes_made else "Post-commit changes committed.")
