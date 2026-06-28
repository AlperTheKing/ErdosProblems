"""C-alltie transport probe. For the CONTRAPOSITIVE structure: a Q-only K-component C
(disjoint from O) with a saturated vertex v (T=N) B-adjacent to a dead z (T=0).
We dissect: deficit(C)=N|C|-Gamma_C, the B-boundary of C, handshake at v, and the
internal-vs-boundary B-edge accounting. We want a discharging invariant that forces O-meet.

Key quantities per K-component C (K-closed):
  - Gamma_C = sum_{v in C} T(v)  (= sum_{f:supp subset C} ell^2)  [mass identity]
  - deficit(C) = N|C| - Gamma_C = 1_C^T (N I - K) 1_C  >= 0  (must, for SPEC)
  - dB(C) = # B-edges with exactly one endpoint in C (boundary)
  - intB(C)= # B-edges with both endpoints in C
For a CRITICAL C: T==N on C, deficit=0, Gamma_C=N|C|.

We test, over census + blowups + Mycielskians (incl. adversarial constructions that
realize Q-only bad-carrying components), several candidate transport invariants:
  (I1) deficit(C) >= dB(C)        [BOUNDARY-DEFICIT, known true]
  (I2) Gamma_C <= |C|^2           [LCB self-cap, known sometimes FALSE]
  (I3) For a Q-only C: does C ever contain a saturated vertex?  (sat-in-Q-only)
  (I4) handshake at saturated v in Q-only C: sum_{e at v} mu(e) = 2N - D(v); how much
       of that mu lands on boundary edges of C vs internal? (boundary mu of crit comp)
Exact Fraction.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _zmu import mu_edges, mycielski
from _superphi import blow

def components(info):
    """K-components via geodesic union-find; return list of (vertexset)."""
    n=info['n']; cyc=info['cyc']
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: par[ra]=rb
    for f,Ps in cyc.items():
        for P in Ps:
            for i in range(1,len(P)): union(P[0],P[i])
    comp={}
    for v in range(n): comp.setdefault(find(v),set()).add(v)
    return list(comp.values()), find

def analyze(name, info):
    if info is None: return
    n=info['n']; T=info['T']; N=n; adj=info['adj']; side=info['side']; Bset=info['Bset']
    O=set(v for v in range(N) if T[v]>N)
    comps,_=components(info)
    mu=mu_edges(info)
    out=[]
    for C in comps:
        load=sum(T[v] for v in C)              # = Gamma_C
        if load==0: continue                   # dead/isolated, skip
        meetsO = bool(C & O)
        deficit = N*len(C) - load
        dB=sum(1 for (a,b) in Bset if (a in C) ^ (b in C))
        intB=sum(1 for (a,b) in Bset if (a in C) and (b in C))
        sat=[v for v in C if T[v]==N]
        # critical?  T==N on all of C
        crit = all(T[v]==N for v in C)
        # dead B-neighbors of saturated vertices in C
        sat_with_dead=[]
        for v in sat:
            deadnb=[w for w in adj[v] if side[w]!=side[v] and T[w]==0]
            if deadnb: sat_with_dead.append((v,deadnb))
        out.append(dict(C=sorted(C),sz=len(C),GammaC=load,deficit=deficit,dB=dB,intB=intB,
                        meetsO=meetsO,crit=crit,nsat=len(sat),sat_with_dead=sat_with_dead))
    qonly=[c for c in out if not c['meetsO']]
    qonly_sat=[c for c in qonly if c['nsat']>0]
    qonly_satdead=[c for c in qonly if c['sat_with_dead']]
    crit_qonly=[c for c in qonly if c['crit']]
    print(f"{name} (N={n}): |O|={len(O)} comps(loaded)={len(out)} "
          f"Q-only={len(qonly)} Q-only-with-sat={len(qonly_sat)} "
          f"Q-only-sat-deadnb={len(qonly_satdead)} CRIT-Q-only={len(crit_qonly)}")
    # LCB check on Q-only components
    for c in qonly:
        lcb = c['GammaC'] <= c['sz']**2
        bdef = c['deficit'] >= c['dB']
        flag=""
        if c['nsat']>0: flag+=" SAT!"
        if c['sat_with_dead']: flag+=" SATDEAD!!"
        print(f"    Q-only C sz={c['sz']} GammaC={c['GammaC']} deficit={c['deficit']} "
              f"dB={c['dB']} LCB(<=sz^2={c['sz']**2}):{lcb} BDEF:{bdef} crit={c['crit']}{flag}")
    return out

if __name__=="__main__":
    print("=== C-alltie transport probe: Q-only K-component structure ===")
    gate=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","I??CABoNo","I??CF@wFo","J??CBAPFvo?"]
    for g6 in gate:
        n,E=dec(g6); analyze(g6, loads(n,E))
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t)
        if nn<=26: analyze(f"{g6}[{t}]", loads(nn,EE))
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1)
    for name,(nn,EE) in [("Grotzsch N=11",(n1,E1)),("Myc(Grotzsch) N=23",(n2,E2))]:
        analyze(name, loads(nn,EE))
