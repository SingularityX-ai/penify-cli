# penify-hook

`penify-hook` is a post-commit hook tool designed to help developers send modified files and their respective changes to a remote API for further processing.

## Features

- **Automated File Handling**: Automatically detects and processes modified files in the latest commit.
- **Modular API Interaction**: Interacts with a configurable API for handling file updates.
- **File Type Support Check**: Verifies whether the file types are supported by the API before processing.

## Installation

To install `penify-hook`, run:

```bash
pip install penify-hook
```

## Usage

`penify-hook` is designed to be used as a post-commit hook. It checks which files were modified in the latest commit, sends their content and modified line numbers to a configured API, and then replaces the existing files with the updated content returned by the API.

### Example Usage

Add `penify-hook` to your post-commit hook:

```bash
#!/bin/sh
penify-hook
```

Make sure to make your hook script executable:

```bash
chmod +x .git/hooks/post-commit
```

## Configuration

The API endpoint can be configured in the `PenifyHook` initialization:

```python
from penify_hook.hook import PenifyHook
from penify_hook.api import APIClient

api_client = APIClient(base_url="http://localhost:8000")
hook = PenifyHook(api_client)
hook.run_hook()
```

## License

This project is licensed under the MIT License.
```

### 5. Testing

To test the package, you can write tests in the `tests/` directory using `pytest` or any other testing framework.

### 6. Publishing to PyPI

1. Build the package:

    ```bash
    python setup.py sdist bdist_wheel
    ```

2. Upload to PyPI:

    ```bash
    twine upload dist/*
    ```

This is the basic outline for creating the `penify-hook` package and publishing it on PyPI. Make sure to replace placeholders like `your.email@example.com` and `yourusername` with your actual details.