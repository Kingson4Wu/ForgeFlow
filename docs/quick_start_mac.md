# Quick Start Guide for Mac Users

This guide will help you quickly set up and use ForgeFlow on macOS.

## Prerequisites

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python 3.9+

```bash
brew install python@3.9
```

### 3. Install tmux

```bash
brew install tmux
```

### 4. Install an AI CLI Tool

For this example, we'll use the Gemini CLI:

```bash
# Install the Gemini CLI tool
# Note: This is just an example. You may need to install the specific AI CLI tool you want to use.
# For Google's Qwen/Gemini CLI, you might install it via pip or other methods depending on availability.
pip install gemini-cli  # This is just an example, replace with actual installation command
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Kingson4Wu/ForgeFlow
cd ForgeFlow
```

### 2. Set Up Python Environment

```bash
# Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Or using Conda:

```bash
conda create -n forgeflow python=3.9
conda activate forgeflow
pip install -e .
```

## Quick Usage

### 1. Basic Command

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/your/project" \
  --ai-cmd "gemini" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

### 2. With Custom Rules

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/your/project" \
  --ai-cmd "gemini" \
  --project myproject \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

## Creating Custom Rules

### 1. Create a Rule File

Create a file named `myproject_rules.py` in your project directory:

```python
from forgeflow.core.rules import Rule

def build_rules() -> list[Rule]:
    """Build a list of custom rules for my project."""
    return [
        # Stop rule - when this condition is met, automation stops
        Rule(check=lambda out: "All tasks completed" in out, command=None),
        
        # Custom error handling rules
        Rule(check=lambda out: "API Error" in out, command="continue"),
        
        # Default rule that always matches (acts as a fallback)
        Rule(check=lambda out: True, command="Please continue with the next task"),
    ]
```

### 2. Run with Custom Rules

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/your/project" \
  --ai-cmd "gemini" \
  --project myproject \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

## Useful tmux Commands

### View Sessions

```bash
tmux list-sessions
```

### Attach to a Session

```bash
tmux attach -t my_session
```

### Detach from a Session

Press `Ctrl+b` then `d`

### Kill a Session

```bash
tmux kill-session -t my_session
```

## Keeping Your Mac Awake During Long Tasks

When running long automation tasks with ForgeFlow, you might want to prevent your Mac from going to sleep or dimming the
screen. macOS provides a built-in utility called `caffeinate` for this purpose.

### Using caffeinate

To keep your Mac awake for the duration of a task, you can wrap your ForgeFlow command with `caffeinate`:

```bash
caffeinate forgeflow \
  --session my_session \
  --workdir "/path/to/your/project" \
  --ai-cmd "gemini" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

### caffeinate Options

- `caffeinate` without any options will prevent sleep assertions as long as it's running
- `caffeinate -d` prevents the display from sleeping
- `caffeinate -i` prevents the system from idle sleeping
- `caffeinate -m` prevents the disk from idle sleeping
- `caffeinate -s` prevents the system from sleeping (only works when plugged in with AC power)

For example, to prevent both the system and display from sleeping:

```bash
caffeinate -d -i forgeflow \
  --session my_session \
  --workdir "/path/to/your/project" \
  --ai-cmd "gemini" \
  --poll 10 \
  --timeout 2000 \
  --log-file forgeflow.log
```

Note that `caffeinate` will release its assertions when the wrapped command finishes executing.

## Troubleshooting

### 1. If tmux sessions are not being created

- Ensure tmux is properly installed: `tmux -V`
- Check if you have proper permissions

### 2. If AI CLI is not starting

- Verify the AI CLI tool is installed and accessible from your PATH
- Test the AI CLI independently to ensure it works

### 3. If rules are not being applied

- Check that your rule file is in the correct location
- Verify the function name is `build_rules`
- Check the log file for any error messages

## Next Steps

1. Explore the [examples](../examples/) directory for more rule templates
2. Read the [main README](../README.md) for detailed documentation
3. Check the [technology documentation](tech.md) to understand the internals