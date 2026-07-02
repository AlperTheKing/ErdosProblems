import sympy as sp
from scipy.optimize import linprog
import numpy as np
from fractions import Fraction
A,C,D,F,R,H=sp.symbols('A C D F R H')
vars=(A,C,D,F,R,H)
a=1+A; c=1+C; d=1+D; f=1+F; e=c+R; b=d+R+1+H; x=d+e
y=sp.Integer(1)
v=a*c+f*x-x*x; u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S)
num=sp.Poly(sp.expand(sp.factor(sp.together(sp.diff(Phi,H)).as_numer_denom()[0])), *vars)
numd={mon:int(coef) for mon,coef in num.terms()}
neg=[mon for mon,coef in numd.items() if coef<0]
print('num terms',len(numd),'neg',len(neg),'deg',num.total_degree())
constraints={
 'u1': sp.Poly(sp.expand(u-1), *vars),
 's1': sp.Poly(sp.expand(e-v), *vars),
 'v1': sp.Poly(sp.expand(v-1), *vars),
}
# candidate multiplier monomials that hit a negative coefficient through a negative term of g
cands=[]
seen=set()
for gname,gpoly in constraints.items():
    terms=[(mon,int(coef)) for mon,coef in gpoly.terms()]
    for target in neg:
        for mon,coef in terms:
            if coef<0 and all(target[i]>=mon[i] for i in range(6)):
                mult=tuple(target[i]-mon[i] for i in range(6))
                key=(gname,mult)
                if key not in seen:
                    seen.add(key); cands.append(key)
print('cands',len(cands))
# build all monomial rows affected or in num
allmons=set(numd)
gdict={}
for key in cands:
    gname,mult=key; gpoly=constraints[gname]
    dd={}
    for mon,coef in gpoly.terms():
        mm=tuple(mon[i]+mult[i] for i in range(6))
        dd[mm]=dd.get(mm,0)+int(coef)
        allmons.add(mm)
    gdict[key]=dd
allmons=sorted(allmons)
idx={m:i for i,m in enumerate(allmons)}
Aub=np.zeros((len(allmons),len(cands)))
bub=np.zeros(len(allmons))
for i,mn in enumerate(allmons):
    bub[i]=float(numd.get(mn,0))
for j,key in enumerate(cands):
    for mn,coef in gdict[key].items():
        Aub[idx[mn],j]=float(coef)
res=linprog(c=np.zeros(len(cands)), A_ub=Aub, b_ub=bub, bounds=(0,None), method='highs')
print(res.status,res.message)
if res.success:
    xs=res.x
    nz=[(cands[i],xs[i]) for i in range(len(cands)) if xs[i]>1e-8]
    print('nz',len(nz))
    print(nz[:50])
    # check min residual
    residual=bub-Aub@xs
    print('min residual',residual.min(),'active rows',sum(residual<1e-7))
