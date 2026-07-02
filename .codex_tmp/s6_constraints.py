import sympy as sp
A,C,D,F,R,H=sp.symbols('A C D F R H')
a=1+A; c=1+C; d=1+D; f=1+F; e=c+R; b=d+R+1+H; x=d+e
v=a*c+f*x-x*x; u=x-v
for name,expr in [('v1',v-1),('u1',u-1),('s1',e-v),('a1',A),('s3',H),('r',R)]:
    print(name, sp.factor(expr))
    print(sp.Poly(sp.expand(expr), A,C,D,F,R,H).terms())
