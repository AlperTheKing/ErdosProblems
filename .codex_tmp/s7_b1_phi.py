import sympy as sp
A,E,D,F,H=sp.symbols('A E D F H')
vars=(A,E,D,F,H)
a=1+A; e=1+E; d=1+D; f=1+F; R=d+H; c=e+R; b=1
x=d+e; y=sp.Integer(1)
v=a*e+f*x-x*x; u=x-v
S=a+b+c+d+e+f
m=x*x+v
N=S+y+x+u+v
Y=a*c+b*f+c*f
Z=e*Y+d*f*(b+c)
AA=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
BB=a*c+a*e+b*f+b*e+c*f+c*e+e*f
Phi=sp.factor(2*(N*N-25*m)-75*(x*x*AA/Z+v*BB/(e*Y)-S))
num=sp.factor(sp.together(Phi).as_numer_denom()[0])
poly=sp.Poly(sp.expand(num), *vars)
terms=poly.terms(); neg=[(m,c) for m,c in terms if c<0]; pos=[(m,c) for m,c in terms if c>0]
print('terms',len(terms),'pos',len(pos),'neg',len(neg),'deg',poly.total_degree())
if neg: print('first neg',neg[:10])
else: print('min',min(c for m,c in pos),'max',max(c for m,c in pos))
# also constraints v/u/s1 maybe not encoded
for name,expr in [('v1',v-1),('u1',u-1),('s1',e-v),('a1',A)]: print(name, sp.factor(expr))
