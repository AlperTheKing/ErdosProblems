"""Fast |O|=1 dissection: census N<=10 + hard instances; answer deg_omega(o)>=Do and LB1>=Do quickly."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _angleD_O1 import gmin_sides
from _angleD_O1_dissect import dissect
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free

def run(label, items):
    t=0;dg=0;l1=0;lm=0;ov=0; mins={'deg':None,'lb1':None}
    for nn,EE in items:
        adj,sides=gmin_sides(nn,EE)
        for s in sides:
            d=dissect(adj,s,nn)
            if d is None: continue
            t+=1
            if d['deg_ge']: dg+=1
            if d['LB1_ge']: l1+=1
            if d['LBmin_ge']: lm+=1
            if d['ovn']>0: ov+=1
            for k,val in [('deg',d['deg']/d['Do']),('lb1',d['LB1']/d['Do'])]:
                if d['Do']>0 and (mins[k] is None or val<mins[k]): mins[k]=val
    print(f"  {label}: |O|=1={t} deg>=Do:{dg} LB1>=Do:{l1} LBmin>=Do:{lm} ovl-nbr:{ov} "
          f"min deg/Do={float(mins['deg']) if mins['deg'] else None} min LB1/Do={float(mins['lb1']) if mins['lb1'] else None}",flush=True)

if __name__=="__main__":
    print("=== FAST |O|=1: deg_omega(o)>=Do (simplest)? vs LB1>=Do (star) ===")
    for nn in (8,9,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        run(f"census N={nn}", [dec(g6) for g6 in outg])
    hard=[]
    n1,E1=mycielski(5,Cn(5)); n2,E2=mycielski(n1,E1)
    hard += [(n1,E1),(n2,E2),mycielski(7,Cn(7))]
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>24 or not is_triangle_free(n,E): continue
                hard.append((n,E))
    run("HARD (Myc/glued)", hard)
