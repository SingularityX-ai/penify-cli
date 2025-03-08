---
layout: doc
title: Streamline Git Commits and Code Documentation with Penify-CLI's Automated Generation
description: Discover how Penify-CLI automates both Git commit messages and code documentation, with Jira integration and flexible options. Save time, improve repository clarity, and boost productivity with this detailed guide to usage and best practices.
keywords: Penify-CLI, Git commit messages, code documentation, Jira integration, automated documentation, version control, repository management, developer productivity
author: Suman Sauarbh
---
# Penify CLI Documentation

Penify CLI is a powerful tool for enhancing your development workflow with AI-powered features like commit message generation, code documentation, and JIRA integration.

## Installation

```bash
pip install penifycli
```

## Getting Started

After installation, you can check the version of Penify CLI:

```bash
penifycli --version
```

## Commands Overview

- `commit`: Generate smart commit messages using local-LLM
- `config`: Configure local-LLM and JIRA settings
- `login`: Log in to Penify to use advanced features
- `docgen`: Generate code documentation for Git diffs, files, or folders

## Detailed Command Documentation

### Commit Command

The `commit` command generates intelligent commit messages using local LLM models or Penify services.

#### Usage:

```bash
penifycli commit [options]
```

#### Options:

- `-m, --message TEXT`: Provide context for the commit message generation
- `-e, --terminal`: Open an editor to modify the generated commit message before applying it
- `-d, --description`: Generate a detailed commit message with both title and description

#### Examples:

**Basic usage:**
```bash
penifycli commit
```

**Provide context for better results:**
```bash
penifycli commit -m "Fixed the login button"
```

**Generate a detailed commit message and open editor:**
```bash
penifycli commit -e -d
```

#### Requirements:

- Either a local LLM configuration (via `penifycli config llm`) or Penify login
- For JIRA integration, configure JIRA settings (via `penifycli config jira`)

---

### Config Command

The `config` command helps you configure local LLM settings and JIRA integration for enhanced commit messages.

#### Usage:

```bash
penifycli config [subcommand]
```

#### Subcommands:

- `llm`: Configure local Large Language Model settings
- `jira`: Configure JIRA integration settings

#### Examples:

**Configure local LLM:**
```bash
penifycli config llm
```
This opens a web interface to configure:
- Model name (e.g., gpt-3.5-turbo, llama2)
- API base URL (e.g., https://api.openai.com/v1)
- API key

**Configure JIRA integration:**
```bash
penifycli config jira
```
This opens a web interface to configure:
- JIRA URL (e.g., https://your-domain.atlassian.net)
- Username (typically your email)
- API token

---

### Login Command

The `login` command authenticates you with Penify for advanced features like code documentation generation.

#### Usage:

```bash
penifycli login
```

#### What happens:
1. A browser window opens to the Penify login page
2. After successful login, your API key is automatically saved
3. The tool is now authorized to use Penify's advanced features

#### Example:

```bash
penifycli login
```

---

### Docgen Command

The `docgen` command generates documentation for your code using Penify's AI services.

#### Usage:

```bash
penifycli docgen [options] [subcommand]
```

#### Options:

- `-l, --location PATH`: Path to a specific file or folder to document (default: current working directory)

#### Subcommands:

- `install-hook`: Install a Git post-commit hook to automatically generate documentation
- `uninstall-hook`: Remove the Git post-commit hook

#### Examples:

**Document current Git diff:**
```bash
penifycli docgen
```

**Document a specific file:**
```bash
penifycli docgen -l src/main.py
```

**Document an entire folder:**
```bash
penifycli docgen -l src/components
```

**Install the Git hook for automatic documentation:**
```bash
penifycli docgen install-hook
```

**Uninstall the Git hook:**
```bash
penifycli docgen uninstall-hook
```

#### Requirements:

- Requires login to Penify (`penifycli login`)

## Configuration Files

Penify CLI stores configuration in the following locations:

- Global configuration: `~/.penify`
- Project-specific configuration: `.penify` in your Git repository root

## Environment Variables

- `PENIFY_API_TOKEN`: Can be used to provide the API token instead of logging in

## Troubleshooting

If you encounter issues:

1. Check your configuration with `cat ~/.penify`
2. Verify network connectivity to API endpoints
3. Ensure your API keys and tokens are valid
4. For JIRA integration issues, verify your JIRA credentials

## Additional Resources

For more information, visit the [Penify Documentation](https://docs.penify.dev/).
