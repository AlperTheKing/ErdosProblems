"""Census diagnostic for UNIT-FLAT5 atom packing.

This enumerates positive pair-row-union UNIT-FLAT5 atoms and computes simple
packing summaries.  It is not a proof of UNIT-PACK; it checks whether the
observed atoms already break natural selected-family proxies such as pairwise
vertex-disjoint U-packings or per-row atom counts.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from functools import lru_cache
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_rowunion_unit_gate import (
        candidate_unions_for_Q,
        fmt_frac,
        unit_flat5_signature,
    )
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of


def set_to_mask(S):
    out = 0
    for v in S:
        out |= 1 << v
    return out


def max_disjoint(masks):
    masks = tuple(sorted(set(masks)))

    @lru_cache(None)
    def rec(i, used):
        if i == len(masks):
            return 0
        best = rec(i + 1, used)
        if masks[i] & used == 0:
            best = max(best, 1 + rec(i + 1, used | masks[i]))
        return best

    return rec(0, 0)


def enumerate_side(g6, cut_idx, n, edges, side, max_union_rows):
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return []
    E, B, M, Mset, cyc = data
    if not M:
        return []
    eta = F(n * n, 25) - len(M)
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    atoms = []
    seen_cases = set()
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                key = (Q, tuple(sorted(U)))
                if key in seen_cases:
                    continue
                seen_cases.add(key)
                tw = subset_tw(n, M, cyc, U)
                lhs = sum(tw[v] for v in Q)
                sig = sigma_of(U, B, Mset)
                pre = lhs - len(U) - sig
                if pre <= 0:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                sigrec = unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows)
                if not sigrec["is_unit"]:
                    continue
                atoms.append(
                    {
                        "g6": g6,
                        "cut": cut_idx,
                        "n": n,
                        "m": len(M),
                        "eta": eta,
                        "Q": Q,
                        "U": tuple(sorted(U)),
                        "Umask": set_to_mask(U),
                        "pre": pre,
                        "rows": tuple((g, tuple(P)) for g, P, _pset in rows),
                    }
                )
    return atoms


def summarize_group(atoms):
    if not atoms:
        return None
    eta = atoms[0]["eta"]
    masks = [a["Umask"] for a in atoms]
    by_q = {}
    for a in atoms:
        by_q.setdefault(a["Q"], []).append(a)
    max_per_q = max(len(v) for v in by_q.values())
    max_disjoint_all = max_disjoint(masks)
    max_disjoint_by_q = max(max_disjoint([a["Umask"] for a in v]) for v in by_q.values())
    return {
        "atoms": len(atoms),
        "eta": eta,
        "max_per_q": max_per_q,
        "max_disjoint_all": max_disjoint_all,
        "max_disjoint_by_q": max_disjoint_by_q,
        "q_count": len(by_q),
    }


def worker(payload):
    g6, max_cuts, max_union_rows = payload
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    out = []
    for cut_idx, side in enumerate(cuts[:max_cuts]):
        atoms = enumerate_side(g6, cut_idx, n, edges, side, max_union_rows)
        if atoms:
            summary = summarize_group(atoms)
            out.append({"g6": g6, "cut": cut_idx, "atoms": atoms, "summary": summary})
    return out


def fmt_summary(rec):
    s = rec["summary"]
    return {
        "g6": rec["g6"],
        "cut": rec["cut"],
        "atoms": s["atoms"],
        "eta": fmt_frac(s["eta"]),
        "q_count": s["q_count"],
        "max_per_q": s["max_per_q"],
        "max_disjoint_all": s["max_disjoint_all"],
        "max_disjoint_by_q": s["max_disjoint_by_q"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--max-union-rows", type=int, default=2)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    groups = []
    payloads = [(g6, args.max_cuts, args.max_union_rows) for g6 in graphs]
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for recs in pool.imap_unordered(worker, payloads, chunksize=args.chunksize):
            done += 1
            groups.extend(recs)
            if done % 1000 == 0 or done == len(graphs):
                print(f"progress graphs={done}/{len(graphs)} groups={len(groups)}", flush=True)

    total_atoms = sum(g["summary"]["atoms"] for g in groups)
    worst_atoms = max(groups, key=lambda g: g["summary"]["atoms"], default=None)
    worst_disjoint = max(groups, key=lambda g: g["summary"]["max_disjoint_all"], default=None)
    violations = []
    for g in groups:
        s = g["summary"]
        eta = s["eta"]
        if F(s["max_disjoint_all"]) > eta or F(s["max_disjoint_by_q"]) > eta:
            violations.append(g)

    print("=== UNIT-FLAT5 packing census diagnostic ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("groups:", len(groups))
    print("total_atoms:", total_atoms)
    print("worst_atoms:", fmt_summary(worst_atoms) if worst_atoms else "")
    print("worst_disjoint:", fmt_summary(worst_disjoint) if worst_disjoint else "")
    print("violations:", len(violations))
    print("first_violation:", fmt_summary(violations[0]) if violations else "")
    print("VERDICT:", "PASS_UNIT_PACK_PROXY" if not violations else "FAIL_UNIT_PACK_PROXY")


if __name__ == "__main__":
    main()
