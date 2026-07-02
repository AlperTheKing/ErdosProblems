import numpy as np
from scipy.optimize import minimize

def vals(w, cap):
    a,b,c,d,e,f,v=w
    S=a+b+c+d+e+f
    Y=a*c+b*f+c*f
    Z=e*Y+d*f*(b+c)
    A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}
    M=caps[cap]
    u=M-2*v; N=S+2+u+v
    deriv=-4*N+75*(A/Z-B/(e*Y))
    sl={'v-1':v-1,'u-1':u-1,'s1':e-v,'s2':d+e-M+v,'s3':b+c-2}
    for k,cm in caps.items():
        if k!=cap: sl[k]=cm-M
    return deriv,sl

def obj(w,cap): return -vals(w,cap)[0]
def cons(cap):
    names=['v-1','u-1','s1','s2','s3']+[k for k in ['s4','s5','s6','s7'] if k!=cap]
    return [{'type':'ineq','fun':lambda w,n=n: vals(w,cap)[1][n]} for n in names]

rng=np.random.default_rng(6)
for cap in ['s4','s5','s6','s7']:
    best=None
    starts=[]
    # feasible starts from endpoints all ones and random with v=1 maybe
    starts.append(np.ones(7))
    for _ in range(100):
        core=1+rng.random(6)*5
        for v in [1, min(core[4], 2), 1+rng.random()*2]:
            starts.append(np.r_[core,v])
    for w0 in starts:
        res=minimize(obj,w0,args=(cap,),bounds=[(1,30)]*7,constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-11})
        if res.success:
            der,sl=vals(res.x,cap)
            if min(sl.values())>=-1e-6 and (best is None or der>best[0]): best=(der,res.x,sl)
    print('\n',cap,'maxder',None if best is None else best[0])
    if best:
        print('vars',best[1]); print('active',{k:round(float(v),8) for k,v in best[2].items() if v<1e-5}, 'minsl',min(best[2].values()))
