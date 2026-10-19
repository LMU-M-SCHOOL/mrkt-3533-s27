"""ASCII, lowercase, hyphenated slugs for brand names and entry filenames."""
from __future__ import annotations

import re
import unicodedata

from tools.taste.schema import Entry


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.replace("'", "").replace(".", "")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if not slug:
        raise ValueError(f"cannot slugify {text!r}")
    return slug


def entry_filename(entry: Entry) -> str:
    return f"{entry.published.isoformat()}-{slugify(entry.brand)}-{entry.student}.md"
