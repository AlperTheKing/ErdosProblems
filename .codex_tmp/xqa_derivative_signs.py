import random, sympy as sp
X,R=sp.symbols('X R', nonnegative=True)
xx=2+X; c=1+X+R; e=c; b=d=2-R; a=(xx*xx-2)/c; f=1; x=xx; u=1; v=xx-1; y=1
m=x*u+x*v+v; N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=sp.factor(2*(N*N-25*m)-75*(x*(u+v)*A/Z+v*B/(e*Y)-(a+b+c+d+e+f)))
print('Phi simplified ops', sp.count_ops(Phi), flush=True)
for var in (X,R):
    num,den=sp.together(sp.diff(Phi,var)).as_numer_denom(); P=sp.Poly(sp.expand(num), X,R)
    neg=sum(1 for mon,coef in P.terms() if coef<0); pos=sum(1 for mon,coef in P.terms() if coef>0)
    print('d',var,'terms',len(P.terms()),'pos',pos,'neg',neg,'deg',P.total_degree(),'num0',num.subs({X:0,R:0}), flush=True)
func=sp.lambdify((X,R),(sp.diff(Phi,X),sp.diff(Phi,R),Phi),'math')
mins=[1e9,1e9,1e9]; maxs=[-1e9,-1e9,-1e9]; neg=[]
for _ in range(100000):
    xv=random.random()*20; rv=random.random()
    vals=func(xv,rv)
    for i,z in enumerate(vals): mins[i]=min(mins[i],z); maxs[i]=max(maxs[i],z)
print('mins',mins,'maxs',maxs)