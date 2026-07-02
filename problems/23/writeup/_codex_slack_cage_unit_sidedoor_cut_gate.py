"""Canonical side-door cuts for UNIT-FLAT5 atoms.

For a local UNIT-FLAT5 atom with two rows sharing four consecutive vertices,
there are two natural terminal side-door cuts:

  head side: {two private row endpoints, first shared vertex, outside head door}
  tail side: {last shared vertex, outside tail door}

The fake shared-path fan has the same local atom but one of these cuts has
negative slack, so it is not a maximum cut.  True census UNIT atoms should have
nonnegative, usually zero, side-door slack.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_flat5_fan_stress import build_fan, build_theta
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, sigma_of


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def fmt_rec(rec):
    if rec is None:
        return ""
    return dict(rec)


def common_sequence(row, common):
    return [v for v in row if v in common]


def side_door_cuts_for_unit(B, Mset, U, rows):
    if len(rows) != 2:
        return []
    P0 = tuple(rows[0][1])
    P1 = tuple(rows[1][1])
    S0 = set(P0)
    S1 = set(P1)
    common = S0 & S1
    if len(common) != 4:
        return []
    priv = (S0 | S1) - common
    if len(priv) != 2:
        return []

    seq0 = common_sequence(P0, common)
    seq1 = common_sequence(P1, common)
    if seq0 == seq1:
        seq = seq0
    elif seq0 == list(reversed(seq1)):
        seq = seq0
    else:
        return []
    if len(seq) != 4:
        return []

    head = seq[0]
    tail = seq[-1]
    out = []
    for e in sorted(delta(B, U)):
        u, v = e
        inside = u if u in U else v
        outside = v if u in U else u
        if inside == head:
            W = frozenset(priv | {head, outside})
            out.append(("head", e, tuple(sorted(W)), sigma_of(W, B, Mset)))
        elif inside == tail:
            W = frozenset({tail, outside})
            out.append(("tail", e, tuple(sorted(W)), sigma_of(W, B, Mset)))
        elif inside in priv:
            # Opposite-ended UNIT atom: the two private endpoints sit on
            # opposite sides of the shared four-path, so the side door is a
            # singleton private endpoint rather than a common-block endpoint.
            W = frozenset({inside, outside})
            out.append(("private", e, tuple(sorted(W)), sigma_of(W, B, Mset)))
        else:
            out.append(("other", e, tuple(sorted({inside, outside})), sigma_of(frozenset({inside, outside}), B, Mset)))
    return out


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "unit_cases": 0,
        "atoms": 0,
        "bad_shape": 0,
        "neg_side": 0,
        "hist": Counter(),
        "first_bad_shape": None,
        "first_neg": None,
    }


def merge(dst, src):
    for k in ("graphs", "cuts", "unit_cases", "atoms", "bad_shape", "neg_side"):
        dst[k] += src[k]
    dst["hist"].update(src["hist"])
    for k in ("first_bad_shape", "first_neg"):
        if dst[k] is None and src[k] is not None:
            dst[k] = src[k]


def check_side(name, n, edges, side, max_union_rows=2):
    acc = empty_acc()
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return acc
    E, B, M, Mset, cyc = data
    if not M:
        return acc
    acc["cuts"] = 1
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    atoms_seen = set()
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                tw = subset_tw(n, M, cyc, U)
                pre = sum(tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)
                if pre <= 0:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                sig = unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows)
                if not sig["is_unit"]:
                    continue
                acc["unit_cases"] += 1
                key = tuple(sorted(tuple(P) for _g, P, _pset in rows))
                if key in atoms_seen:
                    continue
                atoms_seen.add(key)
                acc["atoms"] += 1
                cuts = side_door_cuts_for_unit(B, Mset, U, rows)
                vals = tuple(sorted(c[3] for c in cuts))
                acc["hist"][vals] += 1
                if len(cuts) != 2 or any(c[0] == "other" for c in cuts):
                    acc["bad_shape"] += 1
                    if acc["first_bad_shape"] is None:
                        acc["first_bad_shape"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(str(int(c)) for c in side),
                            "Q": Q,
                            "U": tuple(sorted(U)),
                            "rows": [(g, P) for g, P, _pset in rows],
                            "cuts": cuts,
                        }
                if any(c[3] < 0 for c in cuts):
                    acc["neg_side"] += 1
                    if acc["first_neg"] is None:
                        acc["first_neg"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(str(int(c)) for c in side),
                            "Q": Q,
                            "U": tuple(sorted(U)),
                            "rows": [(g, P) for g, P, _pset in rows],
                            "cuts": cuts,
                        }
    return acc


def worker(payload):
    g6, max_cuts = payload
    n, edges = dec(g6)
    out = empty_acc()
    out["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        merge(out, check_side(f"cen{g6}#cut{idx}", n, edges, side))
    return out


def census(n, workers, chunksize, max_cuts, limit):
    graphs = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True, check=True).stdout.split()
    if limit is not None:
        graphs = graphs[:limit]
    total = empty_acc()
    payloads = [(g6, max_cuts) for g6 in graphs]
    with mp.Pool(processes=workers) as pool:
        done = 0
        for acc in pool.imap_unordered(worker, payloads, chunksize=chunksize):
            done += acc["graphs"]
            merge(total, acc)
            if done % 1000 == 0 or done == len(graphs):
                print(f"progress graphs={done}/{len(graphs)} atoms={total['atoms']} neg={total['neg_side']}", flush=True)
    return total


def generated_family(max_t, family, gmins_mode, max_cuts):
    total = empty_acc()
    if gmins_mode:
        from _stark1 import gmins as gmins_fn
    for t in range(2, max_t + 1):
        n, edges, side = build_theta(t) if family == "theta" else build_fan(t)
        sides = [side]
        if gmins_mode:
            _adj, sides = gmins_fn(n, edges)
            sides = sides[:max_cuts]
        for idx, s in enumerate(sides):
            merge(total, check_side(f"{family}-t{t}#cut{idx}", n, edges, s))
    return total


def print_acc(title, acc):
    print(f"=== {title} ===")
    for k in ("graphs", "cuts", "unit_cases", "atoms", "bad_shape", "neg_side"):
        print(f"{k}:", acc[k])
    print("hist:", dict(sorted(acc["hist"].items(), key=lambda kv: str(kv[0]))))
    print("first_bad_shape:", fmt_rec(acc["first_bad_shape"]))
    print("first_neg:", fmt_rec(acc["first_neg"]))
    verdict = "PASS_UNIT_SIDEDOOR_CUT_GATE" if acc["bad_shape"] == 0 and acc["neg_side"] == 0 else "FAIL_UNIT_SIDEDOOR_CUT_GATE"
    print("VERDICT:", verdict)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("census", "generated"), default="generated")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--family", choices=("fan", "theta"), default="fan")
    ap.add_argument("--max-t", type=int, default=8)
    ap.add_argument("--gmins", action="store_true")
    args = ap.parse_args()

    if args.mode == "census":
        acc = census(args.n, args.workers, args.chunksize, args.max_cuts, args.limit)
        print_acc(f"census N={args.n}", acc)
    else:
        acc = generated_family(args.max_t, args.family, args.gmins, args.max_cuts)
        label = f"{args.family} max_t={args.max_t} {'gmins' if args.gmins else 'intended'}"
        print_acc(label, acc)


if __name__ == "__main__":
    main()
