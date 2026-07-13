import importlib.util, sympy as sp
p='problems/23/writeup/_codex_sib_s7_y1_u1_s4_b_family_probe.py'
spec=importlib.util.spec_from_file_location('bfam', p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
V,H,R,Q=sp.symbols('V H R Q')
X=V+H; x=1+X; v=1+V
s_max=sp.factor((x+1)*(v-1)/2); s=R*s_max
a,c,f,K=m.b_family_values(x,v,s,Q)
expr=sp.factor(m.phi_expr(a,c,sp.Integer(1),c,f,x,v).subs(H,0))
print('BOUNDARY_EXPR', expr)
for Vv in [sp.Rational(1,10), sp.Rational(1,2), sp.Integer(1), sp.Integer(2), sp.Integer(5)]:
  for Rv in [sp.Rational(0), sp.Rational(1,4), sp.Rational(1,2), sp.Rational(3,4), sp.Rational(1)]:
    for Qv in [sp.Rational(0), sp.Rational(1,4), sp.Rational(1,2), sp.Rational(3,4), sp.Rational(1)]:
      val=sp.factor(expr.subs({V:Vv,R:Rv,Q:Qv}))
      if val < 0:
        print('NEG_VALUE', Vv, Rv, Qv, val)
        raise SystemExit
print('GRID_NO_NEG')