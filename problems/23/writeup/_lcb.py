"""Codex block 24: LCB / self-cap. For a full K-component C with C disjoint from O, O nonempty, C carrying a bad edge:
   max_{v in C} T[v] <= |C|   (equivalently Gamma_C = sum_{v in C}T[v] <= |C|^2).
If true => boundary-deficit (N|C|-Gamma_C >= (N-|C|)|C| >= dB(C)). Exact Fraction.
Also directly inspect the workflow's claimed Gamma_C>|C|^2 witness I?AAD@wF_ against the strict filter."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _superphi import blow
from _bdef import components

def analyze(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=set(v for v in range(n) if T[v]>N)
    # which bad edges have support inside each vertex set: a comp is bad-carrying if some bad edge support subset C
    supps=[set(d.keys()) for d in P]
    res=[]
    if not O: return res,N   # O must be nonempty
    for C in components(K,n):
        Cs=set(C)
        if Cs & O: continue            # C disjoint from O
        badcarry=any(s and s<=Cs for s in supps)
        if not badcarry: continue       # C must carry a bad edge
        maxT=max(T[v] for v in C)
        GammaC=sum(T[v] for v in C)      # = mass(C) = Gamma_C
        dB=sum(1 for (a,b) in info['Bset'] if (a in Cs)^(b in Cs))
        viol = (maxT>len(C))             # LCB violation
        res.append((tuple(C),float(maxT),len(C),float(GammaC),len(C)**2,dB,viol))
    return res,N

def show(name,info):
    res,N=analyze(info)
    if not res:
        print(f"  {name} (N={info['n']}): no bad-carrying Q-only comp with O nonempty (LCB vacuous)",flush=True); return
    viol=[r for r in res if r[6]]
    print(f"  {name} (N={N}): bad-carrying Q-only comps={len(res)} LCB-viol={len(viol)}",flush=True)
    for r in res:
        tag=" *** LCB VIOLATION" if r[6] else ""
        print(f"      C(|C|={r[2]}): maxT={r[1]} vs |C|={r[2]} | Gamma_C={r[3]} vs |C|^2={r[4]} dB={r[5]}{tag}")

# direct witness check
print("=== direct check of workflow witness I?AAD@wF_ ===")
n,E=dec("I?AAD@wF_"); info=loads(n,E)
P,M,ell,nn=pf_exact(info); N=nn
K=[[F(0)]*nn for _ in range(nn)]
for d in P:
    it=list(d.items())
    for a in range(len(it)):
        va,pa=it[a]
        for b in range(len(it)):
            vb,pb=it[b]; K[va][vb]+=pa*pb
T=[sum(K[v][w] for w in range(nn)) for v in range(nn)]
O=[v for v in range(nn) if T[v]>N]
print(f"  I?AAD@wF_: N={N} O={O} (O nonempty? {len(O)>0})")
for C in components(K,nn):
    Cs=set(C); GammaC=sum(T[v] for v in C); maxT=max(T[v] for v in C)
    print(f"    comp |C|={len(C)} C={C}: meets-O={bool(Cs&set(O))} Gamma_C={float(GammaC)} |C|^2={len(C)**2} maxT={float(maxT)}")

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        ncomp=0; viol=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            res,N=analyze(info)
            for r in res:
                ncomp+=1
                if r[6]: viol+=1; wit=wit or (g6,r)
        print(f"  census N={nn}(str{stride}): bad-carrying Q-only(O!=empty) comps={ncomp} LCB-viol={viol}"+(f" WIT {wit}" if wit else ""),flush=True)

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    print("=== LCB self-cap exact stress (bad-carrying Q-only comp, O nonempty) ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); show(g6,loads(n,E))
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn>24: continue
        info=loads(nn,EE)
        if info: show(f"{g6}[{t}]",info)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    for name,(nn,EE) in [("Myc(Grotzsch) N=23",(n2,E2)),("Myc(C7) N=15",(m1,F1))]:
        info=loads(nn,EE)
        if info: show(name,info)
    run_census(11,7,1)
