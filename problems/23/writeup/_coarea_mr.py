"""Compute the C25-ROW COAREA quantity m_r(P) EXACTLY (Codex 416 W(I) definition) and dump it next to the
   existing _layer_gate Z[r] and Tail0, to empirically pin the intended row-radius atom Z^row_r (Codex 417 fork).

   For a row P (geodesic of bad edge f, length L odd), cut side, K=K(P):
     geodesic-cycles = {(g,Q): g in M, Q in cyc[g], set(Q) subset K}.  C_Q cyclic order = Q (then edge g back).
     I_{i,r} = cyclic interval {P[(i+j)%L]: j=-r..r}  (saturates to V(P) when 2r+1>=L).
     W(I_{i,r}) = all W with  W cap V(P)=I_{i,r};  for each (g,Q): W cap set(Q) a cyclic interval of C_Q;
                  W subset K;  flip(B) connected and struct valid.
     C25(W)=d(W)+25 q(W),  q=deltaB-deltaM,  d=Gamma(flip)-Gamma.
     m_r(P) = (1/L) sum_i min_{W in W(I_{i,r})} C25(W).
   Dump m_r, (2r+1)*m_r cumulative, vs Z[r]; check sum_r(2r+1)m_r <= Tail0 and per-radius m_r<=Z[r].
   Exact Fraction.  Enumeration capped; flags empty W(I) and cap hits.
"""
import sys, itertools
from fractions import Fraction as F
from collections import deque
from _h import dec, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import deltas, flip, gamma_of

CAP=200000
REQUIRE_CONN=True   # (c) flip-B connected; --noconn sets False to test the relaxed lemma

def Kcomp(n,M,cyc,Pset):
    adjK=[set() for _ in range(n)]
    for g in M:
        for Q in cyc[g]:
            for a in Q:
                for b in Q:
                    if a!=b: adjK[a].add(b)
    seen=set(Pset); dq=deque(Pset)
    while dq:
        u=dq.popleft()
        for w in adjK[u]:
            if w not in seen: seen.add(w); dq.append(w)
    return seen

def cyclic_intervals(order):
    """all cyclic-interval arcs (as frozensets) of cycle given by vertex list 'order': empty, full, and every
       contiguous arc of length 1..L-1."""
    L=len(order); arcs=[frozenset()]
    full=frozenset(order)
    for s in range(L):
        cur=set()
        for ln in range(1,L):
            cur.add(order[(s+ln-1)%L])
            arcs.append(frozenset(cur))
    arcs.append(full)
    # dedup
    out=[]; seen=set()
    for a in arcs:
        if a not in seen: seen.add(a); out.append(a)
    return out

def interval_Iir(P,i,r):
    L=len(P)
    if 2*r+1>=L: return frozenset(P)
    return frozenset(P[(i+j)%L] for j in range(-r,r+1))

def WI_members(n,adj,side,P,cyc_arcsets,I,nonpath,K,Gamma):
    """enumerate W = I ∪ S, S subset (K∖V(P)), with W∩V(Q) a cyclic interval on every geodesic-cycle
       and (c) flip-B connected + struct valid; yield (W, C25).  Enumerate over S subsets (tractable)."""
    base=set(I)
    capped = len(nonpath)>20
    rng = nonpath[:20] if capped else nonpath
    m=len(rng)
    for mask in range(1<<m):
        S=set(rng[j] for j in range(m) if (mask>>j)&1)
        W=base|S
        # arc consistency on every cycle (W∩V(P)=I holds by construction)
        ok=True
        for (Vq,arcs) in cyc_arcsets:
            if frozenset(W & Vq) not in arcs: ok=False; break
        if not ok: continue
        if not W: continue
        s2=flip(side,W)
        if REQUIRE_CONN and not Bconn(n,adj,s2): continue
        g1=gamma_of(n,adj,s2)
        if g1 is None: continue
        dB,dM=deltas(n,adj,side,W)
        C25=(g1-Gamma)+25*(dB-dM)
        yield frozenset(W),C25
    return

def row_mr(n,adj,side,M,ell,T,cyc,f,P):
    L=ell[f]; Gamma=sum(T)
    K=Kcomp(n,M,cyc,set(P))
    Pset=set(P)
    cyc_arcsets=[]
    for g in M:
        for Q in cyc[g]:
            if set(Q)<=K:
                cyc_arcsets.append((set(Q), set(cyclic_intervals(list(Q)))))
    nonpath=sorted(K-Pset)
    _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
    Tail0=sum((2*r+1)*Z[r] for r in range(n))
    res={'L':L,'Tail0':Tail0,'Z':Z,'mr':{},'empty':[],'emptyc':{}}
    for r in range(n):
        mins=[]; empt_centers=[]
        for i in range(L):
            I=interval_Iir(P,i,r)
            best=None
            for Wf,C25 in WI_members(n,adj,side,P,cyc_arcsets,I,nonpath,K,Gamma):
                if best is None or C25<best: best=C25
            if best is None: empt_centers.append(i); mins.append(None)
            else: mins.append(best)
        if empt_centers:
            res['empty'].append(r); res['emptyc'][r]=empt_centers
            # m_r with empty center = +inf; record as None but also the partial avg over nonempty
            nonempty=[x for x in mins if x is not None]
            res['mr'][r]=('INF', sum(nonempty)/L if nonempty else None, len(empt_centers))
        else:
            res['mr'][r]=sum(mins)/L
        if r>=(L-1)//2 + 2: break
    return res

def main():
    global REQUIRE_CONN
    argv=[a for a in sys.argv[1:] if a!="--noconn"]
    if "--noconn" in sys.argv: REQUIRE_CONN=False
    g6=argv[0] if len(argv)>0 else "H?AFBo]"
    sidestr=argv[1] if len(argv)>1 else "000000111"
    print("REQUIRE_CONN (flip-B connected) =",REQUIRE_CONN)
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=[int(c) for c in sidestr]
    st=struct_for_side(n,adj,side)
    if st is None: print("struct invalid"); return
    M,ell,T,mu,cyc=st
    print("g6=%s side=%s Gamma=%d badedges=%s"%(g6,sidestr,sum(T),[(g,ell[g]) for g in M]))
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f]: continue
            res=row_mr(n,adj,side,M,ell,T,cyc,f,list(P))
            print("-"*60)
            print("f=%s P=%s L=%d Tail0=%s"%(f,tuple(P),res['L'],res['Tail0']))
            print(" r |        m_r              |       Z[r]        | m_r<=Z[r]")
            ssum=F(0); allfin=True
            for r in sorted(res['mr']):
                mr=res['mr'][r]; Z=res['Z'][r]
                if isinstance(mr,tuple):  # has empty center(s) -> m_r = +inf
                    allfin=False
                    print(" %2d | +INF (%d empty ctr; partial=%s) | %-16s | (undef)"%(r,mr[2],mr[1],Z)); continue
                ssum+=(2*r+1)*mr
                ok = "Y" if mr<=Z else "N <<<"
                print(" %2d | %-23s | %-16s | %s"%(r,str(mr),str(Z),ok))
            tag = ("%s ; Tail0=%s ; <=Tail0: %s"%(ssum,res['Tail0'],ssum<=res['Tail0'])) if allfin else "(some m_r=+INF; sum undefined)"
            print(" sum_r(2r+1)m_r over finite radii = "+tag)
            if res['empty']: print(" EMPTY-CENTER radii (m_r=+INF):",{r:res['emptyc'][r] for r in res['empty']})

if __name__=="__main__":
    main()
