import json
import re
from pathlib import Path

import pytest

from conftest import write_entry
from tools.taste.index_gen import collect, write_html_index, write_markdown_index

HEADER = "| Published | Brand | Maker | Medium | Student | Gate | Insight | Idea | Execution | Results | Class mean |"


@pytest.fixture
def three(archive: Path) -> Path:
    write_entry(archive / "2026" / "2026-10-07-visit-sweden-GL.md")
    write_entry(archive / "2026" / "2026-09-01-oura-AB.md", brand="Oura", student="AB",
                published="2026-09-01", gate="fail",
                scores={"insight": None, "idea": None, "execution": None, "results": None})
    write_entry(archive / "2027" / "2027-01-20-pringles-CD.md", brand="Pringles", student="CD",
                published="2027-01-20", submitted="2027-01-22",
                class_scores={"insight": 3, "idea": 5, "execution": 4, "results": 4})
    (archive / "index.md").write_text("stale")
    (archive / "index.html").write_text("stale")
    return archive


def test_collect_sorted_newest_first(three):
    assert [e.brand for e in collect(three)] == ["Pringles", "Visit Sweden", "Oura"]


def test_collect_skips_index_files(three):
    assert len(collect(three)) == 3


def test_markdown_index_has_one_row_per_entry(three, tmp_path):
    out = tmp_path / "index.md"
    write_markdown_index(collect(three), out)
    lines = out.read_text().splitlines()
    assert HEADER in lines
    rows = [l for l in lines[lines.index(HEADER) + 2:] if l.startswith("|")]
    assert len(rows) == 3


def test_markdown_index_shows_dash_for_unscored(three, tmp_path):
    out = tmp_path / "index.md"
    write_markdown_index(collect(three), out)
    row = next(l for l in out.read_text().splitlines() if "Oura" in l)
    cells = [c.strip() for c in row.strip("|").split("|")]
    assert cells[6:10] == ["–", "–", "–", "–"]


def test_markdown_index_class_mean(three, tmp_path):
    out = tmp_path / "index.md"
    write_markdown_index(collect(three), out)
    row = next(l for l in out.read_text().splitlines() if "Pringles" in l)
    assert row.strip("|").split("|")[-1].strip() == "4.0"


def test_html_index_embeds_json(three, tmp_path):
    out = tmp_path / "index.html"
    write_html_index(collect(three), out)
    html = out.read_text()
    m = re.search(r'<script id="entries" type="application/json">(.*?)</script>', html, re.S)
    assert m
    data = json.loads(m.group(1))
    assert len(data) == 3
    assert set(data[0]) >= {"brand", "maker", "published", "medium", "student", "gate", "scores", "class_scores", "tags", "path"}


def test_html_index_has_filter_controls(three, tmp_path):
    out = tmp_path / "index.html"
    write_html_index(collect(three), out)
    html = out.read_text()
    for fid in ("filter-medium", "filter-student", "filter-gate", "filter-month"):
        assert f'id="{fid}"' in html
    assert "<script src=" not in html


def test_collect_tolerates_unparseable_published_date(archive: Path):
    write_entry(archive / "2026" / "a.md")
    write_entry(archive / "2026" / "b.md", brand="Bad", published="not-a-date")
    assert len(collect(archive)) == 2
