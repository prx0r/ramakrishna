# HANDOVER — Ramakrishna Gospel

Updated: 2026-11-17 · Companion repo: `prx0r/vivek` (audio pipeline lives there)

## State
- **Extraction complete**: Abhedananda 1907 edition, 15 files / 82,292 words,
  cached HTML + retry-safe extractor (`tools/extract_gospel.py`).
- **Curation complete**: `decisions.tsv` 313 KEEP / 76 CUT (bio intro, Ch-I scene
  bookends, page markers), reconciliation exact.
- **Delivered text**: `output/question-led/question-led.md` = *Complete Sessions*
  (14 sessions, 77,468 w) + `unused.md` (4,824 w verbatim) + `COVERAGE.md` +
  `ledger.json`.
- **Audio: not started.** When it starts, follow the fish law in
  `prx0r/vivek/HANDOVER.md`: old man voice = Ramakrishna, granny = questioners /
  narration; zero-disk streaming on opencode3; R2 destination
  `r2:longform-audio/vivek/ramakrishna/…` (to be created).

## Why not "Question-Led"
The transcription collapses Ch III and V–XIV into 1–3 giant blocks per chapter
(Ch XI = one 4,442-word block), so paragraph-level exchange mining is only
possible for Ch I/II/IV. Spec preserved (`SPEC-QUESTION-LED.md`); delivered as
Complete Sessions instead. See `PROCESS-NOTES.md` for method + mistakes.

## Open items
1. Optional: finer transcription of Ch III/V–XIV → enables true Question-Led compile.
2. Audio render of Complete Sessions (owner approval needed).
