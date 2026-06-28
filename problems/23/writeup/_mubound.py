"""Test edge-traffic bounds and the saturation-corridor budget.
 (MU-MIN)  mu(e=(x,y)) <= min(T(x),T(y))   [each geodesic using e passes through both x and y]
 Combined with handshake at u (T(u)=N): sum_{w B-nbr u} mu(uw) = 2N - D(u), mu(uv)=0.
 Then bound: 2N - D(u) = sum_{w!=v} mu(uw) <= sum_{w!=v} T(w) (other-endpoint bound) -- record slack.
 Also test (MU-MIN-STRICT) and whether sum_{w} min(T(u),T(w)) relates.
 KEY new sub-claim to test:
 (SAT-CORRIDOR) if T(u)=N and uv zero-mu then for EVERY B-neighbor w of u, the edge uw has
     mu(uw)=T(w)  (i.e. ALL of w's traffic that could go through u, does)?  Probe exactly.
 And the real target reform: does T(u)=N force sum_{w B-nbr u, w!=v} T(w) >= 2N-D(u) with equality
     structure that excludes v?
Exact Fraction over census loads-cut."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def pf_through_edge(info, f, x, y):
    Ps=info['cyc'][f]; k=len(Ps); c=0
    for P in Ps:
        for i in range(len(P)-1):
            if {P[i],P[i+1]}=={x,y}: c+=1; break
    return F(c,k)

if __name__=="__main__":
    print("=== MU-MIN: mu(e)<=min(T(x),T(y)) ; saturation-corridor budget ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        mumin_viol=0
        sat_cases=0; budget_min_slack=None  # 2N-D(u) - sum_{w!=v}T(w) ; want <=0 means bound holds
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            N=info['n']; T=info['T']; adj=info['adj']; side=info['side']; M=info['M']; ell=info['ell']
            mu=mu_edges(info)
            # MU-MIN
            for e,val in mu.items():
                x,y=tuple(e)
                if val>min(T[x],T[y]): mumin_viol+=1
            # saturation corridor
            D=[F(0)]*N
            for f in M: D[f[0]]+=ell[f]; D[f[1]]+=ell[f]
            for e,val in mu.items():
                if val!=0: continue
                u0,v0=tuple(e)
                for (u,v) in [(u0,v0),(v0,u0)]:
                    if T[u]!=N: continue
                    sat_cases+=1
                    nbrs=[w for w in adj[u] if side[w]!=side[u]]
                    rhs=sum(T[w] for w in nbrs if w!=v)   # sum_{w!=v} T(w)
                    lhs=2*N-D[u]                            # = sum_w mu(uw) (mu(uv)=0)
                    slack=lhs-rhs                           # want <=0
                    if budget_min_slack is None or slack>budget_min_slack: budget_min_slack=slack
        print(f"  N={nn}: MU-MIN-viol={mumin_viol} | sat-corridor cases={sat_cases} max(2N-D(u) - sum_{{w!=v}}T(w))={None if budget_min_slack is None else float(budget_min_slack)} (<=0 means bound)", flush=True)
