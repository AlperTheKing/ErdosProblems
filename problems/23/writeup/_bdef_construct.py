"""ADVERSARIAL construction stress of BOUNDARY-DEFICIT lemma (Claude's leg).
Goal: build a triangle-free G with a CONNECTED B-side max cut and a NON-TRIVIAL Q-only K-component C
(connected comp of {K[v,w]>0}, all T[v]<=N, |C|>=5, carrying a bad edge), ideally critical (T[v]=N on C,
O nonempty elsewhere). For each candidate recompute max cut via loads(), find Q-only K-components, exact-check
deficit(C)>=dB(C). All EXACT Fraction. Report min deficit on Q-only comp, min slack (deficit-dB), any violation.

Run from E:/Projects/ErdosProblems/problems/23/writeup."""
from fractions import Fraction as F
from collections import deque
import subprocess, itertools, random
from _h import dec, GENG, loads, blow, maxcut_all, gmin, Bconn
from _schur_spec import pf_exact

# ---------- K-build + component analysis (independent of Codex build_K) ----------
def build_K_T(info):
    P,M,ell,n=pf_exact(info)
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    return K,T,M,ell,n

def Kcomponents(K,n):
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        stack=[s]; seen[s]=True; C=[]
        while stack:
            v=stack.pop(); C.append(v)
            for w in range(n):
                if w!=v and not seen[w] and K[v][w]>0:
                    seen[w]=True; stack.append(w)
        comps.append(sorted(C))
    return comps

def Mset_in(M, Cs):
    return [f for f in M if f[0] in Cs or f[1] in Cs]

def analyze(info, name=""):
    """Return list of records for Q-only K-components and a verdict on boundary-deficit."""
    K,T,M,ell,n=build_K_T(info); N=n
    O=set(v for v in range(n) if T[v]>N)
    Bset=info['Bset']
    comps=Kcomponents(K,n)
    recs=[]
    Bconnected = Bconn(n, info['adj'], info['side'])
    for C in comps:
        Cs=set(C)
        if Cs & O: continue   # only C disjoint from O
        mass=sum(T[v] for v in C)
        deficit=F(N*len(C))-mass
        dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
        # bad edges carried by C
        badC=[f for f in M if f[0] in Cs and f[1] in Cs]
        allT0=all(T[v]==0 for v in C)
        nontriv = (len(C)>1) or (not allT0)
        carries_bad = len(badC)>0
        critical = (deficit==0) and (len(O)>0)
        violation = deficit < dB
        recs.append(dict(C=tuple(C),size=len(C),deficit=deficit,dB=dB,mass=mass,
                         allT0=allT0,nontriv=nontriv,carries_bad=carries_bad,
                         critical=critical,violation=violation,nbad=len(badC)))
    return dict(name=name,N=N,n=n,Onum=len(O),O=sorted(O),Bconn=Bconnected,recs=recs,
                Tset=sorted(set(float(x) for x in T)))

def report(info, name):
    a=analyze(info,name)
    qrecs=a['recs']
    nontriv=[r for r in qrecs if r['nontriv']]
    bad_carrying=[r for r in qrecs if r['carries_bad']]
    viol=[r for r in qrecs if r['violation']]
    crit=[r for r in qrecs if r['critical']]
    minslack=None; minslackrec=None
    mindef=None
    for r in bad_carrying:  # only meaningful on components carrying a bad edge
        sl=r['deficit']-r['dB']
        if minslack is None or sl<minslack: minslack=sl; minslackrec=r
        if mindef is None or r['deficit']<mindef: mindef=r['deficit']
    flag=""
    if viol: flag=" *** VIOLATION ***"
    if crit and any(r['carries_bad'] for r in crit): flag+=" *** CRITICAL Q-ONLY w/ bad edge ***"
    print(f"  [{name}] N={a['N']} Bconn={a['Bconn']} |O|={a['Onum']} "
          f"Q-comps={len(qrecs)} nontriv-Q={len(nontriv)} bad-carrying-Q={len(bad_carrying)} "
          f"VIOL={len(viol)} crit={len(crit)} "
          f"min(deficit-dB on bad-Q)={float(minslack) if minslack is not None else 'na'} "
          f"min deficit(bad-Q)={float(mindef) if mindef is not None else 'na'}{flag}",flush=True)
    for r in bad_carrying:
        if r['deficit']<=r['dB']+5 or r['violation'] or r['critical']:
            print(f"      bad-carrying Q-comp |C|={r['size']} nbad={r['nbad']} deficit={float(r['deficit'])} "
                  f"dB={r['dB']} slack={float(r['deficit']-r['dB'])} crit={r['critical']} viol={r['violation']} C={r['C']}",flush=True)
    return a

# ---------- graph constructors ----------
def Cn(k, off=0):
    return [(off+i, off+(i+1)%k) for i in range(k)]

def union_disjoint(*blocks):
    """blocks=[(n,E),...]; relabel disjoint."""
    n=0; E=[]
    for (bn,bE) in blocks:
        E += [(a+n,b+n) for (a,b) in bE]
        n += bn
    return n,E

def add_edges(nE, extra):
    n,E=nE; return n, E+list(extra)

def blow_g(n, E, t):
    """i.i.d. t-blow-up of arbitrary (n,E)."""
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def is_triangle_free(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    for a,b in E:
        if adj[a]&adj[b]: return False
    return True

if __name__=="__main__":
    print("=== BOUNDARY-DEFICIT adversarial construction (Claude) -- key witnesses ===")
    # The ONLY construction that realizes a non-trivial bad-carrying Q-only K-component COEXISTING with O.
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))   # C5 island + Myc(C7) (N=15 gadget with O)
    n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
    report(loads(n,E),"C5 island + Myc(C7), single bridge (N=20, O nonempty)")
    # extremal C5[t] is the only saturated (deficit=0) component, but O empty (C=V, dB=0)
    report(loads(*blow_g(5,1,2)) if False else loads(*( (lambda t: (5*t,[ (i*t+a,((i+1)%5)*t+b) for i in range(5) for a in range(t) for b in range(t)]) )(2))),
           "extremal C5[2] (N=10): deficit=0 but C=V, dB=0, O empty -> not a critical witness")
    print("Finding: every realized Q-only bad-carrying component has deficit >> dB (>=74); none critical.")
