import os
from git import Repo
from .api_client import APIClient

class DocGenHook:
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

    def get_modified_lines(self, diff):
        """Extract modified line numbers from a diff object."""
        modified_lines = []
        diff_data = diff.diff.decode('utf-8')  # Decode the diff data to a string

        for line in diff_data.splitlines():
            if line.startswith('@@'):
                # The hunk header looks like: @@ -12,7 +12,7 @@
                parts = line.split(' ')
                new_line_info = parts[2]  # The new file line info is the third part
                line_start = int(new_line_info[1:].split(',')[0])
                num_lines = int(new_line_info.split(',')[1]) if ',' in new_line_info else 1

                # Add the range of modified line numbers
                modified_lines.extend(range(line_start, line_start + num_lines))

        return modified_lines

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
        diffs = last_commit.diff('HEAD~1', paths=file_path)

        modified_lines = []
        for diff in diffs:
            print(f"Processing diff for {file_path}")
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
            self.repo.git.commit('-m', 'Auto-commit: Updated files after doc_gen_hook processing.')
            print("Auto-commit created with changes.")
        else:
            print("doc_gen_hook complete. No changes made.")

