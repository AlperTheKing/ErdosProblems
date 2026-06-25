"""D5 SKEPTIC audit. Independent of brute_dmono.py and audit_brute12.py.
Goals:
 1. Independent max-cut via numpy XOR-popcount over ALL 2^n masks (no vertex-0 fix shortcut by default,
    so we can cross-check that fixing vertex 0 is valid). Independent triangle-free verifier.
 2. Re-derive in-band sup d_mono for n=9,10,11 and report ANY graph with d_mono > 2/25+delta.
 3. ADVERSARIAL: construct blow-ups G[t] of small triangle-free graphs whose edge density lands IN BAND,
    and check d_mono = 2 beta(G[t]) / (n t)^2 against the bound. The certificate's closure RELIES on the
    blow-up identity beta(G[t]) = t^2 beta(G); if some blow-up in-band exceeded the bound the claim breaks.
 4. Check the band-edge graphs: is the sup TRENDING to 0.08 (i.e. is the margin shrinking dangerously)?
"""
import sys, numpy as np
from fractions import Fraction
import flag_engine as fe

NUM = 12045893274065266971721
DEN = 198450000000000000000000000
delta = Fraction(NUM, DEN)
T = Fraction(2, 25)
BOUND = T + delta            # 2/25 + delta, exact
BOUND_F = float(BOUND)
LO = Fraction(1243, 5000)    # 0.2486
HI = Fraction(3197, 10000)   # 0.3197

def maxcut_full(n, A):
    """Independent exact max-cut: enumerate ALL 2^n side-assignments with numpy, popcount cut edges.
    Different from brute_dmono (which loops 2^(n-1) in pure python) AND from audit_brute12 (vertex-0 fix)."""
    # edge list as arrays
    us = []; vs = []
    for u in range(n):
        for v in range(u+1, n):
            if (A[u] >> v) & 1:
                us.append(u); vs.append(v)
    if not us:
        return 0
    us = np.array(us, dtype=np.int64); vs = np.array(vs, dtype=np.int64)
    masks = np.arange(1 << n, dtype=np.int64)
    bu = (masks[:, None] >> us[None, :]) & 1
    bv = (masks[:, None] >> vs[None, :]) & 1
    cut = (bu ^ bv).sum(axis=1)
    return int(cut.max())

def tri_free_check(n, A):
    """Independent triangle-free verifier by explicit triple scan."""
    for i in range(n):
        for j in range(i+1, n):
            if not ((A[i] >> j) & 1):
                continue
            for k in range(j+1, n):
                if ((A[i] >> k) & 1) and ((A[j] >> k) & 1):
                    return False
    return True

def beta_edges(n, A):
    e = sum(1 for u in range(n) for v in range(u+1, n) if (A[u] >> v) & 1)
    mc = maxcut_full(n, A)
    return e, mc, e - mc

def blowup(n, A, t):
    """G[t]: replace each vertex by an independent set of size t; edges between blobs iff original edge.
    Triangle-free is preserved (no edges inside a blob). Returns (N, B)."""
    N = n * t
    B = [0] * N
    for u in range(n):
        for v in range(u+1, n):
            if (A[u] >> v) & 1:
                for a in range(t):
                    for b in range(t):
                        iu = u*t + a; iv = v*t + b
                        B[iu] |= 1 << iv; B[iv] |= 1 << iu
    return N, B

def run_finite(n0, n1):
    print(f"== finite in-band sup, BOUND=2/25+delta={BOUND_F:.10f} ==", flush=True)
    overall = []
    for n in range(n0, n1+1):
        C2 = Fraction(n*(n-1), 2)
        best_band = None; best_all = None
        viol = 0
        for (nn, A) in fe.enumerate_graphs(n, triangle_free=True):
            assert tri_free_check(n, A), f"geng emitted a NON-triangle-free graph at n={n}!"
            e, mc, beta = beta_edges(n, A)
            de = Fraction(e, 1) / C2
            dm = Fraction(2*beta, n*n)   # EXACT rational d_mono
            if best_all is None or dm > best_all[0]:
                best_all = (dm, e, mc, de)
            if LO <= de <= HI:
                if best_band is None or dm > best_band[0]:
                    best_band = (dm, e, mc, de)
            if dm > BOUND:
                viol += 1
        bb = best_band
        print(f" n={n}: in-band max d_mono = {float(bb[0]):.6f} (e={bb[1]} mc={bb[2]} d_edge={float(bb[3]):.4f}) "
              f"all-max={float(best_all[0]):.6f}@d_edge={float(best_all[3]):.4f}  violations(>bound)={viol}", flush=True)
        overall.append((n, float(bb[0]), viol))
    return overall

def run_blowups(n_small_max, t_max):
    """Adversarial: every small triangle-free graph, every blow-up factor, keep those landing in band,
    track max d_mono and any bound violation."""
    print(f"== blow-up probe (small n<= {n_small_max}, t<= {t_max}) ==", flush=True)
    best = None; viol = 0; n_inband = 0
    for n in range(3, n_small_max+1):
        for (nn, A) in fe.enumerate_graphs(n, triangle_free=True):
            e0, mc0, beta0 = beta_edges(n, A)
            for t in range(1, t_max+1):
                N = n*t
                # blow-up identities: e=t^2 e0, edge density -> approaches e0/C(n,2) but exact:
                E = (t*t)*e0
                C2 = Fraction(N*(N-1), 2)
                de = Fraction(E, 1)/C2
                if not (LO <= de <= HI):
                    continue
                n_inband += 1
                beta = (t*t)*beta0   # claimed blow-up identity; VERIFY exactly for small N
                if N <= 13:
                    Nb, B = blowup(n, A, t)
                    eB, mcB, betaB = beta_edges(Nb, B)
                    assert betaB == beta, f"BLOW-UP IDENTITY FAILS: G n={n} t={t} claimed beta={beta} actual={betaB}"
                dm = Fraction(2*beta, N*N)
                if best is None or dm > best[0]:
                    best = (dm, n, t, N, float(de))
                if dm > BOUND:
                    viol += 1
                    print(f"  !!! VIOLATION blow-up n={n} t={t} N={N} d_mono={float(dm):.6f} > bound", flush=True)
    if best:
        print(f" in-band blow-ups found: {n_inband}; MAX d_mono = {float(best[0]):.8f} "
              f"(small n={best[1]} t={best[2]} N={best[3]} d_edge={best[4]:.4f}); violations={viol}", flush=True)
    else:
        print(f" no in-band blow-ups found for these params (n_inband={n_inband})", flush=True)
    return best, viol

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "finite"
    if mode == "finite":
        a = int(sys.argv[2]); b = int(sys.argv[3])
        run_finite(a, b)
    elif mode == "blowup":
        run_blowups(int(sys.argv[2]), int(sys.argv[3]))
    print("DONE", flush=True)
