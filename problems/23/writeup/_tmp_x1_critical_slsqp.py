import numpy as np
from scipy.optimize import minimize


def vals(z, cap):
    a,b,c,d,e,f=np.exp(z)
    S=a+b+c+d+e+f
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={
        's4':Y,
        's5':a*e+b*f+c*f,
        's6':a*c+d*f+e*f,
        's7':a*e+d*f+e*f,
    }
    M=caps[cap]
    # critical N=75/4*(A/Z-B/eY), v=S+2+M-Ncrit
    Ncrit=75/4*(A/Z-B/(e*Y))
    v=S+2+M-Ncrit
    u=M-2*v
    x=1; y=1
    m=M; N=S+2+u+v
    Phi=2*(N*N-25*m)-75*((u+v)*A/Z+v*B/(e*Y)-S)
    sl={
        'a-1':a-1,'b-1':b-1,'c-1':c-1,'d-1':d-1,'e-1':e-1,'f-1':f-1,
        'v-1':v-1,'u-1':u-1,'s1':e-v,'s2':d+e-(u+v),'s3':b+c-2,
    }
    for k,cm in caps.items():
        if k!=cap: sl[k]=cm-M
    return Phi, v, u, Ncrit, sl

def obj(z, cap):
    Phi,_,_,_,sl=vals(z,cap)
    return Phi

def cons(cap):
    keys=None
    def mk(name):
        return {'type':'ineq','fun':lambda z,name=name: vals(z,cap)[4][name]}
    # all slacks except variable lower already log handles a..f
    names=['v-1','u-1','s1','s2','s3']+[k for k in ['s4','s5','s6','s7'] if k!=cap]
    return [mk(n) for n in names]

rng=np.random.default_rng(4)
for cap in ['s4','s5','s6','s7']:
    best=None
    for i in range(80):
        z0=rng.normal(0,0.8,6)
        res=minimize(obj,z0,args=(cap,),constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-10, 'disp':False})
        if res.success:
            val=vals(res.x,cap)
            if best is None or val[0]<best[0]: best=(val[0],res.x,val,res)
    print('\n',cap,'best', None if best is None else best[0])
    if best:
        Phi,v,u,Ncrit,sl=best[2]
        print('v,u,Ncrit',v,u,Ncrit)
        print('vars',np.exp(best[1]))
        print('active', {k:round(float(w),8) for k,w in sl.items() if w<1e-5})
        print('minsl',min(sl.values()))
