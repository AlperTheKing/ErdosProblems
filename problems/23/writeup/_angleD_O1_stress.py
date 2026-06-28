"""ANGLE D |O|=1 STRESS: push the star lower bound  LB1 = sum_{w~o,w in Q} w*RQ(w)/(w+RQ(w)) >= D_o
   on the KNOWN guardrail blind spots: iterated Mycielskians (N=23), blow-ups, glued islands.
   Only |O|=1 cuts are reported.  A FAIL would mean the clean star certificate is NOT a theorem
   (need a richer 2-hop / full C_eff bound); 0 FAILS strengthens the |O|=1 proof candidate."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _angleD_O1 import gmin_sides, ceff_electrical, test_O1
from _angleD_O1_lb import test as lbtest

def scan(adj,sides,n,nm):
    out=[]
    for s in sides:
        r=lbtest(adj,s,n)
        if r is None or r[0]!='ok': continue
        d=r[1]
        out.append((nm,d['o'],float(d['Ceff']),float(d['Do']),float(d['lb']),d['lb_ge'],d['ceff_ge'],
                    float(d['lb']/d['Do']) if d['Do']>0 else None))
    return out

if __name__=="__main__":
    print("=== |O|=1 STRESS: star LB1 >= D_o on guardrail blind spots ===")
    from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free
    from _superphi import blow
    rows=[]
    # iterated Mycielskians
    C5=(5,Cn(5)); n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1)
    for nm,(nn,EE) in [("Grotzsch11",(n1,E1)),("Myc2(C5)=23",(n2,E2)),
                       ("Myc(C7)=15",mycielski(7,Cn(7)))]:
        adj,sides=gmin_sides(nn,EE); rows+=scan(adj,sides,nn,nm)
    # blow-ups of small triangle-free graphs
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3),("G?bF`w",2),("I?ABCc]}?",2)]:
        try:
            nn,EE=blow(g6,t)
            if nn<=26 and is_triangle_free(nn,EE):
                adj,sides=gmin_sides(nn,EE); rows+=scan(adj,sides,nn,f"{g6}[{t}]")
        except Exception as ex:
            pass
    # glued islands (the guardrail blind spot)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>24 or not is_triangle_free(n,E): continue
                adj,sides=gmin_sides(n,E); rows+=scan(adj,sides,n,f"isl{iN}+{gN}{br}")
    fails=[r for r in rows if not r[5]]
    print(f"  total |O|=1 cuts scanned (named/blowup/glued): {len(rows)}")
    print(f"  star-LB1 FAILS (lb<Do): {len(fails)}")
    if rows:
        mn=min(rows,key=lambda r:r[7] if r[7] else 9e9)
        print(f"  min(LB1/Do) = {mn[7]:.4f}  at {mn[0]} o={mn[1]} (Ceff={mn[2]:.3f} Do={mn[3]:.3f} LB1={mn[4]:.3f})")
    for r in fails[:8]:
        print("   FAIL",r)
    # also census N=11 |O|=1 (triangle-free connected, may be slow) -- cap count
    print("--- census N=11 (-tc), |O|=1, star LB1 ---")
    outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
    tot=0; lbf=0; cf=0; minr=None
    for k,g6 in enumerate(outg):
        n,E=dec(g6); adj,sides=gmin_sides(n,E)
        for s in sides:
            r=lbtest(adj,s,n)
            if r is None or r[0]!='ok': continue
            d=r[1]; tot+=1
            if not d['lb_ge']: lbf+=1
            if not d['ceff_ge']: cf+=1
            rr=d['lb']/d['Do'] if d['Do']>0 else None
            if rr and (minr is None or rr<minr): minr=rr
    print(f"  census N=11: |O|=1 cuts={tot} LB1-FAILS={lbf} Ceff-FAILS={cf} min(LB1/Do)={float(minr) if minr else None}",flush=True)
