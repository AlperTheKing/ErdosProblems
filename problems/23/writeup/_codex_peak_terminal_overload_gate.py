"""Exact gate for the peak terminal-overload selector.

For v with negative K2T residual R[v] < 0, define terminal overloads

  Omega_{L,prefix/suffix}(v)

from the terminal intervals of all length-L shortest rows through v, and pick
maximizers of Omega/(L*m_L).  The proposed peak lemma says a peak bundle is a
neutral, B-connected, terminal-shadow-safe switch with Psi>0.

This gate distinguishes:
  * some peak maximizer works;
  * every peak maximizer works.
"""

import argparse
import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import is_triangle_free
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_lenbundle_switch_gate import h_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


def connected(adj):
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def mask_of(vertices):
    out = 0
    for v in vertices:
        out |= 1 << v
    return out


def peak_bundles(n, st, v):
    """Return peak terminal-overload bundles for v.

    Each item is (score, Omega, L, sign, m, mask), sign in {'pref','suff'}.
    """
    _M, ell, T, _mu, cyc = st
    N = F(n)
    items = []
    for L in sorted(set(ell.values())):
        rows = []
        m = F(0)
        for f, paths in cyc.items():
            if ell[f] != L:
                continue
            w = F(1, len(paths))
            for path0 in paths:
                path = list(path0)
                if v not in path:
                    continue
                rows.append((path, w))
                m += w
        if m == 0:
            continue
        for sign in ("pref", "suff"):
            omega = [F(0)] * n
            support = set()
            for path, w in rows:
                i = path.index(v)
                interval = path[: i + 1] if sign == "pref" else path[i:]
                for x in interval:
                    omega[x] += w
                    support.add(x)
            Omega = sum(omega[x] * (T[x] - N) for x in range(n)) - F(1, 2) * m * (T[v] - N)
            score = Omega / (F(L) * m)
            items.append((score, Omega, L, sign, m, mask_of(support)))
    if not items:
        return []
    best = max(x[0] for x in items)
    return [x for x in items if x[0] == best]


def omega_identity_defect(n, st, v):
    """Check D(v)=sum Omegas for all L/sign."""
    M, ell, T, _mu, cyc = st
    N = F(n)
    D = -residual_from_st(n, st, v)
    total = F(0)
    for L in sorted(set(ell.values())):
        rows = []
        m = F(0)
        for f, paths in cyc.items():
            if ell[f] != L:
                continue
            w = F(1, len(paths))
            for path0 in paths:
                path = list(path0)
                if v not in path:
                    continue
                rows.append((path, w))
                m += w
        for sign in ("pref", "suff"):
            omega = [F(0)] * n
            for path, w in rows:
                i = path.index(v)
                interval = path[: i + 1] if sign == "pref" else path[i:]
                for x in interval:
                    omega[x] += w
            total += sum(omega[x] * (T[x] - N) for x in range(n)) - F(1, 2) * m * (T[v] - N)
    return total - D


def residual_from_st(n, st, v):
    # Inline K2*T coordinate to avoid rebuilding the whole matrix in identity checks.
    M, _ell, T, _mu, cyc = st
    N = F(n)
    kt = F(0)
    for f, paths in cyc.items():
        w = F(1, len(paths))
        for path in paths:
            if v in path:
                kt += w * sum(T[x] for x in path)
    return N * T[v] - kt


def switch_good(n, adj, side, st, mask):
    d = boundary_delta(n, adj, side, mask)
    bc = Bconn(n, adj, flip_side(side, mask))
    psi = terminal_shadow_psi(n, adj, side, st, mask)
    return d == 0 and bc and psi is not None and psi > 0, d, bc, psi


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, _cyc = st
    if not M:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        defect = omega_identity_defect(n, st, v)
        if defect != 0:
            acc["identity_fail"] += 1
            if acc["first_identity_fail"] is None:
                acc["first_identity_fail"] = (name, n, "".join(map(str, side)), v, str(defect))
        if rv >= 0:
            continue
        acc["neg"] += 1
        peaks = peak_bundles(n, st, v)
        if not peaks or peaks[0][0] <= 0:
            acc["peak_positive_fail"] += 1
            if acc["first_peak_positive_fail"] is None:
                acc["first_peak_positive_fail"] = (name, n, "".join(map(str, side)), v, str(rv), peaks)
            continue
        good = []
        bad = []
        for item in peaks:
            score, Omega, L, sign, m, mask = item
            ok, d, bc, psi = switch_good(n, adj, side, st, mask)
            row = (str(score), str(Omega), L, sign, str(m), d, bc, None if psi is None else str(psi),
                   tuple(i for i in range(n) if (mask >> i) & 1))
            (good if ok else bad).append(row)
        if good:
            acc["some_peak_good"] += 1
        else:
            acc["some_peak_fail"] += 1
            if acc["first_some_peak_fail"] is None:
                acc["first_some_peak_fail"] = (name, n, "".join(map(str, side)), v, str(rv), bad)
        if bad:
            acc["all_peak_fail"] += 1
            if acc["first_all_peak_fail"] is None:
                acc["first_all_peak_fail"] = (name, n, "".join(map(str, side)), v, str(rv), bad, good)
        else:
            acc["all_peak_good"] += 1


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def new_acc():
    return dict(
        neg=0,
        identity_fail=0,
        first_identity_fail=None,
        peak_positive_fail=0,
        first_peak_positive_fail=None,
        some_peak_good=0,
        some_peak_fail=0,
        first_some_peak_fail=None,
        all_peak_good=0,
        all_peak_fail=0,
        first_all_peak_fail=None,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
    args = parser.parse_args()

    acc = new_acc()
    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph(g6, nn, edges, acc)
        print(
            "census N=%d neg=%d some_peak=%d fail=%d identity_fail=%d"
            % (n, acc["neg"], acc["some_peak_good"], acc["some_peak_fail"], acc["identity_fail"]),
            flush=True,
        )

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc)
        print(
            "H?AFBo][%d] neg=%d some_peak=%d fail=%d"
            % (t, acc["neg"], acc["some_peak_good"], acc["some_peak_fail"]),
            flush=True,
        )

    if args.random:
        rng = random.Random(882)
        made = 0
        tries = 0
        while made < args.random and tries < 100000:
            tries += 1
            n = rng.choice([11, 12])
            p = rng.uniform(0.16, 0.32)
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
            if not edges or not is_triangle_free(n, edges):
                continue
            adj = adj_from_edges(n, edges)
            if not connected(adj):
                continue
            made += 1
            scan_graph("rand%d" % made, n, edges, acc)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("negative vertices:", acc["neg"])
    print("Omega identity failures:", acc["identity_fail"], acc["first_identity_fail"] or "")
    print("peak positive failures:", acc["peak_positive_fail"], acc["first_peak_positive_fail"] or "")
    print("some peak good:", acc["some_peak_good"])
    print("some peak FAIL:", acc["some_peak_fail"], acc["first_some_peak_fail"] or "")
    print("all peaks good:", acc["all_peak_good"])
    print("all peaks FAIL:", acc["all_peak_fail"], acc["first_all_peak_fail"] or "")


if __name__ == "__main__":
    main()
