"""Emit exact lane-coarea interval-switch certificates for Bank-L pressure rows.

This is the first machine gate for BANKL_LOW_LENGTH_LANE_COAREA_GPTPRO.md.
For clean hard rows (L in {7,9,11}, p=1, h=0, P_Q>0), it constructs
completed interval switches S_i = Comp([i,i+2]) using the currently available
completion primitives:

  closed_interval from component_info/candidate_switches, then
  terminal_prefix_closure, then
  connected-after and terminal-shadow validity checks.

Strict gate: P_Q must be payable by one positive interval nuK term.  This is
stronger than the archived inequality with an unspecified residual.  Any UNSAT
row is useful feedback for the lane-coarea proof shape.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pq_crosstab as pq


def frac_s(x: F | int | None) -> str | None:
    if x is None:
        return None
    if not isinstance(x, F):
        x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def closed_interval_seed(row: tuple[int, ...], comps, i: int) -> set[int]:
    wanted = ("closed_interval", i, i + 2)
    fallback = set(row[i : i + 3])
    for label, verts in skel.candidate_switches(row, comps):
        if label == wanted:
            return set(verts)
    return fallback


def interval_terms(n: int, edges: list[tuple[int, int]], side: list[int], row: tuple[int, ...], st) -> list[dict]:
    adj = skel.adj_from_edges(n, edges)
    base_cut = skel.cut_size(edges, side)
    base_gamma = skel.gamma_data(n, adj, side)
    if base_gamma is None:
        return []
    blue_edges = {norm_edge((u, v)) for u, v in edges if side[u] != side[v]}
    bad_edges = {norm_edge((u, v)) for u, v in edges if side[u] == side[v]}
    old_bad_len = {norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}
    comps = skel.component_info(n, adj, side, row)
    out = []
    seen = set()
    for i in range(len(row) - 2):
        seed = closed_interval_seed(row, comps, i)
        comp = skel.terminal_prefix_closure(seed, st[4], n)
        if not comp or len(comp) == n:
            out.append({"i": i, "status": "degenerate", "seed": sorted(seed), "verts": sorted(comp)})
            continue
        key = tuple(sorted(comp))
        duplicate = key in seen
        seen.add(key)
        side2 = skel.switched(side, comp)
        rec = skel.switch_record(n, blue_edges, bad_edges, old_bad_len, comp, ("lane_interval", i, i + 2))
        sigma_by_cut = base_cut - skel.cut_size(edges, side2)
        if rec["sigma"] != sigma_by_cut:
            raise AssertionError((i, rec["sigma"], sigma_by_cut, row, comp))
        mask = sum(1 << v for v in comp)
        terminal = skel.terminal_shadow_details(n, adj, side, st, mask)
        connected = skel.Bconn(n, adj, side2)
        out.append({
            "i": i,
            "status": "ok",
            "duplicate": duplicate,
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
        })
    return out


def choose_cert(Pq: F, terms: list[dict]) -> dict:
    candidates = []
    for t in terms:
        if not (t.get("connected_after") and t.get("terminal_shadow_valid")):
            continue
        v = t.get("nuK")
        if v is None or v <= 0:
            continue
        candidates.append(t)
    if not candidates:
        return {"status": "UNSAT", "reason": "no_positive_completed_interval_nuK", "terms": []}
    # Prefer smallest support, then smallest positive nuK, producing a compact exact identity.
    best = sorted(candidates, key=lambda t: (len(t["verts"]), t["nuK"], t["i"]))[0]
    coeff = Pq / F(best["nuK"])
    return {
        "status": "SAT",
        "target": frac_s(Pq),
        "terms": [{
            "kind": "lane_interval_nuK",
            "i": best["i"],
            "value": frac_s(best["nuK"]),
            "coeff": frac_s(coeff),
            "contribution": frac_s(coeff * best["nuK"]),
            "verts": best["verts"],
            "sigma": best["sigma"],
            "nu": frac_s(best["nu"]),
            "K_S": best["K_S"],
            "terminal": True,
        }],
        "verified": coeff * best["nuK"] == Pq,
    }


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], out, acc: Counter, args) -> None:
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    for f in M:
        for row0 in cyc[f]:
            row = tuple(row0)
            L = len(set(row))
            if L <= 5:
                continue
            packet = pq.compute_row_packet(n, edges, side, row)
            Pq = packet["P_Q"]
            if not (Pq > 0 and packet["p"] == 1 and packet["h"] == 0 and L in (7, 9, 11)):
                continue
            terms = interval_terms(n, edges, side, row, st)
            cert = choose_cert(Pq, terms)
            rec = {
                "schema": "bankl_lane_coarea_interval_v1",
                "name": name,
                "n": n,
                "m": len(M),
                "side": "".join(str(x) for x in side),
                "f": list(f),
                "row": list(row),
                "L": L,
                "p": packet["p"],
                "h": packet["h"],
                "d": packet["d"],
                "r": packet["r"],
                "P_Q": frac_s(Pq),
                "rho_Q": frac_s(packet["rho_Q"]),
                "interval_terms": [
                    {k: (frac_s(v) if k in ("nu", "nuK") and v is not None else v) for k, v in t.items()}
                    for t in terms
                ] if args.include_terms else [],
                "certificate": cert,
            }
            out.write(json.dumps(rec, sort_keys=True) + "\n")
            acc["rows"] += 1
            acc[f"L:{L}"] += 1
            acc[f"status:{cert['status']}"] += 1
            if cert["status"] != "SAT":
                acc["unsat"] += 1
                if "first_unsat" not in acc:
                    acc["first_unsat"] = rec
            else:
                acc["sat"] += 1
                term = cert["terms"][0]
                acc[f"term_i:{L}:{term['i']}"] += 1
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                return


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], out, acc: Counter, args) -> None:
    _adj, cuts = skel.gmins(n, edges)
    if args.max_cuts is not None:
        cuts = cuts[: args.max_cuts]
    for side0 in cuts:
        scan_side(name, n, edges, [int(x) for x in side0], out, acc, args)
        if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
            return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="tmp/bankl_lane_coarea_interval_v1.jsonl")
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--limit-rows", type=int, default=None)
    ap.add_argument("--include-terms", action="store_true")
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--census-only", action="store_true")
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    acc: Counter = Counter()
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        if not args.census_only:
            for L in (7, 9, 11, 13, 15, 17, 19):
                n, edges = skel.blowup([1] * L)
                scan_side(f"C{L}[1]", n, edges, skel.cycle_blowup_side([1] * L), out, acc, args)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break
            if args.limit_rows is None or acc["rows"] < args.limit_rows:
                for L in range(8, 31, 2):
                    n, edges, side, _bad = skel.build_two_lane(L)
                    scan_side(f"two-lane-L{L}", n, edges, side, out, acc, args)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
            if args.limit_rows is None or acc["rows"] < args.limit_rows:
                for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
                    bad = skel.greedy_chords(Ll, k, gap)
                    n, edges, side, _ = skel.build_k_lane(Ll, k, bad)
                    scan_side(f"klane-L{Ll}k{k}", n, edges, side, out, acc, args)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
            if not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
                named = [
                    ("Grotzsch", skel.mycielski(5, skel.Cn(5))),
                    ("M(C7)", skel.mycielski(7, skel.Cn(7))),
                    ("C7|Grotzsch", skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)),
                ]
                for name, (n, edges) in named:
                    scan_gmins(name, n, edges, out, acc, args)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
        if not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
            for nn in range(args.min_n, args.max_n + 1):
                before = acc["rows"]
                for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                    n, edges = skel.dec(g6)
                    scan_gmins(f"cen{g6}", n, edges, out, acc, args)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
                print(json.dumps({"N": nn, "rows_added": acc["rows"] - before, "rows_total": acc["rows"], "unsat_total": acc["unsat"]}, sort_keys=True), flush=True)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break
    summary = {
        "output": str(out_path),
        "rows": acc["rows"],
        "sat": acc["sat"],
        "unsat": acc["unsat"],
        "counts": {k: v for k, v in sorted(acc.items()) if isinstance(k, str)},
        "first_unsat": acc.get("first_unsat"),
    }
    print(json.dumps(summary, sort_keys=True))
    print("PASS lane interval strict gate" if acc["unsat"] == 0 else "FAIL lane interval strict gate")


if __name__ == "__main__":
    main()
