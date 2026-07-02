"""Protector-path gate for selected UNIT-FLAT5 atoms.

For a UNIT-FLAT5 row-union atom U, the good examples have exactly two blue
boundary door edges.  Their outside endpoints are connected by a B-path wholly
outside U; together with U this forms a protected two-door cell.  The outside
path has length 3 in the smallest atoms and length 4 in a few N=11 census
atoms, so the protected cell is not assumed to have a fixed vertex count.

The fake shared-path fan lacks this outside connector and is not maxcut.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter, deque

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_flat5_fan_stress import build_fan, build_theta
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, sigma_of


def outside_endpoint(edge, U):
    a, b = edge
    if a in U and b not in U:
        return b
    if b in U and a not in U:
        return a
    return None


def restricted_b_distance(n, B, s, t, forbidden):
    if s in forbidden or t in forbidden:
        return None
    adj = [[] for _ in range(n)]
    for u, v in B:
        if u in forbidden or v in forbidden:
            continue
        adj[u].append(v)
        adj[v].append(u)
    q = deque([(s, 0)])
    seen = {s}
    while q:
        u, d = q.popleft()
        if u == t:
            return d
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))
    return None


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "unit_cases": 0,
        "atoms": 0,
        "door_count_hist": Counter(),
        "outside_dist_hist": Counter(),
        "atom_door_count_hist": Counter(),
        "atom_outside_dist_hist": Counter(),
        "first_by_dist": {},
        "missing_protector": 0,
        "atom_missing_protector": 0,
        "first_missing": None,
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "unit_cases", "atoms", "missing_protector", "atom_missing_protector"):
        dst[key] += src[key]
    dst["door_count_hist"].update(src["door_count_hist"])
    dst["outside_dist_hist"].update(src["outside_dist_hist"])
    dst["atom_door_count_hist"].update(src["atom_door_count_hist"])
    dst["atom_outside_dist_hist"].update(src["atom_outside_dist_hist"])
    for key, rec in src["first_by_dist"].items():
        dst["first_by_dist"].setdefault(key, rec)
    if dst["first_missing"] is None and src["first_missing"] is not None:
        dst["first_missing"] = src["first_missing"]


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
    seen_cases = set()
    atoms_seen = set()
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
                acc["unit_cases"] += 1
                bdy = sorted(delta(B, U))
                outs = [outside_endpoint(e, U) for e in bdy]
                outs = [x for x in outs if x is not None]
                acc["door_count_hist"][len(outs)] += 1
                dist = None
                if len(outs) == 2:
                    dist = restricted_b_distance(n, B, outs[0], outs[1], set(U))
                key = "None" if dist is None else dist
                acc["outside_dist_hist"][key] += 1
                atom_key = tuple(sorted((g, tuple(P)) for g, P, _pset in rows))
                is_new_atom = atom_key not in atoms_seen
                if is_new_atom:
                    atoms_seen.add(atom_key)
                    acc["atoms"] += 1
                    acc["atom_door_count_hist"][len(outs)] += 1
                    acc["atom_outside_dist_hist"][key] += 1
                acc["first_by_dist"].setdefault(
                    key,
                    {
                        "name": name,
                        "n": n,
                        "m": len(M),
                        "side": "".join(str(int(c)) for c in side),
                        "Q": Q,
                        "U": tuple(sorted(U)),
                        "boundary": tuple(bdy),
                        "outside_endpoints": tuple(outs),
                        "rows": tuple((g, P) for g, P, _pset in rows),
                    },
                )
                if dist is None:
                    acc["missing_protector"] += 1
                    if is_new_atom:
                        acc["atom_missing_protector"] += 1
                    if acc["first_missing"] is None:
                        acc["first_missing"] = {
                            "name": name,
                            "n": n,
                            "m": len(M),
                            "side": "".join(str(int(c)) for c in side),
                            "Q": Q,
                            "U": tuple(sorted(U)),
                            "boundary": tuple(bdy),
                            "outside_endpoints": tuple(outs),
                            "rows": tuple((g, P) for g, P, _pset in rows),
                        }
    return acc


def worker(payload):
    g6, max_cuts = payload
    n, edges = dec(g6)
    out = empty_acc()
    out["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for side in cuts[:max_cuts]:
        merge_acc(out, check_side(f"cen{g6}", n, edges, side))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--theta", action="store_true")
    ap.add_argument("--family", choices=("fan", "theta"), default="theta")
    ap.add_argument("--intended", action="store_true")
    ap.add_argument("--max-t", type=int, default=8)
    args = ap.parse_args()

    total = empty_acc()
    if args.theta:
        for t in range(2, args.max_t + 1):
            n, edges, intended = build_theta(t) if args.family == "theta" else build_fan(t)
            if args.intended:
                cuts = [intended]
            else:
                _adj, cuts = gmins(n, edges)
                cuts = cuts[: args.max_cuts]
            local = empty_acc()
            for side in cuts:
                merge_acc(local, check_side(f"{args.family}-t{t}", n, edges, side))
            merge_acc(total, local)
            print(
                f"{args.family} t={t} cuts={len(cuts)} unit={local['unit_cases']} atoms={local['atoms']} "
                f"door_hist={dict(sorted(local['door_count_hist'].items()))} "
                f"dist_hist={dict(sorted(local['outside_dist_hist'].items(), key=lambda kv: str(kv[0])))} "
                f"atom_missing={local['atom_missing_protector']}",
                flush=True,
            )
    else:
        if args.n is None:
            raise SystemExit("--n is required unless --theta is used")
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
                    f"progress graphs={done}/{len(graphs)} unit={total['unit_cases']} "
                    f"atoms={total['atoms']} missing={total['missing_protector']}",
                    flush=True,
                )

    print("=== UNIT-FLAT5 protector path gate ===")
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("unit_cases:", total["unit_cases"])
    print("atoms:", total["atoms"])
    print("door_count_hist:", dict(sorted(total["door_count_hist"].items())))
    print("outside_dist_hist:", dict(sorted(total["outside_dist_hist"].items(), key=lambda kv: str(kv[0]))))
    print("atom_door_count_hist:", dict(sorted(total["atom_door_count_hist"].items())))
    print("atom_outside_dist_hist:", dict(sorted(total["atom_outside_dist_hist"].items(), key=lambda kv: str(kv[0]))))
    print("first_by_dist:", dict(sorted(total["first_by_dist"].items(), key=lambda kv: str(kv[0]))))
    print("missing_protector:", total["missing_protector"])
    print("atom_missing_protector:", total["atom_missing_protector"])
    print("first_missing:", total["first_missing"] or "")
    print(
        "VERDICT:",
        "PASS_PROTECTOR_GATE" if total["missing_protector"] == 0 and total["atom_missing_protector"] == 0 else "FAIL_PROTECTOR_GATE",
    )


if __name__ == "__main__":
    main()
