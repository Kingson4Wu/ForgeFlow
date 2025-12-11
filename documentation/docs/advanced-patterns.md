---
sidebar_position: 6
title: CLI Adapters - Supporting Qwen, Gemini, Claude in ForgeFlow
description: Learn about CLI adapters in ForgeFlow that support multiple AI tools like Qwen, Gemini, Claude. Implement custom adapters for different AI CLIs.
---

# CLI Adapters

CLI Adapters are a core component of ForgeFlow that enable support for different AI CLI tools through a consistent interface. They implement the adapter pattern to provide a uniform way to interact with various AI tools while handling their specific behaviors and requirements.

## Adapter Pattern Implementation

The CLI adapter system uses the classic adapter pattern with a base class and specific implementations:

- **Base Interface**: `CLIAdapter` (defined in `forgeflow/core/cli_adapters/base.py`)
- **Concrete Implementations**: Specific adapters for different AI tools
- **Factory**: Creates appropriate adapters based on CLI type

## Base CLIAdapter Interface

All CLI adapters inherit from the `CLIAdapter` base class which defines the following interface:

```python
class CLIAdapter(ABC):
    @abstractmethod
    def is_input_prompt(self, output: str) -> bool:
        """Detects if the AI CLI is waiting for input"""
        pass

    @abstractmethod
    def is_input_prompt_with_text(self, output: str) -> tuple[bool, str]:
        """Detects if there's existing text in the input box"""
        pass

    @abstractmethod
    def is_task_processing(self, output: str) -> bool:
        """Detects if the AI is actively processing a task"""
        pass

    @abstractmethod
    def is_ai_cli_exist(self) -> bool:
        """Checks if the CLI tool is available"""
        pass

    def wants_ansi(self) -> bool:
        """Indicates if CLI wants ANSI output (default True)"""
        return True
```

## Available Adapters

### Gemini Adapter

The default adapter for Google's Gemini CLI tool:

- Located in `forgeflow/core/cli_adapters/gemini.py`
- Implements prompt detection for Gemini's interface
- Handles Gemini-specific input and processing patterns
- Default adapter if no `--cli-type` is specified

### Qwen Adapter

Adapter for Alibaba Cloud's Qwen CLI tool:

- Located in `forgeflow/core/cli_adapters/qwen.py`
- Implements prompt detection for Qwen's interface
- Handles Qwen-specific response patterns
- Used when working with Qwen as the AI CLI tool

### Claude Code Adapter

Placeholder implementation for Anthropic's Claude Code:

- Located in `forgeflow/core/cli_adapters/claude_code.py`
- Currently a placeholder that needs implementation
- Intended to support Claude Code's specific behaviors
- Can be extended for full Claude support

## Using Different CLI Adapters

To specify a CLI adapter type, use the `--cli-type` parameter:

```bash
# Using the default Gemini adapter (explicitly specified)
forgeflow --cli-type gemini [other parameters]

# Using the Qwen adapter
forgeflow --cli-type qwen [other parameters]

# Using the Claude Code adapter
forgeflow --cli-type claude_code [other parameters]
```

## Creating Custom Adapters

To create a custom adapter for a new AI CLI tool, implement the `CLIAdapter` interface:

```python
# Example custom adapter implementation
from forgeflow.core.cli_adapters.base import CLIAdapter

class CustomAdapter(CLIAdapter):
    def is_input_prompt(self, output: str) -> bool:
        # Implementation for detecting input prompts
        return "custom_prompt>" in output.split('\n')[-1]

    def is_input_prompt_with_text(self, output: str) -> tuple[bool, str]:
        # Implementation for detecting existing text
        lines = output.split('\n')
        if lines and "custom_prompt>" in lines[-1]:
            # Extract any pre-filled text if present
            return True, ""
        return False, ""

    def is_task_processing(self, output: str) -> bool:
        # Implementation for detecting task processing
        return "processing..." in output.lower()

    def is_ai_cli_exist(self) -> bool:
        # Check if the CLI is available
        import subprocess
        try:
            result = subprocess.run(['custom-cli', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
```

## Adapter Factory

The factory pattern implementation automatically creates the appropriate adapter based on the CLI type:

```python
from forgeflow.core.cli_adapters.factory import get_cli_adapter

# Creates the appropriate adapter based on CLI type
adapter = get_cli_adapter(cli_type='qwen')
```

## Adapter-Specific Features

### Regular Expression Detection

Adapters use regular expressions to detect specific patterns in CLI output:

- Input prompts: Different CLIs have different prompt indicators
- Existing text: Detection of text already in the input field
- Task processing: Identifying when the AI is actively working
- Error states: Recognizing error conditions

### ANSI Handling

Some CLIs handle ANSI codes differently. Adapters can specify if they want ANSI output via the `wants_ansi()` method, which controls how output is formatted.

### Session Management

Adapters handle the specific requirements for session management with different AI tools, including:

- Command formatting
- Response parsing
- State tracking
- Recovery procedures

## Advanced Adapter Techniques

### Multi-Line Prompt Detection

Some CLIs have complex multi-line prompts. Adapters can implement sophisticated detection logic:

```python
def is_input_prompt(self, output: str) -> bool:
    lines = output.strip().split('\n')
    if len(lines) >= 2:
        return lines[-1].startswith('>') and 'custom' in lines[-2]
    return lines[-1].startswith('custom-prompt>')
```

### Stateful Detection

Some adapters maintain internal state to improve detection accuracy:

```python
class StatefulAdapter(CLIAdapter):
    def __init__(self):
        self.previous_output = ""
        
    def is_task_processing(self, output: str) -> bool:
        # Use both current output and previous state
        is_processing = self._detect_processing(output)
        self.previous_output = output
        return is_processing
```

## Default Rules for CLI Types

ForgeFlow includes default rules specific to each CLI type in the `forgeflow/core/cli_types/` directory. These rules provide optimal interaction patterns for each AI CLI tool.

The adapter system makes ForgeFlow flexible and extensible, allowing support for multiple AI CLI tools while maintaining consistent automation behavior.