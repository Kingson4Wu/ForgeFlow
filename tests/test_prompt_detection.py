from forgeflow.core.rules import is_input_prompt, is_input_prompt_with_text


def test_is_input_prompt_false_on_empty():
    assert not is_input_prompt("")


def test_is_input_prompt_with_text_false_on_empty():
    assert not is_input_prompt_with_text("")


def test_is_input_prompt_true_sample():
    sample = "> Type your message or @tools/test"  # Loose matching
    assert is_input_prompt(sample)
