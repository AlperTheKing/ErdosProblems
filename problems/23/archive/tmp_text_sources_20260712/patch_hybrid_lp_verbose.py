from pathlib import Path
path = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_lp.py')
text = path.read_text(encoding='utf-8')
text = text.replace('''def load_tier0_or_divide(
    args: argparse.Namespace,
    chart: charts.ChartData,
    divisor: Poly,
    target_beta: list[Fraction],
    betas: list[Exp],
) -> tuple[Poly, Poly, dict[str, Any]]:
    if args.tier0_json:
        payload = json.loads(args.tier0_json.read_text(encoding="utf-8"))
''','''def load_tier0_or_divide(
    args: argparse.Namespace,
    chart: charts.ChartData,
    divisor: Poly,
    target_beta: list[Fraction],
    betas: list[Exp],
) -> tuple[Poly, Poly, dict[str, Any]]:
    if args.tier0_json:
        if args.verbose:
            print(f"phase=tier0_reuse read_start path={args.tier0_json}", flush=True)
        payload = json.loads(args.tier0_json.read_text(encoding="utf-8"))
        if args.verbose:
            print("phase=tier0_reuse read_done", flush=True)
''')
text = text.replace('''        return (
            quotient.poly_from_terms_record(payload["remP_terms"]),  # type: ignore[index]
            quotient.poly_from_terms_record(payload["quoP_terms"]),  # type: ignore[index]
            {"target_mode": payload.get("target_mode", "chart_target"), "tier0_json": str(args.tier0_json)},
        )
''','''        if args.verbose:
            print("phase=tier0_reuse parse_terms_start", flush=True)
        rem_p = quotient.poly_from_terms_record(payload["remP_terms"])  # type: ignore[index]
        quo_p = quotient.poly_from_terms_record(payload["quoP_terms"])  # type: ignore[index]
        if args.verbose:
            print(f"phase=tier0_reuse parse_terms_done rem_terms={len(rem_p)} quo_terms={len(quo_p)}", flush=True)
        return (
            rem_p,
            quo_p,
            {"target_mode": payload.get("target_mode", "chart_target"), "tier0_json": str(args.tier0_json)},
        )
''')
old = '''    t0 = time.monotonic()
    chart = charts.build_chart(args.chart)
    betas = charts.all_exps(len(chart.variables), quotient.TARGET_DEGREE)
    beta_index = {beta: i for i, beta in enumerate(betas)}
    target_beta = read_target_beta(args, chart, betas)

    gen_polys = [quotient.homogenize_poly(expr, chart.variables, quotient.GEN_DEGREE) for expr in chart.generators]
    divisor_raw = gen_polys[args.dominant]
    divisor, lead_exp, lead_coeff = quotient.monic_normalize(divisor_raw)
    rem_p, quo_p, target_meta = load_tier0_or_divide(args, chart, divisor, target_beta, betas)
'''
new = '''    t0 = time.monotonic()
    if args.verbose:
        print("phase=hybrid_build chart_start", flush=True)
    chart = charts.build_chart(args.chart)
    if args.verbose:
        print(f"phase=hybrid_build chart_done seconds={time.monotonic() - t0:.3f}", flush=True)
    betas = charts.all_exps(len(chart.variables), quotient.TARGET_DEGREE)
    beta_index = {beta: i for i, beta in enumerate(betas)}
    if args.verbose:
        print(f"phase=hybrid_build target_beta_start rows={len(betas)}", flush=True)
    target_beta = read_target_beta(args, chart, betas)
    if args.verbose:
        print(f"phase=hybrid_build target_beta_done seconds={time.monotonic() - t0:.3f}", flush=True)

    if args.verbose:
        print("phase=hybrid_build gen_hom_start", flush=True)
    gen_polys = [quotient.homogenize_poly(expr, chart.variables, quotient.GEN_DEGREE) for expr in chart.generators]
    divisor_raw = gen_polys[args.dominant]
    divisor, lead_exp, lead_coeff = quotient.monic_normalize(divisor_raw)
    if args.verbose:
        print(f"phase=hybrid_build gen_hom_done seconds={time.monotonic() - t0:.3f}", flush=True)
    rem_p, quo_p, target_meta = load_tier0_or_divide(args, chart, divisor, target_beta, betas)
    if args.verbose:
        print(f"phase=hybrid_build target_division_ready seconds={time.monotonic() - t0:.3f}", flush=True)
'''
if old not in text:
    raise SystemExit('build_hybrid_columns prelude block not found')
text = text.replace(old, new)
text = text.replace('''    columns: list[HybridColumn] = []
    term_count = 0
''','''    if args.verbose:
        print(f"phase=hybrid_convert start qcols={len(kept_qcols)} seconds={time.monotonic() - t0:.3f}", flush=True)
    columns: list[HybridColumn] = []
    term_count = 0
''')
text = text.replace('''    meta = {
        **target_meta,
''','''    if args.verbose:
        print(f"phase=hybrid_convert done columns={len(columns)} terms={term_count} seconds={time.monotonic() - t0:.3f}", flush=True)

    meta = {
        **target_meta,
''')
text = text.replace('''    mat = build_matrix(columns, len(betas))
    solve: dict[str, Any]
''','''    if args.verbose:
        print(f"phase=matrix_build start columns={len(columns)}", flush=True)
    mat = build_matrix(columns, len(betas))
    if args.verbose:
        print(f"phase=matrix_build done rows={len(betas)} cols={len(columns)} nnz={mat.nnz}", flush=True)
    solve: dict[str, Any]
''')
path.write_text(text, encoding='utf-8')
