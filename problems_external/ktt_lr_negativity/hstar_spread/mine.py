#!/usr/bin/env python3
"""Stream every *.jsonl under the KTT tree, extract (r, c, d, hstar), dedup,
and record for each distinct h*-vector the exact slack of every coefficient
inequality.  Writes hstar_atlas.tsv:  d  r  c  M  hstar  minR  argk
R_k = (neg mass)/(pos mass) for functional w_k;  a_k >= 0  <=>  R_k <= 1.
"""
import json, os, sys, re
from fractions import Fraction
from crit import wrow

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
seen = {}
nline = 0
files = []
for dp, dn, fn in os.walk(ROOT):
    if "hstar_spread" in dp:
        continue
    for f in fn:
        if f.endswith(".jsonl"):
            files.append(os.path.join(dp, f))
files.sort()

pat = re.compile(r'"hstar"\s*:\s*\[([0-9,\s\-]*)\]')

for path in files:
    try:
        with open(path, "r", errors="ignore") as fh:
            for line in fh:
                nline += 1
                m = pat.search(line)
                if not m:
                    continue
                body = m.group(1).strip()
                if not body:
                    continue
                try:
                    h = tuple(int(x) for x in body.split(","))
                except ValueError:
                    continue
                if len(h) < 4:
                    continue
                if h in seen:
                    continue
                # metadata (best effort)
                r = c = None
                mm = re.search(r'"r"\s*:\s*(\d+)', line)
                if mm: r = int(mm.group(1))
                mm = re.search(r'"c"\s*:\s*(\d+)', line)
                if mm: c = int(mm.group(1))
                seen[h] = (r, c, path)
    except OSError:
        continue

sys.stderr.write("lines=%d files=%d distinct_hstar=%d\n" % (nline, len(files), len(seen)))

out = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hstar_atlas.tsv"), "w")
out.write("d\tr\tc\tM\tminR_num\tminR_den\targk\thstar\n")
for h, (r, c, path) in seen.items():
    d = len(h) - 1
    M = sum(h)
    best = None; bk = None
    for k in range(1, d):
        W = wrow(d, k)
        pos = sum(h[j] * W[j] for j in range(d + 1) if W[j] > 0)
        neg = sum(-h[j] * W[j] for j in range(d + 1) if W[j] < 0)
        if pos == 0:
            continue
        R = Fraction(neg, pos)
        if best is None or R > best:
            best = R; bk = k
    if best is None:
        best = Fraction(0); bk = -1
    out.write("%d\t%s\t%s\t%d\t%d\t%d\t%d\t%s\n" %
              (d, r, c, M, best.numerator, best.denominator, bk,
               ",".join(map(str, h))))
out.close()
print("wrote hstar_atlas.tsv rows=%d" % len(seen))
