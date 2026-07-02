import itertools, math
import sympy as sp
from scipy.optimize import linprog
B,C,F,R,H,U=sp.symbols('B C F R H U', nonnegative=True)
vars_=(B,C,F,R,H,U)
b=1+B; c=1+C; f=1+F; e=c+R; x=e+1+U; y=sp.Integer(1); v=e; u=x-e
a=sp.factor((x**2+e-f*(b+c))/c); d=b-R+H; m=x**2+e
N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
num=sp.Poly(sp.expand(sp.together(sp.diff(Phi,H)).as_numer_denom()[0]), *vars_)
a1=sp.Poly(sp.expand((x**2+e-f*(b+c)-c)), *vars_) # c*(a-1)
d1=sp.Poly(sp.expand(d-1), *vars_)
print('num terms',len(num.terms()),'deg',num.total_degree(),'a1deg',a1.total_degree(),'d1deg',d1.total_degree(), flush=True)
# build candidate monomial multiples up to total degree cap
cols=[]; names=[]
def gen_exps(n, maxdeg):
    if n==1:
        for k in range(maxdeg+1): yield (k,); return
    for k in range(maxdeg+1):
        for rest in gen_exps(n-1,maxdeg-k): yield (k,)+rest
for gname,gpoly in [('a1',a1),('d1',d1)]:
    maxdeg=num.total_degree()-gpoly.total_degree()
    for exps in gen_exps(len(vars_), maxdeg):
        mon=sp.Poly(sp.prod(vv**ee for vv,ee in zip(vars_,exps)), *vars_)
        poly=mon*gpoly
        cols.append({m:float(c) for m,c in poly.terms()})
        names.append((gname,exps))
# term universe
terms=set(num.monoms())
for col in cols: terms.update(col.keys())
terms=sorted(terms)
idx={m:i for i,m in enumerate(terms)}
print('cols',len(cols),'rows',len(terms), flush=True)
# inequalities M lambda <= num coeff for each row, where M is coeff of columns
A=[]; bvec=[]
numdict={m:float(c) for m,c in num.terms()}
for m in terms:
    A.append([col.get(m,0.0) for col in cols])
    bvec.append(numdict.get(m,0.0))
res=linprog(c=[0.0]*len(cols), A_ub=A, b_ub=bvec, bounds=[(0,None)]*len(cols), method='highs', options={'time_limit':120})
print('success',res.success,'status',res.status,'msg',res.message,'fun',res.fun, flush=True)
if res.success:
    nz=[(names[i],res.x[i]) for i in range(len(cols)) if res.x[i]>1e-7]
    print('nz',len(nz), nz[:80], flush=True)