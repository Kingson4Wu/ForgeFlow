from forgeflow.state import UnchangedTracker


class TestUnchangedTracker:
    def test_detects_unchanged_after_threshold(self):
        tracker = UnchangedTracker(threshold=3)
        assert tracker.is_unchanged_too_long("same") is False
        assert tracker.is_unchanged_too_long("same") is False
        assert tracker.is_unchanged_too_long("same") is False
        assert tracker.is_unchanged_too_long("same") is True

    def test_resets_on_change(self):
        tracker = UnchangedTracker(threshold=3)
        assert tracker.is_unchanged_too_long("a") is False
        assert tracker.is_unchanged_too_long("a") is False
        assert tracker.is_unchanged_too_long("b") is False
        assert tracker.is_unchanged_too_long("b") is False
        assert tracker.is_unchanged_too_long("b") is False
        assert tracker.is_unchanged_too_long("b") is True

    def test_reset_clears_state(self):
        tracker = UnchangedTracker(threshold=2)
        tracker.is_unchanged_too_long("x")
        tracker.is_unchanged_too_long("x")
        tracker.reset()
        assert tracker.is_unchanged_too_long("x") is False

    def test_default_threshold_is_five(self):
        tracker = UnchangedTracker()
        for _ in range(5):
            assert tracker.is_unchanged_too_long("same") is False
        assert tracker.is_unchanged_too_long("same") is True
