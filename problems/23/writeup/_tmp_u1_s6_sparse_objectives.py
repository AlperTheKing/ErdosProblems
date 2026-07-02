from __future__ import annotations
from fractions import Fraction
from itertools import product
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

# Build u=1, cap=s6 cone matrices once, try many objectives; report nz and exactified neg count.
def monoms(n, deg):
    def rec(i,left,cur):
        if i==n: yield tuple(cur); return
        for k in range(left+1): cur.append(k); yield from rec(i+1,left-k,cur); cur.pop()
    yield from rec(0,deg,[])
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def total(m): return sum(m)
def pterms(expr,vars_): return {tuple(m): sp.Rational(c) for m,c in sp.Poly(sp.expand(expr),*vars_).terms()}

a,b,c,d,e,f=sp.symbols('a b c d e f', positive=True); vars_=(a,b,c,d,e,f); x=sp.Integer(1); y=sp.Integer(1); u=sp.Integer(1)
S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c); A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; Mj=caps['s6']; v=(Mj-1)/2; m=Mj; N=S+2+u+v
Phi=2*(N*N-25*m)-75*((u+v)*A/Z+v*B/(e*Y)-S); num=sp.together(Phi).as_numer_denom()[0]; shift={var:var+1 for var in vars_}
target=pterms(num.subs(shift),vars_)
slacks={'v':v-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2}
for on,om in caps.items():
    if on!='s6': slacks[on]=om-Mj
slack_q=[(name,pterms(expr.subs(shift),vars_)) for name,expr in slacks.items()]
candidates=[(i,mono) for i in range(len(slack_q)) for mono in monoms(6,5)]
touched=set(target)
for i,mono in candidates:
    for sm in slack_q[i][1]: touched.add(add(mono,sm))
touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
rows=[]; cols=[]; vals=[]
for j,(si,mono) in enumerate(candidates):
    for sm,coef in slack_q[si][1].items(): rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(float(coef))
A_mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr(); rhs=np.array([float(target.get(m,0)) for m in touched])

def check(x, maxden=1000000):
    rem=dict(target); nz=0
    for j,val in enumerate(x):
        if val<=1e-8: continue
        nz+=1; fr=Fraction(float(val)).limit_denominator(maxden); coef=sp.Rational(fr.numerator,fr.denominator); si,mono=candidates[j]
        for sm,c in slack_q[si][1].items(): rem[add(mono,sm)]=rem.get(add(mono,sm),0)-coef*c
    neg=[c for c in rem.values() if c<0]
    return nz, len(neg), min(rem.values())

objs=[]
objs.append(('zero', np.zeros(len(candidates))))
objs.append(('sum', np.ones(len(candidates))))
rng=np.random.default_rng(123)
for k in range(12): objs.append((f'rand{k}', rng.random(len(candidates))))
for name,c in objs:
    res=linprog(c,A_ub=A_mat,b_ub=rhs,bounds=(0,None),method='highs')
    if not res.success:
        print(name,'fail',res.status); continue
    print(name, check(res.x), 'fun', res.fun)
