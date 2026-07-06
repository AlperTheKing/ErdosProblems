import importlib.util, pathlib, sys, time
from fractions import Fraction
from functools import lru_cache
p = pathlib.Path('problems/23/writeup/_codex_eq_odl1_rung2_face_split_quotient_probe.py').resolve()
sys.path.insert(0, str(p.parent))
spec = importlib.util.spec_from_file_location('qp', p)
qp = importlib.util.module_from_spec(spec); sys.modules['qp'] = qp; spec.loader.exec_module(qp)
chart = qp.charts.build_chart(9)
target = qp.homogenize_poly(chart.target, chart.variables, qp.TARGET_DEGREE)
gen_polys = [qp.homogenize_poly(expr, chart.variables, qp.GEN_DEGREE) for expr in chart.generators]
divisor, _raw_lead_exp, _raw_lead_coeff = qp.monic_normalize(gen_polys[7])
lead_exp, lead_coeff = qp.leading_term(divisor)
assert lead_coeff == 1
quo_p, rem_p = qp.divide_grevlex(target, divisor)
exps = qp.base_candidate_exps(side='face', degree=qp.TARGET_DEGREE, divisor=divisor, rem_support=set(rem_p), quo_support=set(quo_p), support_mode='target', num_vars=len(chart.variables))
slow = exps[1]
rest = tuple((e,c) for e,c in divisor.items() if e != lead_exp)

def add_scaled(out, items, scale):
    for e,c in items:
        v = out.get(e, Fraction(0)) + scale*c
        if v: out[e]=v
        elif e in out: del out[e]

@lru_cache(maxsize=None)
def div_unit(exp):
    if not qp.exp_divides(exp, lead_exp):
        return (), ((exp, Fraction(1)),)
    shift = qp.exp_sub(exp, lead_exp)
    q = {shift: Fraction(1)}
    r = {}
    for de, dc in rest:
        out_exp = qp.exp_add(de, shift)
        q2, r2 = div_unit(out_exp)
        add_scaled(q, q2, -dc)
        add_scaled(r, r2, -dc)
    return tuple(sorted(q.items(), key=lambda item: qp.grevlex_key(item[0]), reverse=True)), tuple(sorted(r.items(), key=lambda item: qp.grevlex_key(item[0]), reverse=True))

print('slow', slow, flush=True)
t=time.monotonic(); q1,r1=qp.divide_grevlex(qp.bernstein_basis_poly(qp.TARGET_DEGREE, slow), divisor); dt1=time.monotonic()-t; print('heap', dt1, len(q1), len(r1), flush=True)
coeff = qp.bernstein_basis_poly(qp.TARGET_DEGREE, slow)[slow]
t=time.monotonic(); q2t,r2t=div_unit(slow); dt2=time.monotonic()-t
q2 = {e:c*coeff for e,c in q2t}; r2={e:c*coeff for e,c in r2t}
print('cached', dt2, len(q2), len(r2), 'cache', div_unit.cache_info(), 'match', q1==q2 and r1==r2, flush=True)
# now a few adjacent exps after cache warm
for idx in [2,3,4,5,10]:
    exp=exps[idx]; coeff=qp.bernstein_basis_poly(qp.TARGET_DEGREE, exp)[exp]
    t=time.monotonic(); q,r=div_unit(exp); dt=time.monotonic()-t
    print('idx',idx,'sec_cached_unit',dt,'terms',len(q)+len(r),'cache',div_unit.cache_info(), flush=True)
