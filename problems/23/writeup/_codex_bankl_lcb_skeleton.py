
"""Emit exact per-row data for the proposed Bank-L/LCB certificate.

This is a certificate-search scaffold, not a closure theorem. For each
L>5 row Q it records the Bank-L deficit

    Delta_Q = 25|M| + L^2 - 25 - N^2 <= 0

and the canonical switch slacks requested by the LCB cone gate:

    sigma(S) = |delta_B(S)| - |delta_M(S)|,

    nu(S) = sum_{e in delta_B(S)} ell_S(e)^2
            - sum_{g in delta_M(S)} ell(g)^2,

    K_S = sum_{g in delta_M(S)} ell(g)^2,
    nu_K(S) = nu(S) + K_S * sigma(S).

Here ell_S(e) is one plus the shortest B^S-distance between the endpoints
of an old blue crossing edge e after flipping S. The intended next layer is
a nonnegative reweighting/LP search over these exact slacks.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from collections import deque
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski
    from _codex_banked_upo_gate import greedy_chords
    from _codex_interval_failure_switch_lab import (
        adj_from_edges,
        candidate_switches,
        cut_size,
        gamma_data,
        switched,
    )
    from _codex_k2t_switch_signature_gate import terminal_shadow_details
    from _codex_rowcap_non5_half_gate import blowup
    from _codex_upo_conditional_interval_uncross_scan import component_info
    from _h import Bconn, GENG, dec
    from _satzmu_conn import kcomponents, struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def as_frac(x) -> F:
    if isinstance(x, F):
        return x
    return F(x)


def lcb_identity_certificate(target: int, terms: list[dict]) -> dict:
    """Return a one-row exact cone identity when the current terms generate it.

    The row cone is one-dimensional after the nonnegative residual facts have
    already been selected. This routine still emits a proper rational identity:

        target = sum_i coeff_i * value_i

    with every coeff_i >= 0 and every value_i visibly nonnegative. It is a
    certificate format, not a proof that the selected residual facts are the
    right universal family.
    """
    if target < 0:
        return {"status": "BANK_FAIL", "target": str(target), "terms": [], "verified": False}
    if target == 0:
        return {"status": "SAT", "target": "0", "terms": [], "verified": True}

    for preferred in ("nuK", "sigma", "detour"):
        for term in terms:
            if term["kind"] != preferred:
                continue
            value = as_frac(term["value"])
            if value <= 0:
                continue
            coeff = F(target, 1) / value
            contribution = coeff * value
            cert_term = {
                "kind": preferred,
                "value": frac_s(value),
                "coeff": frac_s(coeff),
                "contribution": frac_s(contribution),
            }
            for key in ("label", "verts", "vertices", "TQ", "terminal", "size"):
                if key in term:
                    cert_term[key] = term[key]
            return {
                "status": "SAT",
                "kind": preferred,
                "target": str(target),
                "terms": [cert_term],
                "verified": contribution == target,
            }

    sparse_gap = None
    length_gap = None
    for term in terms:
        if term["kind"] == "sparse_gap":
            sparse_gap = as_frac(term["value"])
        elif term["kind"] == "length_gap":
            length_gap = as_frac(term["value"])
    if sparse_gap is not None and length_gap is not None and sparse_gap >= 0 and length_gap >= 0:
        contribution = sparse_gap + length_gap
        if contribution == target:
            return {
                "status": "SAT",
                "kind": "sparse",
                "target": str(target),
                "terms": [
                    {"kind": "sparse_gap", "value": frac_s(sparse_gap), "coeff": "1", "contribution": frac_s(sparse_gap)},
                    {"kind": "length_gap", "value": frac_s(length_gap), "coeff": "1", "contribution": frac_s(length_gap)},
                ],
                "verified": True,
            }

    return {"status": "UNSAT", "target": str(target), "terms": [], "verified": False}


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def delta(edge_set: set[tuple[int, int]], verts: set[int]) -> set[tuple[int, int]]:
    return {e for e in edge_set if ((e[0] in verts) ^ (e[1] in verts))}


def flip_blue_edges(
    blue_edges: set[tuple[int, int]],
    bad_edges: set[tuple[int, int]],
    verts: set[int],
) -> set[tuple[int, int]]:
    dB = delta(blue_edges, verts)
    dM = delta(bad_edges, verts)
    return (blue_edges - dB) | dM


def shortest_distance(n: int, edge_set: set[tuple[int, int]], s: int, t: int) -> int | None:
    adj = [set() for _ in range(n)]
    for u, v in edge_set:
        adj[u].add(v)
        adj[v].add(u)
    seen = {s}
    q = deque([(s, 0)])
    while q:
        u, d = q.popleft()
        if u == t:
            return d
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))
    return None






def terminal_prefix_closure(seed: set[int], cyc: dict, n: int) -> set[int]:
    """Monotone repair for terminal-prefix re-entry along crossing bad rows.

    For every crossing bad edge f with inside endpoint tau, every shortest row
    is oriented from tau.  If the current set appears again after a gap on that
    row, add the whole prefix up to the last current in-set vertex.  Iterate to
    a fixed point.  This is only the terminal-prefix part of the intended
    completed-switch closure; coverage/safety/twin/FLAT5 are still checked
    separately by terminal_shadow_details.
    """
    S = set(seed)
    changed = True
    while changed and S and len(S) < n:
        changed = False
        for f, paths in cyc.items():
            u, v = f
            inu, inv = u in S, v in S
            if inu == inv:
                continue
            tau = u if inu else v
            for path0 in paths:
                path = list(path0)
                if path[0] != tau:
                    path = list(reversed(path))
                if not path or path[0] != tau:
                    continue
                last = -1
                for i, x in enumerate(path):
                    if x in S:
                        last = i
                if last > 0:
                    before = len(S)
                    S.update(path[: last + 1])
                    changed = changed or len(S) != before
    return S

def components_minus_row(n: int, edges: list[tuple[int, int]], side: list[int], rowQ: tuple[int, ...]) -> list[set[int]]:
    row_blue = {norm_edge((a, b)) for a, b in zip(rowQ, rowQ[1:]) if side[a] != side[b]}
    parent = list(range(n))

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
        if side[u] != side[v] and norm_edge((u, v)) not in row_blue:
            union(u, v)
    comps: dict[int, set[int]] = {}
    for v in range(n):
        comps.setdefault(find(v), set()).add(v)
    return list(comps.values())


def row_component_tw(n: int, Ms: list[tuple[int, int]], cyc: dict) -> list[F]:
    tw = [F(0)] * n
    for g in Ms:
        den = F(len(cyc[g]))
        cnt: dict[int, int] = {}
        for P in cyc[g]:
            for v in set(P):
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            tw[v] += F(c, den)
    return tw

def cycle_blowup_side(parts: list[int]) -> list[int]:
    side: list[int] = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1: tuple[int, list[tuple[int, int]]], block2: tuple[int, list[tuple[int, int]]], u: int, v: int):
    n1, e1 = block1
    n2, e2 = block2
    return n1 + n2, e1 + [(a + n1, b + n1) for a, b in e2] + [(u, n1 + v)]


def compact_row(rec: dict | None) -> dict | str:
    if rec is None:
        return ""
    keys = ("name", "n", "m", "L", "f", "row", "best_nuK")
    return {k: rec[k] for k in keys if k in rec}


def switch_record(
    n: int,
    blue_edges: set[tuple[int, int]],
    bad_edges: set[tuple[int, int]],
    old_bad_len: dict[tuple[int, int], int],
    verts: set[int],
    label,
) -> dict:
    dB = delta(blue_edges, verts)
    dM = delta(bad_edges, verts)
    sigma = len(dB) - len(dM)
    flipped_blue = flip_blue_edges(blue_edges, bad_edges, verts)
    K_S = sum(old_bad_len[e] * old_bad_len[e] for e in dM)
    new_sum = 0
    new_lengths: dict[tuple[int, int], int] = {}
    valid = True
    for e in dB:
        d = shortest_distance(n, flipped_blue, e[0], e[1])
        if d is None:
            valid = False
            break
        ell_s = d + 1
        new_lengths[e] = ell_s
        new_sum += ell_s * ell_s
    nu = new_sum - K_S if valid else None
    nuK = nu + K_S * sigma if valid else None
    return {
        "label": repr(label),
        "verts": list(sorted(verts)),
        "sigma": sigma,
        "dB": len(dB),
        "dM": len(dM),
        "K_S": K_S,
        "nu": nu,
        "nuK": nuK,
        "new_lengths": {f"{u}-{v}": L for (u, v), L in sorted(new_lengths.items())},
    }


def summarize_row(
    name: str,
    n: int,
    edges: list[tuple[int, int]],
    side: list[int],
    f,
    row,
    include_switches: bool,
    completed_only: bool,
    prefix_close: bool,
    all_masks: bool,
    all_masks_max_n: int,
    st: tuple | None = None,
    Ms: list[tuple[int, int]] | None = None,
    cyc: dict | None = None,
):
    adj = adj_from_edges(n, edges)
    base_cut = cut_size(edges, side)
    base_gamma = gamma_data(n, adj, side)
    if base_gamma is None:
        return None

    m_bad = sum(1 for u, v in edges if side[u] == side[v])
    L = len(set(row))
    delta_q = 25 * m_bad + L * L - 25 - n * n
    eta = F(n * n, 25) - m_bad
    sigma_l = F(L * L - 25, 50)
    bank_margin = eta - 2 * sigma_l

    comps = component_info(n, adj, side, row)
    detour_terms: list[dict] = []
    detour_sum = F(0)
    row_overlap = None
    row_overlap_minus_n = None
    row_scope = "unknown"
    if Ms is not None and cyc is not None:
        tw = row_component_tw(n, Ms, cyc)
        row_overlap = sum(tw[v] for v in set(row))
        row_overlap_minus_n = row_overlap - n
        if row_overlap_minus_n > 0:
            row_scope = "overfull"
        elif row_overlap_minus_n < 0:
            row_scope = "underfull"
        else:
            row_scope = "equal"
        for K in components_minus_row(n, edges, side, tuple(row)):
            tq = sum(tw[v] for v in set(row) & K)
            deficit = F(len(K)) - tq
            if deficit > 0:
                detour_sum += deficit
                detour_terms.append({
                    "kind": "detour",
                    "value": deficit,
                    "size": len(K),
                    "TQ": tq,
                    "vertices": sorted(K),
                })
    summary = {
        "name": name,
        "n": n,
        "m": m_bad,
        "f": list(f),
        "row": list(row),
        "L": L,
        "Delta_Q": delta_q,
        "minus_Delta_Q": -delta_q,
        "eta": frac_s(eta),
        "Sigma_L": frac_s(sigma_l),
        "bank_margin": frac_s(bank_margin),
        "R_Q": frac_s(row_overlap) if row_overlap is not None else "",
        "R_Q_minus_N": frac_s(row_overlap_minus_n) if row_overlap_minus_n is not None else "",
        "row_scope": row_scope,
        "candidate_switches": 0,
        "sigma_zero": 0,
        "sigma_positive": 0,
        "sigma_negative": 0,
        "connected_after": 0,
        "terminal_shadow_valid": 0,
        "completed_positive_lcb_terms": 0,
        "connected_positive_lcb_terms": 0,
        "neutral_connected": 0,
        "neutral_gamma_descents": 0,
        "max_sigma": 0,
        "has_positive_connected_lcb_term": False,
        "nuK_negative": 0,
        "nuK_invalid": 0,
        "min_nuK": None,
        "max_nuK": 0,
        "best_nuK": None,
        "detour_terms_count": len(detour_terms),
        "detour_sum": frac_s(detour_sum),
    }
    records: list[dict] = []
    scalar_terms: list[dict] = []

    blue_edges = {norm_edge((u, v)) for u, v in edges if side[u] != side[v]}
    bad_edges = {norm_edge((u, v)) for u, v in edges if side[u] == side[v]}
    old_bad_len = {norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}

    seen = set()
    raw_candidates = list(candidate_switches(tuple(row), comps))
    if all_masks and st is not None and n <= all_masks_max_n:
        for mask0 in range(1, (1 << n) - 1):
            raw_candidates.append((("all_mask", mask0), {v for v in range(n) if (mask0 >> v) & 1}))

    for label, verts in raw_candidates:
        seed_verts = set(verts)
        if prefix_close and st is not None:
            seed_verts = terminal_prefix_closure(seed_verts, st[4], n)
        if not seed_verts or len(seed_verts) == n:
            continue
        key = tuple(sorted(seed_verts))
        if key in seen:
            continue
        seen.add(key)
        summary["candidate_switches"] += 1

        verts = seed_verts
        side2 = switched(side, verts)
        sigma_by_cut = base_cut - cut_size(edges, side2)
        rec = switch_record(n, blue_edges, bad_edges, old_bad_len, set(verts), label)
        sigma = rec["sigma"]
        if sigma != sigma_by_cut:
            raise AssertionError((name, f, row, label, key, sigma, sigma_by_cut))

        connected_after = Bconn(n, adj, side2)
        mask = sum(1 << v for v in key)
        term_det = terminal_shadow_details(n, adj, side, st, mask) if st is not None else None
        terminal_valid = term_det is not None
        rec["connected_after"] = connected_after
        rec["terminal_shadow_valid"] = terminal_valid
        if terminal_valid:
            rec["terminal_psi"] = term_det["psi"]
            rec["terminal_cross_count"] = len(term_det["cross_m"])
            rec["terminal_bdy_count"] = len(term_det["bdy_b"])
        records.append(rec)
        if connected_after:
            summary["connected_after"] += 1
        if terminal_valid:
            summary["terminal_shadow_valid"] += 1
        summary["max_sigma"] = max(summary["max_sigma"], sigma)
        nuK = rec["nuK"]
        usable_for_cone = connected_after and (terminal_valid or not completed_only)
        if usable_for_cone and sigma > 0:
            scalar_terms.append({"kind": "sigma", "value": sigma, "label": rec["label"], "verts": rec["verts"], "terminal": terminal_valid})
        if usable_for_cone and nuK is not None and nuK > 0:
            scalar_terms.append({"kind": "nuK", "value": nuK, "label": rec["label"], "verts": rec["verts"], "terminal": terminal_valid})
        if connected_after and terminal_valid and (sigma > 0 or (nuK is not None and nuK > 0)):
            summary["completed_positive_lcb_terms"] += 1
        if connected_after and (sigma > 0 or (nuK is not None and nuK > 0)):
            summary["connected_positive_lcb_terms"] += 1
            summary["has_positive_connected_lcb_term"] = True
        if nuK is None:
            summary["nuK_invalid"] += 1
        else:
            if summary["min_nuK"] is None or nuK < summary["min_nuK"]:
                summary["min_nuK"] = nuK
                summary["best_nuK"] = rec
            summary["max_nuK"] = max(summary["max_nuK"], nuK)
            if nuK < 0:
                summary["nuK_negative"] += 1

        if sigma < 0:
            summary["sigma_negative"] += 1
        elif sigma == 0:
            summary["sigma_zero"] += 1
            if connected_after:
                summary["neutral_connected"] += 1
                gd = gamma_data(n, adj, side2)
                if gd is not None:
                    gamma_drop = base_gamma[0] - gd[0]
                    if gamma_drop > 0:
                        summary["neutral_gamma_descents"] += 1
        else:
            summary["sigma_positive"] += 1

    gap = n - L
    for term in detour_terms:
        scalar_terms.append({
            "kind": "detour",
            "value": term["value"],
            "size": term["size"],
            "TQ": frac_s(term["TQ"]),
            "vertices": term["vertices"],
        })
    if gap > 0 and row_scope == "overfull":
        sparse_gap = gap * gap - 25 * (m_bad - 1)
        scalar_terms.append({"kind": "sparse_gap", "value": F(sparse_gap)})
        scalar_terms.append({"kind": "length_gap", "value": F(2 * L * gap)})

    target = -delta_q
    cert = lcb_identity_certificate(target, scalar_terms)
    if cert.get("status") == "SAT" and not cert.get("terms"):
        cert_kind = "tight"
    elif cert.get("status") == "SAT":
        cert_kind = cert.get("kind", cert["terms"][0]["kind"])
    else:
        cert_kind = cert["status"]

    summary["scalar_cert"] = cert
    summary["scalar_cert_kind"] = cert_kind
    if include_switches:
        summary["switch_records"] = records
    summary["switch_records_count"] = len(records)
    return summary


def scan_side(
    name: str,
    n: int,
    edges: list[tuple[int, int]],
    side: list[int],
    acc: dict,
    emit: bool,
    include_switches: bool,
    completed_only: bool,
    prefix_close: bool,
    all_masks: bool,
    all_masks_max_n: int,
    limit_rows: int | None,
):
    adj = adj_from_edges(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    _comp_map, find = kcomponents(n, cyc)
    by_comp: dict[int, list[tuple[int, int]]] = {}
    for g in M:
        by_comp.setdefault(find(g[0]), []).append(g)
    for f in M:
        Ms = by_comp[find(f[0])]
        for row in cyc[f]:
            L = len(set(row))
            if L <= 5:
                continue
            rec = summarize_row(name, n, edges, [int(x) for x in side], f, tuple(row), include_switches, completed_only, prefix_close, all_masks, all_masks_max_n, st, Ms, cyc)
            if rec is None:
                continue
            acc["rows"] += 1
            acc["switches"] += rec["candidate_switches"]
            acc["neutral_descents"] += rec["neutral_gamma_descents"]
            acc["connected_after"] += rec["connected_after"]
            acc["terminal_shadow_valid"] += rec["terminal_shadow_valid"]
            if rec["minus_Delta_Q"] > 0 and not rec["has_positive_connected_lcb_term"]:
                acc["scalar_uncovered_rows"] += 1
                if acc["first_scalar_uncovered"] is None:
                    acc["first_scalar_uncovered"] = rec
            scope = rec.get("row_scope", "unknown")
            acc["row_scope_counts"][scope] = acc["row_scope_counts"].get(scope, 0) + 1
            kind = rec["scalar_cert_kind"]
            acc["scalar_cert_kinds"][kind] = acc["scalar_cert_kinds"].get(kind, 0) + 1
            scope_kind = f"{scope}:{kind}"
            acc["scope_cert_kinds"][scope_kind] = acc["scope_cert_kinds"].get(scope_kind, 0) + 1
            if scope in ("underfull", "equal") and kind in ("sparse", "size", "size2"):
                acc["bad_lcb_scope_fallback_rows"] += 1
                if acc["first_bad_lcb_scope_fallback"] is None:
                    acc["first_bad_lcb_scope_fallback"] = rec
            if rec["scalar_cert"].get("status") != "SAT":
                acc["scalar_cert_fail"] += 1
                if acc["first_scalar_cert_fail"] is None:
                    acc["first_scalar_cert_fail"] = rec
            acc["nuK_negative"] += rec["nuK_negative"]
            acc["nuK_invalid"] += rec["nuK_invalid"]
            if rec["min_nuK"] is not None and (acc["min_nuK"][1] is None or rec["min_nuK"] < acc["min_nuK"][0]):
                acc["min_nuK"] = (rec["min_nuK"], rec)
            if F(rec["bank_margin"]) < acc["min_bank_margin"][0]:
                acc["min_bank_margin"] = (F(rec["bank_margin"]), rec)
            if rec["neutral_gamma_descents"]:
                acc["rows_with_neutral_descent"] += 1
            else:
                acc["rows_without_neutral_descent"] += 1
                if acc["first_without_neutral_descent"] is None:
                    acc["first_without_neutral_descent"] = rec
            if emit:
                print(json.dumps(rec, sort_keys=True), flush=True)
            if limit_rows is not None and acc["rows"] >= limit_rows:
                return


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], acc: dict, max_cuts: int | None, emit: bool, include_switches: bool, completed_only: bool, prefix_close: bool, all_masks: bool, all_masks_max_n: int, limit_rows: int | None):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        scan_side(name, n, edges, [int(x) for x in side], acc, emit, include_switches, completed_only, prefix_close, all_masks, all_masks_max_n, limit_rows)
        if limit_rows is not None and acc["rows"] >= limit_rows:
            return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--emit-jsonl", action="store_true")
    ap.add_argument("--include-switches", action="store_true")
    ap.add_argument("--completed-only", action="store_true")
    ap.add_argument("--prefix-close", action="store_true")
    ap.add_argument("--all-masks", action="store_true")
    ap.add_argument("--all-masks-max-n", type=int, default=11)
    ap.add_argument("--limit-rows", type=int, default=None)
    args = ap.parse_args()

    acc = {
        "rows": 0,
        "switches": 0,
        "neutral_descents": 0,
        "connected_after": 0,
        "terminal_shadow_valid": 0,
        "scalar_uncovered_rows": 0,
        "first_scalar_uncovered": None,
        "scalar_cert_fail": 0,
        "first_scalar_cert_fail": None,
        "scalar_cert_kinds": {},
        "nuK_negative": 0,
        "nuK_invalid": 0,
        "min_nuK": (0, None),
        "rows_with_neutral_descent": 0,
        "rows_without_neutral_descent": 0,
        "first_without_neutral_descent": None,
        "min_bank_margin": (F(10**9), None),
        "row_scope_counts": {},
        "scope_cert_kinds": {},
        "bad_lcb_scope_fallback_rows": 0,
        "first_bad_lcb_scope_fallback": None,
    }

    if not args.census_only:
        for L in (7, 9, 11, 13, 15, 17, 19):
            n, edges = blowup([1] * L)
            scan_side(f"C{L}[1]", n, edges, cycle_blowup_side([1] * L), acc, args.emit_jsonl, args.include_switches, args.completed_only, args.prefix_close, args.all_masks, args.all_masks_max_n, args.limit_rows)
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                break

    if not args.census_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
        for L in range(8, 31, 2):
            n, edges, side, _bad = build_two_lane(L)
            scan_side(f"two-lane-L{L}", n, edges, side, acc, args.emit_jsonl, args.include_switches, args.completed_only, args.prefix_close, args.all_masks, args.all_masks_max_n, args.limit_rows)
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                break

    if not args.census_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
        for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
            bad = greedy_chords(Ll, k, gap)
            n, edges, side, _ = build_k_lane(Ll, k, bad)
            scan_side(f"klane-L{Ll}k{k}", n, edges, side, acc, args.emit_jsonl, args.include_switches, args.completed_only, args.prefix_close, args.all_masks, args.all_masks_max_n, args.limit_rows)
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                break

    if not args.census_only and not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            scan_gmins(name, n, edges, acc, args.max_cuts, args.emit_jsonl, args.include_switches, args.completed_only, args.prefix_close, args.all_masks, args.all_masks_max_n, args.limit_rows)
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                break

    if not args.skip_census and not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
        for nn in range(args.min_n, args.max_n + 1):
            before_rows = acc["rows"]
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                scan_gmins(f"cen{g6}", n, edges, acc, args.max_cuts, args.emit_jsonl, args.include_switches, args.completed_only, args.prefix_close, args.all_masks, args.all_masks_max_n, args.limit_rows)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break
            print(f"LCB-SKEL census N={nn}: rows+={acc['rows'] - before_rows}", flush=True)
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                break

    min_margin, min_rec = acc["min_bank_margin"]
    min_nuK, min_nuK_rec = acc["min_nuK"]
    print("=== Bank-L LCB skeleton ===")
    print("rows:", acc["rows"])
    print("candidate_switches:", acc["switches"])
    print("connected_after:", acc["connected_after"])
    print("terminal_shadow_valid:", acc["terminal_shadow_valid"])
    print("completed_only:", args.completed_only)
    print("prefix_close:", args.prefix_close)
    print("all_masks:", args.all_masks)
    print("all_masks_max_n:", args.all_masks_max_n)
    print("scalar_uncovered_rows:", acc["scalar_uncovered_rows"])
    print("scalar_cert_fail:", acc["scalar_cert_fail"])
    print("scalar_cert_kinds:", dict(sorted(acc["scalar_cert_kinds"].items())))
    print("row_scope_counts:", dict(sorted(acc["row_scope_counts"].items())))
    print("scope_cert_kinds:", dict(sorted(acc["scope_cert_kinds"].items())))
    print("bad_lcb_scope_fallback_rows:", acc["bad_lcb_scope_fallback_rows"])
    print("nuK_negative:", acc["nuK_negative"])
    print("nuK_invalid:", acc["nuK_invalid"])
    print("neutral_gamma_descents:", acc["neutral_descents"])
    print("rows_with_neutral_descent:", acc["rows_with_neutral_descent"])
    print("rows_without_neutral_descent:", acc["rows_without_neutral_descent"])
    print("min_bank_margin:", frac_s(min_margin), compact_row(min_rec))
    print("min_nuK:", min_nuK, compact_row(min_nuK_rec))
    print("first_scalar_uncovered:", compact_row(acc["first_scalar_uncovered"]))
    print("first_scalar_cert_fail:", compact_row(acc["first_scalar_cert_fail"]))
    print("first_bad_lcb_scope_fallback:", compact_row(acc["first_bad_lcb_scope_fallback"]))
    print("first_without_neutral_descent:", compact_row(acc["first_without_neutral_descent"]))


if __name__ == "__main__":
    main()
