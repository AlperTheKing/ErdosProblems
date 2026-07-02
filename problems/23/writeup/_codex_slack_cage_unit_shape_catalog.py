"""Protected-cell shape catalog for selected UNIT-FLAT5 atoms.

A selected UNIT atom is the two-row length-5 / denominator-1 / intersection-4
row-union obstruction isolated by the bank gates.  The protector gate showed
that every true gmin census atom has exactly two old blue doors and an outside
B-path joining their outside endpoints, while fake fan cuts do not.

This script records the induced protected cell:

    C = U union shortest_B_path_outside_U(door_out_0, door_out_1).

The working proof target is that these cells are separable local units:
large enough to pay one bank atom by induction, and with no bad boundary.
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
    from _codex_slack_cage_flat5_fan_stress import build_theta
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, sigma_of
    from _codex_slack_cage_unit_protector_gate import outside_endpoint


def norm_edge(u, v):
    return (u, v) if u < v else (v, u)


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


def edge_counts(edge_set, S):
    S = set(S)
    inside = 0
    boundary = 0
    outside = 0
    for u, v in edge_set:
        iu = u in S
        iv = v in S
        if iu and iv:
            inside += 1
        elif iu or iv:
            boundary += 1
        else:
            outside += 1
    return inside, boundary, outside


def role_signature(B, Mset, U, rows, path):
    """A small labelled signature stable under the two row orderings.

    It is intentionally not a full graph canonical form.  It records exactly
    the objects used by the local proof: two leaf vertices, the common 4-core,
    and the outside protector path order.  The two leaves and path orientation
    are canonicalized by taking the lexicographically smaller text signature.
    """
    row_paths = [tuple(P) for _g, P, _pset in rows]
    if len(row_paths) != 2 or path is None:
        return None
    common = tuple(sorted(set(row_paths[0]) & set(row_paths[1])))
    leaves = tuple(sorted((set(row_paths[0]) | set(row_paths[1])) - set(common)))
    path = tuple(path)

    def build(leaves_order, path_order):
        labels = {}
        for i, v in enumerate(leaves_order):
            labels[v] = f"L{i}"
        for i, v in enumerate(common):
            labels[v] = f"C{i}"
        for i, v in enumerate(path_order):
            labels[v] = f"P{i}"
        cell = set(U) | set(path_order)
        parts = []
        for edge_set, tag in ((B, "B"), (Mset, "M")):
            for u, v in edge_set:
                if u in cell and v in cell:
                    a = labels.get(u, f"X{u}")
                    b = labels.get(v, f"X{v}")
                    if a > b:
                        a, b = b, a
                    parts.append(f"{tag}:{a}-{b}")
        return "|".join(sorted(parts))

    variants = []
    for leaves_order in (leaves, tuple(reversed(leaves))):
        for path_order in (path, tuple(reversed(path))):
            variants.append(build(leaves_order, path_order))
    return min(variants)


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "unit_cases": 0,
        "atoms": 0,
        "missing_path": 0,
        "cell_shape_hist": Counter(),
        "role_sig_hist": Counter(),
        "bad_boundary_hist": Counter(),
        "blue_boundary_hist": Counter(),
        "first_shape": {},
        "first_bad_boundary": None,
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "unit_cases", "atoms", "missing_path"):
        dst[key] += src[key]
    for key in ("cell_shape_hist", "role_sig_hist", "bad_boundary_hist", "blue_boundary_hist"):
        dst[key].update(src[key])
    for key, rec in src["first_shape"].items():
        dst["first_shape"].setdefault(key, rec)
    if dst["first_bad_boundary"] is None and src["first_bad_boundary"] is not None:
        dst["first_bad_boundary"] = src["first_bad_boundary"]


def record_unit(acc, name, n, edges, side, E, B, M, Mset, cyc, Q, U, rows, atoms_seen):
    atom_key = tuple(sorted((g, tuple(P)) for g, P, _pset in rows))
    is_new_atom = atom_key not in atoms_seen
    if is_new_atom:
        atoms_seen.add(atom_key)
        acc["atoms"] += 1

    bdy = sorted(delta(B, U))
    outs = [outside_endpoint(e, U) for e in bdy]
    outs = [x for x in outs if x is not None]
    path = None
    if len(outs) == 2:
        path = shortest_b_path_avoiding(n, B, outs[0], outs[1], set(U))
    if path is None:
        acc["missing_path"] += 1
        return

    cell = set(U) | set(path)
    b_in, b_boundary, _b_out = edge_counts(B, cell)
    m_in, m_boundary, _m_out = edge_counts(Mset, cell)
    u_b_in, u_b_boundary, _ = edge_counts(B, U)
    u_m_in, u_m_boundary, _ = edge_counts(Mset, U)
    shape = (
        len(cell),
        len(path) - 1,
        b_in,
        m_in,
        b_boundary,
        m_boundary,
        u_b_boundary,
        u_m_boundary,
    )
    acc["cell_shape_hist"][shape] += 1
    acc["bad_boundary_hist"][m_boundary] += 1
    acc["blue_boundary_hist"][b_boundary] += 1
    rsig = role_signature(B, Mset, U, rows, path)
    if rsig is not None:
        acc["role_sig_hist"][rsig] += 1
    acc["first_shape"].setdefault(
        shape,
        {
            "name": name,
            "n": n,
            "m": len(M),
            "side": "".join(str(int(c)) for c in side),
            "Q": tuple(Q),
            "U": tuple(sorted(U)),
            "rows": tuple((g, P) for g, P, _pset in rows),
            "doors": tuple(bdy),
            "outside_endpoints": tuple(outs),
            "path": path,
            "cell": tuple(sorted(cell)),
            "u_boundary": (u_b_boundary, u_m_boundary),
            "cell_boundary": (b_boundary, m_boundary),
        },
    )
    if m_boundary and acc["first_bad_boundary"] is None:
        acc["first_bad_boundary"] = acc["first_shape"][shape]


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
                record_unit(acc, name, n, edges, side, E, B, M, Mset, cyc, Q, U, rows, atoms_seen)
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
                f"theta t={t} cuts={len(cuts)} unit={local['unit_cases']} "
                f"atoms={local['atoms']} missing={local['missing_path']} "
                f"shapes={dict(sorted(local['cell_shape_hist'].items()))}",
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
                        f"atoms={total['atoms']} missing={total['missing_path']}",
                        flush=True,
                    )

    print("=== UNIT-FLAT5 protected-cell shape catalog ===")
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("unit_cases:", total["unit_cases"])
    print("atoms:", total["atoms"])
    print("missing_path:", total["missing_path"])
    print("cell_shape_hist:", dict(sorted(total["cell_shape_hist"].items())))
    print("bad_boundary_hist:", dict(sorted(total["bad_boundary_hist"].items())))
    print("blue_boundary_hist:", dict(sorted(total["blue_boundary_hist"].items())))
    print("role_sig_count:", len(total["role_sig_hist"]))
    print("role_sig_hist:", dict(total["role_sig_hist"].most_common(12)))
    print("first_shape:", dict(sorted(total["first_shape"].items(), key=lambda kv: str(kv[0]))))
    print("first_bad_boundary:", total["first_bad_boundary"] or "")
    print(
        "VERDICT:",
        "PASS_NO_BAD_BOUNDARY" if total["missing_path"] == 0 and not total["first_bad_boundary"] else "FAIL_SHAPE_CATALOG",
    )


if __name__ == "__main__":
    main()
