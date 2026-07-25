"""a(N) for N<=15, vectorised, exact integer arithmetic; reports ALL witnesses."""
import glob, os, sys, time
from fractions import Fraction
from itertools import combinations
import numpy as np
from audit_f8_lib import g6dec, mono_masks, ragged, psi_int_np, bip_exact

D = os.path.dirname(os.path.abspath(__file__))
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 15
PAT = {}
t0 = time.time()
for fn in glob.glob(os.path.join(D, 'f8_rmtf_*.g6')):
    k = int(fn.rsplit('_', 1)[1].split('.')[0])
    if k > NMAX:
        continue
    for l in open(fn):
        l = l.strip()
        if not l:
            continue
        n, adj = g6dec(l)
        E, mn = mono_masks(n, adj)
        p, o = ragged(E, mn)
        PAT.setdefault(n, []).append((l, p, o, len(mn)))
print("patterns:", {k: len(v) for k, v in sorted(PAT.items())},
      " max |M| =", max(x[3] for v in PAT.values() for x in v), f" ({time.time()-t0:.0f}s)")


def comps(N, k):
    for cut in combinations(range(1, N), k - 1):
        prev, out = 0, []
        for c in cut:
            out.append(c - prev)
            prev = c
        out.append(N - prev)
        yield out


for N in range(5, NMAX + 1):
    best, wits = 0, []
    for k, pats in sorted(PAT.items()):
        if k > N:
            continue
        for (g6, p, o, nm) in pats:
            for a in comps(N, k):
                v = psi_int_np(p, o, a)
                if v > best:
                    best, wits = v, [(g6, tuple(a))]
                elif v == best and len(wits) < 6:
                    wits.append((g6, tuple(a)))
    print(f"N={N:>3} a(N)={best:>3} floor(N^2/25)={N*N//25:>3} ratio={str(Fraction(best,N*N)):>8}"
          f"={best/N**2:.7f}  witnesses(<=6): {wits}", flush=True)
