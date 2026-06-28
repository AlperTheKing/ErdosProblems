"""Push the TRUE certificate (1)(2)(3) -- NOT the k2 proxy -- to N=22..25 structural family.
Targets: Myc(Grotzsch) N=23 (already FAIL-on-proxy but TRUE pass), generalized Mycielskians,
C7-Mycielskian, and large unequal blow-ups. Report whether TRUE E-rowsum>=0 (cond3), Aqq nonsingular (cond1),
E offdiag<=0 (cond2), AND independent exact-LDL PSD of A. Also smallest Neumann-k needed (how bad is proxy).
The question: does the CERTIFICATE (real conditions) ever fail at N>=22, or only the proxy?"""
from fractions import Fraction as F
from _h import loads
from _audit_stress import full_test, build_K
from _audit_directpsd import leading_minors_psd
from _schur_neumann import neumann_resid

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def cycle(k): return k,[(i,(i+1)%k) for i in range(k)]

def smallest_k(info):
    K,T,N,n=build_K(info)
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    out=neumann_resid(K,T,O,Q,N,n,20)
    for k in sorted(out):
        if out[k]>=0: return k
    return ">20"

def run_one(name,nn,EE):
    info=loads(nn,EE)
    if info is None: print(f"  {name} N={nn}: loads=None",flush=True); return
    res=full_test(info)
    if res['status']=='noO':
        print(f"  {name} N={nn}: noO (Perron trivial)",flush=True); return
    K,T,N,n=build_K(info)
    A=[[(F(N) if i==j else F(0))-K[i][j] for j in range(n)] for i in range(n)]
    psd=leading_minors_psd(A)
    sk=smallest_k(info)
    # TRUE cert holds iff status in (ok) using real conds minus the proxy:
    real_ok = (res['minrow']>=0) and (not res['inv_neg']) and (not res['offdiag_pos'])
    print(f"  {name} N={nn}: TRUE-cert(1,2,3)={'PASS' if real_ok else 'FAIL'} "
          f"[E-rowsum={float(res['minrow']):+.3f} inv>=0:{not res['inv_neg']} offdiag<=0:{not res['offdiag_pos']}] "
          f"A-PSD(indep-LDL)={psd} | k2_proxy={'ok' if res['mink2']>=0 else 'NEG('+str(float(res['mink2']))+')'} smallest_k={sk}",flush=True)

if __name__=="__main__":
    print("=== TRUE certificate at N=22..25 structural family ===",flush=True)
    # Myc(Grotzsch) N=23
    _,C5=cycle(5); n1,E1=mycielski(5,C5); n2,E2=mycielski(n1,E1)
    run_one("Myc(Grotzsch)",n2,E2)
    # Myc(C7) N=15, then we want bigger: Myc(Myc(C7)) N=31 too big. Use Myc(C7-blowup)
    _,C7=cycle(7); n7,E7=mycielski(7,C7)  # N=15
    run_one("Myc(C7) N15",n7,E7)
    # C9, C11 cycles (odd girth 9,11): blow them
    for k in (9,11):
        nk,Ek=cycle(k)
        # blow t=2
        EE=[]
        for (a,b) in Ek:
            for i in range(2):
                for j in range(2): EE.append((a*2+i,b*2+j))
        run_one(f"C{k}[2]",nk*2,EE)
    # unequal blow-up of Grotzsch parts? Grotzsch blow t=2 = N=22
    n1,E1=mycielski(5,C5)  # Grotzsch N=11
    EE=[]
    for (a,b) in E1:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    run_one("Grotzsch[2]",n1*2,EE)
    # Petersen graph (triangle-free, N=10) blow t=2 = N=20
    pet=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]
    EE=[]
    for (a,b) in pet:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    run_one("Petersen[2]",20,EE)
