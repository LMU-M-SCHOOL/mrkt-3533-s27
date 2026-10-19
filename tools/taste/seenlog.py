"""Check that each student's seen-log meets the weekly minimum.

Line format: YYYY-MM-DD | source | title | url
Usage: python -m tools.taste.seenlog taste/seen-log 2027-01-19 [minimum] [through-week]
Exit status 1 when any student-week is under the minimum. Logs are never modified.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

MINIMUM = 15


@dataclass(frozen=True)
class SeenLine:
    date: date
    source: str
    title: str
    url: str


def parse_log(path: Path) -> list[SeenLine]:
    out: list[SeenLine] = []
    for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) != 4:
            raise ValueError(f"{path}: line {n} must have four fields separated by |: {raw!r}")
        try:
            d = datetime.strptime(parts[0], "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f"{path}: line {n} has a bad date {parts[0]!r}") from exc
        out.append(SeenLine(d, parts[1], parts[2], parts[3]))
    return out


def weekly_counts(lines: list[SeenLine], term_start: date) -> dict[int, int]:
    counts: dict[int, int] = {}
    for s in lines:
        week = (s.date - term_start).days // 7 + 1
        counts[week] = counts.get(week, 0) + 1
    return counts


FIRST_WEEK = 2  # week 1 is a calibration round with no teardown, per taste/ramp.md


def check(log_dir: Path, term_start: date, minimum: int = MINIMUM, through: int | None = None,
          first_week: int = FIRST_WEEK) -> list[str]:
    """Report every student-week under the minimum, including weeks with no lines.

    Weeks run from `first_week` through `through`, or through the latest week present in
    the student's log when `through` is not given.
    """
    messages: list[str] = []
    for p in sorted(Path(log_dir).glob("*.txt")):
        student = p.stem
        counts = weekly_counts(parse_log(p), term_start)
        last = through if through is not None else max(counts, default=0)
        for week in range(first_week, last + 1):
            n = counts.get(week, 0)
            if n < minimum:
                messages.append(f"{student} week {week}: {n} of {minimum}")
    return messages


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4, 5):
        sys.exit("usage: python -m tools.taste.seenlog <log-dir> <term-start YYYY-MM-DD> [minimum] [through-week]")
    start = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
    mn = int(sys.argv[3]) if len(sys.argv) >= 4 else MINIMUM
    thr = int(sys.argv[4]) if len(sys.argv) == 5 else None
    msgs = check(Path(sys.argv[1]), start, mn, thr)
    print("\n".join(msgs) if msgs else "all seen-logs meet the minimum")
    sys.exit(1 if msgs else 0)
