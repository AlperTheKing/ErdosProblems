from fractions import Fraction as F
from _h import dec, GENG, blow
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint
from _wf_b2_probe import probe
import subprocess

worst={k:{'val':F(-10**9)} for k in ['S2_inc_le_2N','S3_D_le_2N','S4_D_le_inc','B2_T_le_2N','S7_inc_le_dc_N']}

# census N<=10
for nn in range(5,11):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg: probe("c"+g6,*dec(g6),worst)
    print(f"  census N={nn} done B2res={float(worst['B2_T_le_2N']['val']):.3f}",flush=True)

# blow-ups
for t in range(1,7):
    probe(f"C5[{t}]",*blow(t),worst)
print(f"  blowups done B2res={float(worst['B2_T_le_2N']['val']):.3f}",flush=True)

# iterated Mycielskians
cur=(5,Cn(5))
for nm in ["Grotzsch11","Myc2C5_23"]:
    cur=mycielski(*cur)
    if cur[0]<=23: probe(nm,cur[0],cur[1],worst)
cur=(7,Cn(7)); cur=mycielski(*cur); probe("MycC7_15",cur[0],cur[1],worst)
print(f"  mycielskians done B2res={float(worst['B2_T_le_2N']['val']):.3f}",flush=True)

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
print("  glued done",flush=True)

# two-lane (build directly, no module side effects)
from _verify_two_lane import build_two_lane
for L in (8,12):
    n,E,side,bad=build_two_lane(L); probe(f"two-lane{L}",n,E,worst)
print("  two-lane done",flush=True)

print("\n--- worst residual per sub-lemma (val>0 => FALSE on gate) ---",flush=True)
for k,d in worst.items():
    verdict="*** FALSE (counterexample) ***" if d['val']>0 else "holds on gate"
    print(f"  {k}: max residual={float(d['val']):.4f}  {verdict}")
    if 'where' in d:
        print(f"      witness {d['where']} v={d['v']} N={d['N']} T={d['Tv']:.3f} inc={d['inc']:.3f} D={d['D']:.3f} dc={d['dc']} dm={d['dm']} maxmu={d['maxmu']:.3f}")
