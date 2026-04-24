# CLI Reference

## 命令格式

```bash
forgeflow --session <name> [options]
```

## 参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--session` | 是 | — | tmux session 名称 |
| `--workdir` | 自动化模式: 是<br>监控模式: 否 | — | tmux session 工作目录 |
| `--ai-cmd` | 自动化模式: 是<br>监控模式: 否 | — | 启动 AI CLI 的命令 |
| `--cli-type` | 否 | `claude_code` | AI CLI 类型：`gemini`、`codex`、`claude_code` |
| `--project` | 否 | — | 加载自定义项目规则的名称 |
| `--task` | 否 | — | 预定义任务类型 |
| `--poll` | 否 | `10` | 轮询间隔（秒） |
| `--timeout` | 否 | `1000` | 输入提示超时（秒） |
| `--log-file` | 否 | `forgeflow.log` | 日志文件路径 |
| `--log-level` | 否 | `INFO` | 日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR` |
| `--monitor-only` | 否 | `False` | 仅监控模式（不自动执行命令） |

## 模式

### 自动化模式

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --cli-type gemini \
  --project myproject \
  --task fix_tests
```

`--ai-cmd` 必填，ForgeFlow 自动驱动 AI CLI 完成指定任务。

### 监控模式

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --monitor-only
```

不自动执行命令，仅监控 AI CLI 状态，在任务完成/停止时发送系统通知。
