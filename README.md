# Penify CLI

Penify CLI is a tool that enhances your development workflow with AI-powered capabilities:

- Generate smart commit messages using local LLM models or cloud API
- Automatically create code documentation
- Integrate with JIRA for enhanced commit messages
- Install Git hooks for automated documentation generation

## Installation

```bash
pip install penifycli
```

## Authentication

Penify CLI supports two authentication methods:

### 1. Login to Penify Account (Required for Advanced Features)

```bash
penifycli login
```

This command will open your browser and prompt you to log in to your Penify account. Once authenticated, your API token will be saved locally.

### 2. Environment Variable

For CI/CD pipelines or automated environments, you can set:

```bash
export PENIFY_API_TOKEN=your_api_token
```

## Basic Usage

### Generate Smart Commit Messages

```bash
penifycli commit
```

### Generate Code Documentation

```bash
# Generate documentation for current Git diff (requires login)
penifycli docgen

# Generate documentation for a specific file
penifycli docgen -l path/to/file.py

# Generate documentation for a folder
penifycli docgen -l path/to/folder
```

### Configure Local LLM or JIRA

```bash
# Configure Local LLM for commit message generation
penifycli config llm

# Configure JIRA integration
penifycli config jira
```

### Automate Documentation with Git Hooks

```bash
# Install a post-commit hook
penifycli docgen install-hook

# Remove the hook
penifycli docgen uninstall-hook
```

## Getting Help

```bash
# Get general help
penifycli --help

# Get help for a specific command
penifycli commit --help
penifycli docgen --help
penifycli config --help
```

For detailed documentation and examples, see [docs/detailed-usage.md](docs/detailed-usage.md).