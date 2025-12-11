---
sidebar_position: 10
---

# Production Deployment

Learn how to deploy and run ForgeFlow in production environments for continuous automation.

## Prepare Your Production Environment

Set up your system for running ForgeFlow in production:

```bash
# Install dependencies in production environment
pip install -e .

# Ensure tmux is available
which tmux
```

## Configure Production Settings

Create a configuration file or use environment variables for production settings:

```bash
# Example production deployment
forgeflow \\
  --session production_session \\
  --workdir \"/var/www/myproject\" \\
  --ai-cmd \"qwen --api-key $QWEN_API_KEY\" \\
  --poll 30 \\
  --timeout 7200 \\
  --log-file /var/log/forgeflow.log
```

## Production Monitoring

Set up monitoring for your ForgeFlow processes:

- Log rotation for `--log-file` output
- Process monitoring to restart if ForgeFlow exits
- Notification systems for task completion or failures

## Run in Background

Use process managers to keep ForgeFlow running continuously:

```bash
# Using nohup
nohup forgeflow [options] > /var/log/forgeflow.log 2>&1 &

# Using systemd (recommended for production)
# Create /etc/systemd/system/forgeflow.service
```

## Deployment Strategies

### Single Task Deployment

For specific tasks like test fixing:

```bash
forgeflow \\
  --session fix_tests \\
  --workdir \"/path/to/project\" \\
  --ai-cmd \"gemini --key $API_KEY\" \\
  --task fix_tests \\
  --poll 15 \\
  --timeout 3600 \\
  --log-file forgeflow_fix_tests.log
```

### Multi-Project Deployment

Run multiple ForgeFlow instances for different projects:

```bash
# Project 1
forgeflow --session project1 --project project1 [other options] &

# Project 2
forgeflow --session project2 --project project2 [other options] &
```

## Best Practices

- Use longer polling intervals in production to reduce system load
- Implement proper logging and log rotation
- Monitor resource usage to ensure optimal performance
- Set appropriate timeouts based on your project complexity
- Use project-specific rules for better automation accuracy
