# User Custom Rules

This directory is for storing your custom rules and configurations for ForgeFlow.

## Purpose

The `user_custom_rules` directory is designed to hold user-defined rule files and configuration files that customize
ForgeFlow's behavior for your specific projects. Unlike the `examples/` directory which contains sample files, and
the `default_rules/` directory which contains built-in rules, this directory is specifically for your own custom rules.

## Usage

### Custom Rule Files

You can place your custom rule files in this directory. ForgeFlow will automatically look for rule files in the
following order:

1. `{project_name}_rules.py` in the current working directory
2. `{project_name}.py` in the current working directory
3. `{project_name}_rules.py` in this `user_custom_rules/` directory
4. `{project_name}.py` in this `user_custom_rules/` directory
5. `{project_name}_rules.py` in the `default_rules/` directory (built-in default rules)
6. `{project_name}.py` in the `default_rules/` directory (built-in default rules)
7. `{project_name}_rules.py` in the `examples/` directory (for backward compatibility)
8. `{project_name}.py` in the `examples/` directory (for backward compatibility)

### Configuration Files

You can also place task configuration files in this directory. ForgeFlow will look for configuration files in the
following order:

1. `{task_name}_config.json` in the current working directory
2. `{task_name}_config.json` in this `user_custom_rules/` directory
3. `{task_name}_config.json` in the `default_rules/` directory
4. `{task_name}_config.json` in the `examples/` directory (for backward compatibility)

## File Naming Convention

- **Rule files**: `{project_name}_rules.py` or `{project_name}.py`
- **Task configuration files**: `{task_name}_config.json`
- **TODO files**: `TODO.md` (or custom name specified in configuration)

## Example

To create a custom rule file for a project named "myproject":

1. Create a file named `myproject_rules.py` in this directory
2. Implement a `build_rules()` function that returns a list of Rule objects
3. Run ForgeFlow with `--project myproject`

Example `myproject_rules.py`:

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

1. **Organize your files**: Use descriptive names for your rule files
2. **Document your rules**: Add comments to explain complex rules
3. **Test your rules**: Verify that your rules work as expected
4. **Version control**: Consider adding your custom rules to version control
5. **Backup**: Keep backups of important rule files

## See Also

- [default_rules/](../default_rules/) - Built-in default rules and configurations
- [examples/](../examples/) - Example rule files for reference
- [Documentation](../docs/) - Full documentation for ForgeFlow