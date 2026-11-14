# Ramakrishna — The Gospel (extraction)

Faithful, machine-readable extraction of *The Gospel of Râmakrishna*,
translated by **Swami Abhedananda** (Vedanta Society, New York, 1907 —
public domain).

Source: the scan-backed 1907 edition on Wikisource
(`The Gospel of Râmakrishna`). Pure extraction: headings and paragraphs are
preserved; navigation, page numbers, footnote markers and the editorial
footnote list are removed. Nothing is rewritten.

> Note: Abhedananda's 1907 edition is a **14-chapter selection** of the
> Bengali *Śrī Śrī Rāmakṛṣṇa Kathāmṛta* recorded by "M." (Mahendranath Gupta).
> It is the public-domain English edition; the later Nikhilananda translation
> is still under copyright and is not used here.

## Contents

- `output/gospel.md` — the whole book (Introduction + Chapters I–XIV)
- `output/chapters/*.md` — one file per chapter
- `output/catalogue.json` / `output/catalogue.csv` — chapter metadata
  (id, chapter, title, word count, source URL)
- `tools/extract_gospel.py` — extractor (Wikisource API, cached, retry/backoff)

## Run

```bash
python3 tools/extract_gospel.py     # writes output/ (uses cache/ when present)
```

## Source & rights

- Text source: `en.wikisource.org/wiki/The_Gospel_of_Râmakrishna`
- Original: *The Gospel of Râmakrishna*, tr. Swami Abhedananda, 1907.
- **Public domain** (published 1907; Library of Congress confirms).
- `cache/` (raw HTML) is not committed.
