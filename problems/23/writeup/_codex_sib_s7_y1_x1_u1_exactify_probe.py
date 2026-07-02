from __future__ import annotations
from fractions import Fraction
from itertools import product
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def monoms(n, deg):
    def rec(i,left,cur):
        if i==n:
            yield tuple(cur); return
        for k in range(left+1):
            cur.append(k); yield from rec(i+1,left-k,cur); cur.pop()
    yield from rec(0,deg,[])

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def total(m): return sum(m)
def poly_terms(expr, vars_):
    return {tuple(m): sp.Rational(c) for m,c in sp.Poly(sp.expand(expr), *vars_).terms()}

def float_terms(expr, vars_):
    return {tuple(m): float(c) for m,c in sp.Poly(sp.expand(expr), *vars_).terms()}

def solve_cap(cap_name, max_deg=5, max_den=1000000):
    a,b,c,d,e,f = sp.symbols('a b c d e f', positive=True)
    vars_=(a,b,c,d,e,f); x=sp.Integer(1); y=sp.Integer(1); u=sp.Integer(1)
    S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}
    Mj=caps[cap_name]; v=(Mj-1)/2
    m=Mj; N=S+x+y+u+v
    Phi=2*(N*N-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-S)
    num=sp.together(Phi).as_numer_denom()[0]
    shift={var:var+1 for var in vars_}
    target_f=float_terms(num.subs(shift), vars_)
    target_q=poly_terms(num.subs(shift), vars_)
    slacks={'v':v-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2}
    for oname,om in caps.items():
        if oname != cap_name:
            slacks[oname]=om-Mj
    slack_q=[]; slack_f=[]
    for name,expr in slacks.items():
        qd=poly_terms(expr.subs(shift), vars_); fd={m:float(c) for m,c in qd.items()}
        slack_q.append((name,qd)); slack_f.append((name,fd))
    candidates=[(i,mono) for i in range(len(slack_f)) for mono in monoms(6,max_deg)]
    touched=set(target_f)
    for i,mono in candidates:
        for sm in slack_f[i][1]: touched.add(add(mono,sm))
    touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm,coeff in slack_f[si][1].items():
            rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(coeff)
    A_mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr()
    rhs=np.array([target_f.get(m,0.0) for m in touched])
    res=linprog(np.zeros(len(candidates)),A_ub=A_mat,b_ub=rhs,bounds=(0,None),method='highs')
    print(cap_name,'success',res.success,'nzfloat',sum(res.x>1e-8))
    if not res.success: return None
    cert=[]
    for j,(si,mono) in enumerate(candidates):
        val=res.x[j]
        if val>1e-8:
            fr=Fraction(float(val)).limit_denominator(max_den)
            if fr:
                cert.append((slack_q[si][0], mono, sp.Rational(fr.numerator, fr.denominator)))
    rem=dict(target_q)
    for si,mono,coef in cert:
        sd=dict(slack_q[[n for n,(nm,_) in enumerate(slack_q) if nm==si][0]][1])
        for sm,c in sd.items():
            mm=add(mono,sm); rem[mm]=rem.get(mm,0)-coef*c
    minc=min(rem.values()) if rem else sp.Rational(0)
    neg=[(m,c) for m,c in rem.items() if c<0]
    print(cap_name,'cert',len(cert),'min',minc,'neg',len(neg))
    if neg:
        print(' firstneg',neg[:10])
    return cert if not neg else None

if __name__=='__main__':
    for cap in ['s4','s5','s6','s7']:
        solve_cap(cap,5,1000000)
