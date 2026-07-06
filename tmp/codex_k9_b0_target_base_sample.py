import importlib.util, pathlib, sys, time
p = pathlib.Path('problems/23/writeup/_codex_eq_odl1_rung2_face_split_quotient_probe.py').resolve()
sys.path.insert(0, str(p.parent))
spec = importlib.util.spec_from_file_location('qp', p)
qp = importlib.util.module_from_spec(spec); sys.modules['qp'] = qp; spec.loader.exec_module(qp)
chart = qp.charts.build_chart(9)
target = qp.homogenize_poly(chart.target, chart.variables, qp.TARGET_DEGREE)
gen_polys = [qp.homogenize_poly(expr, chart.variables, qp.GEN_DEGREE) for expr in chart.generators]
divisor, _, _ = qp.monic_normalize(gen_polys[7])
quo_p, rem_p = qp.divide_grevlex(target, divisor)
for mode in ['target','derived']:
    exps = qp.base_candidate_exps(side='face', degree=qp.TARGET_DEGREE, divisor=divisor, rem_support=set(rem_p), quo_support=set(quo_p), support_mode=mode, num_vars=len(chart.variables))
    print('mode',mode,'candidates',len(exps),'contains_slow',(10,1,0,0,0,0,0,0,0,0) in exps, flush=True)
    for idx in [0,1,2,3,4,5,10,20,50,100]:
        if idx >= len(exps): continue
        exp=exps[idx]
        t=time.monotonic()
        col=qp.qcolumn(side='face', kind='face_base', name='B11', multiplier_exp=exp, poly=qp.bernstein_basis_poly(qp.TARGET_DEGREE, exp), divisor=divisor)
        dt=time.monotonic()-t
        print('mode',mode,'idx',idx,'exp',exp,'sec',round(dt,4),'terms',len(col.rem)+len(col.quo), flush=True)
        if dt > 5:
            print('slow_break', flush=True)
            break
