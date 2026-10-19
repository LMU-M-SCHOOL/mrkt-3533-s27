from pathlib import Path

import pytest

from conftest import write_entry
from tools.taste.submit import submit

PR_URL = "https://github.com/LMU-M-SCHOOL/mrkt-3533-s27/pull/1"


class FakeRun:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str]) -> str:
        self.calls.append(list(cmd))
        if cmd[:3] == ["gh", "pr", "create"]:
            return PR_URL + "\n"
        return ""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "taste" / "archive").mkdir(parents=True)
    (tmp_path / "submissions" / "inbox").mkdir(parents=True)
    return tmp_path


def inbox_entry(repo: Path, **kw) -> Path:
    return write_entry(repo / "submissions" / "inbox" / "anything.md", **kw)


def test_submit_copies_to_archive_year_folder(repo):
    submit(inbox_entry(repo), repo, run=FakeRun())
    assert (repo / "taste" / "archive" / "2026" / "2026-10-07-visit-sweden-GL.md").exists()


def test_submit_branch_and_commit_commands(repo):
    run = FakeRun()
    submit(inbox_entry(repo), repo, run=run)
    assert ["git", "checkout", "-b", "teardown/GL/2026-10-07-visit-sweden"] in run.calls
    commit = next(c for c in run.calls if c[:2] == ["git", "commit"])
    assert commit[commit.index("-m") + 1] == "teardown: Visit Sweden (GL)"
    assert any(c[:4] == ["git", "push", "-u", "origin"] for c in run.calls)
    assert any(c[:3] == ["gh", "pr", "create"] for c in run.calls)


def test_submit_returns_pr_url(repo):
    assert submit(inbox_entry(repo), repo, run=FakeRun()) == PR_URL


def test_submit_rejects_invalid_entry(repo):
    run = FakeRun()
    p = inbox_entry(repo, gate="fail", scores={"insight": 3, "idea": None, "execution": None, "results": None})
    with pytest.raises(ValueError) as exc:
        submit(p, repo, run=run)
    assert "gate" in str(exc.value)
    assert run.calls == []
    assert not list((repo / "taste" / "archive").rglob("*.md"))


def test_submit_refuses_duplicate(repo):
    run = FakeRun()
    write_entry(repo / "taste" / "archive" / "2026" / "2026-10-07-visit-sweden-GL.md")
    with pytest.raises(FileExistsError):
        submit(inbox_entry(repo), repo, run=run)
    assert run.calls == []


def test_submit_removes_inbox_file_on_success(repo):
    p = inbox_entry(repo)
    submit(p, repo, run=FakeRun())
    assert not p.exists()


def test_commit_message_has_no_attribution(repo):
    run = FakeRun()
    submit(inbox_entry(repo), repo, run=run)
    assert not any("Co-Authored-By" in part for c in run.calls for part in c)


def test_submit_starts_and_ends_on_main(repo):
    run = FakeRun()
    submit(inbox_entry(repo), repo, run=run)
    assert run.calls[0] == ["git", "checkout", "main"]
    assert run.calls[1] == ["git", "pull", "--ff-only"]
    assert run.calls[-1] == ["git", "checkout", "main"]


class FailingRun(FakeRun):
    def __call__(self, cmd):
        if cmd[:3] == ["git", "checkout", "-b"]:
            raise RuntimeError("fatal: a branch named 'teardown/GL/2026-10-07-visit-sweden' already exists")
        return super().__call__(cmd)


def test_submit_cleans_up_archive_copy_when_git_fails(repo):
    p = inbox_entry(repo)
    with pytest.raises(RuntimeError) as exc:
        submit(p, repo, run=FailingRun())
    assert "already exists" in str(exc.value)
    assert not (repo / "taste" / "archive" / "2026" / "2026-10-07-visit-sweden-GL.md").exists()
    assert p.exists()


def test_run_subprocess_surfaces_stderr():
    from tools.taste.submit import _run_subprocess
    with pytest.raises(RuntimeError) as exc:
        _run_subprocess(["git", "no-such-git-command-xyz"])
    assert "no-such-git-command-xyz" in str(exc.value)
