import os
from git import Repo
from .api_client import APIClient

class GitDocGenHook:
    def __init__(self, repo_path: str, api_client: APIClient):
        self.repo_path = repo_path
        self.api_client = api_client
        self.repo = Repo(repo_path)
        self.supported_file_types = set(self.api_client.get_supported_file_types())

    def get_modified_files_in_last_commit(self):
        """Get the list of files modified in the last commit."""
        last_commit = self.repo.head.commit
        modified_files = []
        for diff in last_commit.diff('HEAD~1'):
            if diff.a_path not in modified_files:
                modified_files.append(diff.a_path)
        return modified_files

    def get_modified_lines(self, diff_text):
        """Extract modified line numbers from a diff text."""
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
        """Read the file, check if it's supported, and send it to the API."""
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
        """Run the post-commit hook."""
        modified_files = self.get_modified_files_in_last_commit()
        changes_made = False

        for file in modified_files:
            if self.process_file(file):
                # Stage the modified file
                self.repo.git.add(file)
                changes_made = True

        # If any file was modified, create a new commit
        if changes_made:
            # self.repo.git.commit('-m', 'Auto-commit: Updated files after doc_gen_hook processing.')
            print("Auto-commit created with changes.")
        else:
            print("doc_gen_hook complete. No changes made.")