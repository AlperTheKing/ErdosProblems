import importlib.util, sympy as sp
from math import comb
p='problems/23/writeup/_codex_sib_s7_y1_u1_s4_b_family_probe.py'
spec=importlib.util.spec_from_file_location('bfam', p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
V,H,R,Q,D,E = sp.symbols('V H R Q D E', nonnegative=True)
X=V+H; x=1+X; v=1+V
s_max=sp.factor((x+1)*(v-1)/2); s=R*s_max
a,c,f,K=m.b_family_values(x,v,s,Q)
expr=m.phi_expr(a,c,1+D,c+E,f,x,v)
num,_=sp.together(expr).as_numer_denom()
coeffs=[num]
for var in (R,Q):
    nxt=[]
    for coeff in coeffs:
        nxt.extend(m.bernstein_coeffs(coeff,var))
    coeffs=nxt
for idx, coeff in enumerate(coeffs):
    n,dn=sp.together(coeff).as_numer_denom()
    poly=sp.Poly(n,V,H,D,E)
    neg=[]
    for monom, coef in poly.terms():
        if coef < 0:
            neg.append((monom, coef))
    if neg:
        print('FIRST_NEG_BERNSTEIN_INDEX', idx)
        print('NEG_COUNT', len(neg))
        print('NEG_TERMS', neg[:20])
        print('DEN', sp.factor(dn))
        break
else:
    print('NO_NEG')