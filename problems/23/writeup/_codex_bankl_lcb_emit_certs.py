"""Emit compact exact Bank-L/LCB row certificates as JSONL.

This is the Lean-facing companion to _codex_bankl_lcb_skeleton.py.  It uses
that scaffold's exact row summarizer, but writes one compact certificate record
per L>5 row to an output file, without mixing progress lines into the JSONL.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

import _codex_bankl_lcb_skeleton as skel
import _codex_bankl_pq_crosstab as pq


def compact_cert_record(rec: dict) -> dict:
    cert = rec["scalar_cert"]
    return {
        "schema": "bankl_lcb_cert_v2",
        "name": rec["name"],
        "n": rec["n"],
        "m": rec["m"],
        "f": rec["f"],
        "row": rec["row"],
        "L": rec["L"],
        "Delta_Q": rec["Delta_Q"],
        "minus_Delta_Q": rec["minus_Delta_Q"],
        "eta": rec["eta"],
        "Sigma_L": rec["Sigma_L"],
        "bank_margin": rec["bank_margin"],
        "R_Q": rec["R_Q"],
        "R_Q_minus_N": rec["R_Q_minus_N"],
        "row_scope": rec["row_scope"],
        "row_packet_p": rec.get("row_packet_p"),
        "row_packet_h": rec.get("row_packet_h"),
        "row_packet_d": rec.get("row_packet_d"),
        "row_packet_r": rec.get("row_packet_r"),
        "P_Q": rec.get("P_Q"),
        "rho_Q": rec.get("rho_Q"),
        "B_packet": rec.get("B_packet"),
        "pressure_sign": rec.get("pressure_sign"),
        "pressure_identity_verified": bool(rec.get("pressure_identity_verified")),
        "certificate_kind": rec["scalar_cert_kind"],
        "certificate_status": cert.get("status"),
        "certificate_target": cert.get("target"),
        "certificate_terms": cert.get("terms", []),
        "certificate_verified": bool(cert.get("verified")),
        "detour_terms_count": rec.get("detour_terms_count"),
        "detour_sum": rec.get("detour_sum"),
        "completed_positive_lcb_terms": rec.get("completed_positive_lcb_terms"),
        "connected_positive_lcb_terms": rec.get("connected_positive_lcb_terms"),
        "nuK_negative": rec.get("nuK_negative"),
        "nuK_invalid": rec.get("nuK_invalid"),
    }


def scan_side(name: str, n: int, edges: list[tuple[int, int]], side: list[int], args, out, acc: Counter) -> None:
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return
    st = skel.struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    _comp_map, find = skel.kcomponents(n, cyc)
    by_comp: dict[int, list[tuple[int, int]]] = {}
    for g in M:
        by_comp.setdefault(find(g[0]), []).append(g)
    for f in M:
        Ms = by_comp[find(f[0])]
        for row in cyc[f]:
            L = len(set(row))
            if L <= 5:
                continue
            rec = skel.summarize_row(
                name,
                n,
                edges,
                [int(x) for x in side],
                f,
                tuple(row),
                args.include_switches,
                args.completed_only,
                args.prefix_close,
                args.all_masks,
                args.all_masks_max_n,
                st,
                Ms,
                cyc,
            )
            if rec is None:
                continue
            packet = pq.compute_row_packet(n, edges, [int(x) for x in side], tuple(row))
            Pq = packet["P_Q"]
            pressure_sign = "pos" if Pq > 0 else "zero" if Pq == 0 else "neg"
            rec.update({
                "row_packet_p": packet["p"],
                "row_packet_h": packet["h"],
                "row_packet_d": packet["d"],
                "row_packet_r": packet["r"],
                "P_Q": pq.frac_s(Pq),
                "rho_Q": pq.frac_s(packet["rho_Q"]),
                "B_packet": pq.frac_s(packet["B_packet"]),
                "pressure_sign": pressure_sign,
                "pressure_identity_verified": packet["rho_Q"] - Pq == rec["minus_Delta_Q"],
            })
            cert_rec = compact_cert_record(rec)
            out.write(json.dumps(cert_rec, sort_keys=True) + "\n")
            acc["rows"] += 1
            acc[f"kind:{cert_rec['certificate_kind']}"] += 1
            acc[f"scope:{cert_rec['row_scope']}"] += 1
            acc[f"scope_kind:{cert_rec['row_scope']}:{cert_rec['certificate_kind']}"] += 1
            if cert_rec["certificate_status"] != "SAT" or not cert_rec["certificate_verified"]:
                acc["cert_fail"] += 1
                if "first_fail" not in acc:
                    acc["first_fail"] = cert_rec
            if cert_rec["row_scope"] in ("underfull", "equal") and cert_rec["certificate_kind"] in ("sparse", "size", "size2"):
                acc["bad_lcb_scope_fallback_rows"] += 1
                if "first_bad_lcb_scope_fallback" not in acc:
                    acc["first_bad_lcb_scope_fallback"] = cert_rec
            if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                return


def scan_gmins(name: str, n: int, edges: list[tuple[int, int]], args, out, acc: Counter) -> None:
    _adj, cuts = skel.gmins(n, edges)
    if args.max_cuts is not None:
        cuts = cuts[: args.max_cuts]
    for side in cuts:
        scan_side(name, n, edges, [int(x) for x in side], args, out, acc)
        if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
            return


def print_summary(acc: Counter, output: Path) -> None:
    summary = {
        "output": str(output),
        "rows": acc["rows"],
        "cert_fail": acc["cert_fail"],
        "bad_lcb_scope_fallback_rows": acc["bad_lcb_scope_fallback_rows"],
        "certificate_kinds": {k.removeprefix("kind:"): v for k, v in sorted(acc.items()) if k.startswith("kind:")},
        "row_scopes": {k.removeprefix("scope:"): v for k, v in sorted(acc.items()) if k.startswith("scope:")},
        "scope_certificate_kinds": {k.removeprefix("scope_kind:"): v for k, v in sorted(acc.items()) if k.startswith("scope_kind:")},
    }
    print(json.dumps(summary, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--census-only", action="store_true")
    ap.add_argument("--include-switches", action="store_true")
    ap.add_argument("--completed-only", action="store_true")
    ap.add_argument("--prefix-close", action="store_true")
    ap.add_argument("--all-masks", action="store_true")
    ap.add_argument("--all-masks-max-n", type=int, default=11)
    ap.add_argument("--limit-rows", type=int, default=None)
    args = ap.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    acc: Counter = Counter()

    with output.open("w", encoding="utf-8", newline="\n") as out:
        if not args.census_only:
            for L in (7, 9, 11, 13, 15, 17, 19):
                n, edges = skel.blowup([1] * L)
                scan_side(f"C{L}[1]", n, edges, skel.cycle_blowup_side([1] * L), args, out, acc)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

        if not args.census_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
            for L in range(8, 31, 2):
                n, edges, side, _bad = skel.build_two_lane(L)
                scan_side(f"two-lane-L{L}", n, edges, side, args, out, acc)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

        if not args.census_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
            for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
                bad = skel.greedy_chords(Ll, k, gap)
                n, edges, side, _ = skel.build_k_lane(Ll, k, bad)
                scan_side(f"klane-L{Ll}k{k}", n, edges, side, args, out, acc)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

        if not args.census_only and not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
            named = [
                ("Grotzsch", skel.mycielski(5, skel.Cn(5))),
                ("M(C7)", skel.mycielski(7, skel.Cn(7))),
                ("C7|Grotzsch", skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)),
            ]
            for name, (n, edges) in named:
                scan_gmins(name, n, edges, args, out, acc)
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

        if not args.skip_census and not args.direct_only and (args.limit_rows is None or acc["rows"] < args.limit_rows):
            for nn in range(args.min_n, args.max_n + 1):
                before = acc["rows"]
                for g6 in subprocess.run([skel.GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                    n, edges = skel.dec(g6)
                    scan_gmins(f"cen{g6}", n, edges, args, out, acc)
                    if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                        break
                print(f"CERT-EMIT census N={nn}: rows+={acc['rows'] - before}")
                if args.limit_rows is not None and acc["rows"] >= args.limit_rows:
                    break

    print_summary(acc, output)


if __name__ == "__main__":
    main()
