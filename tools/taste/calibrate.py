"""Calibration drift: how far each student's scores sit from the anchor.

CSV: piece_id,rater,round,insight,idea,execution,results. Directors use round 0.
Anchor is the mean of the named raters per piece and section. With no
director scores, the anchor falls back to the round-3 class mean (spec).
Usage: python -m tools.taste.calibrate taste/calibration/scores.csv MS,AR taste/calibration/drift.md
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.taste.schema import SCORE_KEYS

ROUNDS = (1, 2, 3)
FALLBACK_ROUND = 3
DASH = "–"


@dataclass(frozen=True)
class Score:
    piece_id: str
    rater: str
    round: int
    insight: int
    idea: int
    execution: int
    results: int

    def section(self, key: str) -> int:
        return getattr(self, key)


def load_scores(csv_path: Path) -> list[Score]:
    with Path(csv_path).open(newline="", encoding="utf-8") as f:
        return [Score(r["piece_id"], r["rater"], int(r["round"]),
                      *(int(r[k]) for k in SCORE_KEYS)) for r in csv.DictReader(f)]


def anchor(scores: list[Score], raters: list[str]) -> dict[str, dict[str, float]]:
    if raters:
        chosen = [s for s in scores if s.rater in raters]
    else:
        chosen = [s for s in scores if s.round == FALLBACK_ROUND]
    out: dict[str, dict[str, float]] = {}
    for piece in {s.piece_id for s in chosen}:
        rows = [s for s in chosen if s.piece_id == piece]
        out[piece] = {k: sum(s.section(k) for s in rows) / len(rows) for k in SCORE_KEYS}
    return out


def drift(scores: list[Score], anchor_scores: dict[str, dict[str, float]], rater: str, round: int) -> float | None:
    diffs = [abs(s.section(k) - anchor_scores[s.piece_id][k])
             for s in scores if s.rater == rater and s.round == round and s.piece_id in anchor_scores
             for k in SCORE_KEYS]
    return sum(diffs) / len(diffs) if diffs else None


def report(csv_path: Path, anchor_raters: list[str], out: Path) -> None:
    scores = load_scores(csv_path)
    a = anchor(scores, anchor_raters)
    students = sorted({s.rater for s in scores if s.round in ROUNDS})
    lines = ["# Calibration drift", "",
             "Mean absolute distance from the anchor across the calibration set and the four sections. Lower is closer to the house taste.", "",
             "| Student | " + " | ".join(f"Round {r}" for r in ROUNDS) + " |",
             "|---|" + "---|" * len(ROUNDS)]
    for st in students:
        cells = []
        for r in ROUNDS:
            d = drift(scores, a, st, r)
            cells.append(DASH if d is None else f"{d:.2f}")
        lines.append(f"| {st} | " + " | ".join(cells) + " |")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: python -m tools.taste.calibrate <scores.csv> <anchor-raters,comma-separated-or-empty> <out.md>")
    raters = [r for r in sys.argv[2].split(",") if r]
    report(Path(sys.argv[1]), raters, Path(sys.argv[3]))
    print(f"wrote {sys.argv[3]}")
