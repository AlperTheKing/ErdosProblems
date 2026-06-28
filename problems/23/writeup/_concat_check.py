"""Check the geodesic-concatenation argument on a KNOWN both-positive zero-mu edge.
Witness: I?\`DA_wN? edge (8,3): T(8)=5/2>0, T(3)=5>0, zero-mu.  (both positive -> A-alltie NOT triggered
since neither is N; but my concatenation argument, if correct, would wrongly force one to be 0.)
For the bad edge g through v=3 (g=(5,9) geo [5,1,7,3,9]) and u=8:
 - compute d_B(a,u),d_B(a,v),d_B(u,b),d_B(v,b) for a=5,b=9 and check the case analysis.
This will expose the flaw in my concatenation reasoning."""
from fractions import Fraction as F
from _h import dec, loads, bdist_restr
from _zmu import mu_edges

g6="I?`DA_wN?"
n,E=dec(g6); info=loads(n,E)
N=info['n']; T=info['T']; side=info['side']; adj=info['adj']; M=info['M']; ell=info['ell']; cyc=info['cyc']
mu=mu_edges(info)
print("N",N,"T",[str(t) for t in T])
print("side",side)
print("bad edges:")
for f in M: print("  ",f,"ell",ell[f],"geos",cyc[f])
# the zero-mu both-positive edge (8,3)
u,v=8,3
print(f"\nedge ({u},{v}): mu=",str(mu.get(frozenset((u,v)),F(0))),"T(u)=",str(T[u]),"T(v)=",str(T[v]))
print(f"side(u={u})={side[u]} side(v={v})={side[v]}")
# bad edges through v=3
for f in M:
    if any(v in P for P in cyc[f]):
        a,b=f
        print(f"\n bad edge g={f} a={a} b={b} ell={ell[f]} passes thru v={v}")
        for P in cyc[f]:
            if v in P:
                r=P.index(v)
                print(f"   geodesic {P}: v at position r={r} from a")
        dau=bdist_restr(adj,side,a,u); dav=bdist_restr(adj,side,a,v)
        dub=bdist_restr(adj,side,u,b); dvb=bdist_restr(adj,side,v,b)
        print(f"   d_B(a,u)={dau} d_B(a,v)={dav} d_B(u,b)={dub} d_B(v,b)={dvb}  (ell-1=d_B(a,b)={bdist_restr(adj,side,a,b)})")
        print(f"   is u on a g-geodesic? d_B(a,u)+d_B(u,b)={dau+dub} vs d_B(a,b)={bdist_restr(adj,side,a,b)}")
