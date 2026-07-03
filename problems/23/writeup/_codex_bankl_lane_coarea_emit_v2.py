"""Lane-coarea emitter v2: approximate Comp([i,i+2]) by extraction variants.

The first emitter used only closed_interval+terminal_prefix closure and missed rows
whose current v2 certificate is a path_interval or singleton produced by the
informal FLAT5/twin extraction.  This wrapper replaces interval_terms so each
lane index i selects the best completed positive nuK among:

  - path interval {q_i,q_{i+1},q_{i+2}}
  - closed interval from component_info/candidate_switches
  - singleton q_i, q_{i+1}, q_{i+2}

The selected variant is recorded as the current machine approximation to
S_i = Comp([i,i+2]).
"""

from __future__ import annotations

import json
from typing import Any

import _codex_bankl_lane_coarea_emit as base

skel = base.skel


def _complete_and_record(n: int, edges, side, row, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, i: int, variant: str, seed: set[int]) -> dict[str, Any]:
    comp = skel.terminal_prefix_closure(seed, st[4], n)
    if not comp or len(comp) == n:
        return {"i": i, "variant": variant, "status": "degenerate", "seed": sorted(seed), "verts": sorted(comp)}
    side2 = skel.switched(side, comp)
    rec = skel.switch_record(n, blue_edges, bad_edges, old_bad_len, comp, ("lane_interval", i, i + 2, variant))
    sigma_by_cut = base_cut - skel.cut_size(edges, side2)
    if rec["sigma"] != sigma_by_cut:
        raise AssertionError((i, variant, rec["sigma"], sigma_by_cut, row, comp))
    mask = sum(1 << v for v in comp)
    terminal = skel.terminal_shadow_details(n, adj, side, st, mask)
    connected = skel.Bconn(n, adj, side2)
    return {
        "i": i,
        "variant": variant,
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
    selected = []
    for i in range(len(row) - 2):
        seeds: list[tuple[str, set[int]]] = []
        path_seed = set(row[i : i + 3])
        closed_seed = base.closed_interval_seed(row, comps, i)
        seeds.append(("path_interval", path_seed))
        seeds.append(("closed_interval", closed_seed))
        for j in (i, i + 1, i + 2):
            seeds.append((f"singleton_{j}", {row[j]}))
        variants = []
        seen = set()
        for variant, seed in seeds:
            rec = _complete_and_record(n, edges, side, row, st, blue_edges, bad_edges, old_bad_len, base_cut, adj, i, variant, seed)
            key = tuple(rec.get("verts", []))
            if key in seen:
                continue
            seen.add(key)
            variants.append(rec)
        positives = [v for v in variants if v.get("connected_after") and v.get("terminal_shadow_valid") and v.get("nuK") is not None and v.get("nuK") > 0]
        if positives:
            best = sorted(positives, key=lambda t: (len(t["verts"]), t["nuK"], t["variant"]))[0]
        else:
            oks = [v for v in variants if v.get("status") == "ok"]
            best = sorted(oks or variants, key=lambda t: (len(t.get("verts", [])), t.get("variant", "")))[0]
        best = dict(best)
        best["variants"] = [
            {k: (base.frac_s(val) if k in ("nu", "nuK") and val is not None else val) for k, val in v.items() if k != "variants"}
            for v in variants
        ]
        selected.append(best)
    return selected


base.interval_terms = interval_terms

if __name__ == "__main__":
    base.main()
