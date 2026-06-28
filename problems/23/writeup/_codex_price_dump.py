"""Codex diagnostic: dump numerical layer-price certificates.

The convex layer-price solver finds c_{f,i}=1/b_{f,i} with sum_i c_{f,i}<=1
and vertex budget sum p_f(v)/c_{f,i}<=N. This script prints the shape of
those prices beside exact layer S-averages to look for a structural formula.
"""

from fractions import Fraction as F

from _h import dec, loads
from _layerprice import layers_of
from _layerprice_verify import get_prices


def exact_pfs(info):
    out = {}
    S = {v: F(0) for v in range(info["n"])}
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, den) for v, c in cnt.items()}
        out[f] = pf
        for v, val in pf.items():
            S[v] += val
    return out, S


def blowup_edges(n, edges, t):
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def dump(g6, t=1):
    n, e = dec(g6)
    if t != 1:
        n, e = blowup_edges(n, e, t)
    info = loads(n, e)
    b, _, _, _, _, tstar = get_prices(info)
    pfs, S = exact_pfs(info)
    print(f"\nGRAPH {g6}[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} t*={tstar:.6f}")
    for f in info["M"]:
        lay, pf_float, h = layers_of(info, f)
        pf = pfs[f]
        harm = 0.0
        rowsum = F(0)
        print(f"  f={f} ell={info['ell'][f]}")
        for i in range(h + 1):
            bb = b[(f, i)]
            cc = 1.0 / bb
            harm += cc
            verts = sorted(lay[i])
            mass = sum(pf[v] for v in verts)
            contrib = sum(pf[v] * S[v] for v in verts)
            rowsum += contrib
            avg = contrib / mass if mass else F(0)
            print(
                f"    layer {i}: b={bb:.6f} c={cc:.6f} "
                f"avgS={float(avg):.6f} contrib={float(contrib):.6f} "
                f"verts={verts}"
            )
        print(f"    harmonic_sum={harm:.6f} rowsum={float(rowsum):.6f}")


if __name__ == "__main__":
    for case in [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
    ]:
        dump(*case)
