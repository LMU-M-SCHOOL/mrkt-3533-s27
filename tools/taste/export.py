"""Export the archive for sharing beyond the class, with no git metadata.

The zip holds the entries, both indexes, and taste/README.md. Nothing else:
no .git, no seen-logs, no calibration scores. Indexes are regenerated into
a temporary folder so the export never touches the working tree.
Usage: python -m tools.taste.export taste/archive out/teardowns.zip
"""
from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

from tools.taste.index_gen import collect, write_html_index, write_markdown_index


def export(archive_dir: Path, out_zip: Path) -> int:
    archive_dir = Path(archive_dir)
    entries = collect(archive_dir)
    readme = archive_dir.parent / "README.md"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_archive = Path(tmp) / "archive"
        tmp_archive.mkdir()
        # copy entries so index links resolve relative to the temp archive
        for e in entries:
            rel = e.path.relative_to(archive_dir)
            (tmp_archive / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_archive / rel).write_bytes(e.path.read_bytes())
        tmp_entries = collect(tmp_archive)
        write_markdown_index(tmp_entries, tmp_archive / "index.md")
        write_html_index(tmp_entries, tmp_archive / "index.html")
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(tmp_archive.rglob("*")):
                if p.is_file():
                    zf.write(p, "archive/" + p.relative_to(tmp_archive).as_posix())
            if readme.exists():
                zf.write(readme, "README.md")
    return len(entries)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python -m tools.taste.export <archive-dir> <out.zip>")
    n = export(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"exported {n} entries to {sys.argv[2]}")
