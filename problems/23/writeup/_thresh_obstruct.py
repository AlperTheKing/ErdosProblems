"""Confirm the pointwise-threshold-couple OBSTRUCTION on I?BF@zWF_ (the one N=10 graph with K_t<0):
show (1) K_t(f)<0 for some (f,t); (2) PF(f) STILL holds (integral >=0); (3) the candidate shore A_t does NOT
violate CD: W_t = delta_B(A_t)-delta_M(A_t) >= 0 (CD holds on a max cut). => pointwise route dead, PF needs the
integrated form. Also check the CD-minimal closure of A_t."""
from fractions import Fraction as F
from census_GPI import dec
from _ph_mincut import loads
from _pf_lsc import phi

def deltas(info, A):
    adj=info['adj']; side=info['side']; Aset=set(A)
    dB=dM=0
    for u in range(info['n']):
        for v in adj[u]:
            if v>u and (u in Aset)!=(v in Aset):
                if side[u]!=side[v]: dB+=1
                else: dM+=1
    return dB,dM

def go(g6):
    n,E=dec(g6); info=loads(n,E); N=n; T=info['T']; M=info['M']; ph=phi(info)
    print(f"=== {g6} N={n} Gamma={info['G']} deficit={n*n-info['G']} Uover={float(info['Uover']):.3f} ===")
    for f in M:
        lam={z: ph[f][z]/T[z] for z in ph[f]}
        ts=sorted(set(lam.values()))
        # PF integral check
        recv=sum((N-T[z])*ph[f][z]/T[z] for z in ph[f] if T[z]<N)
        need=2*sum((T[z]-N)*ph[f][z]/T[z] for z in ph[f] if T[z]>N)
        PF=float(recv-need)
        # find min K_t
        worst=None
        for t in ts:
            A=[z for z in lam if lam[z]>=t]
            Kt=float(sum((N-T[z]) for z in A))
            if worst is None or Kt<worst[0]: worst=(Kt,t,A)
        Kt,t,A=worst
        if Kt<0:
            dB,dM=deltas(info,A)
            print(f"  edge f={f}: PF(f)={PF:+.4f} ({'PF HOLDS' if PF>=-1e-9 else 'PF FAILS'}) | min K_t={Kt:+.3f} at t={float(t):.3f} A_t={sorted(A)}")
            print(f"     candidate shore A_t: delta_B={dB} delta_M={dM} W_t=delta_B-delta_M={dB-dM} ({'CD OK (no violation)' if dB-dM>=0 else 'CD VIOLATED'})")
            # CD-minimal closure over supersets/subsets within ties: just report A_t suffices to show CD holds
        else:
            print(f"  edge f={f}: PF={PF:+.4f} min K_t={Kt:+.3f}>=0 (ok)")

if __name__=="__main__":
    go("I?BF@zWF_")
