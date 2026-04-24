# Task Mode

Task mode 提供预定义的任务规则，配合 AI CLI 自动完成特定类型的工作。

## 使用

```bash
forgeflow \
  --session my_session \
  --workdir "/path/to/project" \
  --ai-cmd "gemini" \
  --task fix_tests
```

## 内置任务

| 任务名 | 说明 |
|--------|------|
| `fix_tests` | 自动修复失败的测试用例 |
| `improve_coverage` | 提升项目测试覆盖率 |
| `task_planner` | 按 TODO 文件顺序执行任务 |

## 创建自定义任务

在 `~/.forgeflow/user_custom_rules/tasks/` 下创建 `{task_name}_task.py`：

```python
from forgeflow.core.rules import Rule

def build_rules(config: dict) -> list[Rule]:
    return [
        Rule(check=lambda out: "done" in out.lower(), command=None),
        Rule(check=lambda out: True, command="please continue"),
    ]
```

使用：`--task your_task_name`

## 任务配置

在 `~/.forgeflow/user_custom_rules/tasks/` 或 `src/forgeflow/tasks/configs/` 下放置 `{task_name}_config.json`。

内置配置示例 (`src/forgeflow/tasks/configs/task_planner_config.json`)：

```json
{
  "todo_file": "TODO.md",
  "completed_marker": "✓",
  "pending_marker": "☐",
  "task_pattern": "^\\s*[-*]\\s+\\[(.)\\]\\s+(.+)$",
  "next_task_prompt": "Please proceed with the next task in the TODO list.",
  "task_completion_indicators": [
    "task completed",
    "task finished",
    "done with task"
  ]
}
```

## 加载优先级

```
~/.forgeflow/user_custom_rules/tasks/{task}_task.py     ← 用户自定义（优先）
~/.forgeflow/user_custom_rules/tasks/{task}.py
src/forgeflow/tasks/{task}_task.py                       ← 内置（回退）
```

## 与 Project 模式的关系

`--project` 和 `--task` 可以同时使用：

```bash
forgeflow --session s --workdir . --ai-cmd "gemini" \
  --project myproject --task fix_tests
```

最终规则 = `[cli_type_rules] + [task_rules]`
