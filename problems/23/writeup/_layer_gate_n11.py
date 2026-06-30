"""Hard-battery layer-cake tail-dominance gate: Grotzsch (Mycielski witness N=11) + large/lopsided
   blow-ups (N<=16) + bigger glued islands FIRST, then full census N=11 (slow).  Reuses _layer_gate.gate.
"""
import subprocess
from _layer_gate import gate
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _bdef_construct import Cn, union_disjoint, mycielski

def main():
    acc = dict(rows=0, idfail=0, ptfail=0, tailfail=0, idex=None, ptex=None, tailex=None)
    # Grotzsch = mycielski(C5), N=11 -- the canonical Mycielskian witness (gmins-feasible)
    grN, grE = mycielski(5, Cn(5))
    gate("Grotzsch", grN, grE, acc)
    print("Grotzsch N=%d: rows=%d idfail=%d tailfail=%d" % (grN, acc['rows'], acc['idfail'], acc['tailfail']), flush=True)
    # large / lopsided blow-ups
    for sizes in [(3,3,3,3,3),(4,3,4,3,4),(3,2,3,2,4),(4,4,3,3,2),(2,3,2,3,4),(3,3,3,3,2),(4,1,4,1,4)]:
        if sum(sizes) <= 16:
            n, E = odd_blowup(5, list(sizes)); gate("C5%s" % (sizes,), n, E, acc)
    print("big C5 blow-ups: rows=%d idfail=%d tailfail=%d" % (acc['rows'], acc['idfail'], acc['tailfail']), flush=True)
    for sizes in [(2,2,2,1,1,1,1),(2,1,2,1,2,1,2),(3,1,1,1,1,1,1)]:
        if sum(sizes) <= 16:
            n, E = odd_blowup(7, list(sizes)); gate("C7%s" % (sizes,), n, E, acc)
    print("C7 blow-ups: rows=%d tailfail=%d" % (acc['rows'], acc['tailfail']), flush=True)
    # bigger glued islands
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9); n11,E11=11,Cn(11)
    for (a,b,br) in [((n5,E5),(n11,E11),[(0,5)]), ((n7,E7),(n9,E9),[(0,7)]),
                     ((n5,E5),(n9,E9),[(0,5),(2,8)]), ((n9,E9),(n7,E7),[(0,9),(3,13)])]:
        n,E=union_disjoint(a,b); E=E+br; gate("glueX", n, E, acc)
    print("bigger glued: rows=%d tailfail=%d" % (acc['rows'], acc['tailfail']), flush=True)
    # full census N=11 (slow)
    for g6 in subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split():
        n,E=dec(g6); gate("cen11", n, E, acc)
    print("="*60)
    print("TOTAL rows:", acc['rows'])
    print("IDENTITY fails:", acc['idfail'], acc['idex'])
    print("TAIL fails:", acc['tailfail'], acc['tailex'])
    print("VERDICT:", "TAIL DOMINANCE HOLDS on hard battery" if acc['tailfail']==0 and acc['idfail']==0 else "FAIL")

if __name__ == "__main__":
    main()
