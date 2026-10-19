import re
import zipfile
from pathlib import Path

import pytest

from conftest import write_entry
from tools.taste.export import export


@pytest.fixture
def taste_root(tmp_path: Path) -> Path:
    root = tmp_path / "taste"
    write_entry(root / "archive" / "2026" / "2026-10-07-visit-sweden-GL.md")
    write_entry(root / "archive" / "2027" / "2027-01-20-pringles-CD.md", brand="Pringles", student="CD",
                published="2027-01-20", submitted="2027-01-22")
    (root / "README.md").write_text("# Teardowns\n")
    (root / "seen-log").mkdir()
    (root / "seen-log" / "GL.txt").write_text("2027-01-20 | s | t | https://e.com\n")
    (root / "calibration").mkdir()
    (root / "calibration" / "scores.csv").write_text("piece_id,rater,round,insight,idea,execution,results\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[user]\n\temail = greg@example.edu\n")
    return root


def names(z: Path) -> set[str]:
    with zipfile.ZipFile(z) as zf:
        return set(zf.namelist())


def test_export_contains_entries_and_indexes(taste_root, tmp_path):
    out = tmp_path / "archive.zip"
    export(taste_root / "archive", out)
    assert {"archive/2026/2026-10-07-visit-sweden-GL.md", "archive/2027/2027-01-20-pringles-CD.md",
            "archive/index.md", "archive/index.html", "README.md"} <= names(out)


def test_export_excludes_git_seenlog_and_calibration(taste_root, tmp_path):
    out = tmp_path / "archive.zip"
    export(taste_root / "archive", out)
    assert not any(n.startswith((".git", "seen-log", "calibration")) or "scores.csv" in n for n in names(out))


def test_export_entries_contain_no_email_addresses(taste_root, tmp_path):
    out = tmp_path / "archive.zip"
    export(taste_root / "archive", out)
    with zipfile.ZipFile(out) as zf:
        for n in zf.namelist():
            assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", zf.read(n).decode("utf-8")), n


def test_export_returns_count(taste_root, tmp_path):
    assert export(taste_root / "archive", tmp_path / "archive.zip") == 2
