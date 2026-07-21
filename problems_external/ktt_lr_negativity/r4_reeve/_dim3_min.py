import sys, time
import hive4
from census_r4 import parts_le, parts_exact
best=None; n3=0; tot=0; besth2=(0,None); t=time.time()
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 18
cache={}
for N in range(4,NMAX+1):
    nus=parts_exact(N,4)
    for a in range(0,N+1):
        for x in (a,N-a):
            if x not in cache: cache[x]=parts_le(x,4)
        for lam in cache[a]:
            for mu in cache[N-a]:
                if (len(mu),mu)<(len(lam),lam): continue
                for nu in nus:
                    tot+=1
                    r=hive4.analyze(list(lam),list(mu),list(nu))
                    if r['dim']!=3: continue
                    n3+=1
                    s=6*r['poly'][1]
                    if best is None or s<best[0]: best=(s,lam,mu,nu,list(r['hstar']))
                    if r['hstar'][2]>besth2[0]: besth2=(r['hstar'][2],(lam,mu,nu,list(r['hstar'])))
    print('N=%d tot=%d dim3=%d min6a1=%s'%(N,tot,n3,best[0] if best else '-'),flush=True)
print('DIM-3 EXHAUSTIVE |nu|<=%d : %d dim-3 polytopes of %d triples'%(NMAX,n3,tot))
print('min 6*a1 =',best)
print('record h*_2 =',besth2)
print('%.1fs'%(time.time()-t))
