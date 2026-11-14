# SPEC — Question-Led Gospel (Approach 3)

Status: SPEC (not yet implemented)
Source: `output/gospel.md` (Abhedananda 1907, public domain, 15 files, 82,292 words)
Mode: **extract-only** — cut, reorder-free, never splice a sentence, no authored prose.

## 1. Goal

A listenable compilation built around **the questions actually asked in the
book**: each section = a real question (as recorded) + Ramakrishna's full
answer(s) + any attached parable, kept whole. The dialogue provides the flow;
nothing is rewritten.

Secondary requirement (owner): **complete accounting** — at the end we must be
able to see exactly which content was used and what is left over unused.

## 2. Unit of selection

**Exchange** = one contiguous run of source blocks:

```
[question block] → [answer block(s)…] → [optional parable / illustration]
```

- Contiguous in source order. Never assembled from non-adjacent blocks.
- Whole paragraphs only. No sentence-level cutting, no splicing.
- A unit may start at a question that is narrated ("…was asked", "M.
  enquired") or direct ("Q: …").
- Ramakrishna's *own* questions used rhetorically stay inside the answer —
  they are his teaching, not section anchors.

## 3. Reason codes (every block gets exactly one)

| Code | Meaning |
|---|---|
| `INCLUDE` | part of a question-led exchange |
| `EX-BIO` | Abhedananda's Introduction / biography |
| `EX-SCENE` | scene-setting: arrivals, meals, travel, samādhi narration, who-was-present |
| `EX-DUP` | near-duplicate of an already-included teaching (keep the clearest/earliest telling) |
| `EX-EDIT` | marginal notes, footnote text, editorial apparatus |
| `EX-NARR` | narration with no teaching content |
| `DEFER` | uncertain → review queue before emit |

## 4. Pipeline (staged, fail-closed)

1. **Index** — split `gospel.md` into numbered paragraph blocks
   (`block_0001`…, chapter, words, text). Every block enters the ledger.
2. **Anchors** — detect question blocks (interrogative ending, reported
   question, "asked/enquired/queried" cue).
3. **Grow** — from each anchor, absorb following contiguous blocks while they
   are answer/teaching/parable; stop at scene-setting, next anchor (unless
   nested answer continues), or chapter end.
4. **Classify remainder** — leftover blocks → EX-BIO / EX-SCENE / EX-EDIT /
   EX-NARR / DEFER.
5. **Dedup** — TF-IDF cosine ≥ 0.85 between included exchanges → mark later
   one `EX-DUP`.
6. **Review gate** — `DEFER` + all `EX-DUP` decisions listed for owner
   approval before anything is emitted (one-page review file).
7. **Emit** — only after review resolves: book, units, ledger, coverage.

## 5. Outputs (all under `output/question-led/`)

| File | Contents |
|---|---|
| `question-led.md` | the compilation: `##` = one exchange, speaker tag `Q:` / `Master:` minimal, source citation per unit (`Ch. IX · pg ref`) |
| `units.json` | machine list: unit_id, chapter, block range, question text, words |
| `ledger.json` | **every block**: id, chapter, words, status, reason, unit_id — the audit trail |
| `COVERAGE.md` | summary: used vs unused % by chapter and by reason; word reconciliation |
| `unused.md` | the leftovers verbatim, grouped by reason — so we can see exactly what wasn't used |
| `REVIEW.md` | the DEFER/DUP queue awaiting owner decision (gate artifact) |

## 6. Coverage law (why nothing can go missing)

- Every block from step 1 appears in `ledger.json` **exactly once**.
- Reconciliation must hold: `Σ included + Σ excluded + Σ deferred = Σ source words`.
- `unused.md` is generated *from the ledger*, never hand-curated.
- Emit is blocked (exit non-zero) unless: ledger complete, reconciliation
  exact, `DEFER` empty (all resolved by owner), no block in two units.

## 7. Order & style

- **Order:** source order (chapter sequence) — keeps his development intact,
  zero reordering ("don't fuck with it too much").
- **Speaker tag:** minimal `Q:` / `Master:` only where the source leaves the
  speaker ambiguous. No other added words.
- **Headings:** use the source's own question wording as the section title —
  nothing invented.
- **Marginal headings:** dropped (they are Abhedananda's editorial labels,
  EX-EDIT).

## 8. Acceptance checks

1. 100% of blocks classified; ledger reconciles to 82,292 words (± whitespace).
2. Every included span is contiguous (no cross-chapter splices).
3. Review gate signed off (DEFER = 0).
4. Spot-check: 3 random units read as complete exchanges in context.
5. `COVERAGE.md` shows used / unused split per chapter.

## 9. Open decisions (owner)

- [ ] Dedup threshold 0.85 cosine — strict enough? (lower = shorter book)
- [ ] Keep `EX-SCENE` one-line locators (e.g. "at Dakshineswar") as context, or drop entirely?
- [ ] Target length cap (if the selection lands long, do we trim to ~4–5 h?)
- [ ] Order confirmed as source order (vs. grouping by question theme)?

## Outcome 2026-11-14 — delivered as "Complete Sessions"

Measured structure: Ch I–II and IV preserve paragraph breaks (fine-grained
curation possible); Ch III and V–XIV collapse into 1–3 giant blocks per
chapter (Ch XI = one 4,442-word block) in the Wikisource transcription.

Therefore the spec's paragraph-level exchange selection is only feasible where
the transcription preserved breaks. Delivered instead: **Complete Sessions** —
the 14 chapter sessions intact, minus Abhedananda's biography introduction,
Ch-I scene bookends, and stray page-marker blocks. 313 KEEP / 76 CUT, exact
reconciliation, audit trail in `output/question-led/ledger.json`.

The Question-Led compile remains specified above for a future finer
transcription of Ch III/V–XIV.
