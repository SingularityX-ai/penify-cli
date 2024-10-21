import os

class GitRepoNotFoundError(Exception):
    pass

def find_git_parent(path):
    current_dir = os.path.abspath(path)

    while current_dir != os.path.dirname(current_dir):  # Traverse up to the root directory
        if os.path.isdir(os.path.join(current_dir, ".git")):
            return current_dir  # Return the parent folder containing the .git directory
        current_dir = os.path.dirname(current_dir)
    
    raise GitRepoNotFoundError(f"No Git repository found in the path or any of its parent directories: {path}")
