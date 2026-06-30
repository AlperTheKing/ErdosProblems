"""B2 sub-lemma probe (decomposition 2T[v]=inc[v]+D[v]).
At each gamma-min connected-B max cut, record per-vertex residuals of candidate
sub-lemmas toward Tmax<=2N, and the structural data at the argmax-T vertex.
A positive max-residual on the gate = sub-lemma FALSE (counterexample found).
All Fraction-exact.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, blow
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint
from _wf_lrsproof_0 import gmin_cuts, cut_data, cut_degrees

def probe(name,n,E,worst):
    if not is_triangle_free(n,E): return
    adj,cuts=gmin_cuts(n,E)
    for s in cuts:
        cd=cut_data(n,adj,s)
        if cd is None: continue
        N=cd['N']; dc,dm=cut_degrees(cd)
        for v in range(N):
            Tv=cd['T'][v]
            cands={'S2_inc_le_2N':cd['inc'][v]-2*N,
                   'S3_D_le_2N':cd['D'][v]-2*N,
                   'S4_D_le_inc':cd['D'][v]-cd['inc'][v],
                   'B2_T_le_2N':Tv-2*N,
                   'S7_inc_le_dc_N': cd['inc'][v]-dc[v]*N,   # mu(e)<=N would give this
                   }
            for k,val in cands.items():
                if val>worst[k]['val']:
                    worst[k]={'val':val,'where':name,'v':v,'N':N,'Tv':float(Tv),
                              'inc':float(cd['inc'][v]),'D':float(cd['D'][v]),
                              'dc':dc[v],'dm':dm[v],
                              'maxmu':float(max((m for m in cd['mu'].values()),default=0))}

if __name__=="__main__":
    worst={k:{'val':F(-10**9)} for k in
           ['S2_inc_le_2N','S3_D_le_2N','S4_D_le_inc','B2_T_le_2N','S7_inc_le_dc_N']}
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg: probe("c"+g6,*dec(g6),worst)
        print(f"  census N={nn} done; B2 residual so far={float(worst['B2_T_le_2N']['val']):.4f}",flush=True)
    from _verify_two_lane import build_two_lane
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); probe(f"two-lane{L}",n,E,worst)
    for t in range(1,7): probe(f"C5[{t}]",*blow(t),worst)
    cur=(5,Cn(5))
    for nm in ["Grotzsch11","Myc2C5_23"]:
        cur=mycielski(*cur)
        if cur[0]<=23: probe(nm,cur[0],cur[1],worst)
    cur=(7,Cn(7)); cur=mycielski(*cur); probe("MycC7_15",cur[0],cur[1],worst)
    # glued island+gadget
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>23 or not is_triangle_free(n,E): continue
                probe(f"isl{iN}+gad{gN}",n,E,worst)
    print("\n--- worst residual per sub-lemma (val>0 => FALSE on gate) ---")
    for k,d in worst.items():
        verdict="*** FALSE (counterexample) ***" if d['val']>0 else "holds on gate"
        print(f"  {k}: max residual={float(d['val']):.4f}  {verdict}")
        if 'where' in d:
            print(f"      witness {d['where']} v={d['v']} N={d['N']} T={d['Tv']:.3f} "
                  f"inc={d['inc']:.3f} D={d['D']:.3f} dc={d['dc']} dm={d['dm']} maxmu={d['maxmu']:.3f}")
