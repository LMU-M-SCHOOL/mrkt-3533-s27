"""Build the archive index as a markdown table and a single filterable HTML page.

Usage: python -m tools.taste.index_gen taste/archive
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

from tools.taste.schema import SCORE_KEYS, Entry, load_entry

DASH = "–"
HEADER = ["Published", "Brand", "Maker", "Medium", "Student", "Gate",
          "Insight", "Idea", "Execution", "Results", "Class mean"]


def collect(archive_dir: Path) -> list[Entry]:
    archive_dir = Path(archive_dir)
    entries = [load_entry(p) for p in sorted(archive_dir.rglob("*.md")) if p.name != "index.md"]
    return sorted(entries, key=lambda e: (e.published or "", e.brand), reverse=True)


def _class_mean(entry: Entry) -> str:
    vals = [entry.class_scores.get(k) for k in SCORE_KEYS]
    if any(v is None for v in vals):
        return DASH
    return f"{sum(vals) / 4:.1f}"


def _score(entry: Entry, key: str) -> str:
    v = entry.scores.get(key)
    return DASH if v is None else str(v)


def _row(entry: Entry, archive_dir: Path) -> list[str]:
    rel = entry.path.relative_to(archive_dir).as_posix() if archive_dir in entry.path.parents else entry.path.name
    return [entry.published.isoformat() if entry.published else DASH,
            f"[{entry.brand}]({rel})", entry.maker, entry.medium, entry.student, entry.gate,
            *(_score(entry, k) for k in SCORE_KEYS), _class_mean(entry)]


def write_markdown_index(entries: list[Entry], out: Path) -> None:
    out = Path(out)
    archive_dir = out.parent
    lines = ["# Teardown archive", "", f"{len(entries)} entries, newest first.", "",
             "| " + " | ".join(HEADER) + " |",
             "|" + "---|" * len(HEADER)]
    lines += ["| " + " | ".join(_row(e, archive_dir)) + " |" for e in entries]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _to_json(entry: Entry, archive_dir: Path) -> dict:
    rel = entry.path.relative_to(archive_dir).as_posix() if archive_dir in entry.path.parents else entry.path.name
    return {"brand": entry.brand, "maker": entry.maker,
            "published": entry.published.isoformat() if entry.published else None,
            "medium": entry.medium, "student": entry.student, "gate": entry.gate,
            "scores": entry.scores, "class_scores": entry.class_scores,
            "tags": entry.tags, "path": rel, "class_mean": _class_mean(entry)}


_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Teardown archive</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;margin:16px;color:#111;background:#fff}
label{margin-right:12px}select{margin-left:4px}
table{border-collapse:collapse;width:100%;margin-top:12px;font-size:14px}
th,td{border-bottom:1px solid #ddd;padding:6px 8px;text-align:left}
th{background:#f4f4f4}
</style></head><body>
<h1>Teardown archive</h1>
<p><span id="count"></span> entries. Filter:</p>
<label>Medium<select id="filter-medium"><option value="">all</option></select></label>
<label>Student<select id="filter-student"><option value="">all</option></select></label>
<label>Gate<select id="filter-gate"><option value="">all</option><option>pass</option><option>fail</option></select></label>
<label>Month<select id="filter-month"><option value="">all</option></select></label>
<table><thead><tr>__HEAD__</tr></thead><tbody id="rows"></tbody></table>
<script id="entries" type="application/json">__DATA__</script>
<script>
const entries=JSON.parse(document.getElementById('entries').textContent);
const sel=id=>document.getElementById(id);
function fill(id,values){const s=sel(id);[...new Set(values)].sort().forEach(v=>{const o=document.createElement('option');o.textContent=v;s.appendChild(o);});}
fill('filter-medium',entries.map(e=>e.medium));
fill('filter-student',entries.map(e=>e.student));
fill('filter-month',entries.map(e=>(e.published||'').slice(0,7)));
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function render(){
  const m=sel('filter-medium').value,st=sel('filter-student').value,g=sel('filter-gate').value,mo=sel('filter-month').value;
  const rows=entries.filter(e=>(!m||e.medium===m)&&(!st||e.student===st)&&(!g||e.gate===g)&&(!mo||(e.published||'').startsWith(mo)));
  sel('count').textContent=rows.length;
  sel('rows').innerHTML=rows.map(e=>{const s=k=>e.scores[k]??'–';
    return `<tr><td>${esc(e.published)}</td><td><a href="${esc(e.path)}">${esc(e.brand)}</a></td><td>${esc(e.maker)}</td><td>${esc(e.medium)}</td><td>${esc(e.student)}</td><td>${esc(e.gate)}</td><td>${s('insight')}</td><td>${s('idea')}</td><td>${s('execution')}</td><td>${s('results')}</td><td>${esc(e.class_mean)}</td></tr>`;}).join('');
}
['filter-medium','filter-student','filter-gate','filter-month'].forEach(id=>sel(id).addEventListener('change',render));
render();
</script></body></html>
"""


def write_html_index(entries: list[Entry], out: Path) -> None:
    out = Path(out)
    archive_dir = out.parent
    data = json.dumps([_to_json(e, archive_dir) for e in entries], ensure_ascii=False)
    data = data.replace("</", "<\\/")
    head = "".join(f"<th>{html.escape(h)}</th>" for h in HEADER)
    out.write_text(_PAGE.replace("__HEAD__", head).replace("__DATA__", data), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m tools.taste.index_gen <archive-dir>")
    d = Path(sys.argv[1])
    es = collect(d)
    write_markdown_index(es, d / "index.md")
    write_html_index(es, d / "index.html")
    print(f"indexed {len(es)} entries")
