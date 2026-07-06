from pathlib import Path
path = Path(r'E:\Projects\ErdosProblems\problems\23\writeup\_codex_eq_odl1_rung2_hybrid_cg.py')
text = path.read_text()
repls = [
    (
"""    verbose: bool,\n    x_tol: float,\n    solver: str,\n) -> dict[str, Any]:\n""",
"""    verbose: bool,\n    x_tol: float,\n    solver: str,\n    artificial_row_mode: str,\n) -> dict[str, Any]:\n""",
    ),
    (
"""    artificial_rows = np.flatnonzero(target_float < -1.0e-15)\n    art_count = int(len(artificial_rows))\n""",
"""    if artificial_row_mode == \"all\":\n        artificial_rows = np.arange(row_count, dtype=int)\n    elif artificial_row_mode == \"negative\":\n        artificial_rows = np.flatnonzero(target_float < -1.0e-15)\n    else:\n        raise ValueError(f\"unknown artificial_row_mode: {artificial_row_mode}\")\n    art_count = int(len(artificial_rows))\n""",
    ),
    (
"""    x = np.array(sol.col_value[:real_cols], dtype=float)\n    z = np.array(sol.col_value[real_cols:real_cols + art_count], dtype=float)\n    row_dual = np.array(sol.row_dual, dtype=float)\n    col_dual = np.array(sol.col_dual[:real_cols], dtype=float)\n""",
"""    x = np.array(sol.col_value[:real_cols], dtype=float)\n    z = np.array(sol.col_value[real_cols:real_cols + art_count], dtype=float)\n    original_activity = mat.tocsr().dot(x)\n    original_violation = original_activity - target_float\n    row_dual = np.array(sol.row_dual, dtype=float)\n    col_dual = np.array(sol.col_dual[:real_cols], dtype=float)\n""",
    ),
    (
"""        \"real_nonzero\": int(np.sum(x > x_tol)),\n        \"artificial_rows\": art_count,\n        \"artificial_initial_sum\": float((-target_float[artificial_rows]).sum()) if art_count else 0.0,\n        \"artificial_nonzero\": int(np.sum(z > x_tol)),\n        \"artificial_max\": float(z.max()) if len(z) else 0.0,\n        \"artificial_sum\": float(z.sum()) if len(z) else 0.0,\n""",
"""        \"real_nonzero\": int(np.sum(x > x_tol)),\n        \"artificial_rows\": art_count,\n        \"artificial_row_mode\": artificial_row_mode,\n        \"artificial_initial_sum\": float(np.maximum(0.0, -target_float[artificial_rows]).sum()) if art_count else 0.0,\n        \"artificial_nonzero\": int(np.sum(z > x_tol)),\n        \"artificial_max\": float(z.max()) if len(z) else 0.0,\n        \"artificial_sum\": float(z.sum()) if len(z) else 0.0,\n        \"original_max_upper_violation\": float(original_violation.max()) if len(original_violation) else 0.0,\n        \"original_positive_violation_count\": int(np.sum(original_violation > 1.0e-7)),\n        \"original_p95_upper_violation\": float(np.percentile(original_violation, 95)) if len(original_violation) else 0.0,\n""",
    ),
    (
"""            verbose=args.verbose,\n            x_tol=args.x_tol,\n            solver=args.highspy_solver,\n        )\n""",
"""            verbose=args.verbose,\n            x_tol=args.x_tol,\n            solver=args.highspy_solver,\n            artificial_row_mode=args.phase1_artificial_rows,\n        )\n""",
    ),
    (
"""    ap.add_argument(\"--highspy-solver\", choices=[\"simplex\", \"ipm\"], default=\"simplex\")\n""",
"""    ap.add_argument(\"--highspy-solver\", choices=[\"simplex\", \"ipm\"], default=\"simplex\")\n    ap.add_argument(\"--phase1-artificial-rows\", choices=[\"all\", \"negative\"], default=\"all\")\n""",
    ),
]
for old, new in repls:
    if old not in text:
        raise SystemExit(f'missing patch anchor:\n{old}')
    text = text.replace(old, new, 1)
path.write_text(text)
