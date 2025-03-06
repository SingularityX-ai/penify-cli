import os
from git import Repo
from .api_client import APIClient
from penify_hook.utils import get_repo_details, recursive_search_git_folder


class BaseAnalyzer:
    
    def __init__(self, folder_path: str, api_client: APIClient):
        self.folder_path = folder_path
        self.repo_path = recursive_search_git_folder(folder_path)
        self.repo = None
        self.repo_details = None
        if self.folder_path:
            self.repo = Repo(self.repo_path)
            self.repo_details = get_repo_details(self.repo)

        self.relative_file_path = os.path.relpath(folder_path)
        self.api_client = api_client
        self.supported_file_types = set(api_client.get_supported_file_types())