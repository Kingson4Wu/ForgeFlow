import pytest

from forgeflow.core.automation import Config, run_automation
from pathlib import Path


@pytest.mark.skip(reason="just for debug, ignore it ")
def test_main():
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
    cfg = Config(
        session="fastproxy_session",
        workdir=str(Path.home() / "programming/go-src/fast_proxy"),
        ai_cmd="codex --yolo",
        poll_interval=10,
        input_prompt_timeout=2000,
        log_file="forge_flow.log",
        log_to_console=True,
        project="fastproxy",
        cli_type="codex",
    )
    run_automation(cfg)
