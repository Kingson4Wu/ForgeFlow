---
sidebar_position: 7
---

# Custom Project Setup

Learn how to customize ForgeFlow for your specific project needs using custom rules and configurations.

## Project-Specific Configuration

Create a `{project_name}_rules.py` file in your project directory to define custom behavior:

- `myproject_rules.py` → Loaded when using `--project myproject`
- `myproject.py` → Alternative naming option

## Create Project-Specific Rules

Rules determine how ForgeFlow responds to different outputs from your AI CLI tool:

```python title=\"myproject_rules.py\"
from forgeflow.core.rules import Rule

# Define custom rules for your project
Rule(
    check=lambda output: \"feature request\" in output.lower(),
    command=\"Focus on implementing the user authentication module.\"
)

Rule(
    check=lambda output: \"bug\" in output.lower() or \"error\" in output.lower(),
    command=\"Please investigate and fix the reported issue first.\"
)
```

A new rule configuration is now ready for your project.

## Create Custom CLI Adapter

If you need to support a new AI CLI tool, extend the base adapter:

```python title=\"my_custom_adapter.py\"
from forgeflow.core.cli_adapters.base import CLIAdapter

class MyCustomAdapter(CLIAdapter):
    def is_input_prompt(self, output: str) -> bool:
        return \"my_cli_prompt>\" in output.split('\\n')[-1]
        
    def is_task_processing(self, output: str) -> bool:
        return \"working...\" in output.lower()
        
    def is_ai_cli_exist(self) -> bool:
        import subprocess
        try:
            result = subprocess.run(['my-cli', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
```

Your custom adapter is now ready to use with ForgeFlow.
