# Quick Start

## 安装依赖

### macOS

```bash
# tmux
brew install tmux

# Python 3.13+
python3 --version

# AI CLI（任选其一）
# Gemini
pip install google-gemini
# Claude Code
npm install -g @anthropic/claude-code
# Codex
pip install openai-codex
```

### 安装 ForgeFlow

```bash
cd ForgeFlow
uv sync
```

## 运行

### 自动化模式（驱动 AI CLI 执行任务）

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --cli-type gemini \
  --poll 10 \
  --timeout 2000
```

### 监控模式（只监控，不自动执行命令）

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --monitor-only
```

## tmux 常用命令

```bash
tmux list-sessions        # 查看所有 session
tmux attach -t my_session  # 进入 session
Ctrl+b d                   # detach
tmux kill-session -t my_session  # 删除 session
```

## 长时间任务保持 Mac 不休眠

```bash
caffeinate forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --poll 10
```

## 自定义规则

将规则文件放到 `~/.forgeflow/user_custom_rules/projects/`：

```python
# ~/.forgeflow/user_custom_rules/projects/myproject_rules.py
from forgeflow.core.rules import Rule

def build_rules() -> list[Rule]:
    return [
        Rule(check=lambda out: "done" in out.lower(), command=None),
        Rule(check=lambda out: True, command="continue"),
    ]
```

运行时指定 `--project myproject` 即可加载。

完整规则说明见 [rule_system.md](./rule_system.md)，任务模式见 [task_mode.md](./task_mode.md)。
