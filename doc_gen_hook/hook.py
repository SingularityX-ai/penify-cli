import os
from git import Repo
from .api import APIClient

class PostCommitHook:
    def __init__(self, repo_path: str, api_url: str):
        self.repo_path = repo_path
        self.api_client = APIClient(api_url)
        self.repo = Repo(repo_path)

    def get_modified_files_in_last_commit(self):
        """Get the list of files modified in the last commit."""
        last_commit = self.repo.head.commit
        modified_files = []
        for diff in last_commit.diff('HEAD~1'):
            if diff.a_path not in modified_files:
                modified_files.append(diff.a_path)
        return modified_files

    def get_modified_lines(self, diff):
        """Extract modified line numbers from a diff object."""
        modified_lines = []
        for hunk in diff.hunks:
            for line in hunk:
                if line.startswith('+') and not line.startswith('+++'):
                    modified_lines.append(line)
        return modified_lines

    def process_file(self, file_path):
        """Read the file, check if it's supported, and send it to the API."""
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
            self.repo.git.commit('-m', 'Auto-commit: Updated files after post-commit hook processing.')

if __name__ == "__main__":
    repo_path = '/path/to/your/repo'
    api_url = 'http://localhost:8000/api'
    post_commit_hook = PostCommitHook(repo_path, api_url)
    post_commit_hook.run()
