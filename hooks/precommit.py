# hooks/precommit.py

import subprocess
import sys
import os

def get_staged_files():
    """Get the list of staged files."""
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], stdout=subprocess.PIPE)
    files = result.stdout.decode('utf-8').splitlines()
    return files

def run_checks(files):
    """Run checks on the staged files."""
    for file in files:
        if file.endswith('.py'):
            print(f"Checking {file}")
            result = subprocess.run(['flake8', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(result.stdout.decode('utf-8'))
                print(result.stderr.decode('utf-8'))
                print("Commit aborted due to linter errors.")
                sys.exit(1)

def main():
    print("Running pre-commit checks...")
    staged_files = get_staged_files()
    run_checks(staged_files)
    print("All checks passed. Proceeding with commit.")

if __name__ == "__main__":
    main()
