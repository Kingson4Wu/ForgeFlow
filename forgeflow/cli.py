from __future__ import annotations

import argparse
import sys

from .core.automation import Config, run_automation


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ForgeFlow — Drive AI CLI in tmux")
    p.add_argument("--session", required=True, help="tmux session name")
    p.add_argument("--workdir", required=True, help="working directory for tmux session")
    p.add_argument("--ai-cmd", required=True, help="AI CLI command to start")
    p.add_argument("--poll", type=int, default=10, help="poll interval in seconds")
    p.add_argument("--timeout", type=int, default=2000, help="input prompt timeout in seconds")
    p.add_argument("--log-file", default="forgeflow.log", help="log file path")
    p.add_argument("--no-console", action="store_true", help="disable console logging")
    p.add_argument("--project", help="project name to load custom rules")
    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    args = build_parser().parse_args(argv)

    cfg = Config(
        session=args.session,
        workdir=args.workdir,
        ai_cmd=args.ai_cmd,
        poll_interval=args.poll,
        input_prompt_timeout=args.timeout,
        log_file=args.log_file,
        log_to_console=not args.no_console,
        project=args.project,
    )

    return run_automation(cfg)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
