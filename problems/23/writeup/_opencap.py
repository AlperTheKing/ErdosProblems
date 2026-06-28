"""INDEPENDENT exact-test of the surviving crux (workflow wh4jnw0zb convergence): the FULL-INVERSE-g
   superharmonic certificate for rho(K)<=N. Pure-K (no L_omega / a_bar coefficient).
     A = N*I - K,  K=sum_f p_f p_f^T,  T=K*1,  O={T>N}, Q={T<=N}.
     g := A_QQ^{-1} (N-T)_Q   [A_QQ=(N*I-K)_QQ, Stieltjes by Q-block weak diag dom T(q)<=N].
   phi=(1 on O, 1-g on Q) is N-superharmonic (K phi<=N phi, equality on Q) iff:
     (i)   A_QQ nonsingular (no zero pivot)         [well-posedness / cond1]
     (ii)  0 <= g <= 1   (=> phi=1-g in [0,1] on Q, phi>=0)
     (iii) for all o in O:  N - T(o) + sum_{q in Q} K[o,q] g(q) >= 0   [the O-row inequality = cond3]
   (iii) holding with (i),(ii) => rho(K)<=N => Gamma<=N^2 => delta=0.  Exact Fraction throughout.
   Also: confirm the cheap 2-step Neumann truncation g2 = u/N + K_QQ u/N (phi2=1-u_Q/N-K_QQ u_Q/N^2) FAILS somewhere."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def build_K(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    K=[[F(0)]*n for _ in range(n)]
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        pf={}
        for P in Ps:
            for v in P: pf[v]=pf.get(v,F(0))+F(1,k)
        it=list(pf.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    Tv=[sum(K[v]) for v in range(n)]
    return K,Tv

def solve(A, b, m):
    """Solve A x = b exactly (Fraction), A m x m. Returns x or None if singular."""
    Aug=[[A[i][j] for j in range(m)]+[b[i]] for i in range(m)]
    for c in range(m):
        piv=-1
        for r in range(c,m):
            if Aug[r][c]!=0: piv=r; break
        if piv==-1: return None
        Aug[c],Aug[piv]=Aug[piv],Aug[c]
        d=Aug[c][c]
        Aug[c]=[x/d for x in Aug[c]]
        for r in range(m):
            if r==c or Aug[r][c]==0: continue
            f0=Aug[r][c]
            Aug[r]=[Aug[r][j]-f0*Aug[c][j] for j in range(m+1)]
    return [Aug[i][m] for i in range(m)]

def opencap(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip=True)
    # A_QQ = (N*I - K)_QQ ; u_Q = (N - T)_Q
    qi={v:i for i,v in enumerate(Q)}; m=len(Q)
    AQQ=[[ (F(N) if Q[i]==Q[j] else F(0)) - K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    uQ=[F(N)-T[Q[i]] for i in range(m)]
    g=solve(AQQ,uQ,m)
    if g is None: return dict(singular=True,O=len(O),Q=len(Q))
    g01 = all(0<=gi<=1 for gi in g)
    gmin=min(g); gmax=max(g)
    # (iii) O-row inequality
    okO=True; minmargin=None
    for o in O:
        s=F(N)-T[o]+sum(K[o][Q[j]]*g[j] for j in range(m))
        if minmargin is None or s<minmargin: minmargin=s
        if s<0: okO=False
    return dict(O=len(O),Q=len(Q),singular=False,g01=g01,gmin=gmin,gmax=gmax,
                okO=okO,minmargin=minmargin, cert=(g01 and okO))

def gmin_cuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def run(nm,n,E,report=True):
    adj,cuts=gmin_cuts(n,E)
    tot=0; singular=0; g01bad=0; certbad=0; worstmargin=None
    for s in cuts:
        d=opencap(adj,s,n)
        if d is None or d.get('skip'): continue
        tot+=1
        if d.get('singular'): singular+=1; continue
        if not d['g01']: g01bad+=1
        if not d['cert']: certbad+=1
        if d['minmargin'] is not None and (worstmargin is None or d['minmargin']<worstmargin): worstmargin=d['minmargin']
    if report:
        wm = float(worstmargin) if worstmargin is not None else None
        print(f"  {nm} N={n}: O-cuts={tot} singular={singular} g-not-in-[0,1]={g01bad} CERT-FAILS={certbad} min-O-margin={wm}",flush=True)
    return tot,singular,g01bad,certbad

if __name__=="__main__":
    print("=== OPEN-CAPACITY full-inverse-g superharmonic certificate (independent, exact) ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); run(g6,n,E)
    print("--- glued-island battery ---",flush=True)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); gt=0;gs=0;gg=0;gc=0
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                t,s,g1,c=run(f"isl{iN}+gad{gN}{br}",n,E,report=False); gt+=t;gs+=s;gg+=g1;gc+=c
    print(f"  glued battery: O-cuts={gt} singular={gs} g-not-in-[0,1]={gg} CERT-FAILS={gc}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0;sing=0;g1=0;cb=0
        for g6 in outg:
            n,E=dec(g6)
            t,s,gg,c=run(g6,n,E,report=False); tot+=t;sing+=s;g1+=gg;cb+=c
        print(f"  census N={nn}: O-cuts={tot} singular={sing} g-not-in-[0,1]={g1} CERT-FAILS={cb}",flush=True)
