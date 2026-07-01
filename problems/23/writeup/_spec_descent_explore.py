"""SPECTRAL/PERRON angle exploration for the DESCENT LEMMA.

On a B-connected MAX cut with some R(v)<0, examine:
  - the super-N direction of K2 (Perron structure),
  - Over(Q)=sum_{u in Q} T(u) - N*ell_f  for geodesics Q (the 'overloaded odd cycle' witness),
  - candidate deterministic switches W built from the geometry of the MOST overloaded geodesic,
  - whether ANY of a structured switch family is neutral, B-connected, and drops Gamma.

Reports, for each cut with an R(v)<0 witness:
  the max Over(Q) cycle, its structure, and which switch (if any) descends.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side
from _csmspec import build_K2

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

def analyze(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    K2=build_K2(n,M,cyc)
    # R(v)
    R={}
    for v in range(n):
        k2t=sum(K2[v][w]*T[w] for w in range(n))
        R[v]=N*T[v]-k2t
    viol=[v for v in range(n) if R[v]<0]
    if not viol: return
    acc['cuts_with_viol']+=1
    base_cut=cutsize(n,adj,side); base_G=gamma_of(n,adj,side)
    # Enumerate all geodesics Q, compute Over(Q).
    Qs=[]  # (Over, f, Q as tuple)
    for f in M:
        for Q in cyc[f]:
            Over=sum(T[u] for u in Q)-N*ell[f]
            Qs.append((Over,f,tuple(Q)))
    Qs.sort(key=lambda x:-x[0])
    maxOver=Qs[0][0]
    # === candidate switch family (deterministic), all built around geometry ===
    def try_switch(Wset):
        if not Wset: return None
        s2=side[:]
        for v in Wset: s2[v]^=1
        if cutsize(n,adj,s2)!=base_cut: return None
        if not Bconn(n,adj,s2): return None
        g2=gamma_of(n,adj,s2)
        if g2 is None: return None
        return base_G-g2  # >0 means descent
    found_lab=None
    # family 1: singletons on the max-Over cycle's vertices
    Qmax=set(Qs[0][2])
    for v in Qs[0][2]:
        d=try_switch({v})
        if d is not None and d>0: found_lab='sgl_on_maxOverQ'; break
    # family 2: the whole max-Over geodesic vertex set (odd cycle minus the bad edge)
    if found_lab is None:
        d=try_switch(Qmax)
        if d is not None and d>0: found_lab='fullmaxOverQ'
    # family 3: singleton at each violating vertex
    if found_lab is None:
        for v in viol:
            d=try_switch({v})
            if d is not None and d>0: found_lab='sgl_on_viol'; break
    # family 4: singleton at argmax T
    if found_lab is None:
        vmax=max(range(n),key=lambda v:T[v])
        d=try_switch({vmax})
        if d is not None and d>0: found_lab='sgl_argmaxT'
    # family 5: sym-diff of the two extreme geodesics of the max-Over bad edge (if 2+ geodesics)
    if found_lab is None:
        fbad=Qs[0][1]
        if len(cyc[fbad])>=2:
            A=set(cyc[fbad][0]); B=set(cyc[fbad][1]); sd=A^B
            d=try_switch(sd)
            if d is not None and d>0: found_lab='symdiff_geo'
    if found_lab is None:
        acc['nodesc']+=1
        if acc['first'] is None:
            acc['first']=(name,''.join(map(str,side)),str(maxOver),Qs[0][1],Qs[0][2],
                          [(v,str(R[v])) for v in viol])
    else:
        acc['lab'][found_lab]=acc['lab'].get(found_lab,0)+1

def gfam_allmaxcuts(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    from _h import maxcut_all
    cuts=maxcut_all(n,adj)
    mc=max(cutsize(n,adj,s) for s in cuts)
    for s in cuts:
        if cutsize(n,adj,s)==mc:
            analyze(name,n,adj,s,acc)

def main():
    acc=dict(cuts_with_viol=0,nodesc=0,lab={},first=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam_allmaxcuts("cen%d"%nn,n,E,acc)
        print("census N=%d: cuts_with_R<0=%d nodesc=%d labels=%s"%(nn,acc['cuts_with_viol'],acc['nodesc'],acc['lab']),flush=True)
    # h_blowup tier gadget
    def hblow(t):
        # path length tier gadget from the memory: N ~ 5t+3, with a non-gamma-min max cut
        # reuse blow(t) skeleton but this is just C5 blowup; the RIGID W={5t,8t} lives in a specific gadget.
        pass
    print("="*55)
    print("cuts with some R(v)<0:",acc['cuts_with_viol'])
    print("NO-DESCENT (structured family failed):",acc['nodesc'])
    print("descent label distribution:",acc['lab'])
    if acc['first']: print("FIRST NO-DESCENT:",acc['first'])
    print("VERDICT:", "structured spectral switch family DESCENDS on all census R<0 cuts" if acc['nodesc']==0 else "family INSUFFICIENT (need richer W)")

if __name__=="__main__":
    main()
