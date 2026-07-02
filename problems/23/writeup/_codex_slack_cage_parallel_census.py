"""Parallel exact Slack-CAGE census gate.

This is a faster all-subset checker for the candidate

    D_Q(U) <= |U| + sigma(U) + eta

with eta = N^2/25 - |M|.  It distributes by graph6 string and, inside each
gamma-minimum connected-B cut, computes subset-local row load by adding each
row atom to every supermask of its vertex set.
"""

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, Bconn, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def edge_mask(u, v):
    return (1 << u) | (1 << v)


def popcount(x):
    return x.bit_count()


def iter_supermasks(pmask, allmask):
    free = allmask ^ pmask
    sub = free
    while True:
        yield pmask | sub
        if sub == 0:
            break
        sub = (sub - 1) & free


def check_side(name, n, edges, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, _T, _mu, cyc = st
    if not M:
        return None

    allmask = (1 << n) - 1
    bad = {tuple(sorted(e)) for e in M}
    blue = []
    bad_edges = []
    for u, v in edges:
        e = tuple(sorted((u, v)))
        if side[u] != side[v]:
            blue.append((u, v))
        elif e in bad:
            bad_edges.append((u, v))

    subset_count = 1 << n
    slack = [0] * subset_count
    for mask in range(subset_count):
        dB = sum(1 for u, v in blue if popcount(mask & edge_mask(u, v)) == 1)
        dM = sum(1 for u, v in bad_edges if popcount(mask & edge_mask(u, v)) == 1)
        slack[mask] = dB - dM

    tw = [[F(0) for _ in range(n)] for _ in range(subset_count)]
    q_rows = []
    for g in M:
        den = len(cyc[g])
        mass = F(1, den)
        for P in cyc[g]:
            ptuple = tuple(P)
            pmask = 0
            for v in ptuple:
                pmask |= 1 << v
            q_rows.append((g, ptuple))
            for umask in iter_supermasks(pmask, allmask):
                row = tw[umask]
                for v in ptuple:
                    row[v] += mass

    eta = F(n * n, 25) - len(M)
    checks = 0
    min_rec = None
    mins = {"empty": None, "full": None, "proper_nonempty": None, "counted": None, "proper_counted": None}
    max_prebank = {"all": None, "proper_counted": None}
    prebank_pos = Counter()
    first = None

    for f, Q in q_rows:
        for mask in range(subset_count):
            lhs = sum(tw[mask][v] for v in Q)
            rhs = F(popcount(mask) + slack[mask]) + eta
            checks += 1
            margin = rhs - lhs
            rec = (
                margin,
                name,
                n,
                len(M),
                f,
                Q,
                mask,
                lhs,
                rhs,
                popcount(mask),
                slack[mask],
                eta,
            )
            prebank = lhs - F(popcount(mask) + slack[mask])
            if min_rec is None or margin < min_rec[0]:
                min_rec = rec
            if mask == 0:
                cat = "empty"
            elif mask == allmask:
                cat = "full"
            else:
                cat = "proper_nonempty"
            if mins[cat] is None or margin < mins[cat][0]:
                mins[cat] = rec
            if lhs > 0 and (mins["counted"] is None or margin < mins["counted"][0]):
                mins["counted"] = rec
                if cat == "proper_nonempty" and (mins["proper_counted"] is None or margin < mins["proper_counted"][0]):
                    mins["proper_counted"] = rec
            elif lhs > 0 and cat == "proper_nonempty" and (mins["proper_counted"] is None or margin < mins["proper_counted"][0]):
                mins["proper_counted"] = rec
            if max_prebank["all"] is None or prebank > max_prebank["all"][0]:
                max_prebank["all"] = (prebank, rec)
            if lhs > 0 and cat == "proper_nonempty" and (
                max_prebank["proper_counted"] is None or prebank > max_prebank["proper_counted"][0]
            ):
                max_prebank["proper_counted"] = (prebank, rec)
            if prebank > 0:
                prebank_pos["all"] += 1
                prebank_pos[f"value:{prebank}"] += 1
                if lhs > 0 and cat == "proper_nonempty":
                    prebank_pos["proper_counted"] += 1
                    prebank_pos[f"proper_value:{prebank}"] += 1
            if margin < 0:
                first = rec
                break
        if first is not None:
            break

    return {
        "checks": checks,
        "min": min_rec,
        "mins": mins,
        "max_prebank": max_prebank,
        "prebank_pos": prebank_pos,
        "first": first,
    }


def worker(g6):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    total = 0
    min_rec = None
    mins = {"empty": None, "full": None, "proper_nonempty": None, "counted": None, "proper_counted": None}
    max_prebank = {"all": None, "proper_counted": None}
    prebank_pos = Counter()
    first = None
    cut_count = 0
    for idx, side in enumerate(cuts):
        r = check_side(f"cen{g6}#cut{idx}", n, edges, adj, side)
        if r is None:
            continue
        cut_count += 1
        total += r["checks"]
        if r["min"] is not None and (min_rec is None or r["min"][0] < min_rec[0]):
            min_rec = r["min"]
        for cat, rec in r["mins"].items():
            if rec is not None and (mins[cat] is None or rec[0] < mins[cat][0]):
                mins[cat] = rec
        for cat, item in r["max_prebank"].items():
            if item is not None and (max_prebank[cat] is None or item[0] > max_prebank[cat][0]):
                max_prebank[cat] = item
        prebank_pos.update(r["prebank_pos"])
        if r["first"] is not None:
            first = r["first"]
            break
    return {
        "g6": g6,
        "cuts": cut_count,
        "checks": total,
        "min": min_rec,
        "mins": mins,
        "max_prebank": max_prebank,
        "prebank_pos": prebank_pos,
        "first": first,
    }


def fmt_rec(rec):
    if rec is None:
        return ""
    margin, name, n, m, f, Q, mask, lhs, rhs, size, slack, eta = rec
    U = tuple(i for i in range(n) if (mask >> i) & 1)
    return {
        "margin": str(margin),
        "name": name,
        "n": n,
        "m": m,
        "f": f,
        "Q": Q,
        "U": U,
        "lhs": str(lhs),
        "rhs": str(rhs),
        "size": size,
        "slack": slack,
        "eta": str(eta),
    }


def fmt_prebank(item):
    if item is None:
        return ""
    prebank, rec = item
    out = fmt_rec(rec)
    out["prebank"] = str(prebank)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    checks = 0
    cuts = 0
    min_rec = None
    mins = {"empty": None, "full": None, "proper_nonempty": None, "counted": None, "proper_counted": None}
    max_prebank = {"all": None, "proper_counted": None}
    prebank_pos = Counter()
    first = None
    done = 0

    with mp.Pool(processes=args.workers) as pool:
        for r in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            checks += r["checks"]
            cuts += r["cuts"]
            if r["min"] is not None and (min_rec is None or r["min"][0] < min_rec[0]):
                min_rec = r["min"]
            for cat, rec in r["mins"].items():
                if rec is not None and (mins[cat] is None or rec[0] < mins[cat][0]):
                    mins[cat] = rec
            for cat, item in r["max_prebank"].items():
                if item is not None and (max_prebank[cat] is None or item[0] > max_prebank[cat][0]):
                    max_prebank[cat] = item
            prebank_pos.update(r["prebank_pos"])
            if r["first"] is not None and first is None:
                first = r["first"]
                if args.stop_first:
                    pool.terminate()
                    break
            if done % 250 == 0:
                print(f"progress graphs={done}/{len(graphs)} cuts={cuts} checks={checks}", flush=True)

    print("=== parallel Slack-CAGE all-subset census ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("cuts:", cuts)
    print("checks:", checks)
    print("min_margin:", fmt_rec(min_rec))
    print("min_empty:", fmt_rec(mins["empty"]))
    print("min_full:", fmt_rec(mins["full"]))
    print("min_proper_nonempty:", fmt_rec(mins["proper_nonempty"]))
    print("min_counted:", fmt_rec(mins["counted"]))
    print("min_proper_counted:", fmt_rec(mins["proper_counted"]))
    print("max_prebank:", fmt_prebank(max_prebank["all"]))
    print("max_proper_counted_prebank:", fmt_prebank(max_prebank["proper_counted"]))
    print("positive_prebank_checks:", prebank_pos["all"])
    print("positive_proper_counted_prebank_checks:", prebank_pos["proper_counted"])
    value_counts = {k: v for k, v in sorted(prebank_pos.items()) if k.startswith("value:")}
    proper_value_counts = {k: v for k, v in sorted(prebank_pos.items()) if k.startswith("proper_value:")}
    print("positive_prebank_values:", value_counts)
    print("positive_proper_counted_prebank_values:", proper_value_counts)
    print("first:", fmt_rec(first))
    print("VERDICT:", "HOLDS" if first is None else "FAILS")


if __name__ == "__main__":
    main()
