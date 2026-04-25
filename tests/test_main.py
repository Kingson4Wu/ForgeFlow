from pathlib import Path

import pytest

from forgeflow.automation.loop import run_automation
from forgeflow.config import Config


@pytest.mark.skip(reason="just for debug, ignore it ")
def test_main() -> None:
    # cfg = Config(
    #     session="fastproxy_session",
    #     workdir=str(Path.home() / "programming/go-src/fast_proxy"),
    #     ai_cmd="qwen --proxy http://localhost:7890 --yolo",
    #     poll_interval=10,
    #     input_prompt_timeout=2000,
    #     log_file="forgeflow.log",
    #     log_to_console=True,
    #     project="fastproxy",
    # )
    # cfg = Config(
    #     session="fastproxy_session",
    #     workdir=str(Path.home() / "programming/go-src/fast_proxy"),
    #     ai_cmd="codex --yolo",
    #     poll_interval=10,
    #     input_prompt_timeout=2000,
    #     log_file="forgeflow.log",
    #     log_to_console=True,
    #     project="fastproxy",
    #     cli_type="codex",
    # )

    cfg = Config(
        session="forge_flow_session",
        workdir=str(Path.home() / "programming/OctopusGarage/telegram-bridge"),
        ai_cmd="claude-yolo",
        poll_interval=10,
        input_prompt_timeout=2000,
        log_file="forgeflow.log",
        log_to_console=True,
        project="telegram-bridge",
        cli_type="claude_code",
        task="improve_coverage",
    )
    run_automation(cfg)
