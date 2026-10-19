"""Move a validated teardown from the inbox into the archive and open a pull request.

Office agents write the entry file. This script does the git work:
validate, file under the student's initials, branch, commit, push, PR.
Usage: python -m tools.taste.submit submissions/inbox/<file>.md
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from tools.taste.schema import load_entry, validate
from tools.taste.slug import entry_filename, slugify

Runner = Callable[[list[str]], str]


def _run_subprocess(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(cmd)} failed (exit {result.returncode}): {detail}")
    return result.stdout


def submit(inbox_file: Path, repo_root: Path, run: Runner = _run_subprocess) -> str:
    inbox_file = Path(inbox_file)
    repo_root = Path(repo_root)
    entry = load_entry(inbox_file)
    errors = validate(entry)
    if errors:
        raise ValueError("\n".join(errors))

    filename = entry_filename(entry)
    target = repo_root / "taste" / "archive" / str(entry.published.year) / filename
    if target.exists():
        raise FileExistsError(f"{target} already exists; a teardown for this brand, student, and date is filed")
    branch = f"teardown/{entry.student}/{entry.published.isoformat()}-{slugify(entry.brand)}"
    title = f"teardown: {entry.brand} ({entry.student})"
    rel = target.relative_to(repo_root).as_posix()

    # Every teardown branches from an up-to-date main, so a batch of inbox
    # files yields independent pull requests. On any git failure the archive
    # copy is removed and the inbox file is left in place for a retry.
    run(["git", "checkout", "main"])
    run(["git", "pull", "--ff-only"])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(inbox_file, target)
    try:
        run(["git", "checkout", "-b", branch])
        run(["git", "add", rel])
        run(["git", "commit", "-m", title])
        run(["git", "push", "-u", "origin", branch])
        out = run(["gh", "pr", "create", "--title", title,
                   "--body", f"Weekly teardown by {entry.student}.",
                   "--base", "main", "--head", branch])
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        run(["git", "checkout", "main"])
    url = next((line.strip() for line in out.splitlines() if line.strip().startswith("http")), out.strip())
    inbox_file.unlink()
    return url


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m tools.taste.submit <inbox-file.md>")
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                               capture_output=True, text=True).stdout.strip())
    try:
        print(submit(Path(sys.argv[1]), root))
    except (ValueError, FileExistsError, RuntimeError) as exc:
        sys.exit(f"not submitted: {exc}")
