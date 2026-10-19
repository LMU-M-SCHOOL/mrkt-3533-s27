from pathlib import Path

import pytest
import yaml

SAMPLE = {
    "brand": "Visit Sweden",
    "maker": "Forsman & Bodenfors",
    "source_url": "https://www.adsoftheworld.com/campaigns/the-introvert-travel-agency",
    "published": "2026-10-07",
    "submitted": "2026-10-19",
    "medium": "integrated",
    "student": "GL",
    "gate": "pass",
    "gate_reason": "Matches the dry humor of Swedish Numbers and the Swedish Number Two campaign.",
    "scores": {"insight": 4, "idea": 4, "execution": 4, "results": 4},
    "class_scores": {"insight": None, "idea": None, "execution": None, "results": None},
    "tags": ["travel", "pr"],
    "calibration": False,
}

SECTIONS = ("Gate", "Insight", "Idea", "Execution", "Results", "What I'd change")
_PARA = " ".join(["word"] * 20)


def sample_entry_text(body: str | None = None, **overrides) -> str:
    """Return a full entry: YAML frontmatter plus the six headings.

    Top-level keys are overridden by keyword. Nested score dicts are
    replaced whole when passed (scores={...}).
    """
    data = {**SAMPLE, **overrides}
    front = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if body is None:
        body = "\n\n".join(f"## {s}\n\n{_PARA}" for s in SECTIONS)
    return f"---\n{front}---\n\n{body}\n"


def write_entry(path: Path, **kwargs) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sample_entry_text(**kwargs), encoding="utf-8")
    return path


@pytest.fixture
def archive(tmp_path: Path) -> Path:
    (tmp_path / "archive" / "2027").mkdir(parents=True)
    return tmp_path / "archive"
