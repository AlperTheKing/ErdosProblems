"""Run the SPECTRAL-SEAM deterministic switch family on the h_blowup(t) rigid tier family (t=1..5)
and glued C5 chains. This is the canonical hard case (rigid W={5t,8t}, Gamma-drop 24t, t^2 violating rows).

Also outputs, per bad cut, the EXACT DELTA-Gamma of the fired switch and checks it equals
  (ell_long^2 - ell_short^2) * (multiplicity)   ... to validate the ell^2-recut mechanism.
"""
from fractions import Fraction as F
from _h import dec, Bconn, bdist_restr, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2

def h_blowup(t):
    n, edges = dec("H?AFBo]")
    base_side=[int(c) for c in "111110000"]
    out=[]; side=[]
    for i in range(n): side+=[base_side[i]]*t
    for u,v in edges:
        for a in range(t):
            for b in range(t):
                out.append((u*t+a, v*t+b))
    return n*t, out, side

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gamma_of(n,adj,s):
    G=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v)
                if d<0: return None
                G+=(d+1)**2
    return G

def seam_switch(n,adj,side):
    """Deterministic seam family. Returns (label, W, drop) for first admissible descent, else None."""
    st=struct_for_side(n,adj,side)
    if st is None: return 'nostruct',None,None
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return 'noM',None,None
    N=F(n); K2=build_K2(n,M,cyc)
    R=[N*T[v]-sum(K2[v][w]*T[w] for w in range(n)) for v in range(n)]
    if all(R[v]>=0 for v in range(n)): return 'noviol',None,None
    Qs=[]
    for f in M:
        for Q in cyc[f]:
            Over=sum(T[u] for u in Q)-N*ell[f]
            Qs.append((Over,f,tuple(Q)))
    Qs.sort(key=lambda x:-x[0])
    Over_star,f_star,Q_star=Qs[0]
    a_s,b_s=f_star
    base_cut=cutsize(n,adj,side); base_G=gamma_of(n,adj,side)
    def tryW(W):
        if not W: return None
        s2=side[:]
        for v in W: s2[v]^=1
        if cutsize(n,adj,s2)!=base_cut: return None
        if not Bconn(n,adj,s2): return None
        g2=gamma_of(n,adj,s2)
        if g2 is None: return None
        return base_G-g2
    cands=[]
    for e in (a_s,b_s):
        cands.append(({e},'sgl_seam_end'))
        for w in adj[e]:
            if side[w]!=side[e]: cands.append(({e,w},'edge_seam'))
    for g in M:
        if ell[g]>ell[f_star]:
            for c in g:
                for e in (a_s,b_s): cands.append(({c,e},'long+short_end'))
                cands.append(({c},'sgl_long_end'))
    seen=set()
    for W,lab in cands:
        k=frozenset(W)
        if k in seen: continue
        seen.add(k)
        d=tryW(W)
        if d is not None and d>0: return lab,tuple(sorted(W)),d
    return 'NODESC',None,None

def run(name,n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    side=None
    # use inherited side for h_blowup, else all max cuts
    return adj

if __name__=="__main__":
    print("=== SPECTRAL-SEAM family on h_blowup(t) rigid tier + glued chains ===",flush=True)
    for t in range(1,6):
        n,E,side=h_blowup(t)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not Bconn(n,adj,side):
            print("h_blowup t=%d N=%d: inherited side NOT B-connected"%(t,n)); continue
        lab,W,drop=seam_switch(n,adj,side)
        print("h_blowup t=%d N=%d: fired=%s  W=%s  DELTA-Gamma-drop=%s  (predict 24t=%d, i.e. 7^2-5^2 per unit)"
              %(t,n,lab,W,str(drop),24*t),flush=True)
    # glued C5 chains
    from _Klocal_gate import glued_c5_chain
    for q in range(2,9):
        try:
            n,E,side=glued_c5_chain(q)
        except Exception as e:
            print("chain q=%d err %s"%(q,e)); continue
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not Bconn(n,adj,side): print("chain q=%d not Bconn"%q); continue
        lab,W,drop=seam_switch(n,adj,side)
        print("glued_c5_chain q=%d N=%d: fired=%s W=%s drop=%s"%(q,n,lab,W,str(drop)),flush=True)
