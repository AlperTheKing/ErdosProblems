from fractions import Fraction

def phi(a,b,c,d,e,f,x,y,u,v):
    m=x*u+x*v+y*v
    n=a+b+c+d+e+f+x+y+u+v
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    return 2*(n*n-25*m)-75*(x*(u+v)*A/Z+y*v*B/(e*Y)-(a+b+c+d+e+f))

best=None; best_tuple=None
for Xn in range(0,5):
  for Vn in range(0,5):
    X=Fraction(Xn,1); V=Fraction(Vn,1)
    x=1+X; v=1+V; y=u=a=f=Fraction(1,1)
    m=x*(1+v)+v; M3=m-3
    for Rn in range(0,5):
      R=Fraction(Rn,4)
      c=1+R*M3/2
      b=1+(1-R)*M3
      if b+c < x+1: continue
      for dn in range(1,12):
        d=Fraction(dn,1)
        for en in range(1,12):
          e=Fraction(en,1)
          if e < v or e < c: continue
          if d+e < b+c: continue
          if d+2*e < b+2*c: continue
          val=phi(a,b,c,d,e,f,x,y,u,v)
          if best is None or val < best:
            best=val; best_tuple=(X,V,R,b,c,d,e,val)
print('best',best,best_tuple)
