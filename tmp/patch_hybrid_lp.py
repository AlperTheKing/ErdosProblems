from pathlib import Path
path = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_lp.py')
text = path.read_text(encoding='utf-8')
old = '''    qcols = quotient.build_columns(
        chart,
        args.dominant,
        args.band,
        args.tier,
        args.support,
        0,  # no explicit face/lift base cap; filtering below removes face_base only
        None if args.max_pairs_per_family == 0 else args.max_pairs_per_family,
        None if args.max_band_columns == 0 else args.max_band_columns,
        quotient.parse_family_filter(args.face_pair_families),
        divisor,
        rem_p,
        quo_p,
        progress=args.verbose,
        progress_t0=t0,
    )
    kept_qcols = [col for col in qcols if col.kind != "face_base"]
    skipped_face_base = len(qcols) - len(kept_qcols)
'''
new = '''    rem_support = set(rem_p)
    quo_support = set(quo_p)
    face_product_support = set(rem_p)
    for qe in quo_p:
        for de in divisor:
            face_product_support.add(quotient.exp_add(qe, de))
    face_pair_cap, face_band_cap, lift_gen_cap, lift_band_cap = quotient.tier_caps(args.tier)
    num_vars = len(chart.variables)
    family_filter = quotient.parse_family_filter(args.face_pair_families)
    max_pairs = None if args.max_pairs_per_family == 0 else args.max_pairs_per_family
    max_band = None if args.max_band_columns == 0 else args.max_band_columns

    # The hybrid formulation eliminates face_base entirely; do not construct
    # those expensive divided Bernstein columns only to filter them away.
    kept_qcols: list[quotient.QColumn] = []
    kept_qcols.extend(
        quotient.make_face_pair_columns(
            gen_polys=gen_polys,
            gen_names=chart.generator_names,
            dominant=args.dominant,
            degree_cap=face_pair_cap,
            divisor=divisor,
            rem_support=rem_support,
            quo_support=quo_support,
            support_mode=args.support,
            max_pairs_per_family=max_pairs,
            face_pair_family_filter=family_filter,
            num_vars=num_vars,
            face_product_support=face_product_support,
            progress=args.verbose,
            progress_t0=t0,
        )
    )
    kept_qcols.extend(
        quotient.make_band_columns(
            side="face",
            band=args.band,
            band_degree=face_band_cap,
            divisor=divisor,
            rem_support=rem_support,
            quo_support=quo_support,
            support_mode=args.support,
            max_columns=max_band,
            num_vars=num_vars,
            output_support=face_product_support,
            progress=args.verbose,
            progress_t0=t0,
        )
    )
    kept_qcols.extend(
        quotient.make_base_columns(
            side="lift",
            degree=9,
            divisor=divisor,
            rem_support=set(),
            quo_support=quo_support,
            support_mode=args.support,
            max_columns=None,
            num_vars=num_vars,
            progress=args.verbose,
            progress_t0=t0,
        )
    )
    kept_qcols.extend(
        quotient.make_lift_gen_columns(
            gen_polys=gen_polys,
            gen_names=chart.generator_names,
            dominant=args.dominant,
            degree_cap=lift_gen_cap,
            divisor=divisor,
            quo_support=quo_support,
            support_mode=args.support,
            max_columns_per_family=max_pairs,
            num_vars=num_vars,
            progress=args.verbose,
            progress_t0=t0,
        )
    )
    kept_qcols.extend(
        quotient.make_band_columns(
            side="lift",
            band=args.band,
            band_degree=lift_band_cap,
            divisor=divisor,
            rem_support=set(),
            quo_support=quo_support,
            support_mode=args.support,
            max_columns=max_band,
            num_vars=num_vars,
            output_support=quo_support,
            progress=args.verbose,
            progress_t0=t0,
        )
    )
    skipped_face_base = len(charts.all_exps(num_vars, quotient.TARGET_DEGREE))
'''
if old not in text:
    raise SystemExit('old build_columns block not found')
text = text.replace(old, new)
text = text.replace('def write_columns(path: Path, chart: charts.ChartData, args: argparse.Namespace, columns: list[HybridColumn], meta: dict[str, Any]) -> None:', 'def write_columns(path: Path, chart: charts.ChartData, args: argparse.Namespace, columns: list[HybridColumn], meta: dict[str, Any], row_count: int) -> None:')
old2 = '''        "row_count": charts.multinomial(quotient.TARGET_DEGREE + len(chart.variables) - 1, (quotient.TARGET_DEGREE,) + (0,) * (len(chart.variables) - 1)),
'''
new2 = '''        "row_count": row_count,
'''
if old2 not in text:
    raise SystemExit('old row_count line not found')
text = text.replace(old2, new2)
old3 = '''    # The row_count formula above is not the number of simplex exponents; set it
    # directly from the maximum row plus one for safety.
    payload["row_count"] = max((row for col in columns for row, _ in col.terms), default=-1) + 1
    path.parent.mkdir(parents=True, exist_ok=True)
'''
new3 = '''    path.parent.mkdir(parents=True, exist_ok=True)
'''
if old3 not in text:
    raise SystemExit('old row_count override block not found')
text = text.replace(old3, new3)
text = text.replace('write_columns(args.emit_columns_json, chart, args, columns, meta)', 'write_columns(args.emit_columns_json, chart, args, columns, meta, len(betas))')
path.write_text(text, encoding='utf-8')
