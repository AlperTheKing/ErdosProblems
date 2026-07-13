from pathlib import Path
p = Path('problems/23/writeup/_codex_eq_cert2_chart_rowgen.py')
s = p.read_text(encoding='utf-8')
s = s.replace('import clarabel\n', '') if 'import clarabel\n' in s else s
s = s.replace('from pathlib import Path\n\nfrom scipy.optimize import linprog\nfrom scipy.sparse import coo_matrix\n', 'from pathlib import Path\n\nimport clarabel\nimport numpy as np\nfrom scipy.optimize import linprog\nfrom scipy.sparse import csc_matrix, coo_matrix, eye, vstack\n')
marker = '\ndef run(args):\n'
insert = r'''

def solve_lp(matrix, rhs, objective, method, oracle, time_limit, threads):
    if oracle == "scipy":
        return solve_lp_scipy(matrix, rhs, objective, method, time_limit, threads)
    if oracle == "clarabel":
        return solve_lp_clarabel(matrix, rhs, objective, time_limit, threads)
    raise ValueError(f"unknown oracle {oracle!r}")


def solve_lp_scipy(matrix, rhs, objective, method, time_limit, threads):
    options = {
        k: v
        for k, v in {
            "time_limit": time_limit if time_limit > 0 else None,
            "threads": threads if threads > 0 else None,
        }.items()
        if v is not None
    }
    return linprog(
        c=[0.0 if objective == "zero" else 1.0] * matrix.shape[1],
        A_ub=matrix,
        b_ub=rhs,
        bounds=[(0, None)] * matrix.shape[1],
        method=method,
        options=options,
    )


def solve_lp_clarabel(matrix, rhs, objective, time_limit, threads):
    n = matrix.shape[1]
    a_stack = vstack([matrix, -eye(n, format="csr")], format="csc")
    b_stack = np.array([*rhs, *([0.0] * n)], dtype=float)
    q = np.array([0.0 if objective == "zero" else 1.0] * n, dtype=float)
    p_mat = csc_matrix((n, n), dtype=float)
    cones = [clarabel.NonnegativeConeT(a_stack.shape[0])]
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    if time_limit > 0:
        settings.time_limit = time_limit
    if threads > 0:
        settings.max_threads = threads
    solver = clarabel.DefaultSolver(p_mat, q, a_stack, b_stack, cones, settings)
    sol = solver.solve()

    class Result:
        pass

    res = Result()
    status = str(sol.status)
    res.status = 0 if status in {"Solved", "AlmostSolved"} else 1
    res.message = status
    res.success = res.status == 0
    res.x = np.array(sol.x, dtype=float)
    return res
'''
if insert.strip() not in s:
    s = s.replace(marker, insert + marker)
old = '''        res = linprog(
            c=[0.0 if args.objective == "zero" else 1.0] * len(columns),
            A_ub=matrix,
            b_ub=rhs,
            bounds=[(0, None)] * len(columns),
            method=args.method,
            options={k: v for k, v in {"time_limit": args.time_limit if args.time_limit > 0 else None, "threads": args.threads if args.threads > 0 else None}.items() if v is not None},
        )'''
new = '''        res = solve_lp(matrix, rhs, args.objective, args.method, args.oracle, args.time_limit, args.threads)'''
if old not in s:
    raise SystemExit('old linprog block not found')
s = s.replace(old, new)
s = s.replace('            "iteration": iteration,\n            "rows": len(row_mons),', '            "iteration": iteration,\n            "oracle": args.oracle,\n            "rows": len(row_mons),')
s = s.replace('    ap.add_argument("--time-limit", type=float, default=60.0)\n    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")', '    ap.add_argument("--time-limit", type=float, default=60.0)\n    ap.add_argument("--oracle", choices=["scipy", "clarabel"], default="scipy")\n    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")')
p.write_text(s, encoding='utf-8')
