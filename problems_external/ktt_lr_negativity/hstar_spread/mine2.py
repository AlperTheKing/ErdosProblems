#!/usr/bin/env python3
"""Strict re-mine: only records whose held-out verification PASSED.
Rejects DEGREE_ANOMALY lines (interp_exit 3 / extra_match "no").
Emits hstar_atlas2.tsv with lam;mu;nu kept for independent re-verification."""
import os, sys, re
from fractions import Fraction
from crit import wrow

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
seen = {}
nline = nacc = 0
files = []
for dp, dn, fn in os.walk(ROOT):
    if os.path.normpath(dp).startswith(HERE):
        continue
    for f in fn:
        if f.endswith(".jsonl"):
            files.append(os.path.join(dp, f))
files.sort()

pat = re.compile(r'"hstar"\s*:\s*\[([0-9,\s\-]*)\]')
GOOD = ('"heldout_ok": true', '"extra_match": "yes"')
BAD = ('"extra_match": "no"', '"interp_exit": 3', '"heldout_ok": false',
       'ANOMALY', '"status": "CAP', 'CAP_EXCEEDED')


def getstr(line, key):
    m = re.search(r'"%s"\s*:\s*"([^"]*)"' % key, line)
    if m:
        return m.group(1)
    m = re.search(r'"%s"\s*:\s*\[([0-9,\s]*)\]' % key, line)
    if m:
        return ",".join(x.strip() for x in m.group(1).split(",") if x.strip())
    return None


for path in files:
    try:
        with open(path, "r", errors="ignore") as fh:
            for line in fh:
                nline += 1
                if not any(g in line for g in GOOD):
                    continue
                if any(b in line for b in BAD):
                    continue
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
                nacc += 1
                if h in seen:
                    continue
                lam = getstr(line, "lam"); mu = getstr(line, "mu"); nu = getstr(line, "nu")
                if not (lam and mu and nu):
                    continue
                r = re.search(r'"r"\s*:\s*(\d+)', line)
                c = re.search(r'"c"\s*:\s*(\d+)', line)
                seen[h] = (r.group(1) if r else "", c.group(1) if c else "",
                           lam, mu, nu, os.path.relpath(path, ROOT))
    except OSError:
        continue

sys.stderr.write("lines=%d accepted=%d distinct=%d\n" % (nline, nacc, len(seen)))

out = open(os.path.join(HERE, "hstar_atlas2.tsv"), "w")
out.write("d\tr\tc\tM\tmaxR_num\tmaxR_den\targk\thstar\tlam\tmu\tnu\tsrc\n")
for h, (r, c, lam, mu, nu, src) in seen.items():
    d = len(h) - 1
    M = sum(h)
    best = None; bk = -1
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
        best = Fraction(0)
    out.write("%d\t%s\t%s\t%d\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s\n" %
              (d, r, c, M, best.numerator, best.denominator, bk,
               ",".join(map(str, h)), lam, mu, nu, src))
out.close()
print("rows=%d" % len(seen))
