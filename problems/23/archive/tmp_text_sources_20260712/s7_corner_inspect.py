import sympy as sp
from pathlib import Path
ns = {}
exec(Path('tmp/s7_floor_f6_f7_simplex.py').read_text(), ns)
for name,builder in [('F6',ns['f6_base']),('F7',ns['f7_base'])]:
    target, base_vars, W, X, M0 = builder()
    sub = {v:0 for v in base_vars}
    expr = sp.factor(target.subs(sub))
    print(name, 'corner factor:', expr)
    print('as poly X:', sp.Poly(expr, X))
    print('as poly W:', sp.Poly(expr, W))
