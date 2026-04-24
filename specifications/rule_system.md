# Rule System

## Rule 数据结构

```python
@dataclass
class Rule:
    check: Callable[[str], bool]   # 判断条件，参数为 AI CLI 当前输出
    command: str | Callable[[], str] | None  # 为 None 时停止自动化
```

`check` 函数返回 `True` 时执行对应的 `command`。

## 规则加载总流程

```
get_rules(config)
│
├── 基础层: build_default_rules(config.cli_type)
│   → src/forgeflow/core/cli_types/{gemini,codex,claude_code}_rules.py
│
├── 如果 --task 指定:
│   └── get_task_rules(task)
│       ├── load_custom_task_rules(task)  → ~/.forgeflow/user_custom_rules/tasks/
│       └── get_task_rules_builder(task)   → src/forgeflow/tasks/{task}_task.py
│
└── 如果 --project 指定:
    └── load_custom_rules(project)
        → ~/.forgeflow/user_custom_rules/projects/
```

最终返回: `[cli_type_rules] + [task_rules]` 或 `[cli_type_rules] + [custom_rules]`

## 规则查找路径

| 资源 | 路径 |
|------|------|
| 用户自定义任务规则 | `~/.forgeflow/user_custom_rules/tasks/{name}_task.py` |
| 用户自定义项目规则 | `~/.forgeflow/user_custom_rules/projects/{name}_rules.py` |
| 内置任务规则 | `src/forgeflow/tasks/{name}_task.py` |
| 内置任务配置 | `src/forgeflow/tasks/configs/{name}_config.json` |
| 内置 CLI 类型规则 | `src/forgeflow/core/cli_types/{type}_rules.py` |

## 内置 CLI 类型规则

- `gemini` — Google Gemini CLI
- `codex` — OpenAI Codex
- `claude_code` — Claude Code

## 内置任务

- `fix_tests` — 修复失败的测试
- `improve_coverage` — 提升测试覆盖率
- `task_planner` — 按 TODO 顺序执行任务

## 自定义 CLI 适配器

CLI 适配器负责判断 AI CLI 的输出状态：

| 方法 | 说明 |
|------|------|
| `is_input_prompt(output)` | 是否处于等待输入状态 |
| `is_input_prompt_with_text(output)` | 是否处于等待输入且已有文本 |
| `is_task_processing(history)` | 是否有任务正在处理 |
| `is_ai_cli_exist(output)` | AI CLI 是否已启动 |

适配器位于 `src/forgeflow/core/cli_adapters/`。
