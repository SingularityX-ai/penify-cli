import subprocess
import re

class FileProcessor:
    @staticmethod
    def get_staged_files_with_changes(supported_file_types: list[str]):
        """Get the list of staged files with their modified line numbers."""
        result = subprocess.run(['git', 'diff', '--cached', '--unified=0'], stdout=subprocess.PIPE)
        diff_output = result.stdout.decode('utf-8')
        supported_file_types_set = set(supported_file_types)

        files_with_changes = {}
        current_file = None

        for line in diff_output.splitlines():
            if line.startswith('diff --git'):
                current_file = re.search(r'(?<= b/).*$', line).group(0)
                if current_file.split('.')[-1] not in supported_file_types_set:
                    continue
                files_with_changes[current_file] = []
            elif line.startswith('@@'):
                line_numbers = re.search(r'\+(\d+)(?:,(\d+))?', line)
                if line_numbers:
                    start_line = int(line_numbers.group(1))
                    num_lines = int(line_numbers.group(2)) if line_numbers.group(2) else 1
                    files_with_changes[current_file].extend(range(start_line, start_line + num_lines))

        return files_with_changes

    @staticmethod
    def read_file_content(file_path):
        """Read the content of a file."""
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def write_file_content(file_path, content):
        """Write modified content back to the file."""
        with open(file_path, 'w') as file:
            file.write(content)
