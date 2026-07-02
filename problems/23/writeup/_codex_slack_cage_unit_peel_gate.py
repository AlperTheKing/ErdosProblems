"""Protected-cell peel gate for selected UNIT-FLAT5 atoms.

This gate checks the exact finite shadow of the protected-cell peel target:
selected UNIT atoms in a cut should either give disjoint bad-boundary-free
protected cells, or belong to a multi-leaf fan component already killed by the
maxcut fan-collapse lemma.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter, defaultdict, deque

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_flat5_fan_stress import build_theta
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, sigma_of
    from _codex_slack_cage_unit_fan_component_gate import common4_key
    from _codex_slack_cage_unit_protector_gate import outside_endpoint


def shortest_b_path_avoiding(n, B, s, t, forbidden):
    if s in forbidden or t in forbidden:
        return None
    adj = [[] for _ in range(n)]
    for u, v in B:
        if u in forbidden or v in forbidden:
            continue
        adj[u].append(v)
        adj[v].append(u)
    q = deque([s])
    parent = {s: None}
    while q:
        u = q.popleft()
        if u == t:
            path = []
            cur = t
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return tuple(reversed(path))
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                q.append(v)
    return None


def count_boundary(edge_set, S):
    S = set(S)
    return sum(1 for u, v in edge_set if (u in S) ^ (v in S))


def count_inside(edge_set, S):
    S = set(S)
    return sum(1 for u, v in edge_set if u in S and v in S)


def collect_units(name, n, edges, side):
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return []
    E, B, M, Mset, cyc = data
    if not M:
        return []
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    seen_cases = set()
    seen_atoms = set()
    atoms = []
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, 2):
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
                atom_key = tuple(sorted((g, tuple(P)) for g, P, _pset in rows))
                if atom_key in seen_atoms:
                    continue
                seen_atoms.add(atom_key)
                bdy = sorted(delta(B, U))
                outs = [outside_endpoint(e, U) for e in bdy]
                outs = [x for x in outs if x is not None]
                path = None
                if len(outs) == 2:
                    path = shortest_b_path_avoiding(n, B, outs[0], outs[1], set(U))
                cell = None if path is None else frozenset(set(U) | set(path))
                atoms.append(
                    {
                        "name": name,
                        "n": n,
                        "m": len(M),
                        "side": "".join(str(int(c)) for c in side),
                        "Q": Q,
                        "U": frozenset(U),
                        "rows": tuple((g, P) for g, P, _pset in rows),
                        "common4": common4_key(rows),
                        "doors": tuple(bdy),
                        "path": path,
                        "cell": cell,
                        "cell_size": None if cell is None else len(cell),
                        "cell_bad_inside": None if cell is None else count_inside(Mset, cell),
                        "cell_bad_boundary": None if cell is None else count_boundary(Mset, cell),
                        "cell_blue_boundary": None if cell is None else count_boundary(B, cell),
                    }
                )
    return atoms


def components_from_overlaps(atoms):
    n = len(atoms)
    adj = [set() for _ in range(n)]
    for i in range(n):
        ci = atoms[i]["cell"]
        if ci is None:
            continue
        for j in range(i + 1, n):
            cj = atoms[j]["cell"]
            if cj is None:
                continue
            if ci & cj:
                adj[i].add(j)
                adj[j].add(i)
    seen = set()
    comps = []
    for i in range(n):
        if i in seen:
            continue
        stack = [i]
        seen.add(i)
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(tuple(sorted(comp)))
    return comps


def comp_has_fan_collapse(atoms, comp):
    by_core = defaultdict(set)
    for idx in comp:
        key = atoms[idx]["common4"]
        if key is None:
            continue
        for _g, P in atoms[idx]["rows"]:
            by_core[key].add(tuple(P))
    return any(len(rowset) >= 3 for rowset in by_core.values())


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "atom_count_hist": Counter(),
        "cell_comp_hist": Counter(),
        "missing_cell": 0,
        "bad_cell": 0,
        "overlap_fail": 0,
        "first_missing_cell": None,
        "first_bad_cell": None,
        "first_overlap_fail": None,
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "missing_cell", "bad_cell", "overlap_fail"):
        dst[key] += src[key]
    dst["atom_count_hist"].update(src["atom_count_hist"])
    dst["cell_comp_hist"].update(src["cell_comp_hist"])
    for key in ("first_missing_cell", "first_bad_cell", "first_overlap_fail"):
        if dst[key] is None and src[key] is not None:
            dst[key] = src[key]


def check_side(name, n, edges, side):
    acc = empty_acc()
    atoms = collect_units(name, n, edges, side)
    acc["cuts"] = 1
    acc["atom_count_hist"][len(atoms)] += 1
    if not atoms:
        return acc
    for atom in atoms:
        if atom["cell"] is None:
            acc["missing_cell"] += 1
            acc["first_missing_cell"] = acc["first_missing_cell"] or atom
            continue
        if atom["cell_size"] < 10 or atom["cell_bad_inside"] != 2 or atom["cell_bad_boundary"] != 0:
            acc["bad_cell"] += 1
            acc["first_bad_cell"] = acc["first_bad_cell"] or atom
    comps = components_from_overlaps(atoms)
    acc["cell_comp_hist"][tuple(sorted(len(c) for c in comps))] += 1
    for comp in comps:
        if len(comp) <= 1:
            continue
        if comp_has_fan_collapse(atoms, comp):
            continue
        acc["overlap_fail"] += 1
        if acc["first_overlap_fail"] is None:
            acc["first_overlap_fail"] = {
                "name": name,
                "n": n,
                "side": atoms[comp[0]]["side"],
                "component": tuple(comp),
                "atoms": [atoms[i] for i in comp],
            }
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--theta", action="store_true")
    ap.add_argument("--intended", action="store_true")
    ap.add_argument("--max-t", type=int, default=8)
    args = ap.parse_args()

    total = empty_acc()
    if args.theta:
        for t in range(2, args.max_t + 1):
            n, edges, intended = build_theta(t)
            if args.intended:
                cuts = [intended]
            else:
                _adj, cuts = gmins(n, edges)
                cuts = cuts[: args.max_cuts]
            local = empty_acc()
            for idx, side in enumerate(cuts):
                merge_acc(local, check_side(f"theta-t{t}#cut{idx}", n, edges, side))
            merge_acc(total, local)
            print(
                f"theta t={t} cuts={len(cuts)} atom_hist={dict(sorted(local['atom_count_hist'].items()))} "
                f"missing={local['missing_cell']} bad_cell={local['bad_cell']} overlap_fail={local['overlap_fail']}",
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
                        f"progress graphs={done}/{len(graphs)} missing={total['missing_cell']} "
                        f"bad_cell={total['bad_cell']} overlap_fail={total['overlap_fail']}",
                        flush=True,
                    )

    print("=== UNIT-FLAT5 protected-cell peel gate ===")
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("atom_count_hist:", dict(sorted(total["atom_count_hist"].items())))
    print("cell_comp_hist:", dict(sorted(total["cell_comp_hist"].items(), key=lambda kv: str(kv[0]))))
    print("missing_cell:", total["missing_cell"])
    print("bad_cell:", total["bad_cell"])
    print("overlap_fail:", total["overlap_fail"])
    print("first_missing_cell:", total["first_missing_cell"] or "")
    print("first_bad_cell:", total["first_bad_cell"] or "")
    print("first_overlap_fail:", total["first_overlap_fail"] or "")
    print(
        "VERDICT:",
        "PASS_PROTECTED_CELL_PEEL"
        if total["missing_cell"] == 0 and total["bad_cell"] == 0 and total["overlap_fail"] == 0
        else "FAIL_PROTECTED_CELL_PEEL",
    )


if __name__ == "__main__":
    main()
