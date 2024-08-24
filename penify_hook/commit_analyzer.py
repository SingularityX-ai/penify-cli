import os
import re
import subprocess
import tempfile
from typing import Optional
from git import Repo
from tqdm import tqdm
from .api_client import APIClient

class CommitDocGenHook:
    def __init__(self, repo_path: str, api_client: APIClient):
        self.repo_path = repo_path
        self.api_client = api_client
        self.repo = Repo(repo_path)
        self.supported_file_types = set(self.api_client.get_supported_file_types())
        self.repo_details = self.get_repo_details()

    def get_repo_details(self):
        """Get the details of the repository, including the hosting service,
        organization name, and repository name.

        This method checks the remote URL of the repository to determine whether
        it is hosted on GitHub, Azure DevOps, Bitbucket, GitLab, or another
        service. It extracts the organization (or user) name and the repository
        name from the URL. If the hosting service is not recognized, it will
        return "Unknown Hosting Service". The method handles potential errors
        during the extraction process and returns a dictionary with the relevant
        details.

        Returns:
            dict: A dictionary containing the organization name, repository name, and
                hosting service.
        """
        remote_url = None
        hosting_service = "Unknown"
        org_name = None
        repo_name = None

        try:
            # Get the remote URL
            remote = self.repo.remotes.origin.url
            remote_url = remote

            # Determine the hosting service based on the URL
            if "github.com" in remote:
                hosting_service = "GITHUB"
                match = re.match(r".*github\.com[:/](.*?)/(.*?)(\.git)?$", remote)
            elif "dev.azure.com" in remote:
                hosting_service = "AZUREDEVOPS"
                match = re.match(r".*dev\.azure\.com/(.*?)/(.*?)/_git/(.*?)(\.git)?$", remote)
            elif "visualstudio.com" in remote:
                hosting_service = "AZUREDEVOPS"
                match = re.match(r".*@(.*?)\.visualstudio\.com/(.*?)/_git/(.*?)(\.git)?$", remote)
            elif "bitbucket.org" in remote:
                hosting_service = "BITBUCKET"
                match = re.match(r".*bitbucket\.org[:/](.*?)/(.*?)(\.git)?$", remote)
            elif "gitlab.com" in remote:
                hosting_service = "GITLAB"
                match = re.match(r".*gitlab\.com[:/](.*?)/(.*?)(\.git)?$", remote)
            else:
                hosting_service = "Unknown Hosting Service"
                match = None

            if match:
                org_name = match.group(1)
                repo_name = match.group(2)
                
                # For Azure DevOps, adjust the group indices
                if hosting_service == "AZUREDEVOPS":
                    repo_name = match.group(3)

        except Exception as e:
            print(f"Error determining repo details: {e}")

        return {
            "organization_name": org_name,
            "repo_name": repo_name,
            "vendor": hosting_service
        }

    def get_summary(self, instruction: str):
        """Generate a summary for the commit based on the staged changes.

        This function retrieves the differences of the staged changes in the
        repository and generates a commit summary using the provided
        instruction. If there are no changes staged for commit, an exception is
        raised.

        Args:
            instruction (str): A string containing instructions for generating the commit summary.

        Returns:
            str: The generated commit summary based on the staged changes and provided
                instruction.

        Raises:
            Exception: If there are no changes staged for commit.
        """

        diff = self.repo.git.diff('--cached')
        if not diff:
            raise Exception("No changes to commit")
        return self.api_client.generate_commit_summary(diff, instruction, self.repo_details)
    
   
    def run(self, msg: Optional[str], edit_commit_message: bool):
        """Run the post-commit hook.

        This method retrieves the list of modified files from the last commit
        and processes each file. It stages any files that have been modified
        during processing and creates an auto-commit if changes were made. A
        progress bar is displayed to indicate the processing status of each
        file. If there is an error generating the commit summary, an exception
        is raised.

        Args:
            msg (Optional[str]): An optional message to include in the commit.
            edit_commit_message (bool): A flag indicating whether to open the
                git commit edit terminal after committing.

        Raises:
            Exception: If there is an error generating the commit summary.
        """
        summary: dict = self.get_summary(msg)
        if not summary:
            raise Exception("Error generating commit summary")
        title = summary.get('title', "")
        description = summary.get('description', "")

        # commit the changes to the repository with above details
        commit_msg = f"{title}\n\n{description}"
        self.repo.git.commit('-m', commit_msg)
        if edit_commit_message:
            # Open the git commit edit terminal
            print("Opening git commit edit terminal...")
            self._amend_commit()
        

    def _amend_commit(self):
        """Open the default git editor for editing the commit message.

        This function changes the current working directory to the repository
        path, runs the git command to amend the last commit, and opens the
        default editor for the user to modify the commit message. After the
        operation, it returns to the original directory.
        """
        try:
            # Change to the repository directory
            os.chdir(self.repo_path)
            
            # Run git commit --amend
            subprocess.run(['git', 'commit', '--amend'], check=True)
            
            print("Commit message amended successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error amending commit message: {e}")
        finally:
            # Change back to the original directory
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        