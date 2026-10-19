from pathlib import Path

import pytest

from tools.taste.calibrate import Score, anchor, drift, load_scores, report

HEADER = "piece_id,rater,round,insight,idea,execution,results\n"


def S(piece, rater, rnd, *vals) -> Score:
    return Score(piece, rater, rnd, *vals)


def test_load_scores_parses_csv(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text(HEADER + "p1,MS,0,4,3,5,2\n")
    assert load_scores(p) == [S("p1", "MS", 0, 4, 3, 5, 2)]


def test_anchor_is_mean_of_named_raters():
    scores = [S("p1", "MS", 0, 4, 4, 4, 4), S("p1", "AR", 0, 2, 2, 2, 2), S("p1", "GL", 1, 5, 5, 5, 5)]
    assert anchor(scores, ["MS", "AR"])["p1"]["insight"] == 3.0


def test_drift_mean_absolute_difference():
    scores = [S("p1", "GL", 1, 5, 5, 5, 5)]
    a = {"p1": {"insight": 3.0, "idea": 3.0, "execution": 3.0, "results": 3.0}}
    assert drift(scores, a, "GL", 1) == 2.0


def test_drift_ignores_pieces_without_anchor():
    scores = [S("p1", "GL", 1, 5, 5, 5, 5), S("p2", "GL", 1, 1, 1, 1, 1)]
    a = {"p1": {"insight": 3.0, "idea": 3.0, "execution": 3.0, "results": 3.0}}
    assert drift(scores, a, "GL", 1) == 2.0


def test_anchor_falls_back_to_class_mean_when_no_director_scores():
    scores = [S("p1", "GL", 3, 4, 4, 4, 4), S("p1", "AB", 3, 2, 2, 2, 2), S("p1", "GL", 1, 5, 5, 5, 5)]
    assert anchor(scores, [])["p1"]["idea"] == 3.0


def test_report_rows_are_students_and_columns_are_rounds(tmp_path):
    p = tmp_path / "scores.csv"
    p.write_text(HEADER + "p1,MS,0,3,3,3,3\np1,GL,1,5,5,5,5\np1,GL,2,4,4,4,4\np1,AB,1,3,3,3,3\n")
    out = tmp_path / "drift.md"
    report(p, ["MS"], out)
    lines = out.read_text().splitlines()
    assert "| Student | Round 1 | Round 2 | Round 3 |" in lines
    assert "| AB | 0.00 | – | – |" in lines
    assert "| GL | 2.00 | 1.00 | – |" in lines
