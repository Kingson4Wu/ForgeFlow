from forgeflow.rules.base import Command, Rule, RuleEngine, build_default_rules


class FakePostProcessor:
    def post_process_command(self, output: str, initial: str | None) -> str | None:
        if initial == "continue":
            return "modified"
        return None


class TestRuleEngine:
    def test_match_returns_command(self):
        engine = RuleEngine(
            [
                Rule(
                    check=lambda s: "error" in s,
                    command=Command("/clear"),
                    description="clear on error",
                ),
            ]
        )
        result = engine.resolve("there is an error", "gemini")
        assert result == "/clear"

    def test_no_match_returns_continue(self):
        engine = RuleEngine([])
        result = engine.resolve("all good", "gemini")
        assert result == "continue"

    def test_none_command_returns_none(self):
        engine = RuleEngine(
            [
                Rule(check=lambda s: "stop" in s, command=Command(None), description="stop"),
            ]
        )
        result = engine.resolve("please stop", "gemini")
        assert result is None

    def test_exception_in_rule_is_ignored(self):
        engine = RuleEngine(
            [
                Rule(check=lambda s: 1 / 0, command=Command("bad"), description="bad rule"),
                Rule(check=lambda s: "ok" in s, command=Command("yes"), description="fallback"),
            ]
        )
        result = engine.resolve("ok", "gemini")
        assert result == "yes"

    def test_post_processor_modifies_command(self):
        engine = RuleEngine([], post_processors={"gemini": FakePostProcessor()})
        result = engine.resolve("anything", "gemini")
        assert result == "modified"

    def test_post_processor_unchanged_returns_initial(self):
        engine = RuleEngine(
            [
                Rule(check=lambda s: "x" in s, command=Command("do_it")),
            ],
            post_processors={"gemini": FakePostProcessor()},
        )
        result = engine.resolve("x", "gemini")
        assert result == "do_it"

    def test_build_default_rules_gemini(self):
        rules = build_default_rules("gemini")
        assert len(rules) > 0

    def test_build_default_rules_claude_code(self):
        rules = build_default_rules("claude_code")
        assert len(rules) > 0

    def test_build_default_rules_codex(self):
        rules = build_default_rules("codex")
        assert len(rules) > 0
