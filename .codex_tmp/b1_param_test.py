import sympy as sp
from scipy.optimize import linprog
import numpy as np
D,V,S,H,F=sp.symbols('D V S H F')
vars=(D,V,S,H,F)
d=1+D; v=1+V; s1=S; e=v+s1; u=1+D+S; x=u+v; y=sp.Integer(1); b=sp.Integer(1); c=e+d+H; f=1+F
# s7: x^2+v = a*e + f*x, solve a
a=(x*x+v-f*x)/e
Aexpr=sp.factor(a-1)
print('Aexpr', Aexpr)
Ssum=a+b+c+d+e+f
m=x*x+v
N=Ssum+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=sp.factor(2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-Ssum))
num,den=sp.together(Phi).as_numer_denom()
print('den ops', sp.count_ops(den), 'num ops', sp.count_ops(num))
poly=sp.Poly(sp.expand(num), *vars)
terms=poly.terms(); neg=[(m,c) for m,c in terms if c<0]; pos=[(m,c) for m,c in terms if c>0]
print('num terms',len(terms),'pos',len(pos),'neg',len(neg),'deg',poly.total_degree())
print('first neg',neg[:10])
# LP decompose num using Aexpr numerator perhaps, since Aexpr>=0 if numerator>=0 / e
A_num=sp.factor(sp.together(Aexpr).as_numer_denom()[0])
print('A_num', A_num)
constraints={'a1': sp.Poly(sp.expand(A_num), *vars)}
numd={mon:sp.Rational(coef) for mon,coef in poly.terms()}; negmons=[mon for mon,coef in numd.items() if coef<0]
seen=set(); cands=[]
for gname,gpoly in constraints.items():
 for target in negmons:
  for mon,coef in gpoly.terms():
   if coef<0 and all(target[i]>=mon[i] for i in range(5)):
    mult=tuple(target[i]-mon[i] for i in range(5)); key=(gname,mult)
    if key not in seen: seen.add(key); cands.append(key)
print('cands',len(cands))
if cands:
 allmons=set(numd); gdict={}
 for key in cands:
  gname,mult=key; dd={}
  for mon,coef in constraints[gname].terms():
   mm=tuple(mon[i]+mult[i] for i in range(5)); dd[mm]=dd.get(mm,0)+float(coef); allmons.add(mm)
  gdict[key]=dd
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
