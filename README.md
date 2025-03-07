# Penify CLI Tool

A CLI tool to generate smart commit messages, code documentation, and more.

## Installation

Install from PyPI:

```bash
pip install penifycli
```

## Usage

Penify CLI provides several subcommands for different functionalities, organized into basic commands (no login required) and advanced commands (login required).

## Basic Commands (No login required)

### Commit

Generate smart commit messages using local LLM:

```bash
penifycli commit [-m "Optional message"] [-e] [-d]
```

Options:
- `-m, --message`: Optional custom commit message
- `-e, --terminal`: Open editor to modify commit message before committing
- `-d, --description`: Generate commit message with both title and description (without this flag, only title is generated)

### Config

Configure local LLM and JIRA settings:

```bash
# Configure LLM settings
penifycli config llm --model MODEL_NAME [--api-base API_URL] [--api-key API_KEY]

# Configure LLM settings through web interface
penifycli config llm-web

# Configure JIRA settings
penifycli config jira --url JIRA_URL --username USERNAME --api-token TOKEN [--verify]

# Configure JIRA settings through web interface
penifycli config jira-web
```

## Advanced Commands (Login required)

### Login

To log in and obtain an API token:

```bash
penifycli login
```

This command will open a browser window for authentication. After successful login, the API key will be saved locally for future use.

### Documentation Generation

Generate documentation for Git diff, files or folders:

```bash
# Generate documentation for latest Git commit diff
penifycli docgen

# Generate documentation for specific file or folder
penifycli docgen -l /path/to/file/or/folder
```

Options:
- `-l, --location`: Path to specific file or folder for documentation generation (defaults to current directory)

### Git Hook Management

Install or uninstall Git post-commit hooks:

```bash
# Install Git hook
penifycli docgen install-hook [-l /path/to/repo]

# Uninstall Git hook
penifycli docgen uninstall-hook [-l /path/to/repo]
```

Options:
- `-l, --location`: Path to the Git repository (defaults to current directory)

## Authentication

Penify CLI uses an API token for authentication with advanced features.

If no token is available and you try to access an advanced feature, you'll be prompted to log in.

## Local LLM Configuration

For commit message generation, Penify can use a local LLM. Configure it using:

```bash
penifycli config llm --model MODEL_NAME --api-base API_URL --api-key API_KEY
```

Common configurations:
- OpenAI: `--model gpt-3.5-turbo --api-base https://api.openai.com/v1 --api-key YOUR_KEY`
- Anthropic: `--model claude-2 --api-base https://api.anthropic.com --api-key YOUR_KEY`

## JIRA Integration

Configure JIRA integration to enhance commit messages with issue details:

```bash
penifycli config jira --url https://your-domain.atlassian.net --username your-email@example.com --api-token YOUR_API_TOKEN
```

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