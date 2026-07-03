"""Bank-L prefix-coarea emitter using current completed-switch normal forms.

Empirically, all current v2 clean positive-pressure interval certificates are
prefixes 0..k (path or closed) plus terminal endpoint singletons.  This script
uses those cumulative atoms as the machine-facing approximation to the low
length lane-coarea certificate.
"""

from __future__ import annotations

from typing import Any

import _codex_bankl_lane_coarea_emit as base

skel = base.skel


def _record(n: int, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, label: tuple, seed: set[int]) -> dict[str, Any]:
    comp = skel.terminal_prefix_closure(seed, st[4], n)
    if not comp or len(comp) == n:
        return {"label": repr(label), "status": "degenerate", "seed": sorted(seed), "verts": sorted(comp)}
    side2 = skel.switched(side, comp)
    rec = skel.switch_record(n, blue_edges, bad_edges, old_bad_len, comp, label)
    sigma_by_cut = base_cut - skel.cut_size(edges, side2)
    if rec["sigma"] != sigma_by_cut:
        raise AssertionError((label, rec["sigma"], sigma_by_cut, comp))
    mask = sum(1 << v for v in comp)
    terminal = skel.terminal_shadow_details(n, adj, side, st, mask)
    connected = skel.Bconn(n, adj, side2)
    return {
        "i": label[-1] if label[0] != "endpoint_singleton" else label[2],
        "label": repr(label),
        "status": "ok",
        "seed": sorted(seed),
        "verts": sorted(comp),
        "connected_after": bool(connected),
        "terminal_shadow_valid": terminal is not None,
        "sigma": rec["sigma"],
        "nu": rec["nu"],
        "K_S": rec["K_S"],
        "nuK": rec["nuK"],
        "dB": rec["dB"],
        "dM": rec["dM"],
        "new_lengths": rec["new_lengths"],
        "terminal_psi": None if terminal is None else terminal["psi"],
        "terminal_cross_count": None if terminal is None else len(terminal["cross_m"]),
        "terminal_bdy_count": None if terminal is None else len(terminal["bdy_b"]),
    }


def _closed_seed(row: tuple[int, ...], comps, a: int, b: int) -> set[int]:
    wanted = ("closed_interval", a, b)
    fallback = set(row[a : b + 1])
    for label, verts in skel.candidate_switches(row, comps):
        if label == wanted:
            return set(verts)
    return fallback


def interval_terms(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...], st):
    adj = skel.adj_from_edges(n, edges)
    base_cut = skel.cut_size(edges, side)
    base_gamma = skel.gamma_data(n, adj, side)
    if base_gamma is None:
        return []
    blue_edges = {base.norm_edge((u, v)) for u, v in edges if side[u] != side[v]}
    bad_edges = {base.norm_edge((u, v)) for u, v in edges if side[u] == side[v]}
    old_bad_len = {base.norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}
    comps = skel.component_info(n, adj, side, row)
    raw = []
    L = len(row)
    # Endpoint singletons are the FLAT5/twin extraction normal forms present in v2.
    raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("endpoint_singleton", "left", 0), {row[0]}))
    raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("endpoint_singleton", "right", L - 1), {row[-1]}))
    # Cumulative prefixes and suffixes.  Existing v2 uses prefixes only, but suffixes are the oriented mirror.
    for b in range(L):
        raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("prefix_path", 0, b), set(row[: b + 1])))
        raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("prefix_closed", 0, b), _closed_seed(row, comps, 0, b)))
    for a in range(L):
        raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("suffix_path", a, L - 1), set(row[a:])))
        raw.append(_record(n, edges, side, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, ("suffix_closed", a, L - 1), _closed_seed(row, comps, a, L - 1)))
    # Deduplicate by vertex set; keep the best positive representative per set, otherwise shortest record.
    by_verts: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for rec in raw:
        by_verts.setdefault(tuple(rec.get("verts", [])), []).append(rec)
    out = []
    for _verts, bucket in by_verts.items():
        positives = [v for v in bucket if v.get("connected_after") and v.get("terminal_shadow_valid") and v.get("nuK") is not None and v.get("nuK") > 0]
        if positives:
            best = sorted(positives, key=lambda t: (len(t["verts"]), t["nuK"], t["label"]))[0]
        else:
            best = sorted(bucket, key=lambda t: (len(t.get("verts", [])), t.get("label", "")))[0]
        out.append(best)
    return out


base.interval_terms = interval_terms

if __name__ == "__main__":
    base.main()
