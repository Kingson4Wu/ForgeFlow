---
slug: tmux-inner-network-tunneling-for-remote-development
title: 'Tmux Inner Network Tunneling: Simple Remote Development'
authors: [kingsonwu]
tags: [tmux, tunneling, remote-development, networking, ssh]
description: Simple guide to using tmux with SSH tunneling for persistent remote development sessions.
---

# Tmux Inner Network Tunneling: Simple Remote Development

Tmux inner network tunneling is a technique that combines tmux's session persistence with SSH tunneling to create stable remote development connections. This approach allows you to maintain persistent development sessions that survive network disconnections.

## Core Principle

The key insight is simple:
- **tmux** maintains persistent terminal sessions even when SSH connections drop
- **SSH tunneling** creates secure pathways to access internal services
- Together, they enable reliable remote development from anywhere

## Basic Setup

1. Install SSH and tmux on your target machine
2. Set up tunneling tools (like Cloudflare Tunnel, frp, or ZeroTier) to expose SSH service
3. Create persistent tmux sessions to hold your work environment

```bash
# Create a persistent session
tmux new-session -d -s remote_dev

# Attach to the session from anywhere
tmux attach -t remote_dev
```

## SSH Tunneling with tmux

Create a dedicated session for managing tunnels:

```bash
# Create a tunnel management session
tmux new-session -d -s tunnels

# Start SSH port forwarding (forward local port 8080 to remote port 8080)
tmux send-keys -t tunnels 'ssh -L 8080:localhost:8080 user@remote-server -N' Enter

# Add more tunnels as needed
tmux split-window -h -t tunnels
tmux send-keys -t tunnels 'ssh -L 3306:localhost:3306 user@db-server -N' Enter
```

## Why This Works

- When your SSH connection drops, the tmux session remains active on the remote machine
- You can reconnect to the same session later and pick up exactly where you left off
- Multiple tunnels can be managed within organized tmux windows
- Development workflow stays uninterrupted despite network changes

## Quick Start

1. Set up SSH access to your development machine
2. Install and configure a tunneling solution (Cloudflare Tunnel, frp, etc.)
3. Create a persistent tmux session before disconnecting:

```bash
tmux new-session -d -s mydev -c ~
```

4. Connect from anywhere and resume work:

```bash
tmux attach -t mydev
```

## Conclusion

Tmux inner network tunneling simplifies remote development by combining session persistence with secure tunneling. This approach eliminates the complexity of managing multiple connections while ensuring work is never lost due to network interruptions.