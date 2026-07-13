from pathlib import Path
path = Path(r'E:\Projects\ErdosProblems\problems\23\writeup\_codex_eq_odl1_rung2_hybrid_cg.py')
text = path.read_text()
old = """    x = np.array(sol.col_value[:real_cols], dtype=float)\n    z = np.array(sol.col_value[real_cols:real_cols + art_count], dtype=float)\n    original_activity = mat.tocsr().dot(x)\n"""
new = """    x = np.array(sol.col_value[:real_cols], dtype=float)\n    z = np.array(sol.col_value[real_cols:real_cols + art_count], dtype=float)\n    active_artificial = [\n        {\"row\": int(artificial_rows[i]), \"value\": float(val)}\n        for i, val in enumerate(z)\n        if float(val) > x_tol\n    ]\n    active_artificial.sort(key=lambda rec: rec[\"value\"], reverse=True)\n    original_activity = mat.tocsr().dot(x)\n"""
if old not in text:
    raise SystemExit('missing z anchor')
text = text.replace(old, new, 1)
old = """        \"artificial_nonzero\": int(np.sum(z > x_tol)),\n        \"artificial_max\": float(z.max()) if len(z) else 0.0,\n        \"artificial_sum\": float(z.sum()) if len(z) else 0.0,\n"""
new = """        \"artificial_nonzero\": int(np.sum(z > x_tol)),\n        \"active_artificial_rows\": active_artificial[:100],\n        \"active_artificial_value_sum\": float(sum(rec[\"value\"] for rec in active_artificial)),\n        \"artificial_max\": float(z.max()) if len(z) else 0.0,\n        \"artificial_sum\": float(z.sum()) if len(z) else 0.0,\n"""
if old not in text:
    raise SystemExit('missing artificial dict anchor')
text = text.replace(old, new, 1)
old = """def score_column(col: hybrid.HybridColumn, row_dual: np.ndarray) -> float:\n    score = 0.0\n    for row, coeff in col.terms:\n        score += float(coeff) * float(row_dual[row])\n    return score\n\n\ndef price_columns(\n"""
new = """def score_column(col: hybrid.HybridColumn, row_dual: np.ndarray) -> float:\n    score = 0.0\n    for row, coeff in col.terms:\n        score += float(coeff) * float(row_dual[row])\n    return score\n\n\ndef score_column_active_rows(col: hybrid.HybridColumn, active_rows: dict[int, float]) -> float:\n    # The accepted cone uses A x <= target.  Positive artificial rows are\n    # upper-bound violations, so columns with negative coefficients on those\n    # rows are useful.  Weight by current artificial magnitude.\n    score = 0.0\n    for row, coeff in col.terms:\n        weight = active_rows.get(int(row))\n        if weight is not None:\n            score += -float(coeff) * float(weight)\n    return score\n\n\ndef price_columns(\n"""
if old not in text:
    raise SystemExit('missing score function anchor')
text = text.replace(old, new, 1)
old = """    for idx, col in enumerate(columns):\n        if column_key(col) in skip:\n            continue\n        score = score_column(col, row_dual)\n"""
new = """    active_rows = getattr(args, \"_active_artificial_row_weights\", None)\n    for idx, col in enumerate(columns):\n        if column_key(col) in skip:\n            continue\n        if active_rows:\n            score = score_column_active_rows(col, active_rows)\n        else:\n            score = score_column(col, row_dual)\n"""
if old not in text:
    raise SystemExit('missing price loop anchor')
text = text.replace(old, new, 1)
old = """            \"positive_score_count\": len(candidates),\n            \"best_score\": float(best[0]) if best else 0.0,\n            \"added_columns\": len(add_cols),\n            \"top\": top,\n"""
new = """            \"positive_score_count\": len(candidates),\n            \"best_score\": float(best[0]) if best else 0.0,\n            \"added_columns\": len(add_cols),\n            \"targeted_active_rows\": sorted(int(r) for r in getattr(args, \"_active_artificial_row_weights\", {}) or {}),\n            \"top\": top,\n"""
if old not in text:
    raise SystemExit('missing pricing result anchor')
text = text.replace(old, new, 1)
old = """        if price_cols is None:\n            final_status = \"no_price_pool\"\n            iterations.append(rec)\n            break\n        log(f\"iteration={it} pricing columns\")\n        pricing, add_cols = price_columns(price_cols, row_dual, skip=current_keys, args=args)\n"""
new = """        if price_cols is None:\n            final_status = \"no_price_pool\"\n            iterations.append(rec)\n            break\n        if args.target_active_artificials:\n            active_weights = {\n                int(rec[\"row\"]): float(rec[\"value\"])\n                for rec in phase1.get(\"active_artificial_rows\", [])\n            }\n            args._active_artificial_row_weights = active_weights\n            log(f\"iteration={it} targeted active artificial rows={sorted(active_weights)}\")\n        else:\n            args._active_artificial_row_weights = {}\n        log(f\"iteration={it} pricing columns\")\n        pricing, add_cols = price_columns(price_cols, row_dual, skip=current_keys, args=args)\n"""
if old not in text:
    raise SystemExit('missing pricing call anchor')
text = text.replace(old, new, 1)
old = """    ap.add_argument(\"--price-from-nonoptimal\", action=\"store_true\")\n"""
new = """    ap.add_argument(\"--price-from-nonoptimal\", action=\"store_true\")\n    ap.add_argument(\"--target-active-artificials\", action=\"store_true\")\n"""
if old not in text:
    raise SystemExit('missing cli anchor')
text = text.replace(old, new, 1)
path.write_text(text)
