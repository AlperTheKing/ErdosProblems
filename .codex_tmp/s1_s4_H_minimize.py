import random, math
import numpy as np
import sympy as sp
from scipy.optimize import differential_evolution, minimize
B,C,F,R,H,U=sp.symbols('B C F R H U')
b=1+B; c=1+C; f=1+F; e=c+R; x=e+1+U; y=sp.Integer(1); v=e; u=x-e
a=(x**2+e-f*(b+c))/c; d=b-R+H; m=x**2+e
N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
func=sp.lambdify((B,C,F,R,H,U),(sp.diff(Phi,H),a-1,d-1),'numpy')
def obj(z):
    val,a1,d1=func(*z)
    pen=0
    if a1<0: pen += 1e6*a1*a1 + 1e5*(-a1)
    if d1<0: pen += 1e6*d1*d1 + 1e5*(-d1)
    return float(val+pen)
bounds=[(0,20)]*6
res=differential_evolution(obj,bounds,tol=1e-8,polish=True,workers=1,maxiter=500,popsize=10,seed=1)
print('DE',res.fun,res.x,func(*res.x))
for seed in range(20):
    z=np.array([random.random()*10 for _ in range(6)])
    r=minimize(obj,z,bounds=bounds,method='Nelder-Mead',options={'maxiter':5000})
    if r.fun<0 or seed<3:
        print('NM',seed,r.fun,r.x,func(*r.x))