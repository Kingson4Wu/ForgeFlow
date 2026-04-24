---
sidebar_position: 1
title: ForgeFlow Introduction - AI CLI Automation Tool
description: Learn how ForgeFlow automates AI CLI tools in tmux sessions for continuous programming task execution. Robust session management and configurable rules for Gemini, Claude Code, Codex.
---

# ForgeFlow Introduction

ForgeFlow is an automation tool that automatically drives AI CLI tools to continuously complete programming tasks within a `tmux` session. It provides robust session management, configurable rule systems, multi-CLI support, reliable input detection, and timeout recovery strategies.

## Overview

ForgeFlow is designed to automate programming tasks by continuously interacting with AI CLI tools within a tmux session. The system monitors the AI's output, detects when it's waiting for input or processing tasks, and sends appropriate commands based on configurable rules.

The project addresses common challenges in AI-assisted programming:

- **Continuity**: Keeps AI tools engaged in programming tasks without manual intervention
- **Session Management**: Handles tmux sessions robustly, separating text from enter commands
- **Rule-based Logic**: Uses configurable rules to determine appropriate responses
- **Multi-CLI Support**: Works with different AI CLI tools through adapter patterns
- **Reliability**: Implements timeout recovery strategies to handle stalls

## Key Features

- **Robust Session Management**: Automatically creates/reuses `tmux` sessions, separating text from enter when pasting commands
- **Configurable Rule System**: Rules are evaluated in order with priority matching; custom rules supported
- **Multi-CLI Support**: Gemini, Claude Code, Codex — through adapter pattern
- **Reliable Input Detection**: Regex-based detection of input prompts and existing text, per CLI type
- **Timeout Recovery Strategy**: Long periods without input prompt → `ESC` → backspace clear → `continue`
- **Logging**: Dual channel file + console with timestamps
- **Task Monitoring**: Desktop notifications when task processing stalls (macOS supported)
- **Monitor-Only Mode**: Watch existing sessions without sending commands

## Use Cases

ForgeFlow is particularly useful for:

- **Automated Code Generation**: Let AI tools continuously generate code based on project requirements
- **Test Fixing**: Automatically fix failing test cases using AI assistance
- **Code Coverage Improvement**: Enhance test coverage by having AI generate additional tests
- **Task Automation**: Execute predefined programming tasks with minimal manual intervention
- **Background Processing**: Run programming tasks in the background while working on other activities

## Getting Started

To get started with ForgeFlow, explore the installation guide and configure it for your specific AI CLI tool and project requirements.
