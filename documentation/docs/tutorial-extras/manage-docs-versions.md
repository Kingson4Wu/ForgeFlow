---
sidebar_position: 12
---

# Managing Project Versions

Learn how to manage different versions of your project configurations and rules for ForgeFlow.

## Version Configuration Files

Maintain separate configuration files for different project versions:

```
project_configs/
├── v1.0/
│   ├── rules.py
│   └── config.json
├── v2.0/
│   ├── rules.py
│   └── config.json
└── latest/
    ├── rules.py
    └── config.json
```

## Version-Specific Rules

Create version-specific rule files to handle different project requirements:

```python title="myproject_v1.0_rules.py"
from forgeflow.core.rules import Rule

# Rules specific to version 1.0 of your project
Rule(
    check=lambda output: "react v17" in output.lower(),
    command="Use hooks-based approach for this version."
)
```

```python title="myproject_v2.0_rules.py"
from forgeflow.core.rules import Rule

# Rules specific to version 2.0 of your project  
Rule(
    check=lambda output: "react v18" in output.lower(),
    command="Use concurrent features available in this version."
)
```

## Switching Between Versions

Use the project parameter to switch between different configurations:

```bash
# Use v1.0 rules
forgeflow --project myproject_v1.0 [other options]

# Use v2.0 rules
forgeflow --project myproject_v2.0 [other options]
```

## Maintain Rule Compatibility

When upgrading project versions:

- Test rules with the new version before deployment
- Create backup configurations for rollback
- Document differences between version-specific rules
- Use semantic versioning for your configuration files
