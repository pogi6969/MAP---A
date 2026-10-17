#!/usr/bin/env python3
"""Word n-gram overlap between a paper (Markdown) and reference texts.

Turnitin-style similarity comes from runs of identical words. This script finds
every sentence of the paper that shares a run of N or more consecutive words
(default 6) with any reference text, and reports the share of the paper's words
covered by such runs.

Usage:
  python3 similarity_check.py paper.md ref1.txt [ref2.txt ...] [--n 6] [--show 200]
          [--include-references]
"""

import argparse
import re
import sys

WORD = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def words(text):
    return WORD.findall(text.lower())


def clean_markdown(md, include_refs=False):
    out = []
    in_code = False
    skip = False
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^# (5\. REFERENCES|REFERENCES)", line):
            skip = not include_refs
        elif re.match(r"^# APPENDIX", line):
            skip = False
        if skip:
            continue
        if line.startswith(":::") or line.startswith("EQNUM:") or line.startswith("!["):
            continue
        if line.strip().startswith("$$"):
            continue
        line = re.sub(r"\$[^$]*\$", " ", line)          # inline math
        line = re.sub(r"<<[A-Z0-9_]+>>", " 0 ", line)   # placeholders
        line = line.replace("|", " ").replace("*", " ").replace("#", " ")
        out.append(line)
    return "\n".join(out)


def sentences(text):
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [p.strip() for p in parts if len(words(p)) >= 4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper")
    ap.add_argument("refs", nargs="+")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--show", type=int, default=400)
    ap.add_argument("--include-references", action="store_true")
    a = ap.parse_args()
    n = a.n
    grams = set()
    for r in a.refs:
        txt = open(r, encoding="utf-8", errors="ignore").read()
        if r.endswith(".md"):
            txt = clean_markdown(txt, include_refs=False)
        w = words(txt)
        for i in range(len(w) - n + 1):
            grams.add(tuple(w[i:i + n]))
    md = open(a.paper, encoding="utf-8").read()
    body = clean_markdown(md, a.include_references)
    total = 0
    covered = 0
    flagged = []
    for s in sentences(body):
        w = words(s)
        total += len(w)
        hit = [False] * len(w)
        longest = 0
        run = 0
        for i in range(len(w) - n + 1):
            if tuple(w[i:i + n]) in grams:
                for j in range(i, i + n):
                    hit[j] = True
        for h in hit:
            run = run + 1 if h else 0
            longest = max(longest, run)
        c = sum(hit)
        covered += c
        if c:
            flagged.append((longest, c, s))
    flagged.sort(key=lambda x: -x[0])
    print("words checked: %d   words in shared %d-word runs: %d   overlap: %.2f%%" %
          (total, n, covered, 100.0 * covered / max(total, 1)))
    print("sentences with a shared run: %d" % len(flagged))
    for longest, c, s in flagged[:a.show]:
        print("--- run %d words, %d matched ---\n%s" % (longest, c, s[:600]))


if __name__ == "__main__":
    main()
