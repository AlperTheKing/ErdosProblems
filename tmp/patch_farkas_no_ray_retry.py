from pathlib import Path

p = Path('problems/23/writeup/_codex_eq_odl1_rung2_hybrid_farkas_price.py')
s = p.read_text()
reps = [
    (
        '    if args.solver_threads > 0:\n        highs.setOptionValue("threads", int(args.solver_threads))\n\n    status = highs.passModel(lp)\n',
        '    if args.solver_threads > 0:\n        highs.setOptionValue("threads", int(args.solver_threads))\n    if getattr(args, "presolve_off", False):\n        highs.setOptionValue("presolve", "off")\n\n    status = highs.passModel(lp)\n',
    ),
    (
        '        log(f"iteration={it} solving feasibility nnz={mat.nnz}")\n        feas = solve_feasibility(mat, target_beta, args)\n        ray = feas.pop("_ray", None)\n',
        '        log(f"iteration={it} solving feasibility nnz={mat.nnz}")\n        feas = solve_feasibility(mat, target_beta, args)\n        ray = feas.pop("_ray", None)\n        if (\n            args.retry_no_ray_presolve_off\n            and feas.get("message") == "Infeasible"\n            and not feas.get("dual_ray_exists", False)\n        ):\n            log(f"iteration={it} retrying no-ray infeasibility with presolve off")\n            old_presolve_off = getattr(args, "presolve_off", False)\n            args.presolve_off = True\n            retry = solve_feasibility(mat, target_beta, args)\n            retry_ray = retry.pop("_ray", None)\n            retry["retry_presolve_off"] = True\n            retry["initial_no_ray_feasibility"] = feas\n            args.presolve_off = old_presolve_off\n            feas = retry\n            ray = retry_ray\n',
    ),
    (
        '    ap.add_argument("--price-tol", type=float, default=1.0e-8)\n',
        '    ap.add_argument("--price-tol", type=float, default=1.0e-8)\n    ap.add_argument("--presolve-off", action="store_true")\n    ap.add_argument("--retry-no-ray-presolve-off", action="store_true")\n',
    ),
]
for old, new in reps:
    if old not in s:
        raise SystemExit('missing pattern: ' + old[:120])
    s = s.replace(old, new, 1)
p.write_text(s)
print('patched', p)
