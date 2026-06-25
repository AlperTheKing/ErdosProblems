#!/usr/bin/env python3
"""FRESH INDEPENDENT EXACT AUDIT of CLAIM 2:  d_mono(W_G) <= U_8(W_G), triangle-free G, n=6 and n=7.

CRITICAL FIX over validate_dmono_le_u8.py: the profile graphs can have up to ~93 nodes, where the
reference uses a HEURISTIC MaxCut (lower bound on MaxCut => OVER-estimate of U_8, can MASK a violation).
Here MaxCut is EXACT: brute for <=22 off-nodes, ILP (PuLP/CBC, validated vs brute) for larger.
Everything else (d_mono, weights, integer-scaled accumulation) is reimplemented from scratch.
U_8 and d_mono compared as EXACT Fractions.

Canonicalization of the 8-vertex anchor graph R uses compute_U8.canon_label, independently verified
iso-invariant and shown to give IDENTICAL U_8 to a brute 8! WL-class canon on C5 (both = 2/25).
"""
import itertools, time
from math import factorial
from fractions import Fraction as F
import flag_engine as fe
from compute_U8 import canon_label
import pulp


def popc(x):
    return bin(x).count("1")


def edges_count(n, A):
    return sum(popc(A[v]) for v in range(n)) // 2


def maxcut_int(n, A):
    best = 0
    for mask in range(1 << (n - 1)):
        full = mask << 1
        c = 0
        for u in range(n):
            au = A[u]; su = (full >> u) & 1
            w = au >> (u + 1); v = u + 1
            while w:
                if (w & 1) and (((full >> v) & 1) != su):
                    c += 1
                w >>= 1; v += 1
        if c > best:
            best = c
    return best


def d_mono(n, A):
    return F(2 * (edges_count(n, A) - maxcut_int(n, A)), n * n)


def blowup(counts, Tadj):
    parts = []
    for p, c in enumerate(counts):
        parts += [p] * c
    n = len(parts); A = [0] * n
    for u in range(n):
        for w in range(u + 1, n):
            if parts[u] != parts[w] and (Tadj[parts[u]] >> parts[w]) & 1:
                A[u] |= 1 << w; A[w] |= 1 << u
    return n, A


def comps(total, parts):
    if parts == 1:
        yield (total,); return
    for f in range(total + 1):
        for rest in comps(total - f, parts - 1):
            yield (f,) + rest


def maxcut_brute(nodes, edges):
    nn = len(nodes)
    if nn == 0:
        return 0
    idx = {v: i for i, v in enumerate(nodes)}
    el = [(idx[a], idx[b], w) for (a, b), w in edges.items()]
    best = 0
    for mask in range(1 << (nn - 1)):
        c = 0
        for a, b, w in el:
            if ((mask >> a) & 1) != ((mask >> b) & 1):
                c += w
        if c > best:
            best = c
    return best


