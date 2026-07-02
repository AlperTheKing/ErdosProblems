"""Search rational certificates for real-valued DW-Hall.

SciPy is used only to find approximate widths.  A row is counted OK only after
all DW-Hall constraints are verified exactly with Fraction rational widths.
"""

import argparse
from fractions import Fraction as F
from math import sqrt

import scipy.optimize as opt

from _codex_dwhall_uniform_probe import (
    Cn,
    GENG,
    Bconn,
    adj_of,
    blowup,
    bridge,
    build_two_lane,
    components,
    cycle_blowup_side,
    dec,
    gmins,
    mycielski,
    norm,
    struct_for_side,
    supports_and_p,
)


def exact_eps(w, svals, m):
    total = F(0)
    for wi, si in zip(w, svals):
        base = F(m) / wi
        if si > base:
            total += si - base
    return total


def exact_ok(w, svals, n, m):
    D = F(n * n, 25) - m
    if any(x <= 0 for x in w):
        return False, None
    if sum(w, F(0)) > n:
        return False, None
    L = len(w)
    for i in range(L):
        if w[i] * w[(i + 1) % L] < m:
            return False, None
    e = exact_eps(w, svals, m)
    return e <= D, e


def rationalize_vector(x, svals, n, m, max_den):
    # Try direct rounded vector first, then small directed coordinate nudges.
    base = [F(float(v)).limit_denominator(max_den) for v in x]
    ok, e = exact_ok(base, svals, n, m)
    if ok:
        return tuple(base), e

    # Local candidates around each coordinate.  This is intentionally modest.
    cand_lists = []
    for v in x:
        f = F(float(v)).limit_denominator(max_den)
        den = f.denominator
        cands = {f}
        for q in (den, max_den):
            a = int(float(v) * q)
            for da in range(-3, 4):
                if a + da > 0:
                    cands.add(F(a + da, q))
        cand_lists.append(sorted(cands, key=lambda z: abs(float(z) - float(v))))

    best = None
    L = len(cand_lists)

    def dfs(i, cur):
        nonlocal best
        if i == L:
            ok, e = exact_ok(cur, svals, n, m)
            if ok:
                best = (tuple(cur), e)
                return True
            return False
        for val in cand_lists[i][:9]:
            if sum(cur, F(0)) + val > n:
                continue
            if i > 0 and cur[-1] * val < m:
                continue
            if dfs(i + 1, cur + [val]):
                return True
        return False

    dfs(0, [])
    return best


def scipy_candidate(svals, n, m):
    L = len(svals)
    D = float(F(n * n, 25) - m)
    sf = [float(s) for s in svals]

    def eps_sum(x):
        return sum(max(0.0, sf[i] - m / x[i]) for i in range(L))

    def objective(x):
        # Minimize eps, with a tiny sum penalty to stay away from the sum cap.
        return eps_sum(x) + 1e-6 * sum(x)

    cons = []
    cons.append({"type": "ineq", "fun": lambda x: n - sum(x)})
    cons.append({"type": "ineq", "fun": lambda x: D - eps_sum(x)})
    for i in range(L):
        cons.append({"type": "ineq", "fun": lambda x, i=i: x[i] * x[(i + 1) % L] - m})

    starts = []
    r = sqrt(m)
    if L * r <= n:
        starts.append([r] * L)
    starts.append([n / L] * L)
    # Alternating small/large patterns.
    for shift in range(min(L, 5)):
        x = [r] * L
        for i in range(L):
            if (i + shift) % 2 == 0:
                x[i] = max(1e-3, r * 0.75)
            else:
                x[i] = r / 0.75
        scale = min(1.0, n / sum(x))
        x = [max(1e-3, z * scale) for z in x]
        starts.append(x)

    bounds = [(1e-7, n) for _ in range(L)]
    best = None
    for x0 in starts:
        res = opt.minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 1000, "ftol": 1e-12, "disp": False})
        if not res.success and best is not None:
            continue
        val = objective(res.x)
        if best is None or val < best[0]:
            best = (val, res.x, res.success, res.message)
    return best


def find_cert(svals, n, m, max_den):
    # First try simple rational all-equal approximations around sqrt(m).
    cand = scipy_candidate(svals, n, m)
    if cand is None:
        return None
    for den in (max_den, max_den * 10, max_den * 100):
        got = rationalize_vector(cand[1], svals, n, m, den)
        if got is not None:
            return got
    return None


def check_cut(name, n, edges, side, acc, max_den, stop_first=False):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return True
    st = struct_for_side(n, adj, side)
    if st is None:
        return True
    M_raw, _ell, _T, _mu, cyc_raw = st
    if not M_raw:
        return True
    M = [norm(g) for g in M_raw]
    cyc = {norm(g): [tuple(row) for row in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)
    m = len(M)
    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        for Q in cyc[f]:
            svals = [sum((p[g][v] for g in comp), F(0)) for v in Q]
            acc["rows"] += 1
            cert = find_cert(svals, n, m, max_den)
            if cert is None:
                acc["fail"] += 1
                rec = {"name": name, "n": n, "m": m, "f": f, "Q": tuple(Q), "svals": tuple(svals), "D": F(n * n, 25) - m}
                if acc["first_fail"] is None:
                    acc["first_fail"] = rec
                if stop_first:
                    return False
            else:
                w, e = cert
                acc["ok"] += 1
                if acc["first_cert"] is None:
                    acc["first_cert"] = (name, n, m, tuple(Q), w, e)
    return True


def run_gmins(name, n, edges, max_cuts, acc, max_den, stop_first=False):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        if not check_cut(name, n, edges, side, acc, max_den, stop_first):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--max-cuts", type=int, default=4)
    ap.add_argument("--max-den", type=int, default=100)
    ap.add_argument("--two-lane-max", type=int, default=16)
    ap.add_argument("--blowup-t", type=int, default=2)
    ap.add_argument("--blowup-nmax", type=int, default=22)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-blowups", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {"cuts": 0, "rows": 0, "ok": 0, "fail": 0, "first_fail": None, "first_cert": None}

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            if not check_cut(f"two-lane-L{L}", n, edges, side, acc, args.max_den, args.stop_first):
                break

    if not args.skip_blowups and not (args.stop_first and acc["first_fail"]):
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    if not check_cut(f"direct-C{c}[{t}]", n, edges, cycle_blowup_side([t] * c), acc, args.max_den, args.stop_first):
                        break
            if args.stop_first and acc["first_fail"]:
                break

    if not args.skip_named and not (args.stop_first and acc["first_fail"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            if not run_gmins(name, n, edges, args.max_cuts, acc, args.max_den, args.stop_first):
                break

    if not args.skip_census and not (args.stop_first and acc["first_fail"]):
        import subprocess
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                if not run_gmins(f"cen{g6}", n, edges, args.max_cuts, acc, args.max_den, args.stop_first):
                    break
            if args.stop_first and acc["first_fail"]:
                break

    print("=== DW-Hall rational certificate probe ===")
    for k in ("cuts", "rows", "ok", "fail"):
        print(f"{k}: {acc[k]}")
    print("first_cert:", acc["first_cert"] or "")
    print("first_fail:", acc["first_fail"] or "")
    print("VERDICT:", "CERTIFIED" if acc["fail"] == 0 else "UNRESOLVED_OR_FAIL")


if __name__ == "__main__":
    main()