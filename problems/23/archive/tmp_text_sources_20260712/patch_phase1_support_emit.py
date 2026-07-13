from pathlib import Path

p = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_cg.py')
s = p.read_text()
# Internal x for support extraction.
if '"_x": x,' not in s:
    s = s.replace(
        '        "_row_dual": row_dual,\n    }\n',
        '        "_row_dual": row_dual,\n        "_x": x,\n    }\n',
        1,
    )
# Add target writer helper before score_column.
if 'def write_target_beta(' not in s:
    marker = '\n\ndef score_column(col: hybrid.HybridColumn, row_dual: np.ndarray) -> float:\n'
    helper = r'''

def fraction_record(q):
    return {"num": q.numerator, "den": q.denominator}


def write_target_beta(path: Path, target_beta: list) -> None:
    rows = []
    for row, val in enumerate(target_beta):
        if val:
            rows.append({"row": int(row), **fraction_record(val)})
    payload = {"schema": "eq_odl1_rung2_custom_target_beta_v1", "row_count": len(target_beta), "target_beta_sparse": rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")
'''
    if marker not in s:
        raise SystemExit('missing score_column marker')
    s = s.replace(marker, helper + marker, 1)
# Add state variables after current_keys.
if 'last_support_indices: list[int] = []' not in s:
    s = s.replace(
        '    current_keys = {column_key(col) for col in current_cols}\n    iterations = []\n',
        '    current_keys = {column_key(col) for col in current_cols}\n    last_support_indices: list[int] = []\n    last_support_values: list[float] = []\n    iterations = []\n',
        1,
    )
# Pop x and record support.
if 'x_vec = phase1.pop("_x", None)' not in s:
    s = s.replace(
        '        row_dual = phase1.pop("_row_dual", None)\n        rec: dict[str, Any] = {\n',
        '        row_dual = phase1.pop("_row_dual", None)\n        x_vec = phase1.pop("_x", None)\n        if x_vec is not None:\n            support_pairs = [(idx, float(val)) for idx, val in enumerate(x_vec) if float(val) > args.support_tol]\n            last_support_indices = [idx for idx, _val in support_pairs]\n            last_support_values = [val for _idx, val in support_pairs]\n            phase1["support_count"] = len(last_support_indices)\n            phase1["support_value_sum"] = float(sum(last_support_values))\n        rec: dict[str, Any] = {\n',
        1,
    )
# Add emit before return; target exact location after loop before return.
if 'emitted_support_columns_json = None' not in s:
    s = s.replace(
        '    return {\n        "schema": "eq_odl1_rung2_hybrid_phase1_pricing_loop_v1",\n',
        '    emitted_support_columns_json = None\n    emitted_support_target_beta_json = None\n    if args.emit_support_columns_json and last_support_indices:\n        support_cols = [current_cols[i] for i in last_support_indices]\n        support_meta = dict(seed_meta)\n        support_meta["mode"] = "phase1_extracted_support"\n        support_meta["support_source_columns"] = len(current_cols)\n        support_meta["support_count"] = len(support_cols)\n        hybrid.write_columns(args.emit_support_columns_json, chart, args, support_cols, support_meta, len(betas))\n        emitted_support_columns_json = str(args.emit_support_columns_json)\n    if args.emit_support_target_beta_json:\n        write_target_beta(args.emit_support_target_beta_json, target_beta)\n        emitted_support_target_beta_json = str(args.emit_support_target_beta_json)\n\n    return {\n        "schema": "eq_odl1_rung2_hybrid_phase1_pricing_loop_v1",\n',
        1,
    )
# Add return fields.
if '"emitted_support_columns_json": emitted_support_columns_json,' not in s:
    s = s.replace(
        '        "iterations": iterations,\n        "seconds": time.monotonic() - t0,\n',
        '        "iterations": iterations,\n        "last_support_count": len(last_support_indices),\n        "last_support_value_sum": float(sum(last_support_values)),\n        "emitted_support_columns_json": emitted_support_columns_json,\n        "emitted_support_target_beta_json": emitted_support_target_beta_json,\n        "seconds": time.monotonic() - t0,\n',
        1,
    )
# Parser args.
if '--support-tol' not in s:
    s = s.replace(
        '    ap.add_argument("--x-tol", type=float, default=1.0e-9)\n',
        '    ap.add_argument("--x-tol", type=float, default=1.0e-9)\n    ap.add_argument("--support-tol", type=float, default=1.0e-8)\n    ap.add_argument("--emit-support-columns-json", type=Path, default=None)\n    ap.add_argument("--emit-support-target-beta-json", type=Path, default=None)\n',
        1,
    )
# Print fields.
if '"last_support_count": out.get("last_support_count"),' not in s:
    s = s.replace(
        '        "last_positive": None if "pricing" not in last else last["pricing"].get("positive_score_count"),\n        "summary": str(args.summary),\n',
        '        "last_positive": None if "pricing" not in last else last["pricing"].get("positive_score_count"),\n        "last_support_count": out.get("last_support_count"),\n        "emitted_support_columns_json": out.get("emitted_support_columns_json"),\n        "summary": str(args.summary),\n',
        1,
    )
p.write_text(s)
print('patched', p)
