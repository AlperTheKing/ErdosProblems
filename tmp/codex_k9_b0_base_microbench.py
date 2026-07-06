import importlib.util, pathlib, sys, time
p = pathlib.Path('problems/23/writeup/_codex_eq_odl1_rung2_face_split_quotient_probe.py').resolve()
sys.path.insert(0, str(p.parent))
spec = importlib.util.spec_from_file_location('qp', p)
qp = importlib.util.module_from_spec(spec)
sys.modules['qp'] = qp
spec.loader.exec_module(qp)
chart = qp.charts.build_chart(9)
target = qp.homogenize_poly(chart.target, chart.variables, qp.TARGET_DEGREE)
gen_polys = [qp.homogenize_poly(expr, chart.variables, qp.GEN_DEGREE) for expr in chart.generators]
divisor, _, _ = qp.monic_normalize(gen_polys[7])
quo_p, rem_p = qp.divide_grevlex(target, divisor)
exps = qp.base_candidate_exps(side='face', degree=qp.TARGET_DEGREE, divisor=divisor, rem_support=set(rem_p), quo_support=set(quo_p), support_mode='all', num_vars=len(chart.variables))
print('candidates', len(exps), 'divisor_terms', len(divisor))
for n in [1,5,10,25,50,100]:
    t=time.monotonic(); cols=[]
    for exp in exps[:n]:
        cols.append(qp.qcolumn(side='face', kind='face_base', name='B11', multiplier_exp=exp, poly=qp.bernstein_basis_poly(qp.TARGET_DEGREE, exp), divisor=divisor))
    dt=time.monotonic()-t
    avg_terms=sum(len(c.rem)+len(c.quo) for c in cols)/len(cols)
    print('n',n,'sec',round(dt,3),'per',round(dt/n,4),'avg_terms',round(avg_terms,1),'last_terms',len(cols[-1].rem)+len(cols[-1].quo))
