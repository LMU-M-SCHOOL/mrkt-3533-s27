"""Load and validate one teardown entry.

Rules come from instructor/2026-10-19-taste-development-design.md:
Effie section names, 1 to 5 scores, gate fail means unscored,
365-day recency unless calibration, initials only, source URL only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import frontmatter

MEDIA = ("film", "print", "ooh", "digital", "social", "experiential",
         "integrated", "landing-page", "product", "other")
SECTIONS = ("Gate", "Insight", "Idea", "Execution", "Results", "What I'd change")
SCORE_KEYS = ("insight", "idea", "execution", "results")
RECENCY_DAYS = 365
MAX_BODY_WORDS = 800
INITIALS = re.compile(r"^[A-Z]{2,3}$")


class ValidationError(Exception):
    """Raised when a file cannot be parsed as an entry at all."""


@dataclass
class Entry:
    path: Path
    brand: str
    maker: str
    source_url: str
    published: date | None
    submitted: date | None
    medium: str
    student: str
    gate: str
    gate_reason: str
    scores: dict[str, int | None]
    class_scores: dict[str, int | None]
    tags: list[str] = field(default_factory=list)
    calibration: bool = False
    body: str = ""


def _to_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _scores(value) -> dict[str, int | None]:
    out: dict[str, int | None] = {k: None for k in SCORE_KEYS}
    if isinstance(value, dict):
        for k in SCORE_KEYS:
            out[k] = value.get(k)
    return out


def load_entry(path: Path) -> Entry:
    try:
        post = frontmatter.load(str(path))
    except Exception as exc:  # yaml or io failure
        raise ValidationError(f"{path}: cannot parse frontmatter ({exc})") from exc
    m = post.metadata
    return Entry(
        path=Path(path),
        brand=str(m.get("brand") or ""),
        maker=str(m.get("maker") or ""),
        source_url=str(m.get("source_url") or ""),
        published=_to_date(m.get("published")),
        submitted=_to_date(m.get("submitted")),
        medium=str(m.get("medium") or ""),
        student=str(m.get("student") or ""),
        gate=str(m.get("gate") or ""),
        gate_reason=str(m.get("gate_reason") or ""),
        scores=_scores(m.get("scores")),
        class_scores=_scores(m.get("class_scores")),
        tags=list(m.get("tags") or []),
        calibration=bool(m.get("calibration", False)),
        body=post.content,
    )


def _check_scores(name: str, scores: dict, errors: list[str]) -> None:
    for k, v in scores.items():
        if v is None:
            continue
        if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 5:
            errors.append(f"{name}.{k} must be an integer from 1 to 5, got {v!r}")


def validate(entry: Entry) -> list[str]:
    errors: list[str] = []
    if not entry.brand.strip():
        errors.append("brand is required")
    elif any(ord(c) < 32 for c in entry.brand):
        errors.append("brand must be a single line with no control characters")
    if not entry.maker.strip():
        errors.append("maker is required (agency, studio, or in-house team)")
    if not entry.gate_reason.strip():
        errors.append("gate_reason is required: one line saying why it passes or fails the brand gate")
    if not re.match(r"^https?://", entry.source_url):
        errors.append("source_url must start with http:// or https://")
    if entry.published is None:
        errors.append("published must be a YYYY-MM-DD date")
    if entry.submitted is None:
        errors.append("submitted must be a YYYY-MM-DD date")
    if entry.medium not in MEDIA:
        errors.append(f"medium must be one of {', '.join(MEDIA)}, got {entry.medium!r}")
    if not INITIALS.match(entry.student):
        errors.append("student must be initials, 2 or 3 uppercase letters")
    if entry.gate not in ("pass", "fail"):
        errors.append("gate must be pass or fail")
    if entry.gate == "fail" and any(v is not None for v in entry.scores.values()):
        errors.append("gate is fail, so all four scores must be null (unscored)")
    if entry.gate == "pass" and any(v is None for v in entry.scores.values()):
        errors.append("gate is pass, so all four scores must be set from 1 to 5")
    _check_scores("scores", entry.scores, errors)
    _check_scores("class_scores", entry.class_scores, errors)
    if entry.published and entry.submitted and not entry.calibration:
        age = (entry.submitted - entry.published).days
        if age > RECENCY_DAYS:
            errors.append(f"published is {age} days before submitted; limit is {RECENCY_DAYS} unless calibration: true")
    for s in SECTIONS:
        if not re.search(rf"^## {re.escape(s)}\s*$", entry.body, flags=re.M):
            errors.append(f"missing heading: ## {s}")
    words = len(entry.body.split())
    if words > MAX_BODY_WORDS:
        errors.append(f"body is {words} words; limit is {MAX_BODY_WORDS}")
    return errors
