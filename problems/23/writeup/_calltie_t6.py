"""Handshake mu-flow identities per K-component, and a discharging test.
Verify:  sum_{e subset C} mu(e) = sum_{f in F_C} ell(f)*(ell(f)-1)   [derived identity]
and at a saturated v in C:  sum_{e at v} mu(e) = 2N - D(v), all internal to C.

DISCHARGING IDEA: define a flow on the K-component graph. The saturated v has the MAX possible
load N. We ask whether the mu-traffic out of v (=2N-D(v)) combined with the per-edge mu<= structure
can be 'absorbed' inside a Q-only component without reaching an overloaded vertex.

We test a candidate POTENTIAL: phi(w)=T(w). Along a B-edge e=(a,b) carrying mu(e)>0, the traffic
flows. Net flux of T across boundary? For the LP-dual style, check sum over C of (N-T(w)) (=deficit)
vs the mu that must exit. Since boundary mu=0, NO mu exits; everything recirculates. So the handshake
gives NO obstruction for a Q-only comp -- confirm by exhibiting the identity is the ONLY constraint.

Exact Fraction. Confirm identity 0-violation; print whether any LOCAL inequality is tight."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _zmu import mu_edges
from _calltie_glue import components_from_info
from _bdef_theory import build

def check(g6, info):
    n=info['n']; T=info['T']; N=n; Bset=info['Bset']; M=info['M']; ell=info['ell']; cyc=info['cyc']
    mu=mu_edges(info)
    comps=components_from_info(info)
    # supp of each bad edge
    supp={f:set(v for P in cyc[f] for v in P) for f in M}
    bad=0
    for C in comps:
        Cs=set(C)
        if sum(T[v] for v in C)==0: continue
        # internal mu sum
        intmu=F(0)
        for e,val in mu.items():
            a,b=tuple(e) if not isinstance(e,tuple) else e
            if a in Cs and b in Cs: intmu+=val
        FC=[f for f in M if supp[f] and supp[f]<=Cs]
        rhs=sum(F(ell[f])*(ell[f]-1) for f in FC)
        if intmu!=rhs:
            bad+=1
            print(f"  {g6} C={sorted(C)[:6]}: intmu={float(intmu)} != sum ell(ell-1)={float(rhs)}")
    return bad

if __name__=="__main__":
    print("=== mu-flow component identity:  sum_{e in C} mu = sum_{f in F_C} ell(ell-1) ===")
    tot=0; cnt=0
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            tot+=check(g6,info); cnt+=1
        print(f"  N={nn}: graphs={cnt} identity-violations(running)={tot}",flush=True)
    print(f"TOTAL identity violations: {tot}  (0 => mu-flow component identity holds)")
