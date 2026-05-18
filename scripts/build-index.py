#!/usr/bin/env python3
"""Build the static site from chat exports.

Scans chats/ for HTML files, extracts the chat-title and chat-start-date meta
tags from each, copies the chats into _site/chats/, and renders _site/index.html
from index-template.html.

Files missing either required meta tag are skipped with a warning. Invalid
dates (anything not ISO YYYY-MM-DD) are also skipped.
"""

import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
CHATS_DIR = REPO_ROOT / "chats"
SITE_DIR = REPO_ROOT / "_site"
INDEX_TEMPLATE = REPO_ROOT / "index-template.html"


def extract_meta(path: Path):
    """Return {'title', 'date', 'filename'} or None if meta tags are missing/invalid."""
    with path.open("r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    title_tag = soup.find("meta", attrs={"name": "chat-title"})
    date_tag = soup.find("meta", attrs={"name": "chat-start-date"})

    missing = []
    if not title_tag or not (title_tag.get("content") or "").strip():
        missing.append("chat-title")
    if not date_tag or not (date_tag.get("content") or "").strip():
        missing.append("chat-start-date")
    if missing:
        print(f"  skip {path.name}: missing meta {missing}", file=sys.stderr)
        return None

    date_str = date_tag["content"].strip()
    try:
        parsed = date.fromisoformat(date_str)
    except ValueError:
        print(
            f"  skip {path.name}: invalid chat-start-date '{date_str}' (need YYYY-MM-DD)",
            file=sys.stderr,
        )
        return None

    return {
        "title": title_tag["content"].strip(),
        "date": parsed,
        "filename": path.name,
    }


def format_date(d: date) -> str:
    """'May 18, 2026' — portable across platforms (no %-d)."""
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def render_entry(entry) -> str:
    return (
        '        <li class="entry">\n'
        f'          <a class="entry-link" href="chats/{escape(entry["filename"])}">\n'
        f'            <span class="entry-title">{escape(entry["title"])}</span>\n'
        f'            <span class="entry-date">{format_date(entry["date"])}</span>\n'
        '          </a>\n'
        '        </li>'
    )


def main() -> int:
    if not CHATS_DIR.is_dir():
        print(f"error: {CHATS_DIR} does not exist", file=sys.stderr)
        return 1
    if not INDEX_TEMPLATE.is_file():
        print(f"error: {INDEX_TEMPLATE} does not exist", file=sys.stderr)
        return 1

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir()
    site_chats = SITE_DIR / "chats"
    site_chats.mkdir()

    entries = []
    for chat_path in sorted(CHATS_DIR.glob("*.html")):
        meta = extract_meta(chat_path)
        if meta is None:
            continue
        shutil.copy2(chat_path, site_chats / chat_path.name)
        entries.append(meta)

    # newest first
    entries.sort(key=lambda e: e["date"], reverse=True)

    if entries:
        entries_html = "\n".join(render_entry(e) for e in entries)
    else:
        entries_html = '        <li class="entry empty">No chats yet.</li>'

    template = INDEX_TEMPLATE.read_text(encoding="utf-8")
    rendered = (
        template.replace("{{ENTRIES}}", entries_html)
        .replace("{{COUNT}}", str(len(entries)))
        .replace("{{BUILD_DATE}}", format_date(date.today()))
    )
    (SITE_DIR / "index.html").write_text(rendered, encoding="utf-8")

    print(f"built _site/ with {len(entries)} chat(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
