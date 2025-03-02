import re
import logging
from typing import Optional, Dict, List, Any
try:
    from jira import JIRA
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    
class JiraClient:
    """
    Client for interacting with JIRA API
    """
    
    def __init__(self, jira_url: str = None, jira_user: str = None, jira_api_token: str = None):
        """
        Initialize the JIRA client.
        
        Args:
            jira_url: Base URL for JIRA instance (e.g., "https://your-domain.atlassian.net")
            jira_user: JIRA username or email
            jira_api_token: JIRA API token
        """
        self.jira_url = jira_url
        self.jira_user = jira_user
        self.jira_api_token = jira_api_token
        self.jira_client = None
        
        if not JIRA_AVAILABLE:
            logging.warning("JIRA package not available. JIRA integration will not work.")
            return
        
        if jira_url and jira_user and jira_api_token:
            try:
                self.jira_client = JIRA(
                    server=jira_url,
                    basic_auth=(jira_user, jira_api_token)
                )
                logging.info("JIRA client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize JIRA client: {e}")
                self.jira_client = None
    
    def is_connected(self) -> bool:
        """
        Check if the JIRA client is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.jira_client is not None
    
    def extract_issue_keys(self, text: str) -> List[str]:
        """
        Extract JIRA issue keys from text.
        
        Args:
            text: Text to search for JIRA issue keys
            
        Returns:
            List of JIRA issue keys found
        """
        # Common JIRA issue key pattern: PROJECT-123
        pattern = r'[A-Z][A-Z0-9_]+-[0-9]+'
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def get_issue_details(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a JIRA issue.
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJECT-123")
            
        Returns:
            Dict with issue details or None if not found
        """
        if not self.is_connected():
            logging.warning("JIRA client not connected")
            return None
        
        try:
            issue = self.jira_client.issue(issue_key)
            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'description': issue.fields.description,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                'type': issue.fields.issuetype.name,
                'priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else None,
                'url': f"{self.jira_url}/browse/{issue.key}"
            }
        except Exception as e:
            logging.error(f"Error fetching issue {issue_key}: {e}")
            return None
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to a JIRA issue.
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJECT-123")
            comment: Comment text to add
            
        Returns:
            bool: True if comment was added successfully, False otherwise
        """
        if not self.is_connected():
            logging.warning("JIRA client not connected")
            return False
        
        try:
            self.jira_client.add_comment(issue_key, comment)
            logging.info(f"Comment added to {issue_key}")
            return True
        except Exception as e:
            logging.error(f"Error adding comment to {issue_key}: {e}")
            return False
    
    def update_issue_status(self, issue_key: str, transition_name: str) -> bool:
        """
        Update the status of a JIRA issue.
        
        Args:
            issue_key: JIRA issue key (e.g., "PROJECT-123")
            transition_name: Name of the transition (e.g., "In Progress", "Done")
            
        Returns:
            bool: True if status was updated successfully, False otherwise
        """
        if not self.is_connected():
            logging.warning("JIRA client not connected")
            return False
        
        try:
            # Get available transitions
            transitions = self.jira_client.transitions(issue_key)
            
            # Find the transition ID based on name
            transition_id = None
            for t in transitions:
                if t['name'].lower() == transition_name.lower():
                    transition_id = t['id']
                    break
            
            if transition_id:
                self.jira_client.transition_issue(issue_key, transition_id)
                logging.info(f"Updated {issue_key} status to {transition_name}")
                return True
            else:
                logging.warning(f"Transition '{transition_name}' not found for {issue_key}")
                return False
                
        except Exception as e:
            logging.error(f"Error updating status for {issue_key}: {e}")
            return False
            
    def format_commit_message_with_jira_info(self, commit_title: str, commit_description: str, issue_keys: List[str] = None) -> tuple:
        """
        Format commit message with JIRA issue information.
        
        Args:
            commit_title: Original commit title
            commit_description: Original commit description
            issue_keys: List of JIRA issue keys to include (optional, will extract from title/description if not provided)
            
        Returns:
            tuple: (updated_title, updated_description) with JIRA information included
        """
        # If no issue keys provided, extract them from title and description
        if not issue_keys:
            title_keys = self.extract_issue_keys(commit_title)
            desc_keys = self.extract_issue_keys(commit_description)
            issue_keys = list(set(title_keys + desc_keys))
            
        if not issue_keys or not self.is_connected():
            return commit_title, commit_description
            
        # Format the title to include the issue key if not already there
        updated_title = commit_title
        if issue_keys and not any(key in commit_title for key in issue_keys):
            # Add the first issue key to the title
            updated_title = f"{issue_keys[0]}: {commit_title}"
            
        # Add issue details to the description
        updated_description = commit_description
        
        issue_details_section = "\n\n## Related JIRA Issues\n\n"
        has_issue_details = False
        
        for issue_key in issue_keys:
            details = self.get_issue_details(issue_key)
            if details:
                has_issue_details = True
                issue_details_section += (
                    f"* **[{details['key']}]({details['url']})**: {details['summary']}\n"
                    f"  * Status: {details['status']}\n"
                    f"  * Type: {details['type']}\n"
                )
                
        if has_issue_details:
            updated_description += issue_details_section
            
        return updated_title, updated_description
