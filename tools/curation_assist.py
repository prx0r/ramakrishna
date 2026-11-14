#!/usr/bin/env python3
"""Curation assist for the Question-Led Gospel build.

Classifies UNDECIDED blocks using the rules learned in the manual passes on
Ch I and Ch II, then prints each chapter's cut list for human review.

Rules (in order — evaluated on canonical block text):
  KEEP-exchange  : direct speech anywhere (quotes or said/asked/replied/…)
                   or a speaker label ("Bhagavân:", "Narendra:"),
                   or an anchor question (contains '?' + asked/said/:)
  KEEP-teaching  : first person (" I ", " my ") + teaching vocabulary,
                   or >=3 distinct teaching terms
  KEEP-himself   : chapter 7 (incidents "as told by Himself") — all his words
  CUT-narr       : none of the above (pure scene / description / biography)

Usage:
  python3 tools/curation_assist.py --dry     # classify + print cut lists
  python3 tools/curation_assist.py --apply   # write KEEP/CUT into decisions.tsv
"""
import re
import sys

ROOT = "/home/box/Documents/patala/ramakrishna-gospel"
DEC = ROOT + "/decisions.tsv"

SPEECH_RE = re.compile(r"[“”\"]|\b(said|asked|replied|continued|added|remarked|"
                       r"inquired|enquired|exclaimed|answered|whispered|cried|spoke|"
                       r"told|narrated|observed|remarked)\b", re.I)
SPEAKER_RE = re.compile(r"(?:^|\. )([A-Z][A-Za-z\.\-]{1,24}):")
ANCHOR_RE = re.compile(r"\?")
TEACH = {"god", "lord", "brahman", "soul", "mind", "world", "maya", "māyā",
         "love", "bhakti", "karma", "yogi", "yogis", "sannyasin", "truth",
         "reality", "death", "freedom", "knowledge", "divine", "atman", "self",
         "heaven", "sin", "virtue", "pure", "purity", "devotion", "worship"}
FIRST_PERSON = re.compile(r"\b(I|my|me)\b")


def classify(text, chapter):
    low = text.lower()
    if chapter.startswith("CHAPTER VII"):          # as told by Himself
        return "KEEP", "himself"
    if SPEECH_RE.search(text) or SPEAKER_RE.search(text):
        return "KEEP", "exchange"
    if ANCHOR_RE.search(text) and re.search(r"\b(ask|said|say)\b|:", low):
        return "KEEP", "exchange"
    terms = sum(1 for w in TEACH if w in low.split() or (" " + w + " ") in low)
    if FIRST_PERSON.search(text) and terms >= 1:
        return "KEEP", "teaching"
    if terms >= 3:
        return "KEEP", "teaching"
    return "CUT", "narr"


def main():
    apply = "--apply" in sys.argv
    rows = open(DEC, encoding="utf-8").read().splitlines()
    out = []
    per = {}
    for line in rows:
        if line.startswith("#") or not line.strip():
            out.append(line)
            continue
        p = line.split("\t")
        ent = p[3] if len(p) > 3 else ""
        m = re.match(r"\[([^\]]+)\]", ent)
        chapter = m.group(1) if m else ""
        first = ent.split("]", 1)[1].strip() if "]" in ent else ent
        if p[1] == "UNDECIDED":
            status, reason = classify(first, chapter)
            p[1] = status
            p[2] = reason if status == "CUT" else ""
            per.setdefault(chapter[:16], []).append((p[0], status, first[:70]))
        out.append("\t".join(p))
    if apply:
        open(DEC, "w", encoding="utf-8").write("\n".join(out) + "\n")
        print("decisions.tsv updated")
    else:
        for ch, items in per.items():
            cut = [i for i in items if i[1] == "CUT"]
            print(f"\n=== {ch} — {len(items)} undecided -> CUT {len(cut)} ===")
            for bid, st, prev in cut:
                print(f"  CUT {bid}: {prev}")


if __name__ == "__main__":
    main()
