from pathlib import Path

import pytest

from forgeflow.core.automation import Config, run_automation


@pytest.mark.skip(reason="just for debug, ignore it ")
def test_main() -> None:
    # cfg = Config(
    #     session="fastproxy_session",
    #     workdir=str(Path.home() / "programming/go-src/fast_proxy"),
    #     ai_cmd="qwen --proxy http://localhost:7890 --yolo",
    #     poll_interval=10,
    #     input_prompt_timeout=2000,
    #     log_file="forge_flow.log",
    #     log_to_console=True,
    #     project="fastproxy",
    # )
    # cfg = Config(
    #     session="fastproxy_session",
    #     workdir=str(Path.home() / "programming/go-src/fast_proxy"),
    #     ai_cmd="codex --yolo",
    #     poll_interval=10,
    #     input_prompt_timeout=2000,
    #     log_file="forge_flow.log",
    #     log_to_console=True,
    #     project="fastproxy",
    #     cli_type="codex",
    # )

    cfg = Config(
        session="qwen_session",
        workdir=str(Path.home() / "programming/rust-src/mesh-talk"),
        ai_cmd="qwen --proxy http://localhost:7890 --yolo",
        poll_interval=10,
        input_prompt_timeout=2000,
        log_file="forge_flow.log",
        log_to_console=True,
        project="mesh-talk",
        cli_type="gemini",
        task="task_planner",
    )
    run_automation(cfg)
