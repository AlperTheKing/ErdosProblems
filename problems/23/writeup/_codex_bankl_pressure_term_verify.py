"""Recompute current Bank-L pressure-cover term values from graph data.

This is a proof-facing audit for ``bankl_pressure_cover_lean_v1``.  The
Lean-facing artifact already checks rational identities, but its row id omits
the cut side.  This verifier builds a side-candidate index from side-bearing
gate artifacts, then recomputes:

* MU_NUK terms: sigma, nu, K_S, nu_K for the stored switch vertex set;
* DETOUR terms: |K|-T_Q(K) for the stored detour component vertex set.

The current completion engine is still v2/approximate, so this script does not
claim Gate A.  It only says the terms already emitted are exact consequences of
some recorded connected-B maximum cut side.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import _codex_bankl_lcb_skeleton as skel


SIDE_SOURCES = (
    "tmp/bankl_cd_gate_v1.jsonl",
    "tmp/bankl_cd_superset_gate_v1.jsonl",
    "tmp/bankl_lane_prefix_coarea_n11.jsonl",
)


def parse_frac(x: Any) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x, 1)
    if isinstance(x, str):
        return F(x)
    raise TypeError(x)


def frac_s(x: F | int | None) -> str | None:
    if x is None:
        return None
    if not isinstance(x, F):
        x = F(x, 1)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def norm_edge(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def row_key_from_flat(o: dict[str, Any]) -> tuple[str, int, tuple[int, int], tuple[int, ...]]:
    return (o["name"], int(o["n"]), norm_edge(tuple(o["f"])), tuple(o["row"]))


def row_key_from_lean(o: dict[str, Any]) -> tuple[str, int, tuple[int, int], tuple[int, ...]]:
    rid = o["row_id"]
    return (rid["name"], int(rid["n"]), norm_edge(tuple(rid["f"])), tuple(rid["row"]))


def graph_from_name(name: str) -> tuple[int, list[tuple[int, int]]]:
    if name.startswith("cen"):
        return skel.dec(name[3:])
    if name.startswith("C") and name.endswith("[1]"):
        L = int(name[1:-3])
        return skel.blowup([1] * L)
    m = re.fullmatch(r"two-lane-L(\d+)", name)
    if m:
        n, edges, _side, _bad = skel.build_two_lane(int(m.group(1)))
        return n, edges
    m = re.fullmatch(r"klane-L(\d+)k(\d+)", name)
    if m:
        Ll, k = int(m.group(1)), int(m.group(2))
        gap_by = {(12, 4): 6, (14, 4): 8, (16, 5): 8, (20, 6): 10}
        bad = skel.greedy_chords(Ll, k, gap_by[(Ll, k)])
        n, edges, _side, _ = skel.build_k_lane(Ll, k, bad)
        return n, edges
    if name == "Grotzsch":
        return skel.mycielski(5, skel.Cn(5))
    if name == "M(C7)":
        return skel.mycielski(7, skel.Cn(7))
    if name == "C7|Grotzsch":
        return skel.bridge((7, skel.Cn(7)), skel.mycielski(5, skel.Cn(5)), 0, 0)
    raise ValueError(f"unsupported graph name: {name}")


def load_side_candidates(paths: list[str]) -> dict[tuple[str, int, tuple[int, int], tuple[int, ...]], list[str]]:
    idx: dict[tuple[str, int, tuple[int, int], tuple[int, ...]], set[str]] = defaultdict(set)
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                rec = json.loads(line)
                side = rec.get("side")
                if side is None:
                    continue
                idx[row_key_from_flat(rec)].add(side)
    return {k: sorted(v) for k, v in idx.items()}


def graph_context(name: str, side_s: str):
    n, edges0 = graph_from_name(name)
    edges = [norm_edge(tuple(e)) for e in edges0]
    side = [int(ch) for ch in side_s]
    if len(side) != n:
        raise ValueError((name, n, side_s))
    adj = skel.adj_from_edges(n, edges)
    if not skel.Bconn(n, adj, side):
        return None
    st = skel.struct_for_side(n, adj, side)
    base_gamma = skel.gamma_data(n, adj, side)
    if st is None or base_gamma is None:
        return None
    blue_edges = {e for e in edges if side[e[0]] != side[e[1]]}
    bad_edges = {e for e in edges if side[e[0]] == side[e[1]]}
    old_bad_len = {norm_edge((u, v)): L0 for u, v, L0 in base_gamma[1]}
    return {
        "n": n,
        "edges": edges,
        "side": side,
        "adj": adj,
        "st": st,
        "blue_edges": blue_edges,
        "bad_edges": bad_edges,
        "old_bad_len": old_bad_len,
    }


def verify_munuk_term(ctx: dict[str, Any], term: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    verts = set(int(v) for v in term["verts"])
    rec = skel.switch_record(
        ctx["n"],
        ctx["blue_edges"],
        ctx["bad_edges"],
        ctx["old_bad_len"],
        verts,
        ("pressure_term", term.get("kind"), term.get("label"), term.get("i")),
    )
    side2 = skel.switched(ctx["side"], verts)
    connected_after = bool(skel.Bconn(ctx["n"], ctx["adj"], side2))
    mask = sum(1 << v for v in verts)
    terminal = skel.terminal_shadow_details(ctx["n"], ctx["adj"], ctx["side"], ctx["st"], mask)
    got = {
        "verts": sorted(verts),
        "sigma": rec["sigma"],
        "nu": frac_s(rec["nu"]),
        "K_S": rec["K_S"],
        "nuK": frac_s(rec["nuK"]),
        "connected_after": connected_after,
        "terminal_shadow_valid": terminal is not None,
        "dB": rec["dB"],
        "dM": rec["dM"],
    }
    ok = rec["nuK"] is not None and parse_frac(term["value"]) == parse_frac(rec["nuK"])
    if "sigma" in term:
        ok = ok and int(term["sigma"]) == rec["sigma"]
    if "K_S" in term:
        ok = ok and int(term["K_S"]) == rec["K_S"]
    if "nu" in term:
        ok = ok and parse_frac(term["nu"]) == parse_frac(rec["nu"])
    ok = ok and connected_after and terminal is not None
    return ok, got


def verify_detour_term(ctx: dict[str, Any], term: dict[str, Any], f: tuple[int, int], row: tuple[int, ...]) -> tuple[bool, dict[str, Any]]:
    vertices = set(int(v) for v in term["vertices"])
    M, _ell, _T, _mu, cyc = ctx["st"]
    _comp_map, find = skel.kcomponents(ctx["n"], cyc)
    Ms = [g for g in M if find(g[0]) == find(f[0])]
    tw = skel.row_component_tw(ctx["n"], list(Ms), cyc)
    TQ = sum(tw[v] for v in (set(row) & vertices))
    size = len(vertices)
    value = F(size, 1) - TQ
    got = {
        "vertices": sorted(vertices),
        "size": size,
        "TQ": frac_s(TQ),
        "value": frac_s(value),
    }
    ok = (
        int(term["size"]) == size
        and parse_frac(term["TQ"]) == TQ
        and parse_frac(term["value"]) == value
    )
    return ok, got


def verify_record(rec: dict[str, Any], side_idx: dict, graph_cache: dict) -> tuple[str, dict[str, Any]]:
    key = row_key_from_lean(rec)
    terms = rec.get("terms", [])
    if rec["proof_case"] not in ("MU_NUK", "DETOUR_RESIDUAL"):
        return "SKIP", {"reason": rec["proof_case"]}
    candidates = side_idx.get(key, [])
    if not candidates:
        return "NO_SIDE", {"key": repr(key)}
    last_detail = None
    for side_s in candidates:
        cache_key = (key[0], side_s)
        if cache_key not in graph_cache:
            graph_cache[cache_key] = graph_context(key[0], side_s)
        ctx = graph_cache[cache_key]
        if ctx is None:
            continue
        all_ok = True
        details = []
        for term in terms:
            if term["kind"] in ("lane_prefix_nuK", "nuK"):
                ok, got = verify_munuk_term(ctx, term)
            elif term["kind"] == "detour":
                ok, got = verify_detour_term(ctx, term, key[2], key[3])
            else:
                ok, got = False, {"reason": f"unsupported term kind {term['kind']}"}
            details.append({"term": term, "recomputed": got, "ok": ok})
            all_ok = all_ok and ok
        detail = {"side": side_s, "term_details": details}
        last_detail = detail
        if all_ok:
            return "PASS", detail
    return "FAIL", last_detail or {"candidate_count": len(candidates)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_pressure_cover_lean_v1.jsonl")
    ap.add_argument("--summary-output", default="tmp/bankl_pressure_term_verify_v1_summary.json")
    ap.add_argument("--fail-output", default="tmp/bankl_pressure_term_verify_v1_failures.jsonl")
    ap.add_argument("--side-source", action="append", default=[])
    args = ap.parse_args()

    side_sources = args.side_source or list(SIDE_SOURCES)
    side_idx = load_side_candidates(side_sources)
    counts: Counter = Counter()
    by_case: Counter = Counter()
    by_kind: Counter = Counter()
    graph_cache: dict[tuple[str, str], Any] = {}
    first_fail = None

    fail_path = Path(args.fail_output)
    fail_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(args.input).open("r", encoding="utf-8") as fh, fail_path.open("w", encoding="utf-8", newline="\n") as fail_out:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            status, detail = verify_record(rec, side_idx, graph_cache)
            counts[f"status:{status}"] += 1
            by_case[(rec["proof_case"], status)] += 1
            for term in rec.get("terms", []):
                by_kind[(term.get("kind"), status)] += 1
            if status in ("FAIL", "NO_SIDE"):
                out = {
                    "line_no": line_no,
                    "status": status,
                    "detail": detail,
                    "row_id": rec["row_id"],
                    "proof_case": rec["proof_case"],
                    "terms": rec.get("terms", []),
                }
                fail_out.write(json.dumps(out, sort_keys=True) + "\n")
                if first_fail is None:
                    first_fail = out

    summary = {
        "schema": "bankl_pressure_term_verify_v1",
        "input": args.input,
        "side_sources": side_sources,
        "side_index_keys": len(side_idx),
        "graph_contexts_built": len(graph_cache),
        "counts": dict(sorted(counts.items())),
        "by_case": {repr(k): v for k, v in sorted(by_case.items(), key=lambda kv: repr(kv[0]))},
        "by_kind": {repr(k): v for k, v in sorted(by_kind.items(), key=lambda kv: repr(kv[0]))},
        "first_fail": first_fail,
    }
    summary_path = Path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary_output": str(summary_path),
        "fail_output": str(fail_path),
        "counts": summary["counts"],
        "side_index_keys": len(side_idx),
        "graph_contexts_built": len(graph_cache),
    }, sort_keys=True))
    if counts["status:FAIL"] or counts["status:NO_SIDE"]:
        print("FAIL pressure term recomputation verifier")
    else:
        print("PASS pressure term recomputation verifier")


if __name__ == "__main__":
    main()
