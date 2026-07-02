from __future__ import annotations
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from scipy.linalg import qr
from itertools import product


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

def build(cap_name='s6', max_deg=5):
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
    target=poly_terms(num.subs(shift), vars_)
    slacks={'v':v-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2}
    for oname,om in caps.items():
        if oname != cap_name: slacks[oname]=om-Mj
    slack_q=[]
    for name,expr in slacks.items(): slack_q.append((name, poly_terms(expr.subs(shift), vars_)))
    candidates=[(i,mono) for i in range(len(slack_q)) for mono in monoms(6,max_deg)]
    touched=set(target)
    for i,mono in candidates:
        for sm in slack_q[i][1]: touched.add(add(mono,sm))
    touched=sorted(touched,key=lambda m:(total(m),m)); rid={m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm,coeff in slack_q[si][1].items():
            rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(float(coeff))
    A_mat=coo_matrix((vals,(rows,cols)),shape=(len(touched),len(candidates))).tocsr()
    rhs=np.array([float(target.get(m,0)) for m in touched])
    return vars_, target, slack_q, candidates, touched, A_mat, rhs

vars_, target, slack_q, candidates, touched, A_mat, rhs = build('s6',5)
res=linprog(np.zeros(len(candidates)),A_ub=A_mat,b_ub=rhs,bounds=(0,None),method='highs')
print('lp',res.success, res.status)
x=res.x
nz=np.where(x>1e-8)[0]
print('nz',len(nz))
resid=rhs - A_mat.dot(x)
active=np.where(np.abs(resid)<1e-7)[0]
print('active',len(active),'minres',resid.min(),'max active resid',np.abs(resid[active]).max() if len(active) else None)
Af=A_mat[active[:,None], nz].toarray() if False else A_mat[active,:][:,nz].toarray()
# select independent rows using QR pivoting on transpose; piv are row indices into active
Q,R,piv=qr(Af.T, pivoting=True, mode='economic')
rank=np.sum(np.abs(np.diag(R))>1e-8)
print('rank',rank)
sel_active=active[piv[:len(nz)]]
print('sel rows',len(sel_active))
# Build exact matrix and RHS
A_exact=[]; b_exact=[]
for ri in sel_active:
    mon=touched[ri]
    row=[]
    for cj in nz:
        si,mono=candidates[cj]
        coeff=sp.Rational(0)
        # Need slack coeff at mon - mono
        sm=tuple(mon[k]-mono[k] for k in range(6))
        if all(t>=0 for t in sm): coeff=slack_q[si][1].get(sm, sp.Rational(0))
        row.append(coeff)
    A_exact.append(row); b_exact.append(target.get(mon, sp.Rational(0)))
M=sp.Matrix(A_exact); bvec=sp.Matrix(b_exact)
print('exact rank',M.rank(), 'shape', M.shape)
sol = list(M.LUsolve(bvec))
print('sol min', min(sol), 'maxden', max([s.q for s in sol]))
# verify
rem=dict(target)
for cj,coef in zip(nz,sol):
    if coef == 0: continue
    si,mono=candidates[cj]
    for sm,c in slack_q[si][1].items():
        mm=add(mono,sm); rem[mm]=rem.get(mm,0)-coef*c
neg=[(m,c) for m,c in rem.items() if c<0]
print('neg',len(neg),'min',min(rem.values()))
if neg: print(neg[:10])
# emit compact cert if okay
if not neg and min(sol)>=0:
    print('CERT_START')
    for cj,coef in zip(nz,sol):
        if coef:
            si,mono=candidates[cj]
            print(repr((slack_q[si][0], mono, coef)))
    print('CERT_END')
