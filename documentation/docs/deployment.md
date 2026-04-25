---
sidebar_position: 3
title: Deployment
description: Deployment and configuration reference for ForgeFlow.
---

# Deployment

## Environment

ForgeFlow requires Python >= 3.13 and tmux.

```bash
# Clone
git clone https://github.com/Kingson4Wu/ForgeFlow
cd ForgeFlow

# Install
uv sync          # or: pip install -e .
```

## tmux

Ensure tmux is installed and on PATH:

```bash
brew install tmux  # macOS
# or
apt install tmux   # Linux
```

## AI CLI Tools

Install at least one supported AI CLI:

| CLI | Install |
|-----|---------|
| Claude Code | `npm install -g @anthropic/claude-code` |
| Gemini | `pip install google-gemini` |
| Codex | `pip install openai-codex` |

## Long-Running Tasks

To prevent Mac from sleeping during long tasks:

```bash
caffeinate forgeflow --session my_session --workdir "/path/to/project" --ai-cmd "claude"
```

## Running

```bash
forgeflow --session my_session --workdir "/path/to/project" --ai-cmd "claude --dangerously-skip-permissions" --cli-type claude_code
```

Or with `uv run`:

```bash
uv run forgeflow --session my_session --workdir "/path/to/project" --ai-cmd "claude"
```

## Documentation Site

```bash
cd documentation
npm install
npm run start     # development
npm run build     # production build
npm run serve     # serve production build
```

Run `forgeflow --help` for the full CLI reference.
