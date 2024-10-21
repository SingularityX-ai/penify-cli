import os

class GitRepoNotFoundError(Exception):
    pass

def find_git_parent(path):
    """Find the parent directory of a Git repository.

    This function traverses up the directory structure from the given path
    to locate the nearest parent directory that contains a `.git` folder. If
    such a directory is found, it returns the path to that directory. If no
    Git repository is found in the specified path or any of its parent
    directories, it raises a custom exception.

    Args:
        path (str): The path from which to start searching for the Git repository.

    Returns:
        str: The absolute path to the parent directory containing the `.git` folder.

    Raises:
        GitRepoNotFoundError: If no Git repository is found in the specified path or any
    """

    current_dir = os.path.abspath(path)

    while current_dir != os.path.dirname(current_dir):  # Traverse up to the root directory
        if os.path.isdir(os.path.join(current_dir, ".git")):
            return current_dir  # Return the parent folder containing the .git directory
        current_dir = os.path.dirname(current_dir)
    
    raise GitRepoNotFoundError(f"No Git repository found in the path or any of its parent directories: {path}")
