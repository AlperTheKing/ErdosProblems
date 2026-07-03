"""Gate the completion-dominance (CD) bridge for Bank-L lane coarea.

For each positive-pressure L>5 row, compute raw 3-vertex interval cut slack

    sigma_i^0 = |delta_B({q_i,q_{i+1},q_{i+2})| - |delta_M(...)|

and compare it with the current completed interval switch nu_K(S_i) selected by
_codex_bankl_lane_coarea_emit_v2.  This is a machine gate for Claude's
2026-07-03T18:31Z directive, not a proof.
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
import _codex_bankl_lane_coarea_emit_v2 as lane_v2


def frac_s(x: F | int | None) -> str | None:
    if x is None:
        return None
    if not isinstance(x, F):
        x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def delta(edge_set: set[tuple[int, int]], verts: set[int]) -> set[tuple[int, int]]:
    return {e for e in edge_set if (e[0] in verts) ^ (e[1] in verts)}


def raw_sigma(blue: set[tuple[int, int]], bad: set[tuple[int, int]], verts: set[int]) -> int:
    return len(delta(blue, verts)) - len(delta(bad, verts))


def kappa_for(L: int) -> F | None:
    if L == 7:
        return F(11, 4)
    if L == 9:
        return F(7, 4)
    if L == 11:
        return F(3, 4)
    return None


def compact_term(t: dict) -> dict:
    return {
        "i": t.get("i"),
        "variant": t.get("variant"),
        "status": t.get("status"),
        "verts": t.get("verts"),
        "connected_after": t.get("connected_after"),
        "terminal_shadow_valid": t.get("terminal_shadow_valid"),
        "sigma": t.get("sigma"),
        "nu": frac_s(t.get("nu")),
        "K_S": t.get("K_S"),
        "nuK": frac_s(t.get("nuK")),
        "dB": t.get("dB"),
        "dM": t.get("dM"),
    }


def cd_record(name: str, n: int, edges: list[tuple[int, int]], side: list[int], f, row: tuple[int, ...], st) -> dict | None:
    packet = pq.compute_row_packet(n, edges, side, row)
    Pq = packet["P_Q"]
    L = len(row)
    if not (L > 5 and Pq > 0):
        return None
    if L not in (7, 9, 11):
        # If this happens it is itself important, but not part of the low-length CD gate.
        return {
            "schema": "bankl_cd_gate_v1",
            "name": name,
            "n": n,
            "m": len(st[0]),
            "f": list(f),
            "row": list(row),
            "L": L,
            "p": packet["p"],
            "h": packet["h"],
            "d": packet["d"],
            "r": packet["r"],
            "P_Q": frac_s(Pq),
            "rho_Q": frac_s(packet["rho_Q"]),
            "status": "positive_length_out_of_scope",
        }

    blue = {norm_edge(e) for e in edges if side[e[0]] != side[e[1]]}
    bad = {norm_edge(e) for e in edges if side[e[0]] == side[e[1]]}
    raw = []
    for i in range(L - 2):
        verts = set(row[i : i + 3])
        raw.append(raw_sigma(blue, bad, verts))
    if any(s < 0 for s in raw):
        raise AssertionError((name, n, row, raw))

    terms = lane_v2.interval_terms(n, edges, side, row, st)
    by_i: dict[int, dict] = {}
    for t in terms:
        i = t.get("i")
        if isinstance(i, int) and 0 <= i < L - 2 and i not in by_i:
            by_i[i] = t

    intervals = []
    invalid = False
    sum_nuK = F(0)
    sum_raw = sum(raw)
    per_fail = 0
    per_deficit_total = F(0)
    for i, sig in enumerate(raw):
        t = by_i.get(i)
        nuK = None if t is None else t.get("nuK")
        valid = bool(t and t.get("connected_after") and t.get("terminal_shadow_valid") and nuK is not None)
        if not valid:
            invalid = True
        nuKF = F(0) if nuK is None else F(nuK)
        sum_nuK += nuKF
        deficit = F(25 * sig) - nuKF
        if deficit > 0:
            per_fail += 1
            per_deficit_total += deficit
        intervals.append({
            "i": i,
            "raw_vertices": list(row[i : i + 3]),
            "sigma0": sig,
            "twentyfive_sigma0": 25 * sig,
            "nuK": frac_s(nuKF),
            "cd_margin": frac_s(nuKF - 25 * sig),
            "valid_completed": valid,
            "term": None if t is None else compact_term(t),
        })

    cd_margin = sum_nuK - F(25 * sum_raw)
    kappa = kappa_for(L)
    raw_coarea_margin = None if kappa is None else kappa * F(sum_raw) - Pq
    # If CD aggregate holds with no residual, raw coarea gives this coefficient.
    mu_coeff = None if kappa is None else kappa / 25
    mu_margin = None if mu_coeff is None else mu_coeff * sum_nuK - Pq

    status = "SAT"
    if invalid:
        status = "INVALID_COMPLETION"
    elif cd_margin < 0:
        status = "AGG_FAIL"
    elif raw_coarea_margin is not None and raw_coarea_margin < 0:
        status = "RAW_COAREA_FAIL"

    return {
        "schema": "bankl_cd_gate_v1",
        "name": name,
        "n": n,
        "m": len(st[0]),
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
        "kappa": frac_s(kappa),
        "mu_coeff": frac_s(mu_coeff),
        "sum_sigma0": sum_raw,
        "sum_25sigma0": 25 * sum_raw,
        "sum_nuK": frac_s(sum_nuK),
        "cd_margin": frac_s(cd_margin),
        "raw_coarea_margin": frac_s(raw_coarea_margin),
        "mu_margin_no_residual": frac_s(mu_margin),
        "per_interval_fail_count": per_fail,
        "per_interval_deficit_total": frac_s(per_deficit_total),
        "status": status,
        "intervals": intervals,
    }


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], out, acc: Counter, args) -> None:
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    for f in M:
        for row0 in cyc[f]:
            row = tuple(row0)
            rec = cd_record(name, n, edges, side, f, row, st)
            if rec is None:
                continue
            acc["rows"] += 1
            acc[f"status:{rec['status']}"] += 1
            acc[f"L:{rec['L']}"] += 1
            acc[f"ph:{rec.get('p')}:{rec.get('h')}"] += 1
            if rec["status"] != "SAT":
                acc["fail"] += 1
                if "first_fail" not in acc:
                    acc["first_fail"] = rec
            if rec.get("per_interval_fail_count", 0):
                acc["per_interval_fail_rows"] += 1
                if "first_per_interval_fail" not in acc:
                    acc["first_per_interval_fail"] = rec
            if args.include_rows:
                out.write(json.dumps(rec, sort_keys=True) + "\n")
            elif rec["status"] != "SAT" or rec.get("per_interval_fail_count", 0):
                out.write(json.dumps(rec, sort_keys=True) + "\n")
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
    ap.add_argument("--output", default="tmp/bankl_cd_gate_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_cd_gate_v1_summary.json")
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--limit-rows", type=int, default=None)
    ap.add_argument("--include-rows", action="store_true", help="write every checked row, not only failures")
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
            for L in range(8, 31, 2):
                n, edges, side, _bad = skel.build_two_lane(L)
                scan_side(f"two-lane-L{L}", n, edges, side, out, acc, args)
            for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
                bad = skel.greedy_chords(Ll, k, gap)
                n, edges, side, _ = skel.build_k_lane(Ll, k, bad)
                scan_side(f"klane-L{Ll}k{k}", n, edges, side, out, acc, args)
            if not args.direct_only:
                named = [
                    ("Grotzsch", skel.mycielski(5, skel.Cn(5))),
                    ("M(C7)", skel.mycielski(7, skel.Cn(7))),
                    ("C7|Grotzsch", skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)),
                ]
                for name, (n, edges) in named:
                    scan_gmins(name, n, edges, out, acc, args)
        if not args.direct_only:
            for nn in range(args.min_n, args.max_n + 1):
                before = acc["rows"]
                for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                    n, edges = skel.dec(g6)
                    scan_gmins(f"cen{g6}", n, edges, out, acc, args)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
                print(json.dumps({"N": nn, "rows_added": acc["rows"] - before, "rows_total": acc["rows"], "fail_total": acc["fail"]}, sort_keys=True), flush=True)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

    summary = {
        "output": str(out_path),
        "rows": acc["rows"],
        "fail": acc["fail"],
        "per_interval_fail_rows": acc["per_interval_fail_rows"],
        "statuses": {k.removeprefix("status:"): v for k, v in sorted(acc.items()) if k.startswith("status:")},
        "by_L": {k.removeprefix("L:"): v for k, v in sorted(acc.items()) if k.startswith("L:")},
        "by_p_h": {k.removeprefix("ph:"): v for k, v in sorted(acc.items()) if k.startswith("ph:")},
        "first_fail": acc.get("first_fail"),
        "first_per_interval_fail": acc.get("first_per_interval_fail"),
    }
    summary_path = Path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("output", "rows", "fail", "per_interval_fail_rows", "statuses", "by_L", "by_p_h")}, sort_keys=True))
    print("PASS Bank-L CD aggregate gate" if acc["fail"] == 0 else "FAIL Bank-L CD aggregate gate")


if __name__ == "__main__":
    main()