import os
import re
import subprocess
import tempfile
from typing import Optional, List
from git import Repo
from tqdm import tqdm

from penify_hook.base_analyzer import BaseAnalyzer
from .api_client import APIClient

class CommitDocGenHook(BaseAnalyzer):
    def __init__(self, repo_path: str, api_client: APIClient, llm_client=None, jira_client=None):
        super().__init__(repo_path, api_client)

        self.llm_client = llm_client  # Add LLM client as an optional parameter
        self.jira_client = jira_client  # Add JIRA client as an optional parameter

    def get_summary(self, instruction: str, generate_description: bool) -> dict:
        """Generate a summary for the commit based on the staged changes.

        This function retrieves the differences of the staged changes in the
        repository and generates a commit summary using the provided
        instruction. If there are no changes staged for commit, an exception is
        raised. If an LLM client is provided, it will use that for generating
        the summary, otherwise it will use the API client.

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
            raise ValueError("No changes to commit")
        
        # Get JIRA context if available
        jira_context = None
        if self.jira_client and self.jira_client.is_connected():
            try:
                # Check branch name for JIRA issues
                current_branch = self.repo.active_branch.name
                issue_keys = self.jira_client.extract_issue_keys_from_branch(current_branch)
                
                # If issues found in branch, get context
                if issue_keys:
                    jira_context = self.jira_client.get_commit_context_from_issues(issue_keys)
                    print(f"Adding JIRA context from issues: {', '.join(issue_keys)}")
            except Exception as e:
                print(f"Could not get JIRA context: {e}")
        
        # Use LLM client if provided, otherwise use API client
        if self.llm_client:
            return self.api_client.generate_commit_summary_with_llm(
                diff, instruction, generate_description, self.repo_details, self.llm_client, jira_context
            )
        else:
            return self.api_client.generate_commit_summary(diff, instruction, self.repo_details, jira_context)
    
   
    def run(self, msg: Optional[str], edit_commit_message: bool, generate_description: bool):
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
        summary: dict = self.get_summary(msg, generate_description)
        if not summary:
            raise Exception("Error generating commit summary")
        
        title = summary.get('title', "")
        description = summary.get('description', "")
        
        # If JIRA client is available, integrate JIRA information
        if self.jira_client and self.jira_client.is_connected():
            # Add JIRA information to commit message
            title, description = self.process_jira_integration(title, description, msg)
            
        # commit the changes to the repository with above details
        commit_msg = f"{title}\n\n{description}"
        self.repo.git.commit('-m', commit_msg)
        
        if edit_commit_message:
            # Open the git commit edit terminal
            print("Opening git commit edit terminal...")
            self._amend_commit()
    
    def process_jira_integration(self, title: str, description: str, msg: str) -> tuple:
        """
        Process JIRA integration for the commit message.
        
        Args:
            title: Generated commit title
            description: Generated commit description 
            msg: Original user message that might contain JIRA references
            
        Returns:
            tuple: (updated_title, updated_description) with JIRA information
        """
        # Look for JIRA issue keys in commit message, title, description and user message
        issue_keys = []
        if self.jira_client:
            # Extract from message content
            issue_keys = self.jira_client.extract_issue_keys(f"{title} {description} {msg}")
            
            # Also check the branch name (which often follows JIRA naming conventions)
            try:
                current_branch = self.repo.active_branch.name
                branch_issue_keys = self.jira_client.extract_issue_keys_from_branch(current_branch)
                
                # Add any new keys found in branch name
                for key in branch_issue_keys:
                    if key not in issue_keys:
                        issue_keys.append(key)
                        print(f"Added JIRA issue {key} from branch name: {current_branch}")
            except Exception as e:
                print(f"Could not extract JIRA issues from branch name: {e}")
            
            if issue_keys:
                print(f"Found JIRA issues: {', '.join(issue_keys)}")
                
                # Format commit message with JIRA info
                title, description = self.jira_client.format_commit_message_with_jira_info(
                    title, description, issue_keys
                )
                
                # Add comments to JIRA issues
                for issue_key in issue_keys:
                    comment = (
                        f"Commit related to this issue:\n\n"
                        f"**{title}**\n\n"
                        f"{description}\n\n"
                        f"Repository: {self.repo_details.get('organization_name')}/{self.repo_details.get('repo_name')}"
                    )
                    self.jira_client.add_comment(issue_key, comment)
            else:
                print("No JIRA issues found in commit message or branch name")
                
        return title, description

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
