# Penify CLI - Configuration Commands

The `config` command allows you to set up and manage configuration settings for Penify CLI. This document explains all available configuration options and how to use them.

## Configuration Overview

Penify CLI stores configuration in a JSON file at `~/.penify/config.json`. The configuration includes:

- LLM (Large Language Model) settings for local commit message generation
- JIRA integration settings for enhanced commit messages
- API tokens and other credentials

## Basic Usage

```bash
# Configure LLM settings
penifycli config llm

# Configure JIRA integration
penifycli config jira
```

## LLM Configuration

### Web Interface

Running `penifycli config llm` opens a web interface in your browser where you can configure:

1. **Model**: The LLM model to use (e.g., `gpt-3.5-turbo`)
2. **API Base URL**: The endpoint URL for your LLM API (e.g., `https://api.openai.com/v1`)
3. **API Key**: Your authentication key for the LLM API

### Supported LLMs

Penify CLI supports various LLM providers:

#### OpenAI
- Model: `gpt-3.5-turbo` or `gpt-4`
- API Base: `https://api.openai.com/v1`
- API Key: Your OpenAI API key

#### Anthropic
- Model: `claude-instant-1` or `claude-2`
- API Base: `https://api.anthropic.com/v1`
- API Key: Your Anthropic API key

#### Ollama (Local)
- Model: `llama2` or any model you have installed
- API Base: `http://localhost:11434`
- API Key: (leave blank)

#### Azure OpenAI
- Model: Your deployed model name
- API Base: Your Azure endpoint
- API Key: Your Azure API key

### Configuration File Structure

After configuration, your `~/.penify/config.json` will contain:

```json
{
  "llm": {
    "model": "gpt-3.5-turbo",
    "api_base": "https://api.openai.com/v1",
    "api_key": "sk-..."
  }
}
```

## JIRA Configuration

### Web Interface

Running `penifycli config jira` opens a web interface where you can configure:

1. **JIRA URL**: Your JIRA instance URL (e.g., `https://yourcompany.atlassian.net`)
2. **Username**: Your JIRA username (typically your email)
3. **API Token**: Your JIRA API token

### Creating a JIRA API Token

1. Log in to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "Penify CLI")
4. Copy the generated token and paste it into the configuration

### Configuration File Structure

After configuration, your `~/.penify/config.json` will contain:

```json
{
  "jira": {
    "url": "https://yourcompany.atlassian.net",
    "username": "your.email@example.com",
    "api_token": "your-jira-api-token"
  }
}
```

## Configuration Locations

Penify CLI looks for configuration in multiple locations:

1. Project-specific: `.penify/config.json` in the Git repository root
2. User-specific: `~/.penify/config.json` in your home directory

The project-specific configuration takes precedence if both exist.

## Environment Variables

You can override configuration settings using environment variables:

- `PENIFY_API_TOKEN`: Override the stored API token
- `PENIFY_LLM_MODEL`: Override the configured LLM model
- `PENIFY_LLM_API_BASE`: Override the configured LLM API base URL
- `PENIFY_LLM_API_KEY`: Override the configured LLM API key
- `PENIFY_JIRA_URL`: Override the configured JIRA URL
- `PENIFY_JIRA_USER`: Override the configured JIRA username
- `PENIFY_JIRA_TOKEN`: Override the configured JIRA API token

Example:
```bash
export PENIFY_LLM_MODEL="gpt-4"
penifycli commit
```

## Command-Line Configuration

For advanced users or scripting, you can directly edit the configuration file:

```bash
# View current configuration
cat ~/.penify/config.json

# Edit configuration with your preferred editor
nano ~/.penify/config.json
```

## Sharing Configuration

You can share configuration between machines by copying the `.penify/config.json` file. However, be cautious with API keys and credentials.

For team settings, consider:
1. Using a project-specific `.penify/config.json` with shared settings
2. Excluding API keys from shared configuration
3. Using environment variables for sensitive credentials

## Troubleshooting

### Common Issues

1. **"Error reading configuration file"**
   - Check if the file exists: `ls -la ~/.penify`
   - Ensure it contains valid JSON: `cat ~/.penify/config.json`

2. **"Failed to connect to LLM API"**
   - Verify API base URL and API key
   - Check network connectivity to the API endpoint
   - Ensure your account has access to the specified model

3. **"Failed to connect to JIRA"**
   - Check JIRA URL format (should include `https://`)
   - Verify username and API token
   - Ensure your JIRA account has API access permissions
