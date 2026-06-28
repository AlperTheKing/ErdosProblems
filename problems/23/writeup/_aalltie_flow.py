"""A-alltie local-flow dump. For each (saturated u, zero-mu uv) case:
 - list u's B-neighbors w with mu(uw) and T(w)
 - the handshake: sum_w mu(uw) = 2N - D(u)
 - degree of u in B, and whether the zero-mu corridor extends (v's other neighbors)
We look for an invariant that forces T(v)=0. Specifically test sub-claims:
  (S1) For a zero-mu B-edge uv: T(u)=N  =>  v has NO B-neighbor w!=u with mu(vw)>0 carrying a geodesic
       that does NOT also pass through... -- i.e. is v's mu-incidence zero?  (is v itself mu-isolated?)
  (S2) handshake at v: sum_{e at v} mu(e) = 2 T(v) - D(v). If we can show sum_{e at v} mu(e)=0 then
       (since each term >=0) and D(v)=... -> we'd get 2T(v)=D(v).  Does T(v)=0 <=> v mu-isolated AND not an endpoint?
  Actually T(v)=0 <=> v on no geodesic <=> all mu at v are 0 AND v is not a bad-edge endpoint.
Dump exact values.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def dump_case(g6, info):
    N=info['n']; T=info['T']; adj=info['adj']; side=info['side']
    M=info['M']; ell=info['ell']
    mu=mu_edges(info)
    Mdeg=[0]*N
    Dv=[F(0)]*N
    for f in M:
        Dv[f[0]]+=ell[f]; Dv[f[1]]+=ell[f]; Mdeg[f[0]]+=1; Mdeg[f[1]]+=1
    rows=[]
    for e,val in mu.items():
        if val!=0: continue
        u0,v0=tuple(e)
        for (u,v) in [(u0,v0),(v0,u0)]:
            if T[u]!=N: continue
            # v's mu-incidence
            vnb=[w for w in adj[v] if side[w]!=side[v]]
            vmu=[(w, str(mu.get(frozenset((v,w)),F(0))), str(T[w])) for w in vnb]
            sum_mu_v=sum(mu.get(frozenset((v,w)),F(0)) for w in vnb)
            rows.append({
                'g6':g6,'u':u,'v':v,'Tv':str(T[v]),'Dv':str(Dv[v]),'Mdeg_v':Mdeg[v],
                'sum_mu_v':str(sum_mu_v),'vmu':vmu,
                'handshake_v_rhs':str(2*T[v]-Dv[v]),
            })
    return rows

if __name__=="__main__":
    print("=== A-alltie: is v (far end) mu-isolated AND non-endpoint? (T(v)=0 decomposition) ===")
    # sub-claim counters over census
    for nn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        cases=0; v_mu_nonzero=0; v_is_endpoint=0; tv_nonzero=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            T=info['T']; N=info['n']; adj=info['adj']; side=info['side']
            mu=mu_edges(info)
            M=info['M']
            endpts=set()
            for f in M: endpts.add(f[0]); endpts.add(f[1])
            for e,val in mu.items():
                if val!=0: continue
                u0,v0=tuple(e)
                for (u,v) in [(u0,v0),(v0,u0)]:
                    if T[u]!=N: continue
                    cases+=1
                    vnb=[w for w in adj[v] if side[w]!=side[v]]
                    smv=sum(mu.get(frozenset((v,w)),F(0)) for w in vnb)
                    if smv!=0: v_mu_nonzero+=1
                    if v in endpts: v_is_endpoint+=1
                    if T[v]!=0: tv_nonzero+=1
        print(f"  N={nn}: cases={cases}  v-has-nonzero-mu={v_mu_nonzero}  v-is-bad-endpoint={v_is_endpoint}  T(v)!=0={tv_nonzero}", flush=True)
    print("--- dumps ---")
    for g6 in ["I??CABoNo","I??CF@wFo","J??CE?{{?]?"]:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        for r in dump_case(g6, info)[:3]:
            print(f"  {g6} u={r['u']} v={r['v']}: T(v)={r['Tv']} D(v)={r['Dv']} Mdeg(v)={r['Mdeg_v']} sum_mu_v={r['sum_mu_v']} (handshake rhs 2Tv-Dv={r['handshake_v_rhs']})")
            print(f"     v's B-nbrs (w,mu(vw),T(w)): {r['vmu']}")