def maxcut_ilp(nodes, edges):
    """EXACT integer-weighted MaxCut via CBC ILP."""
    if not edges:
        return 0
    prob = pulp.LpProblem("mc", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x{i}", cat="Binary") for i, v in enumerate(nodes)}
    obj = []
    for k, ((a, b), w) in enumerate(edges.items()):
        y = pulp.LpVariable(f"y{k}", lowBound=0, upBound=1)
        prob += y <= x[a] + x[b]
        prob += y <= 2 - x[a] - x[b]
        obj.append(w * y)
    prob += pulp.lpSum(obj)
    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    assert pulp.LpStatus[status] == "Optimal", f"CBC status {pulp.LpStatus[status]}"
    return int(round(pulp.value(prob.objective)))


def maxcut_exact(nodes, edges):
    nn = len(nodes)
    if nn <= 22:
        return maxcut_brute(nodes, edges)
    return maxcut_ilp(nodes, edges)


_cm = {}
def canon_memo(Radj):
    rk = tuple(Radj); v = _cm.get(rk)
    if v is None:
        v = canon_label(8, Radj); _cm[rk] = v
    return v


def U8_exact(n_parts, Tadj):
    SCALE = (n_parts ** 10) * 90
    W = {}
    for counts in comps(10, n_parts):
        mult = factorial(10)
        for c in counts:
            mult //= factorial(c)
        if mult == 0:
            continue
        nn, A = blowup(counts, Tadj)
        for i in range(10):
            Ai = A[i]
            for j in range(10):
                if i != j and (Ai >> j) & 1:
                    anch = [v for v in range(10) if v != i and v != j]
                    idx = {v: p for p, v in enumerate(anch)}
                    Radj = [0] * 8
                    for p in range(8):
                        for q in range(p + 1, 8):
                            if (A[anch[p]] >> anch[q]) & 1:
                                Radj[p] |= 1 << q; Radj[q] |= 1 << p
                    key, inv = canon_memo(Radj)
                    Aset = frozenset(inv[idx[v]] for v in anch if (A[i] >> v) & 1)
                    Bset = frozenset(inv[idx[v]] for v in anch if (A[j] >> v) & 1)
                    d = W.setdefault(key, {})
                    d[(Aset, Bset)] = d.get((Aset, Bset), 0) + mult
    total = 0
    maxnodes = 0
    for key, ed in W.items():
        offdiag = {}; sl = 0
        for (Aset, Bset), w in ed.items():
            if Aset == Bset:
                sl += w
            else:
                a, b = tuple(sorted([Aset, Bset], key=lambda s: (len(s), sorted(s))))
                offdiag[(a, b)] = offdiag.get((a, b), 0) + w
        offnodes = set()
        for (a, b) in offdiag:
            offnodes.add(a); offnodes.add(b)
        maxnodes = max(maxnodes, len(offnodes))
        mc = maxcut_exact(list(offnodes), offdiag) if offdiag else 0
        total += sl + (sum(offdiag.values()) - mc)
    return F(total, SCALE), maxnodes


def main():
    print("FRESH EXACT AUDIT (exact MaxCut): d_mono <= U_8, all triangle-free n=6,7", flush=True)
    worst = None; wg = None; count = 0; viol = 0
    for n in [6, 7]:
        graphs = fe.enumerate_graphs(n, triangle_free=True)
        print(f"\n--- n={n}: {len(graphs)} graphs ---", flush=True)
        t0 = time.time()
        for gi, (nn, A) in enumerate(graphs):
            assert fe.is_triangle_free(nn, A)
            dm = d_mono(nn, A)
            u8, mx = U8_exact(nn, A)
            slack = u8 - dm
            count += 1
            tag = ""
            if slack < 0:
                viol += 1
                tag = "  !!! VIOLATION"
                print(f"  !!! VIOLATION g#{gi} e={edges_count(nn,A)} d_mono={dm} U_8={u8} slack={float(slack):.3e} adj={A}", flush=True)
            if worst is None or slack < worst:
                worst = slack; wg = (n, list(A), dm, u8)
            print(f"  g{gi:3d} e={edges_count(nn,A):2d} maxprofnodes={mx:3d} d_mono={float(dm):.6f} U_8={float(u8):.6f} slack={float(slack):+.3e}{tag}", flush=True)
        print(f"  n={n} done [{time.time()-t0:.0f}s]", flush=True)
    print("\n========== SUMMARY ==========", flush=True)
    print(f"graphs checked = {count}", flush=True)
    print(f"violations (U_8 < d_mono) = {viol}", flush=True)
    print(f"worst slack (min U_8 - d_mono) = {worst} = {float(worst):.6e}", flush=True)
    print(f"worst graph: n={wg[0]} d_mono={float(wg[2]):.6f} U_8={float(wg[3]):.6f} adj={wg[1]}", flush=True)
    print(f"\nCLAIM 2 (d_mono <= U_8) on n=6,7 with EXACT MaxCut: {'CONFIRMED' if viol==0 else 'REFUTED'}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
