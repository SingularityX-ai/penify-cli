# Penify CLI - Detailed Usage Guide

This document provides in-depth information about all features and capabilities of the Penify CLI tool.

## Table of Contents

- [Penify CLI - Detailed Usage Guide](#penify-cli---detailed-usage-guide)
  - [Table of Contents](#table-of-contents)
  - [Authentication](#authentication)
    - [Login Process](#login-process)
    - [API Token Storage](#api-token-storage)
    - [Token Precedence](#token-precedence)
  - [Command Overview](#command-overview)
  - [Commit Message Generation](#commit-message-generation)
  - [Code Documentation Generation](#code-documentation-generation)
    - [Use Cases](#use-cases)
    - [Authentication Requirement](#authentication-requirement)
  - [Configuration Settings](#configuration-settings)
  - [Git Hooks](#git-hooks)
    - [Post-Commit Hook](#post-commit-hook)
    - [Custom Hook Location](#custom-hook-location)
  - [Advanced Use Cases](#advanced-use-cases)
    - [CI/CD Integration](#cicd-integration)
    - [Remote Repository Documentation](#remote-repository-documentation)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Logs](#logs)
    - [Support](#support)

## Authentication

### Login Process

When you run `penifycli login`, the tool:

1. Opens your default web browser
2. Redirects you to Penify's login page
3. Captures the authentication token after successful login
4. Saves the token in `~/.penify` file

### API Token Storage

API tokens are stored in your home directory in the `.penify` file. This JSON file contains:

```json
{
  "api_keys": "your-api-token",
  "llm": { "model": "...", "api_base": "...", "api_key": "..." },
  "jira": { "url": "...", "username": "...", "api_token": "..." }
}
```

### Token Precedence

1. Environment variable `PENIFY_API_TOKEN` (highest priority)
2. Token in `~/.penify` file

## Command Overview

```
penifycli
├── commit        Generate smart commit messages
├── config        Configure local LLM and JIRA
│   ├── llm       Configure local LLM settings
│   └── jira      Configure JIRA integration
├── login         Log in to Penify account
└── docgen        Generate code documentation
    ├── install-hook     Install Git post-commit hook
    └── uninstall-hook   Remove Git post-commit hook
```

## Commit Message Generation

The `commit` command analyzes your staged changes and generates meaningful commit messages. It can:

- Use a local LLM if configured
- Enhance messages with JIRA issue details
- Provide both title and description

For specific options and examples, see [docs/commit-commands.md](commit-commands.md).

## Code Documentation Generation

The `docgen` command generates documentation for your code:

### Use Cases

1. **Current Git Diff**: Default behavior, documents only changed files
2. **Specific File**: Pass a file path with `-l path/to/file.py`
3. **Entire Folder**: Pass a folder path with `-l path/to/folder`

### Authentication Requirement

This feature requires authentication with a Penify account. Run `penifycli login` before using documentation features.

## Configuration Settings

Configure local settings using the `config` command:

- **LLM Settings**: Configure a local LLM for commit message generation
- **JIRA Settings**: Set up JIRA integration for enhanced commit messages

For detailed configuration options, see [docs/config-commands.md](config-commands.md).

## Git Hooks

Penify can install Git hooks to automate documentation generation:

### Post-Commit Hook

- **Install**: `penifycli docgen install-hook`
- **What it does**: Automatically generates documentation for changed files after each commit
- **Uninstall**: `penifycli docgen uninstall-hook`

### Custom Hook Location

You can specify a custom location for Git hooks:

```bash
penifycli docgen install-hook -l /path/to/git/repo
```

## Advanced Use Cases

### CI/CD Integration

For CI/CD pipelines:

1. Set `PENIFY_API_TOKEN` as an environment variable
2. Run commands without requiring interactive login

### Remote Repository Documentation

Generate documentation for an entire repository:

```bash
git clone https://github.com/user/repo
cd repo
penifycli docgen -l .
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure you've run `penifycli login` or set `PENIFY_API_TOKEN`
2. **LLM Configuration**: Check your LLM settings with `cat ~/.penify`
3. **JIRA Integration**: Verify JIRA credentials in your configuration

### Logs

For more detailed logs, you can set the environment variable:

```bash
export PENIFY_DEBUG=1
```

### Support

For additional help, visit [https://docs.penify.dev/](https://docs.penify.dev/) or contact support@penify.dev
