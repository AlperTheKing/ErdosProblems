import sympy as sp
from scipy.optimize import linprog
import numpy as np
A,E,D,F,H=sp.symbols('A E D F H')
vars=(A,E,D,F,H)
a=1+A; e=1+E; d=1+D; f=1+F; b=sp.Integer(1); c=e+d+H; x=d+e; y=sp.Integer(1)
v=a*e+f*x-x*x; u=x-v
Ssum=a+b+c+d+e+f; m=x*x+v; N=Ssum+y+x+u+v
Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-Ssum)
num=sp.Poly(sp.expand(sp.factor(sp.together(sp.diff(Phi,H)).as_numer_denom()[0])), *vars)
terms=num.terms(); neg=[(m,c) for m,c in terms if c<0]; pos=[(m,c) for m,c in terms if c>0]
print('dH terms',len(terms),'pos',len(pos),'neg',len(neg),'deg',num.total_degree(), 'firstneg', neg[:10])
constraints={'u1':sp.Poly(sp.expand(u-1),*vars),'v1':sp.Poly(sp.expand(v-1),*vars),'s1':sp.Poly(sp.expand(e-v),*vars)}
numd={mon:int(coef) for mon,coef in terms}; negmons=[mon for mon,coef in numd.items() if coef<0]
seen=set(); cands=[]
for gname,gpoly in constraints.items():
 for target in negmons:
  for mon,coef in gpoly.terms():
   if coef<0 and all(target[i]>=mon[i] for i in range(5)):
    key=(gname,tuple(target[i]-mon[i] for i in range(5)))
    if key not in seen: seen.add(key); cands.append(key)
print('cands',len(cands))
allmons=set(numd); gdict={}
for key in cands:
 gname,mult=key; dd={}
 for mon,coef in constraints[gname].terms():
  mm=tuple(mon[i]+mult[i] for i in range(5)); dd[mm]=dd.get(mm,0)+int(coef); allmons.add(mm)
 gdict[key]=dd
if cands:
 allmons=sorted(allmons); idx={m:i for i,m in enumerate(allmons)}
 Aub=np.zeros((len(allmons),len(cands))); bub=np.zeros(len(allmons))
 for i,mn in enumerate(allmons): bub[i]=float(numd.get(mn,0))
 for j,key in enumerate(cands):
  for mn,coef in gdict[key].items(): Aub[idx[mn],j]=float(coef)
 res=linprog(c=np.zeros(len(cands)),A_ub=Aub,b_ub=bub,bounds=(0,None),method='highs')
 print(res.status,res.message)
 if res.success:
  nz=[(cands[i],res.x[i]) for i in range(len(cands)) if res.x[i]>1e-8]
  print('nz',len(nz), nz[:80], 'minres',(bub-Aub@res.x).min())
