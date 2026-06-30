"""PINPOINT the origin of the Hardy diagonal  T[v]-N <= d(v)=L*_vv.
Question: is it a gamma-MINIMALITY consequence, or a purely structural (any-max-cut) load bound?
We test the SAME diagonal inequality on:
  (A) gamma-MIN max cuts        (the relevant cuts)
  (B) NON-gamma-min max cuts     (max cut but NOT Gamma-minimizing)  -- (H) itself is FALSE on these, so if the
      DIAGONAL still holds here, the diagonal bound is NOT what carries gamma-minimality; it is structural.
We also test the sharper LOCAL load identity behind d(v): for a vertex v on cycles, with c(v)=#{(f,Q): v in Q}
weighted by beta/|cyc[f]|, we have d(v)=2*sum weights, and T[v]=sum_f ell[f]*(frac of geodesics through v).
Report exact min slack in each regime + whether (H) (full PSD) splits by regime (sanity: must fail on some B).
Run: python _gmin_diag_origin.py
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos, bdist_restr
from _satzmu_conn import struct_for_side
from _hardy_gate import BETA, build_H
from _csmspec import is_psd
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski


def all_maxcuts(n, adj):
    edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
    best = -1; cuts = []
    for m in range(1 << (n - 1)):
        side = [(m >> u) & 1 for u in range(n)]
        c = sum(1 for u, v in edges if side[u] != side[v])
        if c > best: best = c; cuts = [side[:]]
        elif c == best: cuts.append(side[:])
    return cuts


def gamma_of(n, adj, side):
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return None
    G = F(0)
    for (u, v) in M:
        d = bdist_restr(adj, side, u, v)
        if d < 0: return None
        G += (d + 1) ** 2
    return G


def hardy_diag(n, M, ell, cyc):
    d = [F(0)] * n
    for f in M:
        Qs = cyc[f]; L = ell[f]
        w = BETA[L] / len(Qs)
        for Q in Qs:
            for v in set(Q):
                d[v] += 2 * w
    return d


def diag_check(n, adj, side):
    """Return (min_slack, hardy_fail, H_psd) for one max cut, or None if no bad edge / not B-conn struct."""
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n)
    d = hardy_diag(n, M, ell, cyc)
    ms = None; fail = 0
    for v in range(n):
        sl = d[v] - (T[v] - N)
        if sl < 0: fail += 1
        if ms is None or sl < ms: ms = sl
    H = build_H(n, M, ell, T, cyc, BETA)
    psd, _ = is_psd(H)
    return ms, fail, psd


def run(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = all_maxcuts(n, adj)
    # gamma value per max cut
    gv = []
    for s in cuts:
        g = gamma_of(n, adj, s)
        if g is not None:
            gv.append((s, g))
    if not gv:
        return
    gmin = min(g for _, g in gv)
    for s, g in gv:
        r = diag_check(n, adj, s)
        if r is None:
            continue
        ms, fail, psd = r
        regime = 'A_gmin' if g == gmin else 'B_nongmin'
        acc[regime]['cuts'] += 1
        acc[regime]['diag_fail'] += fail
        if fail == 0:
            if acc[regime]['min_slack'] is None or ms < acc[regime]['min_slack']:
                acc[regime]['min_slack'] = ms
        else:
            if acc[regime]['min_slack_neg'] is None or ms < acc[regime]['min_slack_neg']:
                acc[regime]['min_slack_neg'] = ms
                acc[regime]['neg_ex'] = (name, n, float(ms))
        if not psd:
            acc[regime]['H_notpsd'] += 1
        else:
            acc[regime]['H_psd'] += 1


def main():
    acc = {r: dict(cuts=0, diag_fail=0, min_slack=None, min_slack_neg=None, neg_ex=None,
                   H_psd=0, H_notpsd=0) for r in ('A_gmin', 'B_nongmin')}
    # census N=5..9 (ALL max cuts, split by gamma-min vs not)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); run(f"cen{nn}", n, E, acc)
    # blow-ups
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2),(3,3,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 16: run(f"blow{sizes}", nn, EE, acc)
    grN, grE = mycielski(5, Cn(5)); run("Grotzsch_N11", grN, grE, acc)

    print("=" * 72)
    for r in ('A_gmin', 'B_nongmin'):
        a = acc[r]
        print(f"[{r}] max-cuts={a['cuts']}  diag-fails(T-N<=d(v))={a['diag_fail']}  "
              f"min_slack(when all-ok)={(float(a['min_slack']) if a['min_slack'] is not None else None)}  "
              f"min_slack(neg rows)={(float(a['min_slack_neg']) if a['min_slack_neg'] is not None else None)} {a['neg_ex'] or ''}")
        print(f"        (H) full-PSD: PSD={a['H_psd']}  NOT-PSD={a['H_notpsd']}")
    print("=" * 72)
    A = acc['A_gmin']; B = acc['B_nongmin']
    if A['diag_fail'] == 0 and B['diag_fail'] == 0:
        print("CONCLUSION: Hardy DIAGONAL T[v]-N<=d(v) holds on BOTH gamma-min AND non-gamma-min max cuts")
        print("            => the diagonal is a STRUCTURAL load bound, NOT a gamma-minimality consequence.")
        print("            gamma-minimality must enter (H) OFF-DIAGONALLY (B_nongmin has (H) NOT-PSD=%d while diag still holds)." % B['H_notpsd'])
    else:
        print("CONCLUSION: diagonal FAILS somewhere -> it IS gamma-min specific (A_fail=%d B_fail=%d)" % (A['diag_fail'], B['diag_fail']))


if __name__ == "__main__":
    main()
