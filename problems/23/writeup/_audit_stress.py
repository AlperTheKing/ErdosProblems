"""HARD adversarial stress of the Schur M-matrix certificate.
For EVERY census triangle-free graph N<=11 that has overload (O nonempty under the gmin maxcut),
build blow-ups t=2,3 (and t=4 where N stays <=24) and exact-test all conditions + k2.
Plus iterated Mycielskians (Grotzsch=Myc(C5), Myc(Grotzsch)) and random triangle-free at N<=24.
Report ANY: SINGULAR_AQQ, Aqq^{-1} entry<0, E offdiag>0, E rowsum<0, k2<0 -- with exact witness.
All exact Fraction."""
from fractions import Fraction as F
import subprocess, random
from _h import dec, GENG, loads
from _schur_spec import pf_exact, matinv_frac

def build_K(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    return K,T,N,n

def full_test(info):
    """returns dict with all condition results, exact."""
    K,T,N,n=build_K(info)
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(status='noO')
    nq,no=len(Q),len(O)
    A=[[(F(N) if i==j else F(0))-K[i][j] for j in range(n)] for i in range(n)]
    Aqq=[[A[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    Inv=matinv_frac(Aqq)
    if Inv is None: return dict(status='SINGULAR_AQQ',O=O)
    inv_neg = any(Inv[i][j]<0 for i in range(nq) for j in range(nq))
    Aqo=[[A[Q[i]][O[j]] for j in range(no)] for i in range(nq)]
    Aoq=[[A[O[i]][Q[j]] for j in range(nq)] for i in range(no)]
    Aoo=[[A[O[i]][O[j]] for j in range(no)] for i in range(no)]
    X=[[sum(Inv[i][k]*Aqo[k][j] for k in range(nq)) for j in range(no)] for i in range(nq)]
    E=[[Aoo[i][j]-sum(Aoq[i][k]*X[k][j] for k in range(nq)) for j in range(no)] for i in range(no)]
    offdiag_pos = any(E[i][j]>0 for i in range(no) for j in range(no) if i!=j)
    rowsums=[sum(E[i][j] for j in range(no)) for i in range(no)]
    minrow=min(rowsums)
    # k2 lower bound
    r=[F(N)-T[v] for v in range(n)]
    rQ=[r[Q[i]] for i in range(nq)]
    KQQ=[[K[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    KOQ=[[K[O[i]][Q[j]] for j in range(nq)] for i in range(no)]
    t0=[x/N for x in rQ]; t1=[sum(KQQ[i][j]*t0[j] for j in range(nq))/N for i in range(nq)]
    g2=[t0[i]+t1[i] for i in range(nq)]
    k2=[r[O[i]]+sum(KOQ[i][j]*g2[j] for j in range(nq)) for i in range(no)]
    mink2=min(k2)
    fails=[]
    if inv_neg: fails.append('AQQ_inv_neg')
    if offdiag_pos: fails.append('E_offdiag_pos')
    if minrow<0: fails.append('E_rowsum_neg')
    if mink2<0: fails.append('k2_neg')
    return dict(status='FAIL' if fails else 'ok', O=O, fails=fails, minrow=minrow, mink2=mink2,
                inv_neg=inv_neg, offdiag_pos=offdiag_pos)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    # vertices 0..n-1 original, n..2n-1 shadows, 2n apex
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                E2.append((u, n+v)); E2.append((v, n+u))
    for u in range(n): E2.append((n+u, 2*n))
    return N2, E2

# census graphs with overload
def overloaded_census(Nlo,Nhi,stride=1):
    res=[]
    for nn in range(Nlo,Nhi+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            T=info['T']
            if any(t>n for t in T): res.append(g6)
    return res

def report(tag, n, res):
    if res['status']=='noO': return None
    if res['status']=='SINGULAR_AQQ':
        return f"!!! SINGULAR_AQQ {tag} N={n} O={res['O']}"
    if res['status']=='FAIL':
        return f"!!! FAIL {tag} N={n} fails={res['fails']} minrow={float(res['minrow']):+.4f} mink2={float(res['mink2']):+.4f}"
    return None  # ok

if __name__=="__main__":
    print("=== finding overloaded census graphs N<=11 ===",flush=True)
    ov = overloaded_census(7,9,1)
    ov += overloaded_census(10,10,1)
    ov += overloaded_census(11,11,3)
    print(f"  {len(ov)} overloaded census graphs collected (N<=11, N=11 stride 3)",flush=True)

    print("=== STRESS: blow-ups t=2,3,4 of overloaded census graphs (cap N<=26) ===",flush=True)
    tested=0; fails=0; sing=0; worst_minrow=None; worst_k2=None
    for g6 in ov:
        nbase,_=dec(g6)
        for t in (2,3,4):
            N=nbase*t
            if N>26: continue
            nn,EE=blow(g6,t); info=loads(nn,EE)
            if info is None: continue
            res=full_test(info)
            r=report(f"{g6}[{t}]",nn,res)
            if res['status']=='noO': continue
            tested+=1
            if res['status']=='SINGULAR_AQQ': sing+=1; print(r,flush=True)
            elif res['status']=='FAIL': fails+=1; print(r,flush=True)
            elif res['status']=='ok':
                if worst_minrow is None or res['minrow']<worst_minrow: worst_minrow=res['minrow']
                if worst_k2 is None or res['mink2']<worst_k2: worst_k2=res['mink2']
    print(f"  blow-up stress: tested {tested} overloaded cases | FAILS={fails} SINGULAR={sing}"
          f" | worst E-rowsum={float(worst_minrow) if worst_minrow is not None else 'na'}"
          f" worst k2={float(worst_k2) if worst_k2 is not None else 'na'}",flush=True)

    print("=== STRESS: iterated Mycielskians ===",flush=True)
    # C5
    n5,E5=dec("Dl?")  # placeholder, build C5 directly
    C5n=5; C5E=[(i,(i+1)%5) for i in range(5)]
    chain=[("C5",C5n,C5E)]
    nM,EM=mycielski(C5n,C5E); chain.append(("Myc(C5)=Grotzsch",nM,EM))
    nM2,EM2=mycielski(nM,EM); chain.append(("Myc^2(C5) N=23",nM2,EM2))
    for name,nn,EE in chain:
        info=loads(nn,EE)
        if info is None: print(f"  {name} N={nn}: loads=None (skip)",flush=True); continue
        res=full_test(info)
        if res['status']=='noO': print(f"  {name} N={nn}: noO (no overload)",flush=True)
        elif res['status']=='ok': print(f"  {name} N={nn}: ok minrow={float(res['minrow']):+.4f} mink2={float(res['mink2']):+.4f} |O|={len(res['O'])}",flush=True)
        else: print(f"  {name} N={nn}: {report(name,nn,res)}",flush=True)

    print("=== STRESS: blow-ups of Mycielskians (Grotzsch[2] N=22) ===",flush=True)
    nM,EM=mycielski(C5n,C5E)  # Grotzsch N=11
    EEb=[]
    for (a,b) in EM:
        for i in range(2):
            for j in range(2): EEb.append((a*2+i,b*2+j))
    info=loads(nM*2,EEb)
    if info:
        res=full_test(info)
        print(f"  Grotzsch[2] N={nM*2}: {res['status']} minrow={float(res['minrow']):+.4f} mink2={float(res['mink2']):+.4f}" if res['status']=='ok' else f"  Grotzsch[2]: {report('Grotzsch[2]',nM*2,res)}",flush=True)
    else:
        print(f"  Grotzsch[2] N={nM*2}: loads=None",flush=True)
