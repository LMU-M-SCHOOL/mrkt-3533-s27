from pathlib import Path

import pytest

from conftest import sample_entry_text, write_entry
from tools.taste.schema import load_entry, validate


def errs(tmp_path: Path, **kw) -> list[str]:
    p = write_entry(tmp_path / "e.md", **kw)
    return validate(load_entry(p))


def test_valid_entry_has_no_errors(tmp_path):
    assert errs(tmp_path) == []


def test_gate_fail_with_scores_rejected(tmp_path):
    e = errs(tmp_path, gate="fail", scores={"insight": 3, "idea": None, "execution": None, "results": None})
    assert any("gate" in m for m in e)


def test_gate_fail_with_null_scores_ok(tmp_path):
    e = errs(tmp_path, gate="fail", scores={"insight": None, "idea": None, "execution": None, "results": None})
    assert e == []


def test_score_out_of_range_rejected(tmp_path):
    e = errs(tmp_path, scores={"insight": 4, "idea": 6, "execution": 4, "results": 4})
    assert any("1 to 5" in m for m in e)


def test_published_older_than_365_days_rejected(tmp_path):
    e = errs(tmp_path, published="2025-10-01", submitted="2026-10-19")
    assert any("365" in m for m in e)


def test_calibration_exempt_from_recency(tmp_path):
    e = errs(tmp_path, published="2025-10-01", submitted="2026-10-19", calibration=True)
    assert e == []


def test_initials_must_be_2_or_3_uppercase(tmp_path):
    e = errs(tmp_path, student="greg")
    assert any("initials" in m for m in e)


def test_medium_must_be_in_list(tmp_path):
    e = errs(tmp_path, medium="tv")
    assert any("medium" in m for m in e)


def test_missing_heading_rejected(tmp_path):
    body = "\n\n".join(f"## {s}\n\nwords here" for s in ("Gate", "Insight", "Idea", "Execution", "What I'd change"))
    e = errs(tmp_path, body=body)
    assert any("Results" in m for m in e)


def test_body_over_800_words_rejected(tmp_path):
    body = "\n\n".join(f"## {s}\n\n" + " ".join(["w"] * 150) for s in ("Gate", "Insight", "Idea", "Execution", "Results", "What I'd change"))
    e = errs(tmp_path, body=body)
    assert any("800" in m for m in e)


def test_source_url_must_be_http(tmp_path):
    e = errs(tmp_path, source_url="ads.com")
    assert any("source_url" in m for m in e)
