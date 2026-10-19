from datetime import date
from pathlib import Path

import pytest

from tools.taste.seenlog import check, parse_log, weekly_counts

LINE = "2027-01-20 | Ads of the World | Visit Sweden: The Introvert Travel Agency | https://www.adsoftheworld.com/x"
TERM = date(2027, 1, 19)  # a Tuesday


def lines(n: int, day: str) -> str:
    return "\n".join(f"{day} | Source | Title {i} | https://e.com/{i}" for i in range(n)) + "\n"


def test_parse_log_splits_four_fields(tmp_path):
    p = tmp_path / "GL.txt"
    p.write_text(LINE + "\n")
    [s] = parse_log(p)
    assert (s.date, s.source, s.title, s.url) == (
        date(2027, 1, 20), "Ads of the World", "Visit Sweden: The Introvert Travel Agency", "https://www.adsoftheworld.com/x")


def test_parse_log_rejects_malformed_line(tmp_path):
    p = tmp_path / "GL.txt"
    p.write_text(LINE + "\nnot a log line\n")
    with pytest.raises(ValueError) as exc:
        parse_log(p)
    assert "line 2" in str(exc.value)


def test_weekly_counts_groups_by_term_week(tmp_path):
    p = tmp_path / "GL.txt"
    p.write_text(lines(2, "2027-01-20") + lines(3, "2027-01-27"))
    assert weekly_counts(parse_log(p), TERM) == {1: 2, 2: 3}


def test_check_reports_student_and_week_under_minimum(tmp_path):
    (tmp_path / "GL.txt").write_text(lines(14, "2027-01-27"))
    assert check(tmp_path, TERM) == ["GL week 2: 14 of 15"]


def test_check_passes_at_minimum(tmp_path):
    (tmp_path / "GL.txt").write_text(lines(15, "2027-01-27"))
    assert check(tmp_path, TERM) == []


def test_check_does_not_modify_log(tmp_path):
    p = tmp_path / "GL.txt"
    p.write_text(lines(3, "2027-01-27"))
    before = p.read_bytes()
    check(tmp_path, TERM)
    assert p.read_bytes() == before


def test_check_ignores_non_txt_files(tmp_path):
    (tmp_path / ".gitkeep").write_text("")
    (tmp_path / "GL.txt").write_text(lines(15, "2027-01-27"))
    assert check(tmp_path, TERM) == []
