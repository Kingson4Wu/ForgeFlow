import re

from forgeflow.rules.base import Command, Rule


def build_rules() -> list[Rule]:
    """Build rules specific to Gemini CLI."""
    return [
        Rule(
            check=lambda out: bool(
                re.search(
                    r"✕ \[API Error: 400 <400> InternalError\.Algo\.InvalidParameter:.*",
                    out,
                    re.DOTALL,
                )
            ),
            command=Command("/clear"),
            description="Invalid parameter error - send /clear command",
        ),
        Rule(
            check=lambda out: "tool_call" in out
            and ("must be followed" in out or "did not have" in out),
            command=Command("/clear"),
            description="Tool call error - send /clear command",
        ),
        Rule(
            check=lambda out: re.search(
                r"✕ \[API Error: .* API quota exceeded: Your .* API quota has been exhausted\. Please wait for your quota to reset\.\]",
                out,
            )
            is not None,
            command=Command(None),
            description="API quota exceeded - stop automation",
        ),
        Rule(
            check=lambda out: re.search(
                r"\[API Error.*You exceeded your current quota, please check your plan and billing details",
                " ".join(out.split()),
            )
            is not None,
            command=Command(None),
            description="API quota exceeded [new] - stop automation",
        ),
        Rule(
            check=lambda out: "✕ [API Error: terminated]" in out,
            command=Command("continue"),
            description="API terminated error - continue execution",
        ),
        Rule(
            check=lambda out: "API Error" in out,
            command=Command("continue"),
            description="General API error - continue execution",
        ),
    ]
