# Penify CLI Example Workflows

This document demonstrates how to use Penify CLI in real-world development workflows to improve your productivity.

## Workflow 1: Efficient Git Commits with AI

### Setup

First, configure your local LLM for offline operation:

```bash
penifycli config llm
```

Configure your JIRA integration for enhanced commit messages:

```bash
penifycli config jira
```

### Daily Workflow

1. Make your code changes as usual
2. When ready to commit, use Penify to generate a smart commit message:

```bash
penifycli commit
```

3. Review and confirm the generated commit message
4. Git commit and push as usual

### Benefits

- Consistent and descriptive commit messages
- Automatic inclusion of relevant JIRA ticket information
- Time saved from writing detailed commit messages

## Workflow 2: Documentation Generation Pipeline

### Setup

Login to Penify to access advanced documentation features:

```bash
penifycli login
```

Install the Git hook for automatic documentation generation:

```bash
penifycli docgen install-hook
```

### Daily Workflow

1. Make your code changes as usual
2. Commit your changes
3. Documentation is automatically generated for changed files
4. Review the generated documentation

### Manual Documentation

For specific files or folders:

```bash
penifycli docgen -l src/components/authentication
```

### Benefits

- Always up-to-date documentation
- Consistent documentation style
- Time saved from writing detailed documentation

## Workflow 3: Code Review Enhancement

### Setup

Ensure you're logged into Penify:

```bash
penifycli login
```

### Workflow

1. Before submitting a PR, generate documentation for changed files:

```bash
penifycli docgen
```

2. Include the generated documentation in your PR
3. Reviewers can better understand your changes with the AI-generated explanations

### Benefits

- Improved PR quality
- Faster code reviews
- Better team understanding of code changes

## Workflow 4: Onboarding New Team Members

### For Team Leads

Generate comprehensive documentation for the entire codebase:

```bash
penifycli docgen -l .
```

### For New Team Members

Generate focused documentation for components you're working on:

```bash
penifycli docgen -l src/components/my-feature
```

### Benefits

- Faster onboarding
- Better understanding of code structure
- Reduced questions to senior team members

## Workflow 5: Legacy Code Understanding

When working with unfamiliar legacy code:

```bash
# Document a specific complex file
penifycli docgen -l src/legacy/complex_module.py

# Document an entire legacy component
penifycli docgen -l src/legacy/old_component
```

### Benefits

- Quickly understand complex legacy systems
- Reduce time spent deciphering undocumented code
- Make safer changes to legacy systems
