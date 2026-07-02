from __future__ import annotations
from itertools import product
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def monoms(n, deg):
    def rec(i,left,cur):
        if i==n: yield tuple(cur); return
        for k in range(left+1): cur.append(k); yield from rec(i+1,left-k,cur); cur.pop()
    yield from rec(0,deg,[])
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def total(m): return sum(m)
def pterms(expr, vars_): return {tuple(m): float(c) for m,c in sp.Poly(sp.expand(expr),*vars_).terms()}

def probe(cap_name, deg):
    a,b,c,d,e,f=sp.symbols('a b c d e f', positive=True); vars_=(a,b,c,d,e,f)
    x=sp.Integer(1); y=sp.Integer(1); v=sp.symbols('v')
    S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}
    Mj=caps[cap_name]
    u=Mj-2*v; m=Mj; N=S+2+Mj-v
    Phi=2*(N*N-25*m)-75*((u+v)*A/Z+v*B/(e*Y)-S)
    crit=sp.factor(sp.diff(Phi,v))
    v0=sp.factor(S+2+Mj-sp.Rational(75,4)*(A/Z-B/(e*Y)))
    assert sp.factor(crit.subs(v,v0))==0
    Pc=sp.together(Phi.subs(v,v0)).as_numer_denom()[0]
    shift={var:var+1 for var in vars_}
    target=pterms(Pc.subs(shift), vars_)
    # Feasibility slacks at critical, represented by positive-denominator numerators.
    raw_slacks={
        'v': v0-1,
        'u': Mj-2*v0-1,
        's1': e-v0,
        's2': d+e-Mj+v0,
        's3': b+c-2,
    }
    for on,om in caps.items():
        if on!=cap_name: raw_slacks[on]=om-Mj
    slacks=[]
    for name,expr in raw_slacks.items():
        num=sp.together(expr).as_numer_denom()[0]
        slacks.append((name,pterms(num.subs(shift),vars_)))
    candidates=[(i,mono) for i in range(len(slacks)) for mono in monoms(6,deg)]
    touched=set(target)
    for i,mono in candidates:
        for sm in slacks[i][1]: touched.add(add(mono,sm))
    touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm,c in slacks[si][1].items(): rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(c)
    A_mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr(); rhs=np.array([target.get(m,0) for m in touched])
    res=linprog(np.ones(len(candidates)),A_ub=A_mat,b_ub=rhs,bounds=(0,None),method='highs')
    print(cap_name,'deg',deg,'rows',len(touched),'cand',len(candidates),'minrhs',rhs.min(),'success',res.success,'status',res.status)
    if res.success:
        print(' nz',sum(res.x>1e-8))

for deg in [0,1,2,3,4]:
    for cap in ['s4','s5','s6','s7']:
        probe(cap,deg)
