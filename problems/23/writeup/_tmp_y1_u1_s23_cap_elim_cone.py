from __future__ import annotations
from fractions import Fraction
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def monoms(n,deg):
    def rec(i,left,cur):
        if i==n: yield tuple(cur); return
        for k in range(left+1): cur.append(k); yield from rec(i+1,left-k,cur); cur.pop()
    yield from rec(0,deg,[])
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def total(m): return sum(m)
def pterms(expr,vars_): return {tuple(m): sp.Rational(c) for m,c in sp.Poly(sp.expand(expr),*vars_).terms()}

def probe(cap,deg):
    a,b,c,e,f=sp.symbols('a b c e f', positive=True); d=sp.Integer(1); u=sp.Integer(1); y=sp.Integer(1); v=e; x=b+c-1
    allvars=(b,c,e,f)
    S=a+b+c+d+e+f; N=S+x+y+u+v; m=x*u+x*v+y*v
    Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}
    sl={name:expr-m for name,expr in caps.items()}
    sol_a=sp.solve(sp.Eq(sl[cap],0),a)[0]
    denom=sp.denom(sp.together(sol_a))
    Phi=2*(N*N-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-S)
    P=sp.together(Phi.subs(a,sol_a)).as_numer_denom()[0]
    # multiply by denom if needed? together already has denominator; numerator should encode sign since denom positive.
    shift={var:var+1 for var in allvars}
    target=pterms(P.subs(shift), allvars)
    slacks={}
    # a>=1, clear positive denom
    slacks['a']=sp.together((sol_a-1)*denom).as_numer_denom()[0]
    for name,expr in sl.items():
        if name!=cap:
            slacks[name]=sp.together(expr.subs(a,sol_a)*denom).as_numer_denom()[0]
    slack_q=[(name,pterms(expr.subs(shift),allvars)) for name,expr in slacks.items()]
    candidates=[(i,mono) for i in range(len(slack_q)) for mono in monoms(4,deg)]
    touched=set(target)
    for i,mono in candidates:
        for sm in slack_q[i][1]: touched.add(add(mono,sm))
    touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm,c0 in slack_q[si][1].items(): rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(float(c0))
    mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr(); rhs=np.array([float(target.get(m0,0)) for m0 in touched])
    res=linprog(np.ones(len(candidates)),A_ub=mat,b_ub=rhs,bounds=(0,None),method='highs')
    print(cap,'deg',deg,'sola',sol_a,'rows',len(touched),'cand',len(candidates),'minrhs',rhs.min(),'success',res.success)
    if res.success:
        rem=dict(target); nz=0
        for j,val in enumerate(res.x):
            if val<=1e-8: continue
            fr=Fraction(float(val)).limit_denominator(1000000); coef=sp.Rational(fr.numerator,fr.denominator); si,mono=candidates[j]; nz+=1
            for sm,cc in slack_q[si][1].items(): rem[add(mono,sm)]=rem.get(add(mono,sm),0)-coef*cc
        neg=[cc for cc in rem.values() if cc<0]
        print(' exact nz',nz,'neg',len(neg),'min',min(rem.values()))

for deg in range(0,8):
    for cap in ['s4','s5','s6','s7']:
        probe(cap,deg)
