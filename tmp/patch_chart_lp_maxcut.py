from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_lp.py')
s = p.read_text(encoding='utf-8')
if 'from _codex_seed_qmax_constraints import constraint as qmax_constraint' not in s:
    s = s.replace('import _codex_eq_cert2_odl_lp as old_lp\n', 'import _codex_eq_cert2_odl_lp as old_lp\nfrom _codex_seed_qmax_constraints import constraint as qmax_constraint, value as qmax_value\n')
insert = r'''

def maxcut_facet_exprs(mode: str) -> list[tuple[str, sp.Expr]]:
    if mode == "none":
        return []
    if mode not in {"tight", "all"}:
        raise ValueError(f"unknown maxcut facet mode {mode!r}")
    side = tuple(int(c) for c in old_lp.SIDE)
    ones = (1,) * 10
    out: list[tuple[str, sp.Expr]] = []
    seen = set()
    for mask in range(1, (1 << 10) - 1):
        if not (mask & 1):
            continue
        c = qmax_constraint(EQ, side, mask)
        if c is None:
            continue
        if mode == "tight" and qmax_value(c, ones) != 0:
            continue
        key = tuple(sorted(c.items()))
        if key in seen:
            continue
        seen.add(key)
        expr = sp.Integer(0)
        for (a, b), sign in c.items():
            expr += sign * old_lp.ws[a] * old_lp.ws[b]
        out.append((f"QMAX_{mask}", sp.expand(expr)))
    return out
'''
if 'def maxcut_facet_exprs' not in s:
    s = s.replace('\ndef build_chart(', insert + '\ndef build_chart(')
s = s.replace('def build_chart(chart: int) -> tuple[dict[tuple[int, ...], Fraction], list[Generator], dict[str, object]]:', 'def build_chart(chart: int, extra_maxcut: str = "none") -> tuple[dict[tuple[int, ...], Fraction], list[Generator], dict[str, object]]:')
s = s.replace('    raw_generators.extend(g_exprs())\n', '    raw_generators.extend(g_exprs())\n    raw_generators.extend(maxcut_facet_exprs(extra_maxcut))\n')
s = s.replace('        "chart": chart,\n        "target_terms_chart": len(target_hat),', '        "chart": chart,\n        "extra_maxcut": extra_maxcut,\n        "target_terms_chart": len(target_hat),')
s = s.replace('    target_hat, generators, meta = build_chart(chart)\n', '    target_hat, generators, meta = build_chart(chart, extra_maxcut=args.extra_maxcut if "args" in globals() else "none")\n')
# The previous replacement is not suitable inside solve_chart; fix it explicitly.
s = s.replace('def solve_chart(\n    chart: int,\n    support: str,', 'def solve_chart(\n    chart: int,\n    support: str,\n    extra_maxcut: str,')
s = s.replace('    target_hat, generators, meta = build_chart(chart, extra_maxcut=args.extra_maxcut if "args" in globals() else "none")', '    target_hat, generators, meta = build_chart(chart, extra_maxcut=extra_maxcut)')
s = s.replace('    ap.add_argument("--support", choices=["repair", "all"], default="repair")\n', '    ap.add_argument("--support", choices=["repair", "all"], default="repair")\n    ap.add_argument("--extra-maxcut", choices=["none", "tight", "all"], default="none")\n')
s = s.replace('        support=args.support,\n        max_columns_per_generator=limit,', '        support=args.support,\n        extra_maxcut=args.extra_maxcut,\n        max_columns_per_generator=limit,')
p.write_text(s, encoding='utf-8')
