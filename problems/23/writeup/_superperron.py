"""Collatz-Wielandt route: rho(K)<=N  <=>  exists phi>0 with (K phi)(v) <= N phi(v) for all v.
At C5[t] extremal phi=1 works (K1=T=N1). Search for an EXPLICIT phi-formula valid generally,
reducing to constant at the extremal. Test candidate phi's exactly (Fraction):
  phi = 1 (fails at overloaded v: K1=T>N there)
  phi = T
  phi = S
  phi = 1 + c*(T-N)_+  / etc
  phi = Perron vector (sanity, must pass)
For each candidate compute max_v (K phi)(v)/phi(v) and check <= N."""
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact
from _layermax_stress import maxcut_local, myciel
from _myc_spec import buildK_fixedcut
import numpy as np

def buildKTS(info):
    P,M,ell,n=pf_exact(info)
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]
                K[va][vb]+=pa*pb
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    return K,T,S,P,M,ell,n

def Kapply(K,phi,n):
    return [sum(K[v][w]*phi[w] for w in range(n)) for v in range(n)]

def ratio_max(K,phi,n,N):
    Kp=Kapply(K,phi,n)
    rs=[F(Kp[v],1)/phi[v] if phi[v]!=0 else F(10**9) for v in range(n)]
    return max(rs)

def test_candidates(K,T,S,n,N,label):
    cands={}
    cands['ones']=[F(1)]*n
    cands['T']=[T[v] for v in range(n)]
    cands['S']=[S[v] for v in range(n)]
    # 1 + (T-N)_+ /N
    cands['1+(T-N)+/N']=[F(1)+ (max(F(0),T[v]-N))/N for v in range(n)]
    # Perron vector (float -> rationalize coarsely): use float to test only
    Kf=np.array([[float(x) for x in row] for row in K])
    w,V=np.linalg.eigh(Kf); pv=V[:,np.argmax(w)]
    if pv.max()<0: pv=-pv
    print('  [%s] N=%d rho(K)=%.4f'%(label,N,max(w)))
    for name,phi in cands.items():
        if any(p<=0 for p in phi):
            print('     phi=%-14s : has nonpositive entry, skip'%name); continue
        r=ratio_max(K,phi,n,N)
        print('     phi=%-14s : max (Kphi)/phi = %s = %.5f  %s'%(name,str(r),float(r),'<=N OK' if r<=N else 'FAIL >N'))
    # float Perron check
    Kp=Kf@pv
    rr=max(Kp[v]/pv[v] for v in range(n) if pv[v]>1e-12)
    print('     phi=Perron(float)  : max ratio = %.5f (should ~= rho)'%rr)

if __name__=="__main__":
    # extremal C5[3]
    from _h import blow
    nn,EE=blow(3); info=loads(nn,EE)
    K,T,S,P,M,ell,n=buildKTS(info)
    test_candidates(K,T,S,n,n,'C5[3] extremal')
    # an overloaded census graph
    import subprocess
    GENG='E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe'
    out=subprocess.run([GENG,'-tc','9'],capture_output=True,text=True).stdout.split()
    for g6 in out:
        nn2,E2=dec(g6); info2=loads(nn2,E2)
        if info2 is None: continue
        K2,T2,S2,P2,M2,ell2,n2=buildKTS(info2)
        if max(T2)>n2:
            test_candidates(K2,T2,S2,n2,n2,'overloaded %s'%g6)
            break
    # Mycielskian N=23
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g=myciel(*C5); g=myciel(*g)
    nn3,E3=g
    adj=[set() for _ in range(nn3)]
    for a,b in E3: adj[a].add(b); adj[b].add(a)
    side,c=maxcut_local(nn3,adj,restarts=200,seed=7)
    r=buildK_fixedcut(nn3,E3,side)
    K3,T3,S3,P3,M3,ell3,n3,side=r
    test_candidates(K3,T3,S3,n3,n3,'Myc N=23')
