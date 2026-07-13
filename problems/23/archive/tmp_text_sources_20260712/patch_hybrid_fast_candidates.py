from pathlib import Path
path = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_lp.py')
text = path.read_text(encoding='utf-8')
insert_after = '''def load_tier0_or_divide(
'''
fast_fn = '''def fast_candidate_multiplier_exps(
    poly: Poly,
    output_support: set[Exp],
    degree_cap: int,
    max_count: int | None,
) -> list[Exp]:
    """Fast set-equivalent derived candidate generator for hybrid builds.

    The quotient probe's default derived path scans every output-support term
    against every generator monomial.  Hybrid builds often have a very large
    output support and many families.  Here we enumerate the much smaller
    multiplier simplex and use O(1) support membership tests instead.  For
    uncapped runs this returns the same candidate set, sorted by the same
    grevlex order.  For capped diagnostic runs it takes the first sorted
    candidates rather than preserving the old support-scan discovery order.
    """

    if not output_support or not poly:
        return []
    num_vars = len(next(iter(output_support)))
    poly_exps = tuple(poly.keys())
    out: list[Exp] = []
    for mult in charts.exps_upto(num_vars, degree_cap):
        for pexp in poly_exps:
            if quotient.exp_add(pexp, mult) in output_support:
                out.append(mult)
                break
    out.sort(key=quotient.grevlex_key, reverse=True)
    if max_count is not None:
        out = out[:max_count]
    return out


'''
if fast_fn in text:
    raise SystemExit('fast function already present')
idx = text.index(insert_after)
text = text[:idx] + fast_fn + text[idx:]
old = '''    kept_qcols: list[quotient.QColumn] = []
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
'''
new = '''    kept_qcols: list[quotient.QColumn] = []
    old_candidate_fn = quotient.candidate_multiplier_exps
    if args.support == "derived":
        quotient.candidate_multiplier_exps = fast_candidate_multiplier_exps
    try:
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
    finally:
        quotient.candidate_multiplier_exps = old_candidate_fn
'''
if old not in text:
    raise SystemExit('kept_qcols construction block not found')
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
