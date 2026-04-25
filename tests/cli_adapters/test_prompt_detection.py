from forgeflow.adapters.registry import get_adapter

# Get the default gemini adapter for testing
cli_adapter = get_adapter("gemini")


def test_is_input_prompt_false_on_empty() -> None:
    assert not cli_adapter.is_input_prompt("")


def test_is_input_prompt_with_text_false_on_empty() -> None:
    assert not cli_adapter.is_input_prompt_with_text("")


def test_is_input_prompt_true_sample() -> None:
    sample = "> Type your message or @tools/test"  # Loose matching
    assert cli_adapter.is_input_prompt(sample)
