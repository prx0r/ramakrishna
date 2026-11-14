#!/usr/bin/env python3
"""Faithful extraction of The Gospel of Ramakrishna (Abhedananda 1907, public domain).

Source: en.wikisource.org "The Gospel of Râmakrishna" (scan-backed 1907 edition).
Pure extraction of the main text: headings and paragraphs preserved; page
numbers, footnote markers, navigation and the editorial footnote list removed.
"""
import csv
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from html.parser import HTMLParser

API = "https://en.wikisource.org/w/api.php"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")
OUT = os.path.join(ROOT, "output")
PAGES = [("introduction", "The Gospel of Râmakrishna/Introduction", "Introduction")]
for n in range(1, 15):
    PAGES.append((f"chapter_{n:02d}", f"The Gospel of Râmakrishna/Chapter {n}", f"Chapter {n}"))

SKIP_CLASSES = {
    "ws-header", "ws-noexport", "noprint", "thumb", "figure", "mw-editsection",
    "pagenum", "ws-pagenum", "reference", "reflist", "references",
    "ws-summary", "headertemplate", "licenseContainer", "ws-nav",
}
VOID = {"br", "img", "hr", "link", "meta", "input", "wbr", "source", "area", "base", "col", "embed", "param", "track"}


def cache_path(page):
    safe = re.sub(r"[^A-Za-z0-9]+", "_", page)
    return os.path.join(CACHE, "gospel_" + safe + ".html")


def fetch_html(page):
    cp = cache_path(page)
    if os.path.exists(cp) and os.path.getsize(cp) > 0:
        return open(cp, encoding="utf-8").read()
    q = urllib.parse.urlencode({
        "action": "parse", "page": page, "format": "json", "formatversion": "2",
        "prop": "text", "disablelimitreport": "1",
    })
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "Mozilla/5.0 (extraction; contact local)"})
    last = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    else:
        raise last
    text = data["parse"]["text"]
    os.makedirs(CACHE, exist_ok=True)
    with open(cp, "w", encoding="utf-8") as f:
        f.write(text)
    time.sleep(1.2)
    return text


class GospelParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []           # (tag, is_skip)
        self.skip = 0
        self.blocks = []          # [kind, parts]
        self.cur = None

    def _skip_for(self, tag, cls):
        if tag in ("style", "script"):
            return True
        return bool(set(cls) & SKIP_CLASSES)

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if self.skip == 0 and tag == "br" and self.cur is not None:
                self.cur[1].append("\n")
            return
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        is_skip = self._skip_for(tag, cls)
        self.stack.append((tag, is_skip))
        if is_skip:
            self.skip += 1
            return
        if self.skip == 0:
            if tag in ("h2", "h3"):
                self.cur = ["h2", []]
                self.blocks.append(self.cur)
            elif tag == "p":
                self.cur = ["p", []]
                self.blocks.append(self.cur)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        # pop to the matching tag
        while self.stack:
            t, is_skip = self.stack.pop()
            if is_skip:
                self.skip = max(0, self.skip - 1)
            if t == tag:
                break
        if tag in ("p", "h2", "h3", "div"):
            self.cur = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.cur is not None:
            self.cur[1].append(data.replace("\n", " ").replace("\t", " "))


def norm(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n+", "\n", s)
    return s.strip()


def extract(page):
    p = GospelParser()
    p.feed(fetch_html(page))
    p.close()
    blocks = []
    for kind, parts in p.blocks:
        t = norm("".join(parts))
        if t:
            blocks.append((kind, t))
    return blocks


def clean_title(blocks):
    """Return (chapter_label, title) from the leading CHAPTER ... / title blocks."""
    label, title = "", ""
    texts = [t for _, t in blocks]
    for i, t in enumerate(texts[:6]):
        m = re.match(r"^(CHAPTER\s+[IVXLC]+)\.?$", t, re.I)
        if m:
            label = m.group(1).upper()
            if i + 1 < len(texts):
                title = texts[i + 1]
            break
    return label, title


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "chapters"), exist_ok=True)
    combined = ["# The Gospel of Râmakrishna", "",
                "*Translated by Swami Abhedananda (1907). Public domain.*", ""]
    rows = []
    for key, page, fallback in PAGES:
        try:
            blocks = extract(page)
        except Exception as e:
            print(f"[{key}] ERROR: {e}", file=sys.stderr)
            continue
        label, title = clean_title(blocks)
        if not title:
            title = fallback
        heading = f"{label} — {title}" if label else title
        # drop the leading CHAPTER label and title from the body
        body = list(blocks)
        if label:
            for j, (k, t) in enumerate(body[:6]):
                if re.match(r"^CHAPTER\s+[IVXLC]+\.?$", t, re.I):
                    body = body[j + 2:]
                    break
        words = sum(len(t.split()) for _, t in body)
        url = "https://en.wikisource.org/wiki/" + urllib.parse.quote(page.replace(" ", "_"))

        lines = [f"## {heading}", ""]
        for kind, t in body:
            if kind == "h2":
                lines.extend([f"### {t}", ""])
            else:
                lines.extend([t, ""])
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
        with open(os.path.join(OUT, "chapters", key + ".md"), "w", encoding="utf-8") as f:
            f.write(text)

        combined.extend([f"## {heading}", ""])
        for kind, t in body:
            if kind == "h2":
                combined.extend([f"### {t}", ""])
            else:
                combined.extend([t, ""])
        rows.append({
            "id": key, "chapter": label, "title": title,
            "heading": heading, "words": words, "url": url,
        })
        print(f"[{key}] {words} words  {heading}")

    text = re.sub(r"\n{3,}", "\n\n", "\n".join(combined)).strip() + "\n"
    with open(os.path.join(OUT, "gospel.md"), "w", encoding="utf-8") as f:
        f.write(text)

    with open(os.path.join(OUT, "catalogue.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "catalogue.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "chapter", "title", "heading", "words", "url"])
        w.writeheader()
        w.writerows(rows)

    total = sum(r["words"] for r in rows)
    print(f"TOTAL {len(rows)} chapters, {total} words -> output/gospel.md")


if __name__ == "__main__":
    main()
