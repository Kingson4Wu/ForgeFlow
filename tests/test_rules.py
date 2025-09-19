from forgeflow.core.rules import (
    is_all_task_finished,
    is_final_verification_finished,
)


def test_is_all_task_finished_ok() -> None:
    out = "... All tasks have been completed. ..."
    assert is_all_task_finished(out)


def test_is_final_verification_finished_ok() -> None:
    out = "... All test cases are fully covered and executed successfully without errors. ..."
    assert is_final_verification_finished(out)
