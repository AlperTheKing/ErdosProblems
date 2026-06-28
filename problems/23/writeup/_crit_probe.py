"""Two probes:
 (P1) Is every O-isolated KQQ-component a SINGLETON? (empirically). If so, criticality is trivially
      ruled out: a singleton {q} has block [N-K[q,q]], K[q,q]<=S(q)<=T(q)/5<N => block>0.
      But O-isolated comp of size>=2 with all saturated would be critical. Count O-isolated comps by size.
 (P2) x>0 with A_QQ x>0 criterion. Test candidate x and report worst (A_QQ x)[q].
      Candidates: x=1 (gives r+leak, =0 sometimes), x=ones with small global tilt, and
      x = (N - K_QQ-rowsum + eps)-type. Also test x_q = 1 + small*(reachability to O in KQQ-graph)?
      Actually test the THEORETICALLY motivated x: x_q = 1 for all q gives (A_QQ 1)_q = r_q+leak_q>=0,
      zero exactly on critical/saturated-isolated rows. To get STRICT, perturb toward O: define
      h_q = number of KQQ-graph steps... too ad hoc. Just measure x=1 slack and the diagonal dominance
      defect, to confirm where strictness must come from.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, reach_components

def probe(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    m=len(Q); Oset=set(O)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    leak=[sum(K[Q[i]][o] for o in O) for i in range(m)]
    r=[F(N)-T[Q[i]] for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    # O-isolated comps and their sizes; saturation within them
    iso_sizes=[]; iso_ge2_sat=0
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        if all(leak[i]==0 for i in nodes):
            iso_sizes.append(len(nodes))
            if len(nodes)>=2 and all(r[i]==0 for i in nodes): iso_ge2_sat+=1
    # diagonal: K[q,q] vs S(q); confirm K[q,q] <= S(q) and the singleton bound
    # x=1 slack
    x1slack=[r[i]+leak[i] for i in range(m)]
    minx1=min(x1slack)
    return dict(N=N,m=m,ncomp=ncomp,iso_sizes=iso_sizes,
                max_iso_size=max(iso_sizes) if iso_sizes else 0,
                iso_ge2_sat=iso_ge2_sat,minx1slack=float(minx1))

def run(Nmax,Nmin=7):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0; maxiso=0; biggest=None; ge2sat=0; minx1=None
        sizehist={}
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=probe(info)
            if d is None: continue
            nt+=1
            if d['max_iso_size']>maxiso: maxiso=d['max_iso_size']; biggest=g6
            ge2sat+=d['iso_ge2_sat']
            for s in d['iso_sizes']: sizehist[s]=sizehist.get(s,0)+1
            if minx1 is None or d['minx1slack']<minx1: minx1=d['minx1slack']
        print(f"  N={nn}: with-O={nt} | max O-isolated-comp-size={maxiso}{(' @'+biggest) if biggest else ''} | "
              f"O-iso-size-hist={dict(sorted(sizehist.items()))} | O-iso(size>=2 & saturated)={ge2sat} | min(x=1 slack)={minx1}",flush=True)

if __name__=="__main__":
    print("=== Probe: O-isolated KQQ-component sizes; singleton => trivially non-critical ===")
    run(11,7)
