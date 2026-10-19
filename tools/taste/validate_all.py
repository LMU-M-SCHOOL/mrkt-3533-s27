"""Validate every archive entry, including that its filename matches its frontmatter.

Usage: python -m tools.taste.validate_all taste/archive
Exit status 1 when any entry has a problem.
"""
from __future__ import annotations

import sys
from pathlib import Path

from tools.taste.index_gen import collect
from tools.taste.schema import ValidationError, validate
from tools.taste.slug import entry_filename


def validate_all(archive_dir: Path) -> list[tuple[Path, str]]:
    problems: list[tuple[Path, str]] = []
    try:
        entries = collect(Path(archive_dir))
    except ValidationError as exc:
        return [(Path(archive_dir), str(exc))]
    for entry in entries:
        for msg in validate(entry):
            problems.append((entry.path, msg))
        try:
            expected = entry_filename(entry)
        except (ValueError, AttributeError):
            continue
        if entry.path.name != expected:
            problems.append((entry.path, f"filename should be {expected} to match the frontmatter"))
    return problems


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m tools.taste.validate_all <archive-dir>")
    found = validate_all(Path(sys.argv[1]))
    for path, msg in found:
        print(f"{path}: {msg}")
    print(f"{len(found)} problem(s)" if found else "all entries valid")
    sys.exit(1 if found else 0)
