# Penify CLI - Commit Commands

The `commit` command allows you to generate smart, AI-powered commit messages for your Git changes. This document explains all available options and combinations.

## Basic Usage

```bash
penifycli commit
```

By default, this command:
- Analyzes your staged Git changes
- Generates a concise commit title only
- Uses local LLM if configured, or falls back to Penify API

## Command Options

### `-m, --message`

Provide context for the commit message generation:

```bash
penifycli commit -m "Fix login flow"
```

This hint helps the AI understand your intention and improves the quality of the generated message.

### `-e, --terminal`

Open an editor to review and edit the generated commit message before committing:

```bash
penifycli commit -e
```

This opens your default Git editor with the generated message for review.

### `-d, --description`

Generate a detailed commit message with both title and description:

```bash
penifycli commit -d
```

Without this flag, only the commit title is generated.

## Option Combinations

You can combine these options for different workflows:

### Generate Title Only with Context

```bash
penifycli commit -m "Update login UI"
```

### Generate Title and Description with Context

```bash
penifycli commit -m "Update login UI" -d
```

### Generate and Edit Full Commit Message

```bash
penifycli commit -d -e
```

### Generate, Edit, and Provide Context

```bash
penifycli commit -m "Refactor authentication" -d -e
```

## LLM and JIRA Integration

### Using Local LLM

If you've configured a local LLM using `penifycli config llm`, the commit command will automatically use it for message generation.

Benefits:
- Privacy: your code changes don't leave your machine
- Speed: no network latency
- Works offline

### JIRA Enhancement

If you've configured JIRA integration using `penifycli config jira`, the commit command will:

1. Detect JIRA issue references in your changes
2. Fetch issue details from your JIRA instance
3. Include issue information in the commit message
4. Format the commit message according to JIRA's smart commit format

Example output:
```
PROJ-123: Fix authentication bug in login flow

- Updated OAuth token validation
- Fixed session timeout handling
- Added unit tests for edge cases

[PROJ-123]
```

## Configuration Requirements

For the `commit` command to work:

1. You must have configured either:
   - Local LLM via `penifycli config llm`, OR
   - Logged in via `penifycli login`
   
2. For JIRA enhancement (optional):
   - Configure JIRA via `penifycli config jira`

## Examples

### Basic Commit with Default Settings

```bash
# Stage your changes
git add .

# Generate commit message
penifycli commit

# Commit with the generated message
git commit -m "Generated message here"
```

### Full Workflow with All Features

```bash
# Stage your changes
git add .

# Generate detailed commit message with JIRA integration, 
# provide context, and open editor for review
penifycli commit -m "Fix login issue" -d -e

# The commit is automatically completed after you save and exit the editor
```

## Troubleshooting

### Common Issues

1. **"No LLM model or API token provided"**
   - Run `penifycli config llm` to configure a local LLM, or
   - Run `penifycli login` to authenticate with Penify

2. **"Failed to connect to JIRA"**
   - Check your JIRA configuration with `cat ~/.penify`
   - Verify your network connection
   - Ensure your JIRA credentials are valid

3. **"Error initializing LLM client"**
   - Verify your LLM configuration settings
   - Ensure the LLM API is accessible
