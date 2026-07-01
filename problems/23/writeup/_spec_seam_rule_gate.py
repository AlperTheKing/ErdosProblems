"""DETERMINISTIC SPECTRAL-SEAM SWITCH RULE + full battery gate.

RULE (given a B-connected MAX cut with some R(v)<0):
  1. Compute Over(Q)=sum_{u in Q}T(u)-N*ell_f for every geodesic Q of every bad edge f.
     By the identity R(v) = -sum_f (1/|cyc[f]|) sum_{Q ni v} Over(Q), R(v)<0 somewhere
     <=> some Over(Q)>0.  Let Q* = argmax Over(Q), with bad edge f*=(a*,b*), ell*=ell_{f*}.
  2. There must be a LONGER bad edge g=(c,d), ell_g > ell*, whose geodesic corridor SHARES
     the interior of Q* (a "length-tier seam": Q* is a short odd cycle nested inside a long one).
     Find g = the bad edge of maximal ell whose every geodesic contains BOTH a*,b* ... (candidate rules tried).
  3. Candidate switch W: flip one endpoint of the long edge g together with the seam endpoint of f*.
     We ENUMERATE a deterministic family and take the first admissible descending one, then report
     which rule fired, to discover the tightest deterministic description.

This gate: on every census/blowup/glued cut with R<0, does the seam family contain an admissible descent?
Reports coverage + label distribution + any no-descent witness."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, bdist_restr, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free

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
    N=F(n); K2=build_K2(n,M,cyc)
    R=[N*T[v]-sum(K2[v][w]*T[w] for w in range(n)) for v in range(n)]
    if all(R[v]>=0 for v in range(n)): return
    acc['cuts']+=1
    base_cut=cutsize(n,adj,side); base_G=gamma_of(n,adj,side)
    # all geodesics with Over
    Qs=[]
    for f in M:
        for Q in cyc[f]:
            Over=sum(T[u] for u in Q)-N*ell[f]
            Qs.append((Over,f,tuple(Q)))
    Qs.sort(key=lambda x:-x[0])
    Over_star,f_star,Q_star=Qs[0]
    a_s,b_s=f_star  # short-edge endpoints (endpoints of max-Over geodesic)
    def try_switch(W):
        if not W: return None
        s2=side[:]
        for v in W: s2[v]^=1
        if cutsize(n,adj,s2)!=base_cut: return None
        if not Bconn(n,adj,s2): return None
        g2=gamma_of(n,adj,s2)
        if g2 is None: return None
        return base_G-g2
    # DETERMINISTIC seam family:
    # For each endpoint e in {a_s,b_s} of the short (max-Over) edge, and each B-neighbor w of e that
    # lies OFF Q* on the long side, try W={e,w}.  Also try {e} alone.  Plus the mirror.
    fired=None
    cands=[]
    for e in (a_s,b_s):
        cands.append(({e},'sgl_seam_end'))
        for w in adj[e]:
            if side[w]!=side[e]:  # B-neighbor
                cands.append(({e,w},'edge_seam'))
    # long-edge driven: for each bad edge g with ell_g>ell[f_star], flip an endpoint of g with a seam end
    for g in M:
        if ell[g]>ell[f_star]:
            for c in g:
                for e in (a_s,b_s):
                    cands.append(({c,e},'long+short_end'))
                cands.append(({c},'sgl_long_end'))
    # dedup
    seen=set(); ded=[]
    for W,lab in cands:
        key=frozenset(W)
        if key in seen: continue
        seen.add(key); ded.append((W,lab))
    for W,lab in ded:
        d=try_switch(W)
        if d is not None and d>0:
            fired=(lab,d,tuple(sorted(W))); break
    if fired is None:
        acc['nodesc']+=1
        if acc['first'] is None:
            acc['first']=(name,''.join(map(str,side)),str(Over_star),f_star,Q_star)
    else:
        acc['lab'][fired[0]]=acc['lab'].get(fired[0],0)+1

def gfam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); mc=max(cutsize(n,adj,s) for s in cuts)
    for s in cuts:
        if cutsize(n,adj,s)==mc: analyze(name,n,adj,s,acc)

def main():
    acc=dict(cuts=0,nodesc=0,lab={},first=None)
    for nn in range(5,12):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
        print("census N=%d: R<0 cuts=%d nodesc=%d lab=%s"%(nn,acc['cuts'],acc['nodesc'],acc['lab']),flush=True)
    # glued islands (produce non-gamma-min tiered structures)
    from _h import blow
    for pairs in [((5,Cn(5)),(5,Cn(5)),[(0,5)]),((5,Cn(5)),(7,Cn(7)),[(0,5)]),
                  ((5,Cn(5)),(7,Cn(7)),[(0,5),(2,8)]),((7,Cn(7)),(7,Cn(7)),[(0,7)])]:
        a,b,br=pairs; nn,EE=union_disjoint(a,b); EE=EE+br
        if is_triangle_free(nn,EE): gfam("glue",nn,EE,acc)
    print("after glued islands: R<0 cuts=%d nodesc=%d"%(acc['cuts'],acc['nodesc']),flush=True)
    grN,grE=mycielski(5,Cn(5)); gfam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("R<0 cuts tested:",acc['cuts'])
    print("seam-family NO-DESCENT:",acc['nodesc'])
    print("label distribution:",acc['lab'])
    if acc['first']: print("FIRST NO-DESCENT:",acc['first'])
    print("VERDICT:", "seam family descends on all R<0 cuts" if acc['nodesc']==0 else "seam family INSUFFICIENT")

if __name__=="__main__":
    main()
