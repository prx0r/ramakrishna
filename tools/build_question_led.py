#!/usr/bin/env python3
"""Assemble the Question-Led Gospel from human keep/cut decisions.

Workflow:
  1. python3 tools/build_question_led.py --init     # create decisions.tsv (all UNDECIDED)
  2. edit decisions.tsv  (KEEP / CUT with reason, one row per source paragraph)
  3. python3 tools/build_question_led.py --check    # progress: decided/undecided counts
  4. python3 tools/build_question_led.py --emit     # fails if anything undecided

Outputs (output/question-led/):
  question-led.md   the book (KEEP paragraphs, source order)
  unused.md         CUT paragraphs grouped by reason
  COVERAGE.md       per-chapter used/unused + reconciliation
  ledger.json       every block: status, reason, unit id
Fail-closed: keeps + cuts must reconcile to the source exactly.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "gospel.md")
DEC = os.path.join(ROOT, "decisions.tsv")
OUT = os.path.join(ROOT, "output", "question-led")

VALID = {"KEEP", "CUT", "UNDECIDED", "DEFER"}
CUT_REASONS = {"bio", "scene", "dup", "edit", "narr"}


def parse_source():
    """Return list of blocks: {id, chapter, kind, text, words}."""
    text = open(SRC, encoding="utf-8").read()
    blocks = []
    chapter = ""
    n = 0
    for chunk in re.split(r"(?m)^## ", text)[1:]:
        ch, _, body = chunk.partition("\n")
        chapter = ch.strip()
        for para in re.split(r"\n\s*\n", body):
            p = para.strip()
            if not p or p.startswith("*") or p.startswith("#"):
                continue
            n += 1
            blocks.append({
                "id": f"b{n:03d}",
                "chapter": chapter,
                "kind": "h3" if p.startswith("### ") else "p",
                "text": p.lstrip("# ").strip(),
                "words": len(p.split()),
            })
    return blocks


def load_decisions():
    d = {}
    if not os.path.exists(DEC):
        return d
    for line in open(DEC, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        d[parts[0]] = (parts[1].strip(), parts[2].strip() if len(parts) > 2 else "")
    return d


def init(blocks):
    if os.path.exists(DEC):
        print(f"exists: {DEC} (not overwriting)")
        return
    with open(DEC, "w", encoding="utf-8") as f:
        f.write("# block_id\tstatus\treason\t(chapter | first words)\n")
        f.write("# status: KEEP | CUT | UNDECIDED   reason (for CUT): bio scene dup edit narr\n")
        for b in blocks:
            first = " ".join(b["text"].split())[:70]
            f.write(f"{b['id']}\tUNDECIDED\t\t[{b['chapter']}] {first}\n")
    print(f"created {DEC} ({len(blocks)} rows)")


def check(blocks, dec):
    from collections import Counter
    c = Counter(dec.get(b["id"], ("UNDECIDED", ""))[0] for b in blocks)
    missing = [b for b in blocks if b["id"] not in dec]
    print(f"total={len(blocks)}  KEEP={c['KEEP']}  CUT={c['CUT']}  "
          f"UNDECIDED={c['UNDECIDED'] + len(missing)}")
    bad = [i for i, (s, r) in dec.items() if s not in VALID or (s == "CUT" and r not in CUT_REASONS)]
    if bad:
        print(f"INVALID rows: {bad[:10]}")


def emit(blocks, dec):
    missing = [b for b in blocks if dec.get(b["id"], ("UNDECIDED",))[0] in ("UNDECIDED", "DEFER")]
    bad = [i for i, (s, r) in dec.items() if s not in VALID or (s == "CUT" and r not in CUT_REASONS)]
    if missing or bad:
        print(f"REFUSED: {len(missing)} undecided, {len(bad)} invalid rows")
        for b in missing[:5]:
            print(f"  undecided: {b['id']} [{b['chapter']}] {b['text'][:60]}")
        sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    kept = [b for b in blocks if dec[b["id"]][0] == "KEEP"]
    cut = [b for b in blocks if dec[b["id"]][0] == "CUT"]

    # --- units: contiguous KEEP runs (a unit may cross h3 markers, not chapters) ---
    units, cur, cur_ch = [], [], None
    for b in kept:
        if b["chapter"] != cur_ch and cur:
            units.append((cur_ch, cur)); cur = []
        cur_ch = b["chapter"]
        cur.append(b)
    if cur:
        units.append((cur_ch, cur))

    def title(chb):
        t = chb[0]["text"]
        m = re.match(r"^(.{0,90}?\?)\s", t)
        if m:
            return m.group(1)
        m = re.match(r"^(.{0,80}?[.!?])\s", t)
        return (m.group(1) if m else t[:80]).strip()

    lines = ["# The Gospel of Ramakrishna — Question-Led", "",
             "*Extract from Abhedananda 1907 (public domain). Source order, whole paragraphs, nothing rewritten.*", ""]
    ledger = []
    for i, (ch, chb) in enumerate(units, 1):
        uid = f"u{i:03d}"
        lines.append(f"## {title(chb)}")
        lines.append(f"*{ch} · {sum(b['words'] for b in chb):,} words*")
        lines.append("")
        for b in chb:
            lines.append(b["text"])
            lines.append("")
            ledger.append({"block": b["id"], "unit": uid, "chapter": ch, "status": "KEEP"})
    os.path.join(OUT, "question-led.md")
    book = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    open(os.path.join(OUT, "question-led.md"), "w", encoding="utf-8").write(book)

    # --- unused ---
    from collections import defaultdict
    by_reason = defaultdict(list)
    for b in cut:
        by_reason[dec[b["id"]][1] or "narr"].append(b)
    u = ["# Unused source content (verbatim)", ""]
    for reason in sorted(by_reason):
        ws = sum(b["words"] for b in by_reason[reason])
        u.append(f"## CUT — {reason} ({ws:,} words)")
        u.append("")
        for b in by_reason[reason]:
            u.append(f"**{b['id']}** · {b['chapter']}")
            u.append("")
            u.append(b["text"])
            u.append("")
    open(os.path.join(OUT, "unused.md"), "w", encoding="utf-8").write(
        re.sub(r"\n{3,}", "\n\n", "\n".join(u)).strip() + "\n")

    # --- ledger ---
    for b in blocks:
        status = dec[b["id"]][0]
        entry = {"id": b["id"], "chapter": b["chapter"], "words": b["words"],
                 "status": status, "reason": dec[b["id"]][1] if status == "CUT" else ""}
        if status == "KEEP":
            entry["unit"] = next(l["unit"] for l in ledger if l["block"] == b["id"])
        entry["text"] = b["text"][:120]
        ledger.append(entry) if False else None
    full_ledger = []
    unit_of = {l["block"]: l["unit"] for l in ledger}
    for b in blocks:
        status = dec[b["id"]][0]
        e = {"id": b["id"], "chapter": b["chapter"], "words": b["words"],
             "status": status, "reason": dec[b["id"]][1] if status == "CUT" else "",
             "text": b["text"][:120]}
        if status == "KEEP":
            e["unit"] = unit_of[b["id"]]
        full_ledger.append(e)
    json.dump(full_ledger, open(os.path.join(OUT, "ledger.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # --- coverage ---
    src_w = sum(b["words"] for b in blocks)
    defer = [b for b in blocks if dec[b["id"]][0] == "DEFER"]
    keep_w = sum(b["words"] for b in kept)
    cut_w = sum(b["words"] for b in cut)
    defer_w = sum(b["words"] for b in defer)
    assert keep_w + cut_w + defer_w == src_w, f"reconciliation failed: {keep_w}+{cut_w}+{defer_w}!={src_w}"
    chapters = sorted({b["chapter"] for b in blocks})
    cov = ["# Coverage", "",
           f"- source: {len(blocks)} blocks, **{src_w:,} words**",
           f"- used (KEEP): {len(kept)} blocks, **{keep_w:,} words** ({keep_w/src_w:.0%}) → {len(units)} units",
           f"- unused (CUT): {len(cut)} blocks, **{cut_w:,} words** ({cut_w/src_w:.0%})",
           f"- reconciliation: KEEP+CUT = {keep_w + cut_w:,} = source ✔", "", "## by chapter", "",
           "| chapter | source | kept | cut |", "|---|---:|---:|---:|"]
    for ch in chapters:
        cb = [b for b in blocks if b["chapter"] == ch]
        ck = [b for b in cb if dec[b["id"]][0] == "KEEP"]
        cov.append(f"| {ch} | {sum(b['words'] for b in cb):,} | "
                   f"{sum(b['words'] for b in ck):,} | {sum(b['words'] for b in cb) - sum(b['words'] for b in ck):,} |")
    cov += ["", "## by reason", ""]
    for reason in sorted(by_reason):
        cov.append(f"- {reason}: {sum(b['words'] for b in by_reason[reason]):,} words")
    open(os.path.join(OUT, "COVERAGE.md"), "w", encoding="utf-8").write("\n".join(cov) + "\n")
    print(f"EMITTED: {len(units)} units, {keep_w:,} words used / {cut_w:,} unused "
          f"-> {OUT}/question-led.md")


def main():
    blocks = parse_source()
    dec = load_decisions()
    if "--init" in sys.argv:
        init(blocks)
    elif "--check" in sys.argv:
        check(blocks, dec)
    else:
        if not dec:
            init(blocks)
        emit(blocks, dec)


if __name__ == "__main__":
    main()
