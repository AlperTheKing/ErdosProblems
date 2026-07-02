import numpy as np
from scipy.optimize import minimize

def vals(w,cap):
    a,b,c,d,e,f,x=w
    S=a+b+c+d+e+f
    Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c); A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; M=caps[cap]
    v=M-x*x; q=x; u=x-v; m=M; N=S+1+x+q
    Phi=2*(N*N-25*m)-75*(x*q*A/Z+v*B/(e*Y)-S)
    sl={'x-1':x-1,'v-1':v-1,'u-1':u-1,'s1':e-v,'s2':d+e-q,'s3':b+c-x-1}
    for k,cm in caps.items():
        if k!=cap: sl[k]=cm-M
    return Phi, v,u,sl

def obj(w,cap): return vals(w,cap)[0]
def cons(cap):
    names=['x-1','v-1','u-1','s1','s2','s3']+[k for k in ['s4','s5','s6','s7'] if k!=cap]
    return [{'type':'ineq','fun':lambda w,n=n: vals(w,cap)[3][n]} for n in names]
rng=np.random.default_rng(8)
for cap in ['s4','s5','s6','s7']:
    best=None
    for i in range(120):
        w0=1+rng.random(7)*4
        res=minimize(obj,w0,args=(cap,),bounds=[(1,20)]*7,constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-11})
        if res.success:
            val=vals(res.x,cap)
            if min(val[3].values())>=-1e-6 and (best is None or val[0]<best[0]): best=(val[0],res.x,val)
    print('\n',cap,'best',None if best is None else best[0])
    if best:
        Phi,v,u,sl=best[2]
        print('vars a..f,x',best[1],'v,u',v,u)
        print('active',{k:round(float(v),8) for k,v in sl.items() if v<1e-5},'minsl',min(sl.values()))
