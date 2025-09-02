import pytest

from forgeflow.core.automation import Config, run_automation


@pytest.mark.skip(reason="调试程序用的，忽略测试")
def test_main():
    cfg = Config(
        session="qwen_session",
        workdir="/Users/kingsonwu/programming/ts-src/ts-playground",
        ai_cmd="qwen --proxy http://localhost:7890 --yolo",
        poll_interval=10,
        input_prompt_timeout=2000,
        log_file="forgeflow.log",
        log_to_console=True,
    )
    run_automation(cfg)
