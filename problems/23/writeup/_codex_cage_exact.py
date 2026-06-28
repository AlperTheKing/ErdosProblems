"""Exact rational checker prototype for CAGE certificates.

This script uses the floating CAGE solver only as a guide.  It then:
  * approximates gate ratios r_g by rational Fractions;
  * repairs alpha exactly against the R1/R2 equalities using an exact RREF;
  * verifies alpha>=0, R1/R2, and all vertex budget inequalities exactly.

It is currently a prototype for small/hard named cases, not a proof.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from math import exp

import sympy as sp

from _codex_cage import blowup_edges, canon_edge, solve_cage
from _h import dec, loads


class ExactInstance:
    def __init__(self, label, n, gates, vars_, aeq, beq, cap):
        self.label = label
        self.n = n
        self.gates = gates
        self.vars = vars_
        self.aeq = aeq
        self.beq = beq
        self.cap = cap


def build_exact_instance(info, label):
    n = info["n"]
    gates = []
    gate_index = {}
    pair_index = {}
    pair_count = 0
    vars_ = []
    r2_rows = {}
    r2_rhs = {}
    S = [F(0) for _ in range(n)]

    for f_idx, f in enumerate(info["M"]):
        paths = info["cyc"][f]
        nf = len(paths)
        L = info["ell"][f]
        layer_vertices = [dict() for _ in range(L)]
        for P in paths:
            if len(P) != L:
                raise AssertionError((label, f, P, L))
            for i, v in enumerate(P):
                layer_vertices[i][v] = layer_vertices[i].get(v, F(0)) + F(1, nf)
        for i in range(L):
            for v, pfv in layer_vertices[i].items():
                S[v] += pfv

        pi = [dict() for _ in range(L - 1)]
        for P in paths:
            for t in range(L - 1):
                e = canon_edge(P[t], P[t + 1])
                pi[t][e] = pi[t].get(e, F(0)) + F(1, nf)

        H = []
        for t in range(L - 1):
            ht = F(0)
            for i in range(t + 1):
                for j in range(t + 1, L):
                    ht += F(1, j - i)
            H.append(ht)

        for i in range(L):
            for j in range(i + 1, L):
                pair_index[(f_idx, i, j)] = pair_count
                pair_count += 1

        for t in range(L - 1):
            for e, pe in pi[t].items():
                key = (f_idx, t, e)
                g = len(gates)
                gate_index[key] = g
                gates.append(key)
                r2_rows[g] = {}
                r2_rhs[g] = H[t] * pe

        for i in range(L):
            for j in range(i + 1, L):
                pidx = pair_index[(f_idx, i, j)]
                for t in range(i, j):
                    for e, _pe in pi[t].items():
                        g = gate_index[(f_idx, t, e)]
                        vidx = len(vars_)
                        vars_.append(
                            {
                                "pair": pidx,
                                "gate": g,
                                "left": list(layer_vertices[i].items()),
                                "right": list(layer_vertices[j].items()),
                            }
                        )
                        r2_rows[g][vidx] = F(1)

    m = len(vars_)
    aeq = []
    beq = []
    for p in range(pair_count):
        row = [F(0) for _ in range(m)]
        for k, av in enumerate(vars_):
            if av["pair"] == p:
                row[k] = F(1)
        aeq.append(row)
        beq.append(F(1))
    for g in range(len(gates)):
        row = [F(0) for _ in range(m)]
        for k, coeff in r2_rows[g].items():
            row[k] = coeff
        aeq.append(row)
        beq.append(r2_rhs[g])

    cap = [F(n) - S[v] for v in range(n)]
    return ExactInstance(label, n, gates, vars_, aeq, beq, cap)


def to_sp(x: F):
    return sp.Rational(x.numerator, x.denominator)


def from_sp(x):
    x = sp.Rational(x)
    return F(int(x.p), int(x.q))


def repair_alpha(ex: ExactInstance, alpha_float, denom: int):
    mat = [[to_sp(x) for x in row] + [to_sp(b)] for row, b in zip(ex.aeq, ex.beq)]
    rref, pivots = sp.Matrix(mat).rref()
    pivots = [p for p in pivots if p < len(ex.vars)]
    pivot_set = set(pivots)
    free = [i for i in range(len(ex.vars)) if i not in pivot_set]
    alpha = [None for _ in ex.vars]
    for i in free:
        # Keep tiny LP noise at zero; it helps preserve nonnegativity.
        val = 0.0 if abs(alpha_float[i]) < 1e-11 else float(alpha_float[i])
        alpha[i] = F(val).limit_denominator(denom)
    for row_idx, p in enumerate(pivots):
        rhs = from_sp(rref[row_idx, len(ex.vars)])
        acc = F(0)
        for i in free:
            coeff = from_sp(rref[row_idx, i])
            if coeff:
                acc += coeff * alpha[i]
        alpha[p] = rhs - acc
    return alpha, pivots


def check_equalities(ex: ExactInstance, alpha):
    for row, rhs in zip(ex.aeq, ex.beq):
        lhs = sum(c * a for c, a in zip(row, alpha))
        if lhs != rhs:
            return False, (lhs, rhs)
    return True, None


def exact_budget(ex: ExactInstance, alpha, r):
    out = [F(0) for _ in range(ex.n)]
    for a, av in zip(alpha, ex.vars):
        if a == 0:
            continue
        g = av["gate"]
        rg = r[g]
        inv = F(1, 1) / rg
        for v, pfv in av["left"]:
            out[v] += a * rg * pfv
        for v, pfv in av["right"]:
            out[v] += a * inv * pfv
    return out


def verify_exact(ex: ExactInstance, alpha, r):
    if any(a < 0 for a in alpha):
        return False, "negative alpha", min(alpha)
    ok, detail = check_equalities(ex, alpha)
    if not ok:
        return False, "equality fail", detail
    if any(x <= 0 for x in r):
        return False, "nonpositive r", min(r)
    bud = exact_budget(ex, alpha, r)
    slacks = [ex.cap[v] - bud[v] for v in range(ex.n)]
    if min(slacks) < 0:
        return False, "budget fail", (min(slacks), slacks.index(min(slacks)))
    return True, "ok", min(slacks)


def frac_json(x: F):
    return [x.numerator, x.denominator]


def frac_from_json(x):
    return F(int(x[0]), int(x[1]))


def write_certificate(path, *, ex: ExactInstance, g6, blow, alpha, r, src_name, rden, aden, pivots, min_slack):
    payload = {
        "format": "codex-cage-exact-v1",
        "g6": g6,
        "blow": blow,
        "label": ex.label,
        "n": ex.n,
        "num_gates": len(ex.gates),
        "num_alpha": len(ex.vars),
        "alpha_source": src_name,
        "rden": rden,
        "aden": aden,
        "pivots": list(pivots),
        "min_slack": frac_json(min_slack),
        "r": [frac_json(x) for x in r],
        "alpha": [frac_json(x) for x in alpha],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
        fh.write("\n")


def read_certificate(path):
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if payload.get("format") != "codex-cage-exact-v1":
        raise ValueError(f"unsupported certificate format: {payload.get('format')!r}")
    return payload, [frac_from_json(x) for x in payload["alpha"]], [frac_from_json(x) for x in payload["r"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--restarts", type=int, default=32)
    ap.add_argument("--denom", type=int, default=10**7)
    ap.add_argument("--save-cert", default=None)
    ap.add_argument("--load-cert", default=None)
    args = ap.parse_args()

    if args.blow == 1:
        n, edges = dec(args.g6)
    else:
        n, edges = blowup_edges(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")

    ex = build_exact_instance(info, f"{args.g6}[{args.blow}]")

    if args.load_cert:
        payload, alpha, r = read_certificate(args.load_cert)
        if payload.get("g6") != args.g6 or int(payload.get("blow", -1)) != args.blow:
            raise SystemExit(
                f"certificate graph ({payload.get('g6')!r}, blow={payload.get('blow')}) "
                f"!= requested ({args.g6!r}, blow={args.blow})"
            )
        if payload["label"] != ex.label:
            raise SystemExit(f"certificate label {payload['label']} != instance label {ex.label}")
        if len(alpha) != len(ex.vars) or len(r) != len(ex.gates):
            raise SystemExit("certificate dimension mismatch")
        ok, kind, detail = verify_exact(ex, alpha, r)
        print(f"CERT load label={ex.label} ok={ok} kind={kind} detail={detail}")
        if not ok:
            raise SystemExit(1)
        return

    # Build float and exact instances independently but with identical loop order.
    from _codex_cage import build_instance

    fl = build_instance(info, f"{args.g6}[{args.blow}]")
    row = solve_cage(fl, rounds=args.rounds, restarts=args.restarts)
    print(
        f"float label={ex.label} gap={row['gap']:+.6g} ratio={row['ratio']:.9f} "
        f"eta={row['eta']:.9f} vars={len(ex.vars)} gates={len(ex.gates)}",
        flush=True,
    )

    alpha_sources = [("lp", row["alpha"])]
    for eps in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
        alpha_sources.append((f"mix{eps:g}", (1.0 - eps) * row["alpha"] + eps * fl.alpha0))

    for rden in [10**4, 10**5, 10**6, args.denom]:
        r = [F(exp(float(x))).limit_denominator(rden) for x in row["x"]]
        for src_name, alpha_src in alpha_sources:
            for aden in [10**4, 10**5, 10**6, args.denom]:
                alpha, pivots = repair_alpha(ex, alpha_src, aden)
                ok, kind, detail = verify_exact(ex, alpha, r)
                print(
                    f"try src={src_name} rden={rden} aden={aden} "
                    f"ok={ok} kind={kind} detail={detail}",
                    flush=True,
                )
                if ok:
                    if args.save_cert:
                        write_certificate(
                            args.save_cert,
                            ex=ex,
                            g6=args.g6,
                            blow=args.blow,
                            alpha=alpha,
                            r=r,
                            src_name=src_name,
                            rden=rden,
                            aden=aden,
                            pivots=pivots,
                            min_slack=detail,
                        )
                    print(
                        f"CERT ok label={ex.label} src={src_name} "
                        f"rden={rden} aden={aden} min_slack={detail} pivots={len(pivots)}",
                        flush=True,
                    )
                    if args.save_cert:
                        print(f"CERT saved {args.save_cert}", flush=True)
                    return
    raise SystemExit("no exact certificate found with tested denominators")


if __name__ == "__main__":
    main()
