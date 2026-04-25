"""Tests for ClaudeCodeCLIAdapter.is_task_processing."""

from forgeflow.adapters.claude_code import ClaudeCodeCLIAdapter


def _make_history(frames: list[str]) -> list[str]:
    """Helper to create history list."""
    return frames


def _above_prompt(lines: list[str]) -> str:
    """Build a Claude Code output with lines above prompt and ❯ at end."""
    above = "\n".join(lines)
    return f"{above}\n❯ "


class TestClaudeCodeIsTaskProcessing:
    """Test is_task_processing logic.

    Idle (False): 5+ consecutive unchanged frames AND exactly 1 "⏺" line in last 4 lines.
    Processing (True): otherwise.
    """

    def setup_method(self) -> None:
        """Create fresh adapter for each test."""
        self.adapter = ClaudeCodeCLIAdapter()

    def test_empty_history_returns_false(self) -> None:
        """Empty history → not processing."""
        assert self.adapter.is_task_processing([]) is False

    def test_single_frame_returns_true(self) -> None:
        """Single frame → not enough data, return True (processing)."""
        history = [_above_prompt(["⏺ 你好！有什么需要帮忙的吗？"])]
        assert self.adapter.is_task_processing(history) is True

    def test_one_play_line_not_5_unchanged_is_processing(self) -> None:
        """1 play line but fewer than 5 unchanged → processing."""
        # Frame 1: ⏺ line (1 play line)
        # Frame 2: same (1 unchanged count)
        # Frame 3: same (2 unchanged count)
        # Not yet 5 → should be True (processing)
        frames = [
            _above_prompt(["⏺ 你好！"]),
            _above_prompt(["⏺ 你好！"]),
            _above_prompt(["⏺ 你好！"]),
        ]
        assert self.adapter.is_task_processing(frames) is True

    def test_five_unchanged_one_play_is_idle(self) -> None:
        """5 unchanged frames with exactly 1 play line → idle (False)."""
        # Simulate automation.py: each call appends 1 frame, history grows
        # Call 1-2: _last_4_lines was '' so no increment
        # Call 3-6: 4 increments → need call 7 for unchanged_count=5
        # Need 7 frames so call 7 (i=6) is the 5th consecutive unchanged
        frames = [_above_prompt(["⏺ 你好！"])] * 7
        history: list[str] = []
        for i in range(7):
            history.append(frames[i])
            result = self.adapter.is_task_processing(history)
            if i == 6:  # 7th call = 5 consecutive unchanged
                assert result is False, f"Call {i + 1} should be idle, got {result}"

    def test_five_unchanged_zero_play_is_processing(self) -> None:
        """5 unchanged but 0 play lines → processing (True)."""
        frames = [_above_prompt(["其他内容"])] * 6
        assert self.adapter.is_task_processing(frames) is True

    def test_five_unchanged_two_play_is_processing(self) -> None:
        """5 unchanged but 2 play lines → processing (True)."""
        frames = [
            _above_prompt(["⏺ line1", "⏺ line2"]),
            _above_prompt(["⏺ line1", "⏺ line2"]),
            _above_prompt(["⏺ line1", "⏺ line2"]),
            _above_prompt(["⏺ line1", "⏺ line2"]),
            _above_prompt(["⏺ line1", "⏺ line2"]),
            _above_prompt(["⏺ line1", "⏺ line2"]),
        ]
        assert self.adapter.is_task_processing(frames) is True

    def test_not_5_unchanged_even_with_1_play_is_processing(self) -> None:
        """Only 4 unchanged but 1 play line → still processing (need 5)."""
        frames = [_above_prompt(["⏺ 你好！"])] * 5
        assert self.adapter.is_task_processing(frames) is True

    def test_5_unchanged_but_1_play_in_last_4_only(self) -> None:
        """5 unchanged, only 1 play line in last 4 → idle."""
        # Need 7 frames for unchanged_count to reach 5 (call 1-2 no increment, call 3-7 increment)
        frames = [_above_prompt(["⏺ 你好！"])] * 7
        history: list[str] = []
        for i in range(7):
            history.append(frames[i])
            result = self.adapter.is_task_processing(history)
            if i == 6:
                assert result is False, f"Call {i + 1} should be idle, got {result}"

    def test_5_unchanged_but_play_lines_in_last_4(self) -> None:
        """5 unchanged but last 4 lines have more than 1 play → processing."""
        frames = [_above_prompt(["前内容", "前内容", "前内容", "⏺ a", "⏺ b"])] * 6
        assert self.adapter.is_task_processing(frames) is True

    def test_change_resets_counter(self) -> None:
        """Frame change resets unchanged counter."""
        # 5 identical frames with 1 play line
        frames = [_above_prompt(["⏺ 你好！"])] * 5
        # Next frame changes
        frames.append(_above_prompt(["⏺ 你好！！"]))
        # Counter reset, so not idle even though we have 5 before change
        assert self.adapter.is_task_processing(frames) is True

    def test_last_4_lines_only_count(self) -> None:
        """Only lines in last 4 count for play detection."""
        # Only last 4 lines matter
        frames = [_above_prompt(["a", "b", "c", "d", "⏺ 第5行"])] * 6
        # 第5行 is beyond last 4, count is 0
        assert self.adapter.is_task_processing(frames) is True

    def test_5_unchanged_last4_has_1_play_in_middle(self) -> None:
        """Last 4 has 1 play line in middle, 5 unchanged → idle (False)."""
        # Need 7 frames for unchanged_count to reach 5 (call 1-2 no increment, call 3-7 increment)
        frames = [_above_prompt(["header", "⏺ mid", "footer"])] * 7
        history: list[str] = []
        for i in range(7):
            history.append(frames[i])
            result = self.adapter.is_task_processing(history)
            if i == 6:
                assert result is False, f"Call {i + 1} should be idle, got {result}"

    def test_5_unchanged_2_play_lines_in_last4(self) -> None:
        """Last 4 has 2 play lines, 5 unchanged → processing."""
        frames = [_above_prompt(["⏺ line1", "normal", "⏺ line2"])] * 6
        assert self.adapter.is_task_processing(frames) is True
