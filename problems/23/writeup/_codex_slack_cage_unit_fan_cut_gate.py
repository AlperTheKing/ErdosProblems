"""Endpoint fan-cut gate for grouped UNIT-FLAT5 atoms.

For UNIT-FLAT5 atoms whose two rows share a common 4-vertex path, collect all
rows sharing that common path.  For each endpoint of the common path, form the
canonical fan-side set

    W = {private row endpoints attached to that endpoint} union {endpoint}.

If three or more bad leaves are attached to the same endpoint and only two
blue side doors leave W, then sigma(W)<0 and the cut is not maximum.  This
gate computes the actual sigma(W), so it is a direct maxcut falsifier for
multi-leaf overpacking.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter, defaultdict

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_flat5_fan_stress import build_fan, build_theta
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, sigma_of


def common_sequence(row, common):
    return tuple(v for v in row if v in common)


def private_endpoint(row, common):
    priv = [v for v in row if v not in common]
    return priv[0] if len(priv) == 1 else None


def adjacent_in_path(row, a, b):
    return any({row[i], row[i + 1]} == {a, b} for i in range(len(row) - 1))


def classify_private_side(row, seq):
    common = set(seq)
    p = private_endpoint(row, common)
    if p is None:
        return None
    if adjacent_in_path(row, p, seq[0]):
        return "head", p
    if adjacent_in_path(row, p, seq[-1]):
        return "tail", p
    return None


def atom_key(rows):
    return tuple(sorted((g, tuple(P)) for g, P, _pset in rows))


def collect_unit_atoms(n, edges, side, max_union_rows=2):
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return None, []
    E, B, M, Mset, cyc = data
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    seen_cases = set()
    seen_atoms = set()
    atoms = []
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                case_key = (Q, tuple(sorted(U)))
                if case_key in seen_cases:
                    continue
                seen_cases.add(case_key)
                tw = subset_tw(n, M, cyc, U)
                pre = sum(tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)
                if pre <= 0:
                    continue
                rows = counted_rows(Q, U, M, cyc)
                sig = unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows)
                if not sig["is_unit"]:
                    continue
                key = atom_key(rows)
                if key in seen_atoms:
                    continue
                seen_atoms.add(key)
                row_paths = tuple(tuple(P) for _g, P, _pset in rows)
                common = set(row_paths[0]).intersection(row_paths[1])
                if len(common) != 4:
                    continue
                atoms.append({"Q": Q, "U": frozenset(U), "rows": rows, "row_paths": row_paths, "common": frozenset(common)})
    return data, atoms


def candidate_sequences(atoms):
    seqs = set()
    for atom in atoms:
        common = set(atom["common"])
        for row in atom["row_paths"]:
            seq = common_sequence(row, common)
            if len(seq) == 4:
                seqs.add(seq)
                seqs.add(tuple(reversed(seq)))
    return sorted(seqs)


def endpoint_fan_records(n, data, atoms):
    E, B, M, Mset, cyc = data
    by_common = defaultdict(list)
    for atom in atoms:
        by_common[tuple(sorted(atom["common"]))].append(atom)

    records = []
    for common_key, group_atoms in by_common.items():
        rows_by_path = {}
        for atom in group_atoms:
            for g, P, _pset in atom["rows"]:
                rows_by_path[tuple(P)] = g
        rows = sorted(rows_by_path)
        for seq in candidate_sequences(group_atoms):
            if set(seq) != set(common_key):
                continue
            sides = {"head": set(), "tail": set()}
            bad_by_side = {"head": set(), "tail": set()}
            for row in rows:
                got = classify_private_side(row, seq)
                if got is None:
                    continue
                side_name, p = got
                sides[side_name].add(p)
                bad_by_side[side_name].add(rows_by_path[row])
            for side_name, leaves in sides.items():
                if not leaves:
                    continue
                endpoint = seq[0] if side_name == "head" else seq[-1]
                W = frozenset(set(leaves) | {endpoint})
                dB = len(delta(B, W))
                dM = len(delta(Mset, W))
                sig = dB - dM
                records.append(
                    {
                        "common4": common_key,
                        "seq": seq,
                        "side": side_name,
                        "W": tuple(sorted(W)),
                        "leaves": tuple(sorted(leaves)),
                        "bad_edges": tuple(sorted(bad_by_side[side_name])),
                        "dB": dB,
                        "dM": dM,
                        "sigma": sig,
                    }
                )
    # Same W may appear from reversed sequence; deduplicate.
    dedup = {}
    for rec in records:
        key = (rec["W"], rec["dB"], rec["dM"])
        old = dedup.get(key)
        if old is None or (rec["dM"], -rec["dB"]) > (old["dM"], -old["dB"]):
            dedup[key] = rec
    return list(dedup.values())


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "atoms": 0,
        "fan_records": 0,
        "negative": 0,
        "min_sigma": None,
        "sigma_hist": Counter(),
        "first_negative": None,
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "atoms", "fan_records", "negative"):
        dst[key] += src[key]
    dst["sigma_hist"].update(src["sigma_hist"])
    if src["min_sigma"] is not None and (dst["min_sigma"] is None or src["min_sigma"]["sigma"] < dst["min_sigma"]["sigma"]):
        dst["min_sigma"] = src["min_sigma"]
    if dst["first_negative"] is None and src["first_negative"] is not None:
        dst["first_negative"] = src["first_negative"]


def check_side(name, n, edges, side):
    acc = empty_acc()
    data, atoms = collect_unit_atoms(n, edges, side)
    if data is None:
        return acc
    acc["cuts"] = 1
    acc["atoms"] = len(atoms)
    for rec in endpoint_fan_records(n, data, atoms):
        acc["fan_records"] += 1
        acc["sigma_hist"][rec["sigma"]] += 1
        full = {"name": name, "n": n, "side_string": "".join(str(int(c)) for c in side), **rec}
        if acc["min_sigma"] is None or rec["sigma"] < acc["min_sigma"]["sigma"]:
            acc["min_sigma"] = full
        if rec["sigma"] < 0:
            acc["negative"] += 1
            if acc["first_negative"] is None:
                acc["first_negative"] = full
    return acc


def worker(payload):
    g6, max_cuts = payload
    n, edges = dec(g6)
    out = empty_acc()
    out["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        merge_acc(out, check_side(f"cen{g6}#cut{idx}", n, edges, side))
    return out


def fmt_rec(rec):
    return "" if rec is None else str(rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--generated", action="store_true")
    ap.add_argument("--family", choices=("fan", "theta"), default="theta")
    ap.add_argument("--intended", action="store_true")
    ap.add_argument("--max-t", type=int, default=8)
    args = ap.parse_args()

    total = empty_acc()
    if args.generated:
        for t in range(2, args.max_t + 1):
            n, edges, intended = build_theta(t) if args.family == "theta" else build_fan(t)
            if args.intended:
                cuts = [intended]
            else:
                _adj, cuts = gmins(n, edges)
                cuts = cuts[: args.max_cuts]
            local = empty_acc()
            for idx, side in enumerate(cuts):
                merge_acc(local, check_side(f"{args.family}-t{t}#cut{idx}", n, edges, side))
            merge_acc(total, local)
            print(
                f"{args.family} t={t} cuts={len(cuts)} atoms={local['atoms']} "
                f"fan_records={local['fan_records']} negative={local['negative']} "
                f"min_sigma={'' if local['min_sigma'] is None else local['min_sigma']['sigma']} "
                f"hist={dict(sorted(local['sigma_hist'].items()))}",
                flush=True,
            )
    else:
        if args.n is None:
            raise SystemExit("--n is required unless --generated is used")
        graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
        if args.limit is not None:
            graphs = graphs[: args.limit]
        payloads = [(g6, args.max_cuts) for g6 in graphs]
        with mp.Pool(processes=args.workers) as pool:
            done = 0
            for acc in pool.imap_unordered(worker, payloads, chunksize=args.chunksize):
                done += acc["graphs"]
                merge_acc(total, acc)
                if done % 1000 == 0 or done == len(graphs):
                    print(
                        f"progress graphs={done}/{len(graphs)} atoms={total['atoms']} "
                        f"negative={total['negative']}",
                        flush=True,
                    )

    print("=== UNIT-FLAT5 endpoint fan-cut gate ===")
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("atoms:", total["atoms"])
    print("fan_records:", total["fan_records"])
    print("negative:", total["negative"])
    print("sigma_hist:", dict(sorted(total["sigma_hist"].items())))
    print("min_sigma:", fmt_rec(total["min_sigma"]))
    print("first_negative:", fmt_rec(total["first_negative"]))
    print("VERDICT:", "PASS_FAN_CUT_GATE" if total["negative"] == 0 else "FAIL_FAN_CUT_GATE")


if __name__ == "__main__":
    main()
