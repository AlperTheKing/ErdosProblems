from __future__ import annotations
import sympy as sp

A0,B0,C0,D0,E0,F0,Q = sp.symbols('A0 B0 C0 D0 E0 F0 Q')
a,b,c,d,e,f,q = 1+A0,1+B0,1+C0,1+D0,1+E0,1+F0,1+Q
Y = a*c + b*f + c*f
R = b+c
D = d+e
Z = e*Y + d*f*R
AA = b*d + c*d + d*f + a*c + a*e + b*f + b*e + c*f + c*e + e*f
BB = a*c + a*e + b*f + b*e + c*f + c*e + e*f
S = a+b+c+d+e+f
Ms = {4:Y,5:a*e+b*f+c*f,6:a*c+d*f+e*f,7:a*e+d*f+e*f}

def pi(M,N,x,v):
    return sp.expand(2*e*Y*Z*(N*N-25*M) - 75*(e*Y*x*q*AA + Z*v*BB - e*Y*Z*S))

def st(expr, vars_):
    P=sp.Poly(sp.expand(expr), *vars_)
    coeffs=P.coeffs(); neg=[(m,c) for m,c in zip(P.monoms(), coeffs) if c<0]
    return len(coeffs), P.total_degree(), min(coeffs) if coeffs else 0, len(neg), neg[:5]
vars_=(A0,B0,C0,D0,E0,F0,Q)
for fam in ['YXCOR','YCOR']:
  for j,M in Ms.items():
    if fam=='YXCOR':
      x=1; v=M-q; N=S+2+q
    else:
      x=R-1; v=M-(R-1)*q; N=S+R+q
    print(fam,j,st(pi(M,N,x,v), vars_))
