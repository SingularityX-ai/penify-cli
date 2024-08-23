# Post Commit Hook

`post_commit_hook` is a Python library designed to be used as a post-commit hook for Git repositories. It checks the modified files in the last commit, sends their content and modified lines to a specified API, and replaces the file content with the response received from the API.

## Features

- Identifies files modified in the last commit.
- Checks if the file type is supported by the API.
- Sends the file content and modified lines to an API endpoint.
- Replaces the file content with the API response.

## Installation

You can install `post_commit_hook` via pip:

```bash
pip install post_commit_hook
```

## Usage

1. **Setup Post-Commit Hook**: 

   Add the following script to your `.git/hooks/post-commit`:

   ```bash
   #!/bin/bash
   post-commit-hook /path/to/your/repo http://localhost:8000/api
   ```

   Make sure to replace `/path/to/your/repo` with the actual path to your Git repository.

2. **Run the Hook**:

   The hook will automatically run after each commit and process the modified files.

## Configuration

- **API URL**: The API URL should be provided during initialization. It should support the following endpoints:
  - `/supported_files`: To check supported file types.
  - `/analyze`: To analyze the file content and return the modified content.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### Step 5: Publish to PyPI

1. Ensure you have a `setup.py`, `README.md`, and `requirements.txt` in the project directory.
2. Register on [PyPI](https://pypi.org/) if you haven't already.
3. Build the package:

   ```bash
   python setup.py sdist bdist_wheel
   ```

4. Upload to PyPI:

   ```bash
   pip install twine
   twine upload dist/*
   ```

### Final Step: Set Up Post-Commit Hook

You can now install your package via pip and set it up as a post-commit hook for any repository.

This setup ensures that your library is modular, checks if file types are supported, and is packaged correctly for distribution on PyPI.