"""Gate Codex 382 SINGLETON-CORE EXTRACTION + the one-port contrapositive.
   Singleton-core W_i = parity completion of path-span (i,i): include x_i; off-path B-component C with
   Att(C)={i} forced in, Att(C) disjoint from {i} out, straddler (Att(C) meets {i} and other indices) ->
   one parity class (enumerate tau).  Reduced cost  H_i = min_tau [ Lambda*mu + DeltaGamma ], Lambda=|E|N^2+1,
   disconnected forbidden.  H_i<0  <=>  exists neutral (mu=0) connected DeltaGamma<0 singleton completion.

   GATES on ALL connected-B max cuts (gamma-min AND non), census N<=10:
     (1) Tail_k(P)<0  =>  min_i H_i < 0 (a negative singleton port) AND its W_i meets the relaxed rotation invariant.
     (2) CONTRAPOSITIVE: min_i H_i >= 0  =>  min_k Tail_k(P) >= 0  (no row with all ports closed but Tail<0).
   ALL exact Fraction.
"""
import subprocess, itertools
import _crux_extract as cx
from _crux_extract import components_off_path
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def ell_map(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    return {frozenset(e):st[1][e] for e in st[0]}

def singleton_completions(n,adj,side,P,i):
    """yield frozenset(W_i) over straddler parity choices for span (i,i)."""
    Pset=set(P); comps=components_off_path(n,adj,side,Pset)
    forced={P[i]}; straddle=[]
    for C in comps:
        attach=set()
        for v in C:
            for w in adj[v]:
                if w in Pset and side[w]!=side[v]: attach.add(P.index(w))
        if not attach: continue
        if attach=={i}: forced|=C
        elif i in attach:  # straddles (i and others)
            col={}; start=next(iter(C)); col[start]=0; st=[start]
            while st:
                u=st.pop()
                for w in adj[u]:
                    if w in C and side[w]!=side[u] and w not in col: col[w]=col[u]^1; st.append(w)
            cls0={v for v in C if col.get(v,0)==0}; cls1={v for v in C if col.get(v,0)==1}
            straddle.append((cls0,cls1))
        # attach has indices but not i -> out
    choices=[()] if not straddle else itertools.product(*[(0,1)]*len(straddle))
    for ch in choices:
        W=set(forced)
        for s,pick in enumerate(ch): W|=(straddle[s][0] if pick==0 else straddle[s][1])
        yield frozenset(W)

def Hi_and_best(n,adj,side,em0,P,i,Lam):
    best=None; bestW=None; bestdec=None
    for W in singleton_completions(n,adj,side,P,i):
        dB,dM=deltas(n,adj,side,W); mu=dB-dM
        s2=flip(side,W)
        if not Bconn(n,adj,s2): continue
        em1=ell_map(n,adj,s2)
        if em1 is None: continue
        k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
        bd=sum(em1[e]**2 for e in added)-sum(em0[g]**2 for g in removed)
        rt=sum(em1[h]**2-em0[h]**2 for h in ret)
        dG=bd+rt
        cost=Lam*mu+dG
        if best is None or cost<best:
            best=cost; bestW=W
            no_len=all(em1[h]<=em0[h] for h in ret); strict_ret=any(em1[h]<em0[h] for h in ret)
            pair=(len(added)==len(removed)) and (sum(em1[e]**2 for e in added)<=sum(em0[g]**2 for g in removed))
            relaxed=(dG<0) and (mu==0) and (bd<=0) and no_len and pair and (bd<0 or strict_ret)
            bestdec=(mu,dG,bd,rt,relaxed)
    return best,bestW,bestdec

def main():
    g1_fail=0; g1_ok=0; g2_fail=0; rows_neg=0; g2_ex=None; g1_ex=None; rows_all=0
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); Lam=len(E)*n*n+1
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            mc,cuts=cx.all_max_cuts(n,adj,E)
            structs=[]
            for side in cuts:
                if not Bconn(n,adj,side): continue
                st=struct_for_side(n,adj,side)
                if st is None: continue
                structs.append((side,st))
            for (side,st) in structs:
                M,ell,T,cyc=st[0],st[1],st[2],st[4]
                if not M: continue
                em0=ell_map(n,adj,side)
                for f in M:
                    if ell[f]%2==0: continue
                    for P in cyc[f]:
                        if len(P)!=ell[f]: continue
                        _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                        mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                        rows_all+=1
                        # min_i H_i
                        minH=None; best_relaxed=False
                        for i in range(len(P)):
                            Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                            if Hi is None: continue
                            if minH is None or Hi<minH: minH=Hi
                            if dec_ and dec_[4] and dec_[1]<0: best_relaxed=True
                        if mintail<0:
                            rows_neg+=1
                            if minH is not None and minH<0:
                                g1_ok+=1
                                if not best_relaxed:
                                    g1_fail+=1
                                    if g1_ex is None: g1_ex=(g6,tuple(P),str(mintail),'no relaxed singleton')
                            else:
                                g1_fail+=1
                                if g1_ex is None: g1_ex=(g6,tuple(P),str(mintail),'no negative singleton port minH=%s'%minH)
                        # contrapositive (2): minH>=0 => Tail>=0
                        if (minH is None or minH>=0) and mintail<0:
                            g2_fail+=1
                            if g2_ex is None: g2_ex=(g6,n,tuple(P),str(mintail),str(minH))
    print("rows(all max cuts):",rows_all," Tail<0 rows:",rows_neg)
    print("(1) SINGLETON CORE  ok:",g1_ok," fail:",g1_fail, g1_ex or '')
    print("(2) CONTRAPOSITIVE minH>=0 => Tail>=0  violations:",g2_fail, g2_ex or '')
    print("VERDICT:", "ONE-PORT singleton proof structure HOLDS" if g1_fail==0 and g2_fail==0 and rows_neg>0 else "FAILS")

if __name__=="__main__":
    main()
