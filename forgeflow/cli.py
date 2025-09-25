from __future__ import annotations

import argparse
import sys

from .core.automation import Config, run_automation, run_monitor_mode


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ForgeFlow — Drive AI CLI in tmux")
    p.add_argument("--session", required=True, help="tmux session name")
    p.add_argument(
        "--workdir",
        help="working directory for tmux session (required in normal mode, optional in monitor-only mode)",
    )
    p.add_argument("--ai-cmd", help="AI CLI command to start (required unless in monitor mode)")
    p.add_argument("--poll", type=int, default=10, help="poll interval in seconds")
    p.add_argument("--timeout", type=int, default=2000, help="input prompt timeout in seconds")
    p.add_argument("--log-file", default="forgeflow.log", help="log file path")
    p.add_argument("--no-console", action="store_true", help="disable console logging")
    p.add_argument("--project", help="project name to load custom rules")
    p.add_argument("--task", help="task type to load predefined task rules")
    p.add_argument("--cli-type", default="gemini", help="AI CLI type (gemini, claude_code, etc.)")
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="logging level",
    )
    p.add_argument(
        "--monitor-only",
        action="store_true",
        help="run in monitor-only mode (only sends notifications when tasks stop processing)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    args = build_parser().parse_args(argv)

    cfg = Config(
        session=args.session,
        workdir=args.workdir,
        ai_cmd=args.ai_cmd or "",  # Not required in monitor mode
        poll_interval=args.poll,
        input_prompt_timeout=args.timeout,
        log_file=args.log_file,
        log_to_console=not args.no_console,
        project=args.project,
        task=args.task,
        cli_type=args.cli_type,
        log_level=args.log_level,
    )

    if args.monitor_only:
        return run_monitor_mode(cfg)
    else:
        # ai_cmd is required in normal mode
        if not args.ai_cmd:
            print("Error: --ai-cmd is required unless running in --monitor-only mode")
            return 1
        return run_automation(cfg)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
