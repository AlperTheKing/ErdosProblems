"""Verify the traffic-load handshake identity (toward SAT-ZMU):
   sum_{e incident to v, e in B} mu(e)  ==  2*T(v) - D(v),   D(v)=sum_{f bad edge with v an endpoint} ell(f).
Derivation: a geodesic of f through v uses 2 incident edges if v interior, 1 if v is an endpoint of f.
Exact Fraction. Check on the 3 SAT-ZMU witnesses + a few named/overloaded graphs."""
from fractions import Fraction as F
from _h import dec, loads
from _zmu import mu_edges

def check(g6):
    n,E=dec(g6); info=loads(n,E); N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    mu=mu_edges(info)
    M=info['M']; ell=info['ell']
    bad=0
    for v in range(N):
        incident=[w for w in range(N) if w in adj[v] and side[w]!=side[v]]
        smu=sum(mu.get(frozenset((v,w)),F(0)) for w in incident)
        Dv=sum(ell[f] for f in M if v in f)
        rhs=2*T[v]-Dv
        if smu!=rhs: bad+=1; print(f"   MISMATCH {g6} v={v}: sum mu={smu} vs 2T-D={rhs}")
        # also: is any incident-edge mu zero while T[v]=N?  (SAT-ZMU at v)
        if T[v]==N:
            zero=[w for w in incident if mu.get(frozenset((v,w)),F(0))==0]
            print(f"   {g6} SAT v={v}: T={T[v]}=N, D(v)={Dv}, sum mu={float(smu)} over {len(incident)} edges; zero-mu incident={zero}")
    return bad

if __name__=="__main__":
    print("=== traffic-load handshake: sum_{e at v in B} mu(e) == 2 T(v) - D(v) ===")
    tot=0
    for g6 in ["J?AADBWeay?","J?ABBBWVCu?","J?`D@_w{EB?","G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        b=check(g6); tot+=b
        print(f"  {g6}: handshake mismatches={b}")
    print(f"TOTAL handshake mismatches: {tot} (0 => identity holds)")
