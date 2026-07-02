import numpy as np
from scipy.optimize import minimize

def vals(w,cap):
    a,b,c,d,e,f,v=w
    S=a+b+c+d+e+f; Y=a*c+b*f+c*f; Z=e*Y+d*f*(b+c); A=b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f; B=a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps={'s4':Y,'s5':a*e+b*f+c*f,'s6':a*c+d*f+e*f,'s7':a*e+d*f+e*f}; M=caps[cap]
    q=1+v; x=(M-v)/q; N=S+1+x+q
    # derivative after substituting x=(M-v)/(1+v), M constant core
    # use finite formula in code symbolic? derive manually via numeric finite? Use central diff for now.
    def phi(vv):
        qq=1+vv; xx=(M-vv)/qq; NN=S+1+xx+qq
        return 2*(NN*NN-25*M)-75*(xx*qq*A/Z+vv*B/(e*Y)-S)
    h=1e-6*max(1,abs(v)); der=(phi(v+h)-phi(v-h))/(2*h)
    sl={'x-1':x-1,'v-1':v-1,'s1':e-v,'s2':d+e-q,'s3':b+c-x-1}
    for k,cm in caps.items():
        if k!=cap: sl[k]=cm-M
    return der,sl,x

def obj(w,cap): return vals(w,cap)[0]
def cons(cap):
    names=['x-1','v-1','s1','s2','s3']+[k for k in ['s4','s5','s6','s7'] if k!=cap]
    return [{'type':'ineq','fun':lambda w,n=n: vals(w,cap)[1][n]} for n in names]
rng=np.random.default_rng(10)
for cap in ['s4','s5','s6','s7']:
    bestmin=None; bestmax=None
    for i in range(120):
        w0=1+rng.random(7)*4
        res=minimize(obj,w0,args=(cap,),bounds=[(1,20)]*7,constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-10})
        if res.success:
            der,sl,x=vals(res.x,cap)
            if min(sl.values())>=-1e-6:
                if bestmin is None or der<bestmin[0]: bestmin=(der,res.x,sl,x)
        res2=minimize(lambda w,cap=cap:-vals(w,cap)[0],w0,bounds=[(1,20)]*7,constraints=cons(cap),method='SLSQP',options={'maxiter':1000,'ftol':1e-10})
        if res2.success:
            der,sl,x=vals(res2.x,cap)
            if min(sl.values())>=-1e-6:
                if bestmax is None or der>bestmax[0]: bestmax=(der,res2.x,sl,x)
    print('\n',cap,'dermin',None if bestmin is None else bestmin[0], 'dermax', None if bestmax is None else bestmax[0])
    for lab,best in [('min',bestmin),('max',bestmax)]:
        if best:
            print(lab,'x',best[3],'vars',best[1],'active',{k:round(float(v),8) for k,v in best[2].items() if v<1e-5})
