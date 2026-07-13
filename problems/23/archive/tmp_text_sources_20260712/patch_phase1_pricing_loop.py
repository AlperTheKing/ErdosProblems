from pathlib import Path

p = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_cg.py')
s = p.read_text()
if 'import sys\n' not in s:
    s = s.replace('import math\nimport time\n', 'import math\nimport sys\nimport time\n')
if 'def log(msg: str) -> None:' not in s:
    s = s.replace(
        'def column_key(col: hybrid.HybridColumn) -> tuple[str, str, str, tuple[int, ...]]:\n    return (col.side, col.kind, col.name, col.multiplier_exp)\n\n\n',
        'def column_key(col: hybrid.HybridColumn) -> tuple[str, str, str, tuple[int, ...]]:\n    return (col.side, col.kind, col.name, col.multiplier_exp)\n\n\ndef log(msg: str) -> None:\n    print(f"[phase1-cg] {msg}", file=sys.stderr, flush=True)\n\n\n',
    )
if '"_row_dual": row_dual,' not in s:
    s = s.replace(
        '        "p95_rc_formula_error": p95_rc_formula_error,\n    }\n\n\ndef run',
        '        "p95_rc_formula_error": p95_rc_formula_error,\n        "_row_dual": row_dual,\n    }\n\n\ndef run',
    )
if 'def score_column(col: hybrid.HybridColumn, row_dual: np.ndarray)' not in s:
    marker = '\n\ndef run(args: argparse.Namespace) -> dict[str, Any]:\n'
    insert = r'''

def score_column(col: hybrid.HybridColumn, row_dual: np.ndarray) -> float:
    score = 0.0
    for row, coeff in col.terms:
        score += float(coeff) * float(row_dual[row])
    return score


def price_columns(
    columns: list[hybrid.HybridColumn],
    row_dual: np.ndarray,
    *,
    skip: set,
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[hybrid.HybridColumn]]:
    candidates: list[tuple[float, int, hybrid.HybridColumn]] = []
    best: tuple[float, int, hybrid.HybridColumn] | None = None
    for idx, col in enumerate(columns):
        if column_key(col) in skip:
            continue
        score = score_column(col, row_dual)
        if best is None or score > best[0]:
            best = (score, idx, col)
        if score > args.price_tol:
            candidates.append((score, idx, col))
    candidates.sort(key=lambda item: item[0], reverse=True)
    top = []
    for score, idx, col in candidates[: args.top]:
        top.append(
            {
                "score": float(score),
                "pool_index": int(idx),
                "side": col.side,
                "kind": col.kind,
                "name": col.name,
                "multiplier_exp": list(col.multiplier_exp),
                "terms": len(col.terms),
            }
        )
    add_cols = [col for _score, _idx, col in candidates[: args.add_top]]
    return (
        {
            "priced_columns": len(columns),
            "skipped_columns": len(skip),
            "positive_score_count": len(candidates),
            "best_score": float(best[0]) if best else 0.0,
            "added_columns": len(add_cols),
            "top": top,
        },
        add_cols,
    )
'''
    if marker not in s:
        raise SystemExit('missing run marker')
    s = s.replace(marker, insert + marker, 1)
