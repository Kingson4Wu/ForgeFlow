from __future__ import annotations

import re
from dataclasses import dataclass, replace

# General ANSI escape pattern (CSI and others). Useful for stripping.
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

# Only SGR sequences (Select Graphic Rendition) that end with 'm'
SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")


@dataclass(eq=True)
class Style:
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    inverse: bool = False
    strike: bool = False

    # Foreground color representations (choose one)
    fg_basic: int | None = None  # 30-37, 90-97
    fg_256: int | None = None  # 0-255
    fg_truecolor: tuple[int, int, int] | None = None  # (r, g, b)

    # Background color representations (choose one)
    bg_basic: int | None = None  # 40-47, 100-107
    bg_256: int | None = None  # 0-255
    bg_truecolor: tuple[int, int, int] | None = None  # (r, g, b)

    @staticmethod
    def default() -> Style:
        return Style()

    def reset_colors(self) -> Style:
        return replace(
            self,
            fg_basic=None,
            fg_256=None,
            fg_truecolor=None,
            bg_basic=None,
            bg_256=None,
            bg_truecolor=None,
        )

    def reset_all(self) -> Style:
        return Style.default()


@dataclass(eq=True)
class Segment:
    text: str
    style: Style


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences from text."""
    return ANSI_RE.sub("", s)


def _apply_sgr_params(style: Style, params: list[int]) -> Style:
    i = 0
    # Work on a mutable copy
    cur = Style(
        bold=style.bold,
        dim=style.dim,
        italic=style.italic,
        underline=style.underline,
        blink=style.blink,
        inverse=style.inverse,
        strike=style.strike,
        fg_basic=style.fg_basic,
        fg_256=style.fg_256,
        fg_truecolor=style.fg_truecolor,
        bg_basic=style.bg_basic,
        bg_256=style.bg_256,
        bg_truecolor=style.bg_truecolor,
    )

    while i < len(params):
        p = params[i]
        i += 1

        if p == 0:
            cur = cur.reset_all()
        elif p == 1:
            cur.bold = True
        elif p == 2:
            cur.dim = True
        elif p == 3:
            cur.italic = True
        elif p == 4:
            cur.underline = True
        elif p == 5:
            cur.blink = True
        elif p == 7:
            cur.inverse = True
        elif p == 9:
            cur.strike = True

        # Attribute resets
        elif p == 22:
            cur.bold = False
            cur.dim = False
        elif p == 23:
            cur.italic = False
        elif p == 24:
            cur.underline = False
        elif p == 25:
            cur.blink = False
        elif p == 27:
            cur.inverse = False
        elif p == 29:
            cur.strike = False

        # Foreground basic 30-37, 90-97; reset 39
        elif 30 <= p <= 37 or 90 <= p <= 97:
            cur.fg_basic = p
            cur.fg_256 = None
            cur.fg_truecolor = None
        elif p == 39:
            cur.fg_basic = None
            cur.fg_256 = None
            cur.fg_truecolor = None

        # Background basic 40-47, 100-107; reset 49
        elif 40 <= p <= 47 or 100 <= p <= 107:
            cur.bg_basic = p
            cur.bg_256 = None
            cur.bg_truecolor = None
        elif p == 49:
            cur.bg_basic = None
            cur.bg_256 = None
            cur.bg_truecolor = None

        # Extended colors: 38 (fg) / 48 (bg)
        elif p in (38, 48):
            is_fg = p == 38
            if i >= len(params):
                break
            mode = params[i]
            i += 1
            if mode == 5 and i < len(params):
                # 256-color
                idx = params[i]
                i += 1
                if is_fg:
                    cur.fg_basic = None
                    cur.fg_truecolor = None
                    cur.fg_256 = idx
                else:
                    cur.bg_basic = None
                    cur.bg_truecolor = None
                    cur.bg_256 = idx
            elif mode == 2 and i + 2 < len(params):
                # truecolor r;g;b
                r, g, b = params[i], params[i + 1], params[i + 2]
                i += 3
                if is_fg:
                    cur.fg_basic = None
                    cur.fg_256 = None
                    cur.fg_truecolor = (r, g, b)
                else:
                    cur.bg_basic = None
                    cur.bg_256 = None
                    cur.bg_truecolor = (r, g, b)
            else:
                # Unsupported mode, skip gracefully
                pass
        else:
            # Unhandled parameter; ignore to be robust
            pass

    return cur


def parse_ansi_segments(text: str) -> list[Segment]:
    """Parse text into segments where each segment holds a snapshot of the active SGR style.

    Non-SGR escape sequences are kept in text. This function focuses on SGR (…m) only.
    """
    segments: list[Segment] = []
    cur_style = Style.default()
    pos = 0

    for m in SGR_RE.finditer(text):
        start, end = m.span()
        if start > pos:
            # Emit text before this SGR code with current style
            segments.append(Segment(text=text[pos:start], style=cur_style))

        params_str = m.group(1)
        if params_str == "":
            params = [0]
        else:
            try:
                params = [int(x) for x in params_str.split(";") if x != ""]
            except ValueError:
                params = [0]

        cur_style = _apply_sgr_params(cur_style, params)
        pos = end

    if pos < len(text):
        segments.append(Segment(text=text[pos:], style=cur_style))

    return segments


def split_segments_lines(segments: list[Segment]) -> list[list[Segment]]:
    """Split segments by newline, preserving styles across line splits."""
    lines: list[list[Segment]] = []
    current: list[Segment] = []
    for seg in segments:
        parts = seg.text.split("\n")
        for idx, part in enumerate(parts):
            if part:
                current.append(Segment(text=part, style=seg.style))
            if idx != len(parts) - 1:
                lines.append(current)
                current = []
    lines.append(current)
    return lines
