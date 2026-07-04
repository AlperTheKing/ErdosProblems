#!/usr/bin/env python3
"""Exact replay of the EQ-ODL1 Rung-2 seed-ray identities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

import _codex_eq_odl1_shifted_lp as eq
from _codex_c5lift_weighted_quotient_gate import EQ, b_edges, edges_of, m_edges, shortest_paths


def verify() -> dict[str, object]:
    t = sp.symbols("t")
    n, edges = edges_of(EQ)
    side = tuple(int(c) for c in eq.old_lp.SIDE)
    bset = b_edges(edges, side)
    bad = sorted(m_edges(edges, side))
    paths_by_bad = {edge: shortest_paths(n, bset, edge[0], edge[1]) for edge in bad}
    i_eq = eq.row_overlap_expr(eq.old_lp.ACTIVE_ROW, eq.ws, paths_by_bad)
    d_eq = eq.old_lp.eq_denominator(eq.ws)
    sub = {eq.xs[i]: (sp.Integer(0) if i < 5 else t - 1) for i in range(10)}
    i_seed = sp.factor(i_eq.subs(sub))
    n_seed = sp.factor(eq.old_lp.N.subs(sub))
    d_seed = sp.factor(d_eq.subs(sub))
    eta25_seed = sp.factor(eq.old_lp.eta25.subs(sub))
    p_seed = sp.factor(d_seed * (eta25_seed - 25 * (i_seed - n_seed)))

    expected_i_minus_n = sp.factor((t + 1) * (3 * t + 2) / ((t + 2) * (t * t + 3 * t + 1)))
    expected_d = sp.factor(t**5 * (t + 2) ** 2 * (t * t + 3 * t + 1))
    expected_p = sp.factor(25 * t**6 * (t + 2) * (t * t + 2 * t + 2))
    u = sp.symbols("u")
    shifted_p = sp.Poly(sp.expand(expected_p.subs(t, 1 + u)), u, domain=sp.ZZ)
    shifted_coeffs = [int(c) for c in reversed(shifted_p.all_coeffs())]
    return {
        "schema": "eq_odl1_seed_ray_verify_v1",
        "graph": EQ,
        "side": eq.old_lp.SIDE,
        "active_row": list(eq.old_lp.ACTIVE_ROW),
        "bad_edges": [list(edge) for edge in bad],
        "seed_ray": "w0..w4=1, w5..w9=t",
        "I_minus_N": str(sp.factor(i_seed - n_seed)),
        "expected_I_minus_N": str(expected_i_minus_n),
        "I_minus_N_ok": bool(sp.simplify((i_seed - n_seed) - expected_i_minus_n) == 0),
        "D_EQ": str(d_seed),
        "expected_D_EQ": str(expected_d),
        "D_EQ_ok": bool(sp.simplify(d_seed - expected_d) == 0),
        "eta25": str(eta25_seed),
        "P_EQ1": str(p_seed),
        "expected_P_EQ1": str(expected_p),
        "P_EQ1_ok": bool(sp.simplify(p_seed - expected_p) == 0),
        "P_EQ1_shifted_t_1_plus_u_coeffs_low_to_high": shifted_coeffs,
        "P_EQ1_shifted_coeffs_nonnegative": all(c >= 0 for c in shifted_coeffs),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_seed_ray_verify_v1.json"))
    args = ap.parse_args()
    out = verify()
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["I_minus_N_ok", "D_EQ_ok", "P_EQ1_ok", "P_EQ1_shifted_coeffs_nonnegative"]}, sort_keys=True))


if __name__ == "__main__":
    main()
