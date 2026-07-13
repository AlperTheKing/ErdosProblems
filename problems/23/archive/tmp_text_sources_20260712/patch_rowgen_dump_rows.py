from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_rowgen.py')
s = p.read_text(encoding='utf-8')
s = s.replace('    row_set = {mon for mon, coeff in target.items() if coeff < 0}\n', '    if args.seed_rows:\n        seed_data = json.loads(Path(args.seed_rows).read_text(encoding="utf-8"))\n        row_set = {tuple(int(v) for v in row) for row in seed_data["rows"]}\n    else:\n        row_set = {mon for mon, coeff in target.items() if coeff < 0}\n')
s = s.replace('                "final": "LP_FAIL",\n            }', '                "active_rows": [list(row) for row in row_mons] if args.dump_rows else None,\n                "final": "LP_FAIL",\n            }')
s = s.replace('    ap.add_argument("--dynamic-columns", action="store_true")\n', '    ap.add_argument("--dynamic-columns", action="store_true")\n    ap.add_argument("--seed-rows", default="")\n    ap.add_argument("--dump-rows", action="store_true")\n')
p.write_text(s, encoding='utf-8')
