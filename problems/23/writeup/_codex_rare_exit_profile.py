"""Profile the rare-exit first candidate SDR.

This prints aggregate invariants after the canonical shortest-tier matching:
which F1-degree classes are consumed, which remain, and the minimum Hall slack
of the residual longer-tier matching problem.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import (
    best_seed_moat_mask,
    h_blowup,
    residuals,
)
from _codex_balanced_stage0_gate import min_cost_stage0


def min_hall_slack(left, right, adj):
    """Return min |N(Y)|-|Y| over Y subset right."""
    right = tuple(right)
    best = None
    zeros = 0
    for bits in range(1 << len(right)):
        Y = {right[i] for i in range(len(right)) if (bits >> i) & 1}
        N = {u for u in left if adj.get(u, set()) & Y}
        slack = len(N) - len(Y)
        if best is None or slack < best:
            best = slack
        zeros += int(slack == 0)
    return best, zeros, 1 << len(right)


def comp_hall(left, right, adj):
    right = tuple(right)
    best = None
    zeros = 0
    for bits in range(1 << len(right)):
        Y = {right[i] for i in range(len(right)) if (bits >> i) & 1}
        N = {u for u in left if adj.get(u, set()) & Y}
        slack = len(N) - len(Y)
        if best is None or slack < best:
            best = slack
        zeros += int(slack == 0)
    return best, zeros, 1 << len(right)


def comp_signature(left, right, adj):
    left = tuple(left)
    right = tuple(right)
    unseen_l = set(left)
    unseen_r = set(right)
    comps = []
    while unseen_l or unseen_r:
        if unseen_l:
            start = ("L", next(iter(unseen_l)))
        else:
            start = ("R", next(iter(unseen_r)))
        q = [start]
        cl = set()
        cr = set()
        if start[0] == "L":
            unseen_l.remove(start[1])
        else:
            unseen_r.remove(start[1])
        while q:
            side, node = q.pop()
            if side == "L":
                cl.add(node)
                for e in adj.get(node, set()):
                    if e in unseen_r:
                        unseen_r.remove(e)
                        q.append(("R", e))
            else:
                cr.add(node)
                for f in left:
                    if node in adj.get(f, set()) and f in unseen_l:
                        unseen_l.remove(f)
                        q.append(("L", f))
        edges = sum(1 for f in cl for e in cr if e in adj.get(f, set()))
        comps.append((len(cl), len(cr), edges, edges == len(cl) * len(cr), comp_hall(cl, cr, adj)))
    return tuple(sorted(comps))


def profile(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det["cross_m"]))
    E_edges = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    min_len = min(ell[f] for f in F_edges)
    min_lam = min(lamb[e] for e in E_edges)
    F0 = tuple(f for f in F_edges if ell[f] == min_len)
    F1 = tuple(f for f in F_edges if ell[f] > min_len)
    E0 = tuple(e for e in E_edges if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return None
    used = set(m0.values())
    rem = tuple(e for e in E_edges if e not in used)
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    hall = min_hall_slack(F1, rem, adj1)
    comps = comp_signature(F1, rem, adj1)
    return {
        "F0": len(F0),
        "F1": len(F1),
        "E0": len(E0),
        "Erem": len(rem),
        "used_deg": tuple(sorted(Counter(deg_f1[e] for e in used).items())),
        "rem_deg": tuple(sorted(Counter(deg_f1[e] for e in rem if e in deg_f1).items())),
        "res_hall": hall,
        "res_comp": comps,
    }


def scan_cut(name, n, adj, side, acc, examples, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, rv in enumerate(R):
        if rv >= 0:
            continue
        got = best_seed_moat_mask(n, adj, side, st, v, max_add)
        if got is None:
            continue
        _seed, mask, _psi = got
        det = terminal_shadow_details(n, adj, side, st, mask)
        if det is None:
            continue
        p = profile(st, det)
        if p is None:
            acc["none"] += 1
            continue
        key = tuple(sorted((k, repr(v)) for k, v in p.items()))
        acc["profiles"][key] += 1
        examples.setdefault(key, dict(name=name, n=n, side="".join(map(str, side)), v=v, S=tuple(i for i in range(n) if (mask >> i) & 1), R=str(rv), profile=p))


def scan_allmax(name, n, edges, acc, examples, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, examples, max_add)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=1)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-inherited", type=int, default=0)
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()

    acc = {"profiles": Counter(), "none": 0}
    examples = {}
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_allmax("cen%d" % nn, n, edges, acc, examples, args.max_add)
    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        scan_allmax("H2-allmax", n, edges, acc, examples, args.max_add)
    for t in range(2, args.h_inherited + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H%d-inherited" % t, n, adj_from_edges(n, edges), side, acc, examples, args.max_add)

    print("profile_count:", len(acc["profiles"]), "none:", acc["none"])
    for idx, (key, count) in enumerate(acc["profiles"].most_common(args.top), 1):
        ex = examples[key]
        print("-" * 72)
        print("rank", idx, "count", count)
        print("profile", ex["profile"])
        print("example", ex)


if __name__ == "__main__":
    main()
