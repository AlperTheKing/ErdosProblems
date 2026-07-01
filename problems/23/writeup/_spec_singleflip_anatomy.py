"""Anatomy of a SINGLE-VERTEX seam flip W={z}, z = seam endpoint of max-Over geodesic.
For h_blowup(1) (N=9) and the raw H?AFBo] cut, show for z=8 (and z that fires):
  - neighbors of z, split by side
  - delta_B, delta_M of flipping z (must be 0 => neutral)
  - exact list of bad edges before/after and their ell => DELTA-Gamma decomposition
General principle to extract: flipping z is neutral iff z has equal #neighbors on each side (tie).
On a MAX cut every vertex has >=deg/2 on the opposite side; a TIE vertex (exactly deg/2 each) is
exactly a neutral single-flip. Then DELTA-Gamma = sum over newly-created bad edges ell^2 - removed bad edges ell^2.
"""
from fractions import Fraction as F
from _h import dec, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _csmspec import build_K2

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def bad_edges_ell(n,adj,s):
    out=[]
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v); out.append(((u,v), d+1 if d>=0 else None))
    return out

def anat(n,E,side,z):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    same=[w for w in adj[z] if side[w]==side[z]]
    opp=[w for w in adj[z] if side[w]!=side[z]]
    print("  vertex z=%d deg=%d  #same-side=%d  #opp-side=%d  (neutral single-flip <=> equal)"
          %(z,len(adj[z]),len(same),len(opp)))
    be0=bad_edges_ell(n,adj,side)
    s2=side[:]; s2[z]^=1
    be1=bad_edges_ell(n,adj,s2)
    G0=sum(l*l for _,l in be0 if l); G1=sum(l*l for _,l in be1 if l)
    print("    before bad:",be0,"Gamma=",G0)
    print("    after  bad:",be1,"Gamma=",G1,"Bconn_after=",Bconn(n,adj,s2))
    print("    DELTA-Gamma=",G1-G0)
    # decomposition: edges from z that flip status
    removed=[(z,w) for w in same]  # were bad (same side), now B
    created=[(z,w) for w in opp]   # were B, now bad (same side)
    print("    removed-bad (z-same nbrs):",same,"  created-bad (z-opp nbrs):",opp)

if __name__=="__main__":
    n,E=dec("H?AFBo]")
    side=[1,1,1,1,1,1,0,0,0]
    print("H?AFBo] cut 111111000:")
    for z in range(n):
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        same=sum(1 for w in adj[z] if side[w]==side[z]); opp=len(adj[z])-same
        if same==opp:  # neutral candidate
            print(" z=%d is a TIE vertex:"%z); anat(n,E,side,z)
    print()
    # h_blowup(1) with base_side 111110000
    side2=[1,1,1,1,1,0,0,0,0]
    print("H?AFBo] cut 111110000 (h_blowup base), z=8:")
    anat(n,E,side2,8)
