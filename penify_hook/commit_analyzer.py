import os
import re
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
        """
        Get the details of the repository, including the hosting service (e.g., GitHub, Azure DevOps),
        organization name, and repository name.

        This method checks the remote URL of the repository to determine whether it is hosted on
        GitHub, Azure DevOps, or another service. It also extracts the organization (or user) name
        and the repository name from the URL.

        Returns:
            dict: A dictionary containing the hosting service, organization name, repository name, and remote URL.
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
        diff = self.repo.git.diff('--cached')
        if not diff:
            raise Exception("No changes to commit")
        return self.api_client.generate_commit_summary(diff, instruction, self.repo_details)
    
   
    def run(self, msg: Optional[str]):
        """Run the post-commit hook.

        This method retrieves the list of modified files from the last commit
        and processes each file. It stages any files that have been modified
        during processing and creates an auto-commit if changes were made. A
        progress bar is displayed to indicate the processing status of each
        file. If there is an error generating the commit summary, an exception
        is raised.

        Args:
            msg (Optional[str]): An optional message to include in the commit.

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
        print(f"Committing changes with message:\n {commit_msg}")
        self.repo.git.commit('-m', commit_msg)
        