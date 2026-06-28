"""Probe H2's dependence on the threshold T(u)=N.
H2: T(u)=N, mu(uv)=0  =>  mu(vw)=0 for all B-nbrs w of v.
Test variants:
  (V0) require T(u)=N  (original H2)
  (V1) require only T(u)>0  and mu(uv)=0  -> does mu(vw)=0 still hold? (is saturation needed?)
  (V2) require T(u)>=N/2, etc.
Also: among H2 cases, record the structure: is v always such that v has NO geodesic through it
(T(v)=0) trivially because v sits 'past' u on the far side, OR is there real flow blocking?

Key alternative reduction to test (DEAD-CORRIDOR):
  (D) if mu(uv)=0 and T(u)=N, then T(v)=0 AND every B-nbr w!=u of v has T(w)=0 OR mu(vw)=0.
This is just A-alltie + H2 restated. Let's instead test the contrapositive-friendly:
  (E) 'mu(uv)=0 and T(u)>0' already forces 'v on NO geodesic that enters via a DIFFERENT edge using
      the layer past u'. Test: for zero-mu edge uv with T(u)>0 (not nec =N), is T(v)=0?
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _zmu import mu_edges

def Bnbrs(info,x):
    adj=info['adj']; side=info['side']
    return [w for w in adj[x] if side[w]!=side[x]]

def test(info):
    N=info['n']; T=info['T']; mu=mu_edges(info)
    # For each zero-mu edge uv, with orientation (u has higher/eq T), record:
    #   T(u), T(v), and whether all v-edges are zero-mu.
    out=dict(v0_case=0,v0_viol=0, # T(u)=N
             tup_case=0,tup_Tv_pos=0, # T(u)>0 (either endpoint), is T(v)=0?
             )
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        # E-test: zero-mu edge, both orientations
        for (a,b) in [(u,v),(v,u)]:
            if T[a]>0:
                out['tup_case']+=1
                if T[b]!=0: out['tup_Tv_pos']+=1
            if T[a]==N:
                out['v0_case']+=1
                nb=Bnbrs(info,b)
                if not all(mu.get(frozenset((b,w)),F(0))==0 for w in nb):
                    out['v0_viol']+=1
    return out

def run(nmin=7,nmax=11):
    agg=dict(v0_case=0,v0_viol=0,tup_case=0,tup_Tv_pos=0)
    for nn in range(nmin,nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        loc=dict(v0_case=0,v0_viol=0,tup_case=0,tup_Tv_pos=0)
        wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=test(info)
            for k in loc: loc[k]+=r[k]
            if r['tup_Tv_pos']>0 and wit is None: wit=g6
        for k in agg: agg[k]+=loc[k]
        print(f"  N={nn}: [E-test] zero-mu edge w/ T(u)>0: cases={loc['tup_case']} T(v)>0={loc['tup_Tv_pos']}"
              + (f" wit={wit}" if wit else "")
              + f"  | [H2] sat cases={loc['v0_case']} viol={loc['v0_viol']}", flush=True)
    print("TOTAL",agg)

if __name__=="__main__":
    print("=== H2 threshold probe ===")
    run(7,11)
