from forgeflow.core.rules import Rule


def build_rules() -> list[Rule]:
    """Build rules specific to Gemini CLI."""
    return [
        Rule(
            check=lambda out: "✕ [API Error: 400 <400> InternalError.Algo.InvalidParameter" in out,
            command="/clear",
        ),
        Rule(check=lambda out: "✕ [API Error: terminated]" in out, command="continue"),
        Rule(check=lambda out: "API Error" in out, command="continue"),
    ]
