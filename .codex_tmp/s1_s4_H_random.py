import random, sympy as sp
B,C,F,R,H,U=sp.symbols('B C F R H U')
b=1+B; c=1+C; f=1+F; e=c+R; x=e+1+U; y=sp.Integer(1); v=e; u=x-e
a=(x**2+e-f*(b+c))/c; d=b-R+H; m=x**2+e
N=a+b+c+d+e+f+x+y+u+v; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-(a+b+c+d+e+f))
func=sp.lambdify((B,C,F,R,H,U),(sp.diff(Phi,H),a,d),'math')
mins=1e9; maxs=-1e9; count=0; neg=[]
for _ in range(100000):
    vals=[random.random()*5 for _ in range(6)]
    z,aa,dd=func(*vals)
    if aa<1 or dd<1: continue
    count+=1; mins=min(mins,z); maxs=max(maxs,z)
    if z< -1e-7:
        neg.append((z,vals,aa,dd)); break
print('count',count,'min',mins,'max',maxs,'neg',neg[:1])