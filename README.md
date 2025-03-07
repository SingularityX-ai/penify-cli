# Penify CLI Tool

A CLI tool to generate Documentation, Commit-summary, and more.

## Installation

Install from PyPI:

```bash
pip install penifycli
```

## Usage

Penify CLI provides several subcommands for different functionalities:

### Login

To log in and obtain an API token:

```bash
penifycli login
```

This command will open a browser window for authentication. After successful login, the API key will be saved locally for future use.

### Install Git Hook

To install the Git post-commit hook:

```bash
penifycli install-hook -l /path/to/git/repo
```

- `-l, --location`: The path to the Git repository where you want to install the hook.

### Uninstall Git Hook

To uninstall the Git post-commit hook:

```bash
penifycli uninstall-hook -l /path/to/git/repo
```

- `-l, --location`: The path to the Git repository from which you want to uninstall the hook.

### Generate Documentation

To generate documentation for files or folders:

```bash
penifycli docgen [options]
```

Options:
- `-fl, --file_path`: Path to a specific file for which to generate documentation.
- `-cf, --complete_folder_path`: Path to a folder for which to generate documentation for all files.
- `-gf, --git_folder_path`: Path to a Git repository to generate documentation for modified files. Defaults to the current directory.

### Commit Code

To commit code with an automatically generated commit message:

```bash
penifycli commit -gf /path/to/git/repo [-m "Optional message"] [-e True/False]
```

- `-gf, --git_folder_path`: Path to the Git repository. Defaults to the current directory.
- `-m, --message`: Optional commit message. If not provided, a default message will be used.
- `-e, --terminal`: Set to "True" to open the terminal for editing the commit message. Defaults to "False".

### JIRA Integration

To integrate with JIRA and automate issue tracking:

```bash
penifycli jira [options]
```

Options:
- `-u, --url`: JIRA instance URL.
- `-p, --project`: JIRA project key.
- `-i, --issue`: JIRA issue key.
- `-a, --assignee`: Assignee for the JIRA issue.

## Authentication

Penify CLI uses an API token for authentication. The token is obtained and used in the following priority:

1. Command-line argument: `-t` or `--token`
2. Environment variable: `PENIFY_API_TOKEN`
3. Stored credentials: `~/.penify` file (created after successful login)

If no token is available, you'll be prompted to log in or provide a token.

## Environment Variables

- `PENIFY_API_TOKEN`: You can set this environment variable with your API token to avoid passing it as an argument each time.

## Development

To set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/SingularityX-ai/penify-cli.git
   ```

2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## License

This project is licensed under the MIT License.

## Author

Suman Saurabh (ss.sumansaurabh92@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any problems or have suggestions, please file an issue on the [GitHub repository](https://github.com/SingularityX-ai/penifycli/issues).

## Support

For automated API Documentation, Architecture Documentation, Code Documentation, Pull Request Documentation, or if you need a demo, please join our [Discord support channel](https://discord.gg/wqrc8JeV).