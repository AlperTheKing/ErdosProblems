import sympy as sp
from scipy.optimize import linprog
import numpy as np
D,V,S,H,F=sp.symbols('D V S H F')
vars=(D,V,S,H,F)
d=1+D; v=1+V; e=v+S; u=1+D+S; x=u+v; y=sp.Integer(1); b=sp.Integer(1); c=e+d+H; f=1+F
a=(x*x+v-f*x)/e
A_num=sp.together(a-1).as_numer_denom()[0]
Ssum=a+b+c+d+e+f; m=x*x+v; N=Ssum+y+x+u+v
Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-Ssum)
for name,var in [('H',H),('D',D),('V',V),('S',S),('F',F)]:
 num=sp.Poly(sp.expand(sp.factor(sp.together(sp.diff(Phi,var)).as_numer_denom()[0])), *vars)
 terms=num.terms(); neg=[(m,c) for m,c in terms if c<0]
 print(name,'terms',len(terms),'neg',len(neg),'deg',num.total_degree(), 'first',neg[:3])
 # LP with A_num maybe
 constraints={'a1':sp.Poly(sp.expand(A_num),*vars)}
 numd={mon:sp.Rational(coef) for mon,coef in terms}; negmons=[mon for mon,coef in numd.items() if coef<0]
 seen=set(); cands=[]
 for gname,gpoly in constraints.items():
  for target in negmons:
   for mon,coef in gpoly.terms():
    if coef<0 and all(target[i]>=mon[i] for i in range(5)):
     key=(gname,tuple(target[i]-mon[i] for i in range(5)))
     if key not in seen: seen.add(key); cands.append(key)
 print(' cands',len(cands))
 if len(cands)>0 and len(cands)<2000:
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
  print(' lp',res.status)
