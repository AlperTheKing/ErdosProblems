import numpy as np
from scipy.optimize import minimize


def vals(w, cap):
    a,b,c,d,e,f=w
    S=a+b+c+d+e+f
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}
    M=caps[cap]
    Ncrit=75/4*(A/Z-B/(e*Y))
    v=S+2+M-Ncrit
    u=M-2*v
    Phi=2*(Ncrit*Ncrit-25*M)-75*((u+v)*A/Z+v*B/(e*Y)-S)
    sl={'v-1':v-1,'u-1':u-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2}
    for k,cm in caps.items():
        if k!=cap: sl[k]=cm-M
    return Phi,v,u,Ncrit,sl

def obj(w,cap): return vals(w,cap)[0]
def cons(cap):
    names=['v-1','u-1','s1','s2','s3']+[k for k in ['s4','s5','s6','s7'] if k!=cap]
    return [{'type':'ineq','fun':lambda w,n=n: vals(w,cap)[4][n]} for n in names]

rng=np.random.default_rng(5)
for cap in ['s4','s5','s6','s7']:
    best=None
    starts=[np.ones(6)]
    starts += [1+rng.random(6)*4 for _ in range(120)]
    for w0 in starts:
        res=minimize(obj,w0,args=(cap,),bounds=[(1,20)]*6,constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-12})
        if res.success:
            val=vals(res.x,cap)
            if min(val[4].values())>=-1e-6 and (best is None or val[0]<best[0]): best=(val[0],res.x,val,res)
    print('\n',cap,'best', None if best is None else best[0])
    if best:
        Phi,v,u,Ncrit,sl=best[2]
        print('v,u,Ncrit',v,u,Ncrit)
        print('vars',best[1])
        print('active', {k:round(float(w),8) for k,w in sl.items() if w<1e-5})
        print('minsl',min(sl.values()))
