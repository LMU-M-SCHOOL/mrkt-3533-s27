from pathlib import Path

from conftest import write_entry
from tools.taste.validate_all import validate_all


def test_validate_all_returns_empty_for_valid_archive(archive: Path):
    write_entry(archive / "2026" / "2026-10-07-visit-sweden-GL.md")
    assert validate_all(archive) == []


def test_validate_all_lists_path_and_message_for_bad_entry(archive: Path):
    p = write_entry(archive / "2026" / "2026-10-07-visit-sweden-GL.md", medium="tv")
    [(path, msg)] = validate_all(archive)
    assert path == p
    assert "medium" in msg


def test_validate_all_flags_filename_not_matching_frontmatter(archive: Path):
    write_entry(archive / "2026" / "2026-10-07-visit-sweden-GL.md", student="AB")
    msgs = [m for _, m in validate_all(archive)]
    assert any("filename" in m for m in msgs)


def test_validate_all_skips_index_files(archive: Path):
    write_entry(archive / "2026" / "2026-10-07-visit-sweden-GL.md")
    (archive / "index.md").write_text("# index")
    assert validate_all(archive) == []
