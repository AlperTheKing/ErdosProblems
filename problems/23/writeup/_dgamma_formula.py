"""Gate Codex 351 exact single-vertex-flip Delta_Gamma identity vs brute-force struct_for_side.
For a connected-B cut, vertex v: A=N_B(v) (blue nbrs), C=N_M(v) (bad nbrs). H = blue graph minus v. d_H = BFS dist in H.
Port distance D_P(x,y) = min( d_H(x,y), min_{p,p' in P, p!=p'} d_H(x,p)+2+d_H(p',y) ).
Formula:
  dGamma = sum_{xy in M, x,y!=v} ((D_C(x,y)+1)^2 - (D_A(x,y)+1)^2)
         + sum_{a in A} (2+min_{c in C} d_H(c,a))^2  -  sum_{c in C} (2+min_{a in A} d_H(a,c))^2.
Compare to struct_for_side(flip v) Gamma - Gamma whenever flipped B connected + valid. EXACT (integers)."""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

INF=10**9
def bfs_H(n,adj,side,v,src):
    # distance in blue graph excluding vertex v
    d=[INF]*n;
    if src==v: return d
    d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if w==v: continue
            if side[w]!=side[u] and d[w]==INF: d[w]=d[u]+1; q.append(w)
    return d
def Dport(x,y,distfrom,P):
    # distfrom[a] = dict of d_H from a ; need d_H(x,y), d_H(x,p), d_H(p',y)
    base=distfrom[x][y]
    best=base
    if len(P)>=2:
        for p in P:
            dxp=distfrom[x][p]
            if dxp>=INF: continue
            for pp in P:
                if pp==p: continue
                dppy=distfrom[pp][y]
                if dppy>=INF: continue
                best=min(best,dxp+2+dppy)
    return best

def dgamma_formula(n,adj,side,v,M):
    A=[w for w in adj[v] if side[w]!=side[v]]   # blue nbrs
    C=[w for w in adj[v] if side[w]==side[v]]   # bad nbrs
    # precompute d_H from every relevant source
    need=set(A)|set(C)
    for e in M:
        need.add(e[0]); need.add(e[1])
    distfrom={s:bfs_H(n,adj,side,v,s) for s in need}
    tot=0
    for (x,y) in M:
        if x==v or y==v: continue
        DC=Dport(x,y,distfrom,C); DA=Dport(x,y,distfrom,A)
        if DC>=INF or DA>=INF: return None
        tot += (DC+1)**2 - (DA+1)**2
    for a in A:
        mn=min((distfrom[c][a] for c in C), default=INF)
        if mn>=INF: return None
        tot += (2+mn)**2
    for c in C:
        mn=min((distfrom[a][c] for a in A), default=INF)
        if mn>=INF: return None
        tot -= (2+mn)**2
    return tot

def gamma_of(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    return sum(st[2])

def chk(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    # iterate gamma-min + a few max cuts via a simple enumeration is heavy; use all sides? too many.
    # Use struct on the canonical max cuts via gmins-like: instead, test on all 2^(n-1) sides is too many for n>12.
    # We test connected-B cuts that have bad edges, enumerated by a light pass for small n.
    from itertools import product
    if n>11: return
    for bits in product((0,1),repeat=n-1):
        side=[0]+list(bits)
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        if not M: continue
        G0=sum(T)
        for v in range(n):
            nb=side[:]; nb[v]^=1
            if not Bconn(n,adj,nb): continue
            g1=gamma_of(n,adj,nb)
            if g1 is None: continue
            f=dgamma_formula(n,adj,side,v,M)
            acc['tested']+=1
            if f is None:
                acc['none']+=1; continue
            if F(f)!=(g1-G0):
                acc['mismatch']+=1
                if acc['fmis'] is None: acc['fmis']=(name,n,v,f,str(g1-G0))
        # only test a bounded number of cuts per graph to keep it fast
        acc['cuts']+=1
        if acc['cuts']%50000==0: pass

if __name__=="__main__":
    acc=dict(tested=0,mismatch=0,none=0,cuts=0,fmis=None)
    # H?AFBo] explicitly
    n,E=dec('H?AFBo]'); chk('H?AFBo]',n,E,acc)
    print("  after H?AFBo]: tested=%d mismatch=%d none=%d"%(acc['tested'],acc['mismatch'],acc['none']),flush=True)
    for nn in range(5,10):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); chk('cen%s'%g6,n,E,acc)
        print("  census N=%d done (tested=%d mismatch=%d none=%d)"%(nn,acc['tested'],acc['mismatch'],acc['none']),flush=True)
    print("\n  dGAMMA FORMULA vs brute struct_for_side: tested=%d  mismatches=%d %s  (none/invalid=%d)"%(
        acc['tested'],acc['mismatch'],acc['fmis'] or '',acc['none']),flush=True)
    print("  === dGAMMA FORMULA %s ==="%("EXACT (0 mismatch) -- proof handle valid" if acc['mismatch']==0 else "FAILS"),flush=True)
