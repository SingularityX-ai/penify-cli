import subprocess
import re
import sys

def get_staged_files_with_changes():
    """Get the list of staged files with their modified line numbers."""
    result = subprocess.run(['git', 'diff', '--cached', '--unified=0'], stdout=subprocess.PIPE)
    diff_output = result.stdout.decode('utf-8')
    
    files_with_changes = {}
    current_file = None

    for line in diff_output.splitlines():
        if line.startswith('diff --git'):
            current_file = re.search(r'(?<= b/).*$', line).group(0)
            files_with_changes[current_file] = []
        elif line.startswith('@@'):
            line_numbers = re.search(r'\+(\d+)(?:,(\d+))?', line)
            if line_numbers:
                start_line = int(line_numbers.group(1))
                num_lines = int(line_numbers.group(2)) if line_numbers.group(2) else 1
                files_with_changes[current_file].extend(range(start_line, start_line + num_lines))
    
    return files_with_changes

def run_docstring_generation(files_with_changes):
    """Generate docstrings for the modified lines in the staged files."""
    for file, line_numbers in files_with_changes.items():
        print(f"Generating docstrings for {file} at lines {line_numbers}")
        # Example: Placeholder for docstring generation logic
        # You would call your docstring generation tool or function here
        # For demonstration, we just print the file and lines
        # Implement actual docstring generation logic here

def main():
    print("Running pre-commit docstring generation...")
    staged_files_with_changes = get_staged_files_with_changes()
    if staged_files_with_changes:
        run_docstring_generation(staged_files_with_changes)
    else:
        print("No changes detected in staged files.")
    print("Pre-commit hook completed.")

if __name__ == "__main__":
    main()
