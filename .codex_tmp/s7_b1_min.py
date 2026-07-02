import random, math
from scipy.optimize import minimize

def phi(vars):
    A,E,D,F,H=vars
    a=1+A; e=1+E; d=1+D; f=1+F; R=d+H; c=e+R; b=1; x=d+e; y=1
    v=a*e+f*x-x*x; u=x-v
    S=a+b+c+d+e+f; m=x*x+v; N=S+y+x+u+v
    Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
    AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S)
def cons(vars):
    A,E,D,F,H=vars; a=1+A; e=1+E; d=1+D; f=1+F; x=d+e; v=a*e+f*x-x*x; u=x-v
    return [A,E,D,F,H,v-1,u-1,e-v]
constraints=[{'type':'ineq','fun':lambda z,i=i: cons(z)[i]} for i in range(8)]
best=(1e9,None)
for seed in range(50):
    z0=[random.random()*5 for _ in range(5)]
    res=minimize(phi,z0,method='SLSQP',constraints=constraints,bounds=[(0,None)]*5,options={'maxiter':1000,'ftol':1e-10})
    if res.success and res.fun<best[0]: best=(res.fun,res.x)
print(best)
print('cons', cons(best[1]))
