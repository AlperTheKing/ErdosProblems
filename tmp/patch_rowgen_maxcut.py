from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_rowgen.py')
s = p.read_text(encoding='utf-8')
s = s.replace('    target, generators, meta = base.build_chart(args.chart)\n', '    target, generators, meta = base.build_chart(args.chart, extra_maxcut=args.extra_maxcut)\n')
s = s.replace('    ap.add_argument("--support", choices=["repair", "all"], default="repair")\n', '    ap.add_argument("--support", choices=["repair", "all"], default="repair")\n    ap.add_argument("--extra-maxcut", choices=["none", "tight", "all"], default="none")\n')
s = s.replace('        "support": args.support,\n        "dynamic_columns": bool(args.dynamic_columns),', '        "support": args.support,\n        "extra_maxcut": args.extra_maxcut,\n        "dynamic_columns": bool(args.dynamic_columns),')
p.write_text(s, encoding='utf-8')
