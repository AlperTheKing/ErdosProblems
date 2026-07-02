import sympy as sp
from scipy.optimize import linprog
import numpy as np
from fractions import Fraction
A,E,D,F,R,Bv=sp.symbols('A E D F R B')
vars=(A,E,D,F,R,Bv)
a=1+A; e=1+E; d=1+D; f=1+F; c=e+R; b=1+Bv
x=d+e; y=sp.Integer(1)
v=a*e+f*x-x*x; u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S)
num=sp.Poly(sp.expand(sp.factor(sp.together(sp.diff(Phi,Bv)).as_numer_denom()[0])), *vars)
numd={mon:int(coef) for mon,coef in num.terms()}; neg=[mon for mon,coef in numd.items() if coef<0]
constraints={'u1':sp.Poly(sp.expand(u-1),*vars),'s1':sp.Poly(sp.expand(e-v),*vars),'v1':sp.Poly(sp.expand(v-1),*vars),'s3':sp.Poly(sp.expand(b+c-x-1),*vars)}
seen=set(); cands=[]
for gname,gpoly in constraints.items():
    for target in neg:
        for mon,coef in gpoly.terms():
            if coef<0 and all(target[i]>=mon[i] for i in range(6)):
                mult=tuple(target[i]-mon[i] for i in range(6)); key=(gname,mult)
                if key not in seen: seen.add(key); cands.append(key)
allmons=set(numd); gdict={}
for key in cands:
    gname,mult=key; dd={}
    for mon,coef in constraints[gname].terms():
        mm=tuple(mon[i]+mult[i] for i in range(6)); dd[mm]=dd.get(mm,0)+int(coef); allmons.add(mm)
    gdict[key]=dd
allmons=sorted(allmons); idx={m:i for i,m in enumerate(allmons)}
Aub=np.zeros((len(allmons),len(cands))); bub=np.zeros(len(allmons))
for i,mn in enumerate(allmons): bub[i]=float(numd.get(mn,0))
for j,key in enumerate(cands):
    for mn,coef in gdict[key].items(): Aub[idx[mn],j]=float(coef)
res=linprog(c=np.zeros(len(cands)),A_ub=Aub,b_ub=bub,bounds=(0,None),method='highs')
assert res.success
cert=[]
for i,val in enumerate(res.x):
    if val>1e-8:
        cert.append((cands[i][0],cands[i][1],Fraction(float(val)).limit_denominator(1000000)))
print('len',len(cert))
print('CERT = [')
for item in cert: print('    '+repr(item)+',')
print(']')
resid=dict(numd)
for gname,mult,lam in cert:
    q=sp.Rational(lam.numerator,lam.denominator)
    for mon,coef in constraints[gname].terms():
        mm=tuple(mon[i]+mult[i] for i in range(6))
        resid[mm]=resid.get(mm,0)-q*int(coef)
neg2=[(m,c) for m,c in resid.items() if c<0]
print('exact residual neg',len(neg2),'terms',len(resid),'min',min(resid.values()))
if neg2: print(neg2[:20])
