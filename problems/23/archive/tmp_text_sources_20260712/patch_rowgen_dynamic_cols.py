from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_rowgen.py')
s = p.read_text(encoding='utf-8')
insert = r'''

def repair_columns_for_rows(row_set, generators, max_columns_per_generator):
    seen = set()
    columns = []
    counts = [0] * len(generators)
    for gi, gen in enumerate(generators):
        beta_degree = base.TARGET_DEGREE - gen.degree
        gen_negative = [exp for exp, coeff in gen.terms.items() if coeff < 0]
        for target_exp in sorted(row_set):
            for gen_exp in gen_negative:
                beta = base.sub_exp(target_exp, gen_exp)
                if beta is None or sum(beta) != beta_degree:
                    continue
                key = (gi, beta)
                if key in seen:
                    continue
                seen.add(key)
                columns.append(base.Column(gi, beta, base.multinomial(beta_degree, beta)))
                counts[gi] += 1
                if max_columns_per_generator is not None and counts[gi] >= max_columns_per_generator:
                    break
            if max_columns_per_generator is not None and counts[gi] >= max_columns_per_generator:
                break
    return columns
'''
if 'def repair_columns_for_rows' not in s:
    s = s.replace('\ndef run(args):\n', insert + '\ndef run(args):\n')
old = '''    columns = base.repair_columns(target, generators, args.support, args.max_columns_per_generator or None)
    term_maps = [base.column_terms(col, generators[col.gen_index]) for col in columns]
    all_mons = sorted(set(target) | set().union(*(set(mp) for mp in term_maps)))
    row_set = {mon for mon, coeff in target.items() if coeff < 0}
    history = []
    solution = None

    for iteration in range(args.iterations):
        row_mons = sorted(row_set)
        matrix, rhs = build_scaled_matrix(row_mons, columns, term_maps, target)
'''
new = '''    max_cols_per_gen = args.max_columns_per_generator or None
    row_set = {mon for mon, coeff in target.items() if coeff < 0}
    if args.dynamic_columns:
        columns = []
        term_maps = []
        all_mons = sorted(target)
    else:
        columns = base.repair_columns(target, generators, args.support, max_cols_per_gen)
        term_maps = [base.column_terms(col, generators[col.gen_index]) for col in columns]
        all_mons = sorted(set(target) | set().union(*(set(mp) for mp in term_maps)))
    history = []
    solution = None

    for iteration in range(args.iterations):
        if args.dynamic_columns:
            columns = repair_columns_for_rows(row_set, generators, max_cols_per_gen)
            term_maps = [base.column_terms(col, generators[col.gen_index]) for col in columns]
            all_mons = sorted(set(target) | set().union(*(set(mp) for mp in term_maps)))
        row_mons = sorted(row_set)
        matrix, rhs = build_scaled_matrix(row_mons, columns, term_maps, target)
'''
if old not in s:
    raise SystemExit('run init block not found')
s = s.replace(old, new)
s = s.replace('            "columns": len(columns),\n            "nonzeros": int(matrix.nnz),', '            "columns": len(columns),\n            "dynamic_columns": bool(args.dynamic_columns),\n            "nonzeros": int(matrix.nnz),')
s = s.replace('    ap.add_argument("--max-columns-per-generator", type=int, default=0)\n    ap.add_argument("--iterations", type=int, default=6)', '    ap.add_argument("--max-columns-per-generator", type=int, default=0)\n    ap.add_argument("--dynamic-columns", action="store_true")\n    ap.add_argument("--iterations", type=int, default=6)')
s = s.replace('        "support": args.support,\n        "meta": meta,', '        "support": args.support,\n        "dynamic_columns": bool(args.dynamic_columns),\n        "meta": meta,')
p.write_text(s, encoding='utf-8')
