---
sidebar_position: 8
---

# Project Documentation

Learn how to document your ForgeFlow project configurations and customizations effectively.

## Document Your Custom Rules

Document your custom rules to help team members understand their purpose:

```md title="docs/myproject-custom-rules.md"
---
sidebar_label: 'MyProject Rules'
sidebar_position: 10
---

# MyProject Custom Rules

This document describes the custom rules implemented for the MyProject repository.

## Rule: Feature Request Handling
- **Condition**: When AI output contains "feature request"
- **Action**: Focus on authentication module implementation

## Rule: Error Handling
- **Condition**: When AI output contains "bug" or "error"
- **Action**: Investigate and fix issues before proceeding
```

A new documentation page is now available for your project.

## Document Your Task Configurations

Keep track of your task configurations for team collaboration:

```json title="task_configs/myproject_task_config.json"
{
  "name": "MyProject Task Config",
  "description": "Configuration for MyProject automation tasks",
  "default_task": "task_planner",
  "rules": [
    {
      "check": "feature request detected",
      "command": "Focus on authentication module"
    }
  ]
}
```

Documenting your configurations helps maintain consistency across your team.

## Document Your Custom CLI Setup

If you're using custom CLI adapters, document the setup process:

```md title="docs/cli-setup.md"
# CLI Setup for MyProject

## Prerequisites
- Install MyCLI tool: `npm install -g my-cli`
- Configure API key: `my-cli config set api_key [your_key]`

## ForgeFlow Integration
Run with the custom adapter: `forgeflow --cli-type my_cli ...`
```

Proper documentation ensures your team can maintain and extend your ForgeFlow setup.
