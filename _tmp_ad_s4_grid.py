from fractions import Fraction

def phi(a,b,c,d,e,f,x,y,u,v):
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n*n-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

best=None
best_tuple=None
for Xn in range(0,5):
  for Vn in range(0,5):
    X=Fraction(Xn,1); V=Fraction(Vn,1)
    x=1+X; v=1+V; y=u=a=d=Fraction(1,1)
    m=x*(1+v)+v
    M3=m-3
    # p+2q<=M3, use denom 4 grid
    for qn in range(0, int(4*M3)+1):
      q=Fraction(qn,4)
      for pn in range(0, int(4*(M3-2*q))+1):
        p=Fraction(pn,4)
        b=1+p; c=1+q
        f=(m-c)/(b+c)
        if f < 1: continue
        emin=max(v,b+c-1)
        for En in range(0,4):
          e=emin+Fraction(En,4)
          val=phi(a,b,c,d,e,f,x,y,u,v)
          if best is None or val < best:
            best=val; best_tuple=(X,V,p,q,e, val)
print('best', best, best_tuple)
