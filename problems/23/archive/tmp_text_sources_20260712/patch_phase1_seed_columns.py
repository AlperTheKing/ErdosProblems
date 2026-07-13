from pathlib import Path
path = Path(r'E:\Projects\ErdosProblems\problems\23\writeup\_codex_eq_odl1_rung2_hybrid_cg.py')
text = path.read_text()
if 'from fractions import Fraction\n' not in text:
    text = text.replace('import time\nfrom pathlib import Path\n', 'import time\nfrom fractions import Fraction\nfrom pathlib import Path\n', 1)
insert_after = """def build_matrix(columns: list[hybrid.HybridColumn], row_count: int) -> coo_matrix:\n    return hybrid.build_matrix(columns, row_count)\n\n\n"""
new_func = """def parse_column_json_kind(kind: str) -> tuple[str, str]:\n    for side in (\"face\", \"lift\"):\n        prefix = f\"{side}_\"\n        if kind.startswith(prefix):\n            return side, kind[len(prefix):]\n    return \"custom\", kind\n\n\ndef read_seed_columns_json(path: Path, expected_row_count: int) -> tuple[list[hybrid.HybridColumn], dict[str, Any]]:\n    data = json.loads(path.read_text(encoding=\"utf-8\"))\n    row_count = int(data.get(\"row_count\", -1))\n    if row_count != expected_row_count:\n        raise ValueError(f\"seed row_count {row_count} != expected {expected_row_count}\")\n    columns: list[hybrid.HybridColumn] = []\n    for cidx, rec in enumerate(data.get(\"columns\", [])):\n        side, kind = parse_column_json_kind(str(rec.get(\"kind\", \"\")))\n        terms = []\n        for term in rec.get(\"terms\", []):\n            row = int(term[\"row\"])\n            if row < 0 or row >= expected_row_count:\n                raise ValueError(f\"seed column {cidx} has row out of range: {row}\")\n            terms.append((row, Fraction(int(term[\"num\"]), int(term[\"den\"]))))\n        columns.append(\n            hybrid.HybridColumn(\n                side=side,\n                kind=kind,\n                name=str(rec.get(\"name\", \"\")),\n                multiplier_exp=tuple(int(x) for x in rec.get(\"multiplier_exp\", [])),\n                terms=tuple(sorted(terms)),\n            )\n        )\n    return columns, data\n\n\n"""
if new_func.strip() not in text:
    if insert_after not in text:
        raise SystemExit('missing build_matrix insertion anchor')
    text = text.replace(insert_after, insert_after + new_func, 1)
old = """    chart, betas, target_beta, current_cols, seed_meta = build_columns(\n        args,\n        max_pairs=args.seed_max_pairs,\n        max_band=args.seed_max_band,\n    )\n    log(f\"seed columns={len(current_cols)} rows={len(betas)}\")\n"""
new = """    chart, betas, target_beta, current_cols, seed_meta = build_columns(\n        args,\n        max_pairs=args.seed_max_pairs,\n        max_band=args.seed_max_band,\n    )\n    if args.seed_columns_json:\n        current_cols, seed_payload = read_seed_columns_json(args.seed_columns_json, len(betas))\n        seed_meta = dict(seed_payload.get(\"meta\", {}))\n        seed_meta[\"seed_columns_json\"] = str(args.seed_columns_json)\n        log(f\"loaded seed columns from {args.seed_columns_json} count={len(current_cols)}\")\n    log(f\"seed columns={len(current_cols)} rows={len(betas)}\")\n"""
if old not in text:
    raise SystemExit('missing seed replacement anchor')
text = text.replace(old, new, 1)
if 'current_keys = {column_key(col) for col in current_cols}' not in text:
    old_iter = """    iterations = []\n"""
    if old_iter not in text:
        raise SystemExit('missing iterations anchor')
    text = text.replace(old_iter, "    current_keys = {column_key(col) for col in current_cols}\n\n" + old_iter, 1)
old_arg = '    ap.add_argument("--seed-max-band", type=int, default=4096)\n'
new_arg = old_arg + '    ap.add_argument("--seed-columns-json", type=Path, default=None)\n'
if '--seed-columns-json' not in text:
    if old_arg not in text:
        raise SystemExit('missing seed arg anchor')
    text = text.replace(old_arg, new_arg, 1)
path.write_text(text)
