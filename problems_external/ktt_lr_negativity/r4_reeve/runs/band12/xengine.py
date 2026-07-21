#!/usr/bin/env python3
"""Cross-engine gate for band 12: for a sample of band-12 triples, compare
P(n) from hive4.py (polytope Ehrhart) with the exact LR counts
c(n*nu; n*lam, n*mu) from engine A (lr_hive.exe) and engine B (engineB_lrrule.py),
for n = 1..4.  Any disagreement is printed in full and never smoothed over.
"""
import sys, random, subprocess, json
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve")
from hive4 import analyze, trim, polyval
from fractions import Fraction

ENG = r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/engine"

def degenerate(p):
    q = [x for x in p if x > 0]
    if not q: return True
    for i in range(len(q) - 1):
        if q[i] == q[i + 1]: return True
    if all(x == 1 for x in q[1:]): return True
    return False

def partitions4(W):
    out = []
    for a in range(W, 0, -1):
        for b in range(min(a, W - a), -1, -1):
            for c in range(min(b, W - a - b), -1, -1):
                d = W - a - b - c
                if d <= c: out.append((a, b, c, d))
    return out

def sub(nu, w):
    out = []
    for a in range(nu[0], -1, -1):
        for b in range(min(a, nu[1]), -1, -1):
            for c in range(min(b, nu[2]), -1, -1):
                d = w - a - b - c
                if 0 <= d <= min(c, nu[3]): out.append((a, b, c, d))
    return out

def s(p):
    q = [x for x in p if x > 0]
    return ",".join(map(str, q)) if q else "0"

random.seed(1212)
cands = []
for W in range(4, 31):
    for nu in partitions4(W):
        for a in range(1, W):
            for lam in sub(nu, a):
                for mu in sub(nu, W - a):
                    if mu < lam: continue
                    if not (degenerate(lam) or degenerate(mu) or degenerate(nu)): continue
                    cands.append((lam, mu, nu))
random.shuffle(cands)

picked = []
for lam, mu, nu in cands:
    r = analyze(list(lam), list(mu), list(nu))
    if r["dim"] >= 1:
        picked.append((lam, mu, nu, r))
    if len(picked) >= 250: break

# build batch files for both engines
linesA = []
for lam, mu, nu, r in picked:
    for n in range(1, 5):
        linesA.append("%s;%s;%s;%d" % (
            s([x * n for x in lam]), s([x * n for x in mu]), s([x * n for x in nu]), 10**12))
batchA = "xa.batch"
open(batchA, "w").write("\n".join(linesA) + "\n")

outA = subprocess.run([ENG + "/lr_hive.exe", "--batch", batchA],
                      capture_output=True, text=True).stdout.split()
outB = subprocess.run([sys.executable, ENG + "/engineB_lrrule.py", "--batch", batchA],
                      capture_output=True, text=True).stdout.split()
print("engineA outputs:", len(outA), "engineB outputs:", len(outB), "expected", len(linesA))

bad = 0; checked = 0
i = 0
for lam, mu, nu, r in picked:
    P = trim(r["poly"])
    for n in range(1, 5):
        pv = polyval(P, n)
        va = outA[i] if i < len(outA) else "MISSING"
        vb = outB[i] if i < len(outB) else "MISSING"
        i += 1
        checked += 1
        if str(pv) != va or str(pv) != vb:
            bad += 1
            print("DISAGREE", lam, mu, nu, "n=", n, "P(n)=", pv, "A=", va, "B=", vb)
print("cross-engine checks: %d  disagreements: %d  (band-12 triples: %d, dim>=1)"
      % (checked, bad, len(picked)))
dh = {}
for lam, mu, nu, r in picked:
    dh[r["dim"]] = dh.get(r["dim"], 0) + 1
print("dim histogram of the sampled band-12 triples:", dh)
