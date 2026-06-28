"""GLOBAL structure probe. Key identity: ROWSUM(f) = <p_f, S> = sum_g <p_f,p_g>.
Since <p_f,p_f> = sum_v p_f(v)^2 and p_f(v)<=1 with sum_v p_f(v)=ell(f), we have <p_f,p_f> <= ell(f).
Write ROWSUM(f) = <p_f,p_f> + X(f) where X(f) = sum_{g!=f} <p_f,p_g> = cross-load.
Conjecture family to test EXACTLY:
  (Q1) <p_f,p_f> = ell(f) always? (i.e. p_f(v) in {0,1}? NO in general -- multiple geodesics)
  (Q2) ROWSUM(f) <= ell(f) + (something). What bounds X(f)?
  (Q3) Symmetry: <p_f,p_g> = <p_g,p_f> (trivially). Is sum_g X over all f telescoping?
We compute, for EVERY gamma-min cut of the witness and 3 other band-bad N=12 graphs:
  - <p_f,p_f>, X(f), ROWSUM(f), ell(f)
  - the Gram matrix O[f,g]=<p_f,p_g> and its row sums
  - check ROWSUM(f) <= N and the margin
  - test: is ROWSUM(f) <= sum_g ell(g)*ell(f)/N-ish?  No -- test a CLEAN global bound.
Main candidate global bound to EXACT-test:
  (GB) sum_f ell(f) * ROWSUM(f) ... no. Instead the operator bound:
  ROWSUM(f) = (O 1)_f, and rho(O) <= max_f (O1)_f. We want (O1)_f <= N for each f.
  Equivalent: <p_f, S> <= N where S = sum_g p_g = total load vector, ||p_f||_1 = ell(f).
  Since p_f(v) <= 1 entrywise: <p_f,S> <= sum_{v: p_f(v)>0} S(v) <= (support of f-geodesic-interval) * max S.
  TEST the sharp form: <p_f,S> <= sum over the ell(f) layers of (max load contributed per layer)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _stark1 import gmins
from _satzmu_conn import struct_for_side

def cut_data(n, adj, s):
    st = struct_for_side(n, adj, s)
    if st is None: return None
    M, ell, T, mu, cyc = st
    pf = {}; S = [F(0)]*n
    for g in M:
        Ps = cyc[g]; k = len(Ps); d = {}
        for P in Ps:
            for v in P: d[v] = d.get(v, F(0)) + F(1, k)
        pf[g] = d
        for v, pv in d.items(): S[v] += pv
    O = {}
    for f in M:
        for g in M:
            O[(f,g)] = sum(pv*pf[g].get(v,F(0)) for v,pv in pf[f].items())
    return dict(M=M, ell=ell, S=S, pf=pf, O=O, n=n)

def probe(g6):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    adj2, cuts = gmins(n, E)
    rows_all = []
    for ci, s in enumerate(cuts):
        cd = cut_data(n, adj2, s)
        if cd is None: continue
        M = cd['M']; O = cd['O']; ell = cd['ell']
        for f in M:
            ROW = sum(O[(f,g)] for g in M)
            self_ = O[(f,f)]
            X = ROW - self_
            rows_all.append((g6, ci, f, ell[f], self_, X, ROW))
    return rows_all, n

def find_band_bad_n12(limit=400):
    """scan census N=12 for graphs whose gamma-min cut has a 'bad band row':
    R=ROWSUM-N could be anything, but use the original criterion that the band split bound fails.
    Simpler: collect graphs where some gamma-min cut has max ROWSUM > N - 1.5 (tight)."""
    out = subprocess.run([GENG,"-tc","12","-d2"],capture_output=True,text=True).stdout.split()
    found = []
    for g6 in out[:limit]:
        n, E = dec(g6)
        adj2, cuts = gmins(n, E)
        if not cuts: continue
        mx = F(0)
        for s in cuts:
            cd = cut_data(n, adj2, s)
            if cd is None: continue
            M = cd['M']; O = cd['O']
            for f in M:
                ROW = sum(O[(f,g)] for g in M)
                if ROW > mx: mx = ROW
        if mx >= F(n) - 1:  # tight: within 1 of N
            found.append((g6, mx))
    return found

if __name__ == "__main__":
    print("=== witness decomposition: ROWSUM = self + cross ===")
    ra, n = probe("K??CE@A{?]Fc")
    print(f"N={n}")
    print(f"{'cut':>3} {'f':>10} {'ell':>3} {'self':>8} {'cross_X':>8} {'ROWSUM':>8} {'N-ROW':>8}")
    seen = set()
    for g6, ci, f, L, sf, X, ROW in ra:
        key = (ci, f)
        print(f"{ci:>3} {str(f):>10} {L:>3} {float(sf):>8.3f} {float(X):>8.3f} {float(ROW):>8.3f} {float(F(n)-ROW):>8.3f}")
    # key aggregate facts
    print("\n--- facts ---")
    print(f"max self <p_f,p_f> = {max(float(r[4]) for r in ra):.4f} (<= max ell?)")
    print(f"max cross X(f)     = {max(float(r[5]) for r in ra):.4f}")
    print(f"max ROWSUM         = {max(float(r[6]) for r in ra):.4f}  (N={n})")
    # is self == ell when single geodesic? show ell vs self
    print("\n--- self vs ell (self < ell iff f has multiple geodesics) ---")
    for g6, ci, f, L, sf, X, ROW in ra:
        if abs(float(sf)-L) > 1e-9:
            print(f"  cut{ci} f={f}: ell={L} but self={sf}={float(sf):.3f} (multi-geodesic)")
