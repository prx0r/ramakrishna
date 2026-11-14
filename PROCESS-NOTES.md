# PROCESS NOTES — Gospel extraction & curation

Append-only engineering log for `prx0r/ramakrishna`.

## 1. What this repo is

- `output/gospel.md` + `output/chapters/*.md` — verbatim extraction of *The
  Gospel of Râmakrishna*, tr. Swami Abhedananda (1907, public domain), from the
  scan-backed Wikisource edition (15 pages: Introduction + Chapters I–XIV,
  82,292 words). `tools/extract_gospel.py` uses the MediaWiki API (cached HTML,
  retry/backoff on HTTP 429), drops navigation, page numbers, footnote markers
  and the editorial footnote list.
- `output/catalogue.json|csv` — chapter metadata (title, words, source URL).
- `SPEC-QUESTION-LED.md` — the intended ispired compilation spec.
- `tools/build_question_led.py` — the curation assembler (see §3).
- `output/question-led/` — the delivered book + `unused.md` + `COVERAGE.md` +
  `ledger.json`.

## 2. Curation method

`decisions.tsv` = one row per source paragraph (`block_id status reason`).
Statuses: `KEEP`, `CUT` (reasons `bio|scene|dup|edit|narr`), `DEFER`.
`build_question_led.py --check` prints progress; `--emit` is fail-closed:
it refuses while any row is UNDECIDED/DEFER, and proves
`KEEP + CUT + DEFER = source words` before writing anything.

Manual pass (Ch I, read line by line):
- KEEP: every paragraph carrying direct speech, a question, a parable, or
  teaching ("the recorded exchanges").
- CUT `scene`: temple description, evening ârati, the Brindâ doorway
  exchange, samâdhi narration, departure lines.
- CUT `bio`: Abhedananda's 29-paragraph biographical Introduction.
- CUT `edit`: stray page-marker blocks (`i`, `ii`, `iii`, …).
- DEFER: one borderline line ("Sandhyâ? Evening service? It is not that.") —
  later resolved KEEP.

**Attempted automation and why it failed.** A rule-based classifier
(`tools/curation_assist.py`: quote/speech-verb/speaker-label detection) was
written and dry-run, but it mis-cut teaching because (a) speaker labels use
diacritics ("Bhagavân:", "Râmakrishna:") that break `[A-Za-z]` patterns and
(b) this edition reports dialogue without quotation marks, so continuous
discourse is textually indistinguishable from narration. The heuristic was
**never applied** (dry-run only). Manual reading remains the only reliable
method.

## 3. Structural finding — why "Complete Sessions", not Question-Led

The Wikisource transcription preserves paragraph breaks in Ch I, II and IV,
but collapses Ch III and V–XIV into 1–3 giant blocks per chapter
(Ch III = one 7,621-word block; Ch XI = one 4,442-word block). Paragraph-level
Question-Led selection is therefore impossible for those chapters without a
finer transcription (which would be new work, not extraction).

Delivered instead, and labelled honestly in the book: **Complete Sessions** —
the 14 recorded sessions intact and in order, minus the biography intro, Ch-I
scene bookends and page markers. Final counts: **313 KEEP / 76 CUT**
(29 bio, 12 scene, 35 edit), 77,468 of 82,292 words, reconciliation exact.
The Question-Led spec is preserved for a future re-transcription pass.

## 4. Runbook

```bash
python3 tools/extract_gospel.py            # re-extract (cache/ first)
python3 tools/build_question_led.py --check
python3 tools/build_question_led.py --emit # fail-closed; writes output/question-led/
```

No audio is rendered from this repo yet. When it is, it must use the
Vivekananda repo's fish law (same direction tags, same casting: old man =
Ramakrishna, granny = questioners/narration) and the same Indic guard —
Gospel text is English-only, so the guard is a no-op here.

## 5. Mistakes log (append-only)

1. **Catalogue key mismatch** — the Gospel catalogue uses `title`; the
   Vivekananda one uses `chapter`. Lookups must be per-repo.
2. **Re-extraction invalidates stored paragraph indices** — any re-extract or
   block-filtering (e.g. Indic guard) shifts spans; relocate by preview text.
3. **`--emit` must stay fail-closed** — an early version could have written the
   book with undecided rows; it now asserts the full reconciliation and
   refuses otherwise.
4. **Don't label a curated compilation "Question-Led" if it isn't** — the book
   header and README were corrected to "Complete Sessions" when the structural
   limit was discovered.
