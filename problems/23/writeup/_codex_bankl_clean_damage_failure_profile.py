"""Structural diagnostic for clean P_Q>0 rows where naive damage fails.

This replays the exact failure records emitted by
_codex_bankl_clean_damage_gate.py, finds the matching gamma-min connected cut,
and records the off-row graph, row attachment masks, other bad edge, optimal
recolorings, and current Bank-L certificate terms.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import _codex_bankl_clean_damage_gate as dmg
import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pq_crosstab as pq


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def row_key(name: str, n: int, f, row) -> str:
    return json.dumps({"name": name, "n": n, "f": list(f), "row": list(row)}, sort_keys=True)


def load_certs(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rec = json.loads(line)
                out[row_key(rec["name"], rec["n"], rec["f"], rec["row"])].append(rec)
    return out


def blue_bad_sets(edges: list[tuple[int, int]], side: list[int]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    blue = {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}
    bad = {norm_edge(e) for e in edges if side[e[0]] == side[e[1]]}
    return blue, bad


def components_from_edges(vertices: list[int], edges: set[tuple[int, int]]) -> list[list[int]]:
    parent = {v: v for v in vertices}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for u, v in edges:
        if u in parent and v in parent:
            union(u, v)
    comps: dict[int, list[int]] = defaultdict(list)
    for v in vertices:
        comps[find(v)].append(v)
    return [sorted(x) for x in comps.values()]


def opt_colorings(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...]) -> dict:
    W = set(row)
    R = [v for v in range(n) if v not in W]
    idx = {v: i for i, v in enumerate(R)}
    inside = [(u, v) for u, v in edges if u in idx and v in idx]
    boundary_blue = [norm_edge((u, v)) for u, v in edges if side[u] != side[v] and ((u in W) ^ (v in W))]
    best_inside = None
    best_damage = None
    best = []
    for mask in range(1 << len(R)):
        def col(x: int) -> int:
            if x in W:
                return side[x]
            return (mask >> idx[x]) & 1
        mono_inside = sum(1 for u, v in inside if col(u) == col(v))
        if best_inside is not None and mono_inside > best_inside:
            continue
        damaged = [e for e in boundary_blue if col(e[0]) == col(e[1])]
        damage = len(damaged)
        flip_damage = len(boundary_blue) - damage
        if flip_damage < damage:
            damage = flip_damage
            damaged = [e for e in boundary_blue if col(e[0]) != col(e[1])]
        record = {
            "mask": mask,
            "colors": {str(v): col(v) for v in R},
            "damaged_boundary_edges": [list(e) for e in sorted(damaged)],
        }
        if best_inside is None or mono_inside < best_inside:
            best_inside = mono_inside
            best_damage = damage
            best = [record]
        elif mono_inside == best_inside:
            if damage < best_damage:
                best_damage = damage
                best = [record]
            elif damage == best_damage:
                best.append(record)
    return {"beta_R": best_inside, "min_damage": best_damage, "best_colorings": best}


def row_attachments(n: int, blue: set[tuple[int, int]], row: tuple[int, ...]) -> dict:
    W = set(row)
    pos = {v: i for i, v in enumerate(row)}
    outer = []
    row_deg = [0 for _ in row]
    for v in range(n):
        if v in W:
            continue
        hits = []
        for u in row:
            if norm_edge((u, v)) in blue:
                hits.append(pos[u])
                row_deg[pos[u]] += 1
        outer.append({"v": v, "hit_positions": hits, "hit_vertices": [row[i] for i in hits]})
    return {"outer": outer, "row_boundary_degrees": row_deg}


def row_component_data(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...], Ms, cyc) -> list[dict]:
    tw = skel.row_component_tw(n, Ms, cyc)
    out = []
    for comp in skel.components_minus_row(n, edges, side, row):
        tq = sum(tw[v] for v in set(row) & comp)
        out.append({
            "vertices": sorted(comp),
            "size": len(comp),
            "TQ": pq.frac_s(tq),
            "deficit": pq.frac_s(len(comp) - tq),
        })
    return out


def analyze_failure(fail: dict, certs: dict[str, list[dict]]) -> list[dict]:
    name = fail["name"]
    g6 = name[3:] if name.startswith("cen") else name
    n, edges = skel.dec(g6)
    assert n == fail["n"]
    want_f = norm_edge(tuple(fail["f"]))
    want_row = tuple(fail["row"])
    records = []
    _adj, cuts = skel.gmins(n, edges)
    for side0 in cuts:
        side = [int(x) for x in side0]
        adj = skel.adj_from_edges(n, edges)
        if not skel.Bconn(n, adj, side):
            continue
        st = skel.struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        for f in M:
            if norm_edge(f) != want_f:
                continue
            for row0 in cyc[f]:
                row = tuple(row0)
                if row != want_row:
                    continue
                blue, bad = blue_bad_sets(edges, side)
                packet = pq.compute_row_packet(n, edges, side, row)
                cert_bucket = certs.get(row_key(name, n, list(f), row), [])
                cert = cert_bucket[0] if cert_bucket else None
                W = set(row)
                R = [v for v in range(n) if v not in W]
                blue_R = {e for e in blue if e[0] in R and e[1] in R}
                bad_R = {e for e in bad if e[0] in R and e[1] in R}
                other_bad = sorted(e for e in bad if e != want_f)
                comp_map, find = skel.kcomponents(n, cyc)
                Ms = [g for g in M if find(g[0]) == find(f[0])]
                records.append({
                    "name": name,
                    "side": "".join(str(x) for x in side),
                    "n": n,
                    "edges": [list(e) for e in sorted(norm_edge(e) for e in edges)],
                    "f": list(f),
                    "row": list(row),
                    "row_sides": [side[v] for v in row],
                    "bad_edges": [list(e) for e in sorted(bad)],
                    "bad_lengths": {f"{u}-{v}": ell[(u, v)] for (u, v) in sorted(M)},
                    "other_bad_edges": [list(e) for e in other_bad],
                    "offrow_vertices": R,
                    "offrow_blue_edges": [list(e) for e in sorted(blue_R)],
                    "offrow_bad_edges": [list(e) for e in sorted(bad_R)],
                    "offrow_blue_components": components_from_edges(R, blue_R),
                    "packet": {
                        "p": packet["p"], "h": packet["h"], "d": packet["d"], "r": packet["r"],
                        "P_Q": pq.frac_s(packet["P_Q"]), "rho_Q": pq.frac_s(packet["rho_Q"]),
                        "B_packet": pq.frac_s(packet["B_packet"]),
                    },
                    "attachments": row_attachments(n, blue, row),
                    "opt_recoloring": opt_colorings(n, edges, side, row),
                    "components_minus_row": row_component_data(n, edges, side, row, Ms, cyc),
                    "certificate": None if cert is None else {
                        "kind": cert.get("certificate_kind"),
                        "target": cert.get("certificate_target"),
                        "terms": cert.get("certificate_terms"),
                        "detour_terms_count": cert.get("detour_terms_count"),
                        "detour_sum": cert.get("detour_sum"),
                        "completed_positive_lcb_terms": cert.get("completed_positive_lcb_terms"),
                        "connected_positive_lcb_terms": cert.get("connected_positive_lcb_terms"),
                    },
                })
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--failures", default="tmp/bankl_clean_damage_failures.json")
    ap.add_argument("--certs", default="tmp/bankl_lcb_certs_n11_v2.jsonl")
    ap.add_argument("--output", default="tmp/bankl_clean_damage_failure_profile.json")
    args = ap.parse_args()

    failures = json.loads(Path(args.failures).read_text(encoding="utf-8"))
    certs = load_certs(Path(args.certs))
    all_records = []
    for fail in failures:
        recs = analyze_failure(fail, certs)
        if not recs:
            raise SystemExit(f"no match for failure {fail}")
        all_records.extend(recs)
    summary = {
        "failure_inputs": len(failures),
        "matched_records": len(all_records),
        "certificate_kinds": {},
        "other_bad_edges": {},
        "row_boundary_degree_patterns": {},
        "offrow_blue_component_patterns": {},
    }
    from collections import Counter
    cert_k = Counter()
    other = Counter()
    rowdeg = Counter()
    comps = Counter()
    for rec in all_records:
        cert_k[rec["certificate"]["kind"] if rec["certificate"] else "missing"] += 1
        other[tuple(tuple(e) for e in rec["other_bad_edges"])] += 1
        rowdeg[tuple(rec["attachments"]["row_boundary_degrees"])] += 1
        comps[tuple(tuple(c) for c in rec["offrow_blue_components"])] += 1
    summary["certificate_kinds"] = dict(cert_k)
    summary["other_bad_edges"] = {str(k): v for k, v in other.items()}
    summary["row_boundary_degree_patterns"] = {str(k): v for k, v in rowdeg.items()}
    summary["offrow_blue_component_patterns"] = {str(k): v for k, v in comps.items()}
    payload = {"summary": summary, "records": all_records}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