start = s.index('def run(args: argparse.Namespace) -> dict[str, Any]:\n')
end = s.index('\n\ndef main() -> None:', start)
new_run = r'''def run(args: argparse.Namespace) -> dict[str, Any]:
    t0 = time.monotonic()
    log(f"building seed columns max_pairs={args.seed_max_pairs} max_band={args.seed_max_band}")
    chart, betas, target_beta, current_cols, seed_meta = build_columns(
        args,
        max_pairs=args.seed_max_pairs,
        max_band=args.seed_max_band,
    )
    log(f"seed columns={len(current_cols)} rows={len(betas)}")
    price_cols: list[hybrid.HybridColumn] | None = None
    price_meta = None
    if args.price_max_pairs > 0:
        log(f"building price pool max_pairs={args.price_max_pairs} max_band={args.price_max_band}")
        _chart2, _betas2, _target2, price_cols, price_meta = build_columns(
            args,
            max_pairs=args.price_max_pairs,
            max_band=args.price_max_band,
        )
        log(f"price pool columns={len(price_cols)}")

    current_keys = {column_key(col) for col in current_cols}
    iterations = []
    final_status = "iteration_limit"
    for it in range(args.iterations + 1):
        log(f"iteration={it} building matrix columns={len(current_cols)}")
        mat = build_matrix(current_cols, len(betas))
        log(f"iteration={it} solving Phase-I nnz={mat.nnz}")
        phase1 = solve_phase1(
            mat,
            target_beta,
            threads=args.solver_threads,
            time_limit=args.time_limit,
            verbose=args.verbose,
            x_tol=args.x_tol,
        )
        row_dual = phase1.pop("_row_dual", None)
        rec: dict[str, Any] = {
            "iteration": it,
            "columns": len(current_cols),
            "nnz": int(mat.nnz),
            "phase1": phase1,
        }
        artificial_sum = float(phase1.get("artificial_sum", math.inf))
        log(
            "iteration={} phase1 status={} objective={} artificial_sum={}".format(
                it,
                phase1.get("message"),
                phase1.get("objective"),
                artificial_sum,
            )
        )
        if phase1.get("success") and artificial_sum <= args.art_tol:
            final_status = "phase1_zero"
            iterations.append(rec)
            break
        if not phase1.get("success") and not args.price_from_nonoptimal:
            final_status = "phase1_not_optimal"
            iterations.append(rec)
            break
        if row_dual is None:
            final_status = "no_row_dual"
            iterations.append(rec)
            break
        if price_cols is None:
            final_status = "no_price_pool"
            iterations.append(rec)
            break
        log(f"iteration={it} pricing columns")
        pricing, add_cols = price_columns(price_cols, row_dual, skip=current_keys, args=args)
        rec["pricing"] = pricing
        iterations.append(rec)
        log(
            "iteration={} positives={} add={} best={}".format(
                it,
                pricing.get("positive_score_count"),
                pricing.get("added_columns"),
                pricing.get("best_score"),
            )
        )
        if not add_cols:
            final_status = "no_positive_priced_columns"
            break
        for col in add_cols:
            key = column_key(col)
            if key not in current_keys:
                current_cols.append(col)
                current_keys.add(key)

    return {
        "schema": "eq_odl1_rung2_hybrid_phase1_pricing_loop_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": chart.generator_names[args.dominant],
        "band": args.band,
        "tier": args.tier,
        "support": args.support,
        "face_pair_families": args.face_pair_families,
        "seed_max_pairs": args.seed_max_pairs,
        "seed_max_band": args.seed_max_band,
        "price_max_pairs": args.price_max_pairs,
        "price_max_band": args.price_max_band,
        "add_top": args.add_top,
        "iterations_requested": args.iterations,
        "final_status": final_status,
        "rows": len(betas),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "seed_meta": seed_meta,
        "price_meta": price_meta,
        "iterations": iterations,
        "seconds": time.monotonic() - t0,
    }
'''
s = s[:start] + new_run + s[end:]
# Add parser arguments if absent.
if '--price-max-pairs' not in s:
    s = s.replace(
        '    ap.add_argument("--seed-max-band", type=int, default=4096)\n',
        '    ap.add_argument("--seed-max-band", type=int, default=4096)\n    ap.add_argument("--price-max-pairs", type=int, default=0)\n    ap.add_argument("--price-max-band", type=int, default=0)\n    ap.add_argument("--iterations", type=int, default=3)\n    ap.add_argument("--add-top", type=int, default=1000)\n    ap.add_argument("--top", type=int, default=50)\n',
    )
if '--price-tol' not in s:
    s = s.replace(
        '    ap.add_argument("--time-limit", type=float, default=900.0)\n',
        '    ap.add_argument("--time-limit", type=float, default=900.0)\n    ap.add_argument("--price-tol", type=float, default=1.0e-8)\n    ap.add_argument("--art-tol", type=float, default=1.0e-7)\n    ap.add_argument("--price-from-nonoptimal", action="store_true")\n',
    )
# Replace final print to match loop shape.
old_print = '''    print(json.dumps({\n        "chart": out["chart"],\n        "dominant": out["dominant"],\n        "columns": out["columns"],\n        "nnz": out["nnz"],\n        "phase1": out["phase1"],\n        "summary": str(args.summary),\n    }, sort_keys=True))\n'''
new_print = '''    last = out["iterations"][-1] if out["iterations"] else {}\n    print(json.dumps({\n        "chart": out["chart"],\n        "dominant": out["dominant"],\n        "final_status": out["final_status"],\n        "iterations": len(out["iterations"]),\n        "last_columns": last.get("columns"),\n        "last_message": last.get("phase1", {}).get("message"),\n        "last_artificial_sum": last.get("phase1", {}).get("artificial_sum"),\n        "last_positive": None if "pricing" not in last else last["pricing"].get("positive_score_count"),\n        "summary": str(args.summary),\n    }, sort_keys=True))\n'''
if old_print in s:
    s = s.replace(old_print, new_print, 1)
else:
    raise SystemExit('missing final print block')
p.write_text(s)
print('patched', p)
