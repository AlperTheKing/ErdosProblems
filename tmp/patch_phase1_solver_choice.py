from pathlib import Path

p = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_cg.py')
s = p.read_text()
reps = [
    (
        '    x_tol: float,\n) -> dict[str, Any]:\n',
        '    x_tol: float,\n    solver: str,\n) -> dict[str, Any]:\n',
    ),
    (
        '    highs.setOptionValue("output_flag", bool(verbose))\n    highs.setOptionValue("solver", "simplex")\n',
        '    highs.setOptionValue("output_flag", bool(verbose))\n    highs.setOptionValue("solver", solver)\n',
    ),
    (
        '            x_tol=args.x_tol,\n        )\n',
        '            x_tol=args.x_tol,\n            solver=args.highspy_solver,\n        )\n',
    ),
    (
        '    ap.add_argument("--highspy-solver", choices=["simplex"], default="simplex")\n',
        '    ap.add_argument("--highspy-solver", choices=["simplex", "ipm"], default="simplex")\n',
    ),
]
for old, new in reps:
    if old not in s:
        raise SystemExit('missing pattern: ' + old[:120])
    s = s.replace(old, new, 1)
p.write_text(s)
print('patched', p)
