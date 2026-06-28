"""Test whether A-alltie is a PURE geodesic fact, independent of max-cut / gamma-min.
For each small triangle-free graph, enumerate ALL 2-colorings 'side' (not just max cuts)
that make B connected and have bad edges + odd girth >= 5 in B-distance (ell>=5? -- no,
we allow ANY ell, but the triangle-free hyp means ell>=4 actually >=4? let's allow all).
Build T, mu, and check A-alltie. Goal: find the WEAKEST hypotheses under which A-alltie holds.

We test the raw geodesic statement:
  in a bipartite graph B (= cut graph), with M = monochromatic edges, each f in M closing a
  shortest odd cycle ell(f)=d_B(f)+1, p_f, T, mu defined as usual; then
  for a zero-mu B-edge uv with T(u)=N (N=#vertices), T(v)=0.

But N=#vertices is specific to the max-cut. For arbitrary cut, 'saturated' = T(u)=N is the
relevant threshold (since the certificate uses N*I-K). Test with the SAME threshold N=n.
"""
import subprocess
from fractions import Fraction as F
from itertools import product
from _h import dec, GENG, Bconn, bdist_restr, geos
from _aforce import build_info_for_cut, check_A

def run(nmin=6,nmax=9, maxcolorings=20000):
    for nn in range(nmin,nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot_cases=0; tot_viol=0; wit=None; ncolorings=0
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            # all 2-colorings with vertex 0 fixed to side 0 (symmetry)
            for bits in product([0,1], repeat=n-1):
                side=[0]+list(bits)
                info=build_info_for_cut(n,adj,side)
                if info is None: continue
                ncolorings+=1
                cases,viol=check_A(info,n)
                tot_cases+=cases; tot_viol+=len(viol)
                if viol and wit is None:
                    wit=(g6,side,viol[:3],info['G'],info['beta'])
        print(f"  N={nn}: ALL cuts ({ncolorings} valid colorings): A-cases={tot_cases} A-viol={tot_viol}"
              + (f"  WIT {wit}" if wit else ""), flush=True)

if __name__=="__main__":
    print("=== A-alltie over ALL 2-colorings (pure geodesic test, threshold N=n) ===")
    run(6,9)
