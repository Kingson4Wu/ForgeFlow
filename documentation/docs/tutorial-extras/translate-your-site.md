---
sidebar_position: 13
---

# Customizing for Different Teams

Learn how to customize ForgeFlow for different teams, projects, or organizational needs.

## Team-Specific Configurations

Create team-specific configuration files to match different team workflows:

```
team_configs/
├── backend-team/
│   ├── rules.py
│   └── config.json
├── frontend-team/
│   ├── rules.py
│   └── config.json
└── devops-team/
    ├── rules.py
    └── config.json
```

## Adapting to Different Workflows

Different teams may have different working patterns. Customize rules accordingly:

```python title="backend-team_rules.py"
from forgeflow.core.rules import Rule

# Backend-specific rules
Rule(
    check=lambda output: "database" in output.lower(),
    command="Consider connection pooling and transaction management."
)

Rule(
    check=lambda output: "api" in output.lower(),
    command="Follow REST principles and document endpoints properly."
)
```

```python title="frontend-team_rules.py"
from forgeflow.core.rules import Rule

# Frontend-specific rules
Rule(
    check=lambda output: "ui" in output.lower() or "interface" in output.lower(),
    command="Ensure responsive design and accessibility compliance."
)

Rule(
    check=lambda output: "performance" in output.lower(),
    command="Optimize bundle size and implement lazy loading where appropriate."
)
```

## Environment-Specific Customizations

Adapt rules for different environments (development, staging, production):

```python title="production_env_rules.py"
from forgeflow.core.rules import Rule

# Production-specific considerations
Rule(
    check=lambda output: "deploy" in output.lower() or "release" in output.lower(),
    command="Ensure all security checks and performance tests pass before deployment."
)

Rule(
    check=lambda output: "logging" in output.lower(),
    command="Use structured logging with appropriate log levels for production monitoring."
)
```

## Multi-Project Management

Use project-specific identifiers to load appropriate configurations:

```bash
# For backend team working on API project
forgeflow --project api_backend [other options]

# For frontend team working on web project
forgeflow --project web_frontend [other options]
```

## Best Practices for Customization

- Document your custom rules for team members
- Test configurations in a staging environment first
- Use descriptive names for configuration files
- Regularly review and update rules based on team feedback
- Share successful configurations across teams when appropriate
