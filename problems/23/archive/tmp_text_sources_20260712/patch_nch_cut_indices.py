from pathlib import Path
p = Path('problems/23/writeup/_codex_nch_weighted_blowup_hunt.py')
s = p.read_text(encoding='utf-8')
if '--cut-indices' not in s:
    s = s.replace('    ap.add_argument("--cut-limit", type=int, default=0, help="0 means all gamma-min connected cuts")\n', '    ap.add_argument("--cut-limit", type=int, default=0, help="0 means all gamma-min connected cuts")\n    ap.add_argument("--cut-indices", default="", help="comma-separated gamma-min cut indices to scan")\n')
    s = s.replace('    terminals = None if not args.terminals else [int(x) for x in args.terminals.split(",") if x.strip()]\n', '    terminals = None if not args.terminals else [int(x) for x in args.terminals.split(",") if x.strip()]\n    cut_indices = None if not args.cut_indices else {int(x) for x in args.cut_indices.split(",") if x.strip()}\n')
    s = s.replace('        for idx, (side_int, _side, st, gamma) in enumerate(structs):\n            if args.cut_limit and idx >= args.cut_limit:\n                break\n', '        for idx, (side_int, _side, st, gamma) in enumerate(structs):\n            if cut_indices is not None and idx not in cut_indices:\n                continue\n            if args.cut_limit and idx >= args.cut_limit:\n                break\n')
p.write_text(s, encoding='utf-8')
