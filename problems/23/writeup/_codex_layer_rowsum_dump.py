"""Codex-only diagnostic: exact ROWSUM-O contribution by layers of a bad edge.

This does not certify anything. It prints the decomposition
  (O 1)_f = sum_i sum_{v in I_i(f)} p_f(v) S(v)
for selected graphs, using Fraction arithmetic.
"""
from fractions import Fraction as F
import subprocess

from _h import dec, GENG, loads
from _layerprice import layers_of


def exact_pf(info, f):
    ps = info["cyc"][f]
    nf = len(ps)
    cnt = {}
    for path in ps:
        for v in path:
            cnt[v] = cnt.get(v, 0) + 1
    return {v: F(c, nf) for v, c in cnt.items()}


def all_pf_and_s(info):
    pfs = {}
    s = {v: F(0) for v in range(info["n"])}
    for f in info["M"]:
        pf = exact_pf(info, f)
        pfs[f] = pf
        for v, val in pf.items():
            s[v] += val
    return pfs, s


def best_edge(info):
    pfs, s = all_pf_and_s(info)
    best = None
    for f, pf in pfs.items():
        rs = sum(val * s[v] for v, val in pf.items())
        if best is None or rs > best[0]:
            best = (rs, f)
    return best, pfs, s


def dump_graph(g6, blow=1):
    n, e = dec(g6)
    if blow != 1:
        ee = []
        for a, b in e:
            for i in range(blow):
                for j in range(blow):
                    ee.append((a * blow + i, b * blow + j))
        n, e = n * blow, ee
    info = loads(n, e)
    if info is None:
        print(f"{g6}[{blow}] skipped")
        return
    (rs, f), pfs, s = best_edge(info)
    lay_float, _, h = layers_of(info, f)
    pf = pfs[f]
    print(f"\nGRAPH {g6}[{blow}] N={n} Gamma={info['G']} |M|={len(info['M'])}")
    print(f"best f={f} ell={info['ell'][f]} rowsum={rs} = {float(rs):.6f}; slack N-rs={float(F(n)-rs):.6f}")
    prefix = set()
    for i in range(h + 1):
        verts = sorted(lay_float[i])
        prefix.update(verts)
        d_b = sum(1 for a, b in info["Bset"] if (a in prefix) != (b in prefix))
        d_m = sum(1 for a, b in info["Mset"] if (a in prefix) != (b in prefix))
        contrib = sum(pf[v] * s[v] for v in verts)
        mass = sum(pf[v] for v in verts)
        avg = contrib / mass if mass else F(0)
        items = " ".join(f"{v}:p={pf[v]},S={s[v]}" for v in verts)
        print(f"  layer {i}: mass={mass} contrib={contrib} avgS={avg} prefix_dB={d_b} prefix_dM={d_m} :: {items}")


def census_worst(nmax=10):
    worst = None
    for nn in range(5, nmax + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        for g6 in out:
            n, e = dec(g6)
            info = loads(n, e)
            if info is None:
                continue
            (rs, f), _, _ = best_edge(info)
            gap = rs - n
            if worst is None or gap > worst[0]:
                worst = (gap, g6, f, rs, n)
    print(f"\nCENSUS-WORST N<= {nmax}: g6={worst[1]} f={worst[2]} rowsum={worst[3]} N={worst[4]} gap={worst[0]}")
    dump_graph(worst[1])


if __name__ == "__main__":
    for g6 in ["FCp`_", "H?bB@_W", "I?BD@g]Qo", "I?ABCc]}?", "J?AEB?oE?W?"]:
        dump_graph(g6)
    dump_graph("J???E?pNu\\?", blow=2)
    census_worst(10)
