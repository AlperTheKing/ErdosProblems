from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_cg.py')
s = p.read_text()
s = s.replace(
    '    if args.emit_support_columns_json and last_support_indices:\n        support_cols = [current_cols[i] for i in last_support_indices]\n',
    '    if args.emit_support_columns_json and (last_support_indices or args.emit_all_current_columns):\n        if args.emit_all_current_columns:\n            support_cols = list(current_cols)\n        else:\n            support_cols = [current_cols[i] for i in last_support_indices]\n',
    1,
)
s = s.replace(
    '    ap.add_argument("--emit-support-columns-json", type=Path, default=None)\n    ap.add_argument("--emit-support-target-beta-json", type=Path, default=None)\n',
    '    ap.add_argument("--emit-support-columns-json", type=Path, default=None)\n    ap.add_argument("--emit-support-target-beta-json", type=Path, default=None)\n    ap.add_argument("--emit-all-current-columns", action="store_true")\n',
    1,
)
p.write_text(s)
print('patched', p)
