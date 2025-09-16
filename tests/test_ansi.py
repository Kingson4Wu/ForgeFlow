from forgeflow.core.ansi import Style, parse_ansi_segments, split_segments_lines, strip_ansi


def test_strip_ansi_basic():
    s = "Hello \x1b[31mred\x1b[0m world\n\x1b[1mBold\x1b[22m!"
    assert strip_ansi(s) == "Hello red world\nBold!"


def test_parse_segments_basic_colors():
    s = "X \x1b[31mred\x1b[0m Y"
    segs = parse_ansi_segments(s)
    assert [seg.text for seg in segs] == ["X ", "red", " Y"]
    # Middle segment should be red (basic fg 31)
    assert segs[1].style.fg_basic == 31
    # Other segments have default style
    assert segs[0].style == Style.default()
    assert segs[2].style == Style.default()


def test_parse_segments_attributes_and_reset():
    s = "\x1b[1;4mBU\x1b[22m still_ul \x1b[24m plain"
    segs = parse_ansi_segments(s)
    # Expect segments: ["", "BU", " still_ul ", " plain"] where first may be empty
    texts = [seg.text for seg in segs if seg.text]
    assert "BU" in texts
    # Segment with "BU" must be bold and underline
    seg_bu = next(seg for seg in segs if seg.text == "BU")
    assert seg_bu.style.bold is True
    assert seg_bu.style.underline is True
    # After 22, bold off; after 24, underline off
    seg_plain = segs[-1]
    assert seg_plain.style.bold is False
    assert seg_plain.style.underline is False


def test_parse_segments_256_and_truecolor():
    s = "\x1b[38;5;196mERR\x1b[0m and \x1b[48;2;10;20;30mBG\x1b[0m"
    segs = parse_ansi_segments(s)
    # Find ERR segment
    seg_err = next(seg for seg in segs if seg.text == "ERR")
    assert seg_err.style.fg_256 == 196
    # Find BG segment
    seg_bg = next(seg for seg in segs if seg.text == "BG")
    assert seg_bg.style.bg_truecolor == (10, 20, 30)


def test_split_segments_lines():
    s = "Line1\n\x1b[31mLine2\x1b[0m\nLine3"
    lines = split_segments_lines(parse_ansi_segments(s))
    assert len(lines) == 3
    # Line2 should be red
    segs_l2 = lines[1]
    assert len(segs_l2) == 1
    assert segs_l2[0].text == "Line2"
    assert segs_l2[0].style.fg_basic == 31
