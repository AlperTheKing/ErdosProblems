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

def probe(branch, cap, deg):
    a,b,c,d,e,f=sp.symbols('a b c d e f', positive=True); vars_=(a,b,c,d,e,f); x=sp.Integer(1); y=sp.Integer(1)
    S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; M=caps[cap]
    if branch=='u1':
        u=sp.Integer(1); v=(M-1)/2
    elif branch=='s1':
        v=e; u=M-2*e
    else: raise ValueError
    N=S+2+u+v
    neg_der=4*N + 75*(B/(e*Y)-A/Z)
    target_expr=sp.together(neg_der*e*Y*Z).as_numer_denom()[0]
    shift={var:var+1 for var in vars_}
    target=pterms(target_expr.subs(shift),vars_)
    slacks={'u':u-1,'v':v-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2}
    if branch=='u1': slacks.pop('u')
    if branch=='s1': slacks.pop('s1')
    for on,om in caps.items():
        if on!=cap: slacks[on]=om-M
    slack_q=[(name,pterms(expr.subs(shift),vars_)) for name,expr in slacks.items()]
    candidates=[(i,mono) for i in range(len(slack_q)) for mono in monoms(6,deg)]
    touched=set(target)
    for i,mono in candidates:
        for sm in slack_q[i][1]: touched.add(add(mono,sm))
    touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm,c in slack_q[si][1].items(): rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(float(c))
    mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr(); rhs=np.array([float(target.get(m,0)) for m in touched])
    res=linprog(np.ones(len(candidates)),A_ub=mat,b_ub=rhs,bounds=(0,None),method='highs')
    print(branch,cap,'deg',deg,'rows',len(touched),'cand',len(candidates),'minrhs',rhs.min(),'success',res.success)
    if res.success:
        rem=dict(target); nz=0
        for j,val in enumerate(res.x):
            if val<=1e-8: continue
            fr=Fraction(float(val)).limit_denominator(1000000); coef=sp.Rational(fr.numerator,fr.denominator); si,mono=candidates[j]; nz+=1
            for sm,c in slack_q[si][1].items(): rem[add(mono,sm)]=rem.get(add(mono,sm),0)-coef*c
        neg=[c for c in rem.values() if c<0]
        print(' exact nz',nz,'neg',len(neg),'min',min(rem.values()))

for branch in ['u1','s1']:
    for deg in range(0,5):
        for cap in ['s4','s5','s6','s7']:
            probe(branch,cap,deg)
