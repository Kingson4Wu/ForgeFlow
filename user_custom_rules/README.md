# User Custom Rules

This directory is for storing your custom rules and configurations for ForgeFlow.

## Purpose

The `user_custom_rules` directory is designed to hold user-defined rule files and configuration files that customize
ForgeFlow's behavior for your specific projects. Unlike the `examples/` directory which contains sample files, and
the built-in configurations in `forgeflow/tasks/configs/`, this directory is specifically for your own custom rules.

## Directory Structure

- `projects/` - Custom project rule files
- `tasks/` - Custom task rule files and configurations

## Usage

### Custom Rule Files

You can place your custom rule files in the appropriate subdirectories. ForgeFlow will automatically look for rule files in the
following order:

1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `user_custom_rules/projects/{project_name}_rules.py` 
4. `user_custom_rules/projects/{project_name}.py`
5. `forgeflow/core/cli_types/{cli_type}_rules.py` (built-in CLI type rules)
6. `examples/projects/{project_name}_rules.py` (example rules for backward compatibility)
7. `examples/projects/{project_name}.py` (example rules for backward compatibility)

### Configuration Files

You can also place task configuration files in the tasks subdirectory. ForgeFlow will look for configuration files in the
following order:

1. `{task_name}_config.json` in the current working directory
2. `user_custom_rules/tasks/{task_name}_config.json`
3. `forgeflow/tasks/configs/{task_name}_config.json` (built-in configurations)
4. `examples/tasks/{task_name}_config.json` (example configurations for backward compatibility)

## File Naming Convention

- **Project rule files**: `{project_name}_rules.py` or `{project_name}.py` (placed in `projects/` subdirectory)
- **Task rule files**: `{task_name}_task.py` (placed in `tasks/` subdirectory)
- **Task configuration files**: `{task_name}_config.json` (placed in `tasks/` subdirectory)
- **TODO files**: `TODO.md` (or custom name specified in configuration)

## Example

To create a custom rule file for a project named "myproject":

1. Create a file named `myproject_rules.py` in the `user_custom_rules/projects/` directory
2. Implement a `build_rules()` function that returns a list of Rule objects
3. Run ForgeFlow with `--project myproject`

Example `user_custom_rules/projects/myproject_rules.py`:

```python
from forgeflow.core.rules import Rule

def build_rules() -> list[Rule]:
    return [
        # Your custom rules here
        Rule(check=lambda out: "task completed" in out.lower(), command=None),
        Rule(check=lambda out: True, command="Continue with the next task"),
    ]
```

## Best Practices

1. **Organize your files**: Use descriptive names for your rule files and place them in the appropriate subdirectories
2. **Document your rules**: Add comments to explain complex rules
3. **Test your rules**: Verify that your rules work as expected
4. **Version control**: Consider adding your custom rules to version control
5. **Backup**: Keep backups of important rule files

## See Also

- [forgeflow/core/cli_types/](../forgeflow/core/cli_types/) - Built-in CLI type rules
- [examples/projects/](../examples/projects/) - Example project rule files for reference
- [examples/tasks/](../examples/tasks/) - Example task rule files for reference
- [Documentation](../docs/) - Full documentation for ForgeFlow