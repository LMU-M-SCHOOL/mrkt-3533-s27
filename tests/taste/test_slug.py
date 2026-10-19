from datetime import date
from pathlib import Path

import pytest

from conftest import write_entry
from tools.taste.schema import load_entry
from tools.taste.slug import entry_filename, slugify


@pytest.mark.parametrize("raw,expected", [
    ("Lürzer's Archive", "lurzers-archive"),
    ("e.l.f. Cosmetics", "elf-cosmetics"),
    ("  Visit  Sweden ", "visit-sweden"),
    ("McDonald's", "mcdonalds"),
    ("Chanel  / Coco Neige 2026", "chanel-coco-neige-2026"),
])
def test_slugify(raw, expected):
    assert slugify(raw) == expected


def test_entry_filename(tmp_path: Path):
    entry = load_entry(write_entry(tmp_path / "x.md", published="2026-10-07", brand="Visit Sweden", student="GL"))
    assert entry_filename(entry) == "2026-10-07-visit-sweden-GL.md"


def test_slugify_empty_raises():
    with pytest.raises(ValueError):
        slugify("!!!")
