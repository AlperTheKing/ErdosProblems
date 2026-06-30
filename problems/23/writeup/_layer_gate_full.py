"""Escalated battery for the GPT-Pro layer-cake TAIL dominance lemma (reuses _layer_gate.gate).
   census N<=10 + C5/C7 blow-ups (uniform/lopsided up to N=13) + glued islands + theta witnesses.
   Confirms: identity exact (0 fail), tail dominance sum_{r>=k}(2r+1)Z_r>=0 (0 fail).
"""
import subprocess
from _layer_gate import gate
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _bdef_construct import Cn, union_disjoint, mycielski

def main():
    acc = dict(rows=0, idfail=0, ptfail=0, tailfail=0, idex=None, ptex=None, tailex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gate("cen%d" % nn, n, E, acc)
        print("census N=%d: rows=%d idfail=%d ptfail=%d tailfail=%d"
              % (nn, acc['rows'], acc['idfail'], acc['ptfail'], acc['tailfail']), flush=True)
    blow5 = [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,3),
             (2,2,2,1,2),(3,1,2,1,2),(1,2,1,2,1),(3,3,2,2,2)]
    for sizes in blow5:
        if sum(sizes) <= 13:
            n, E = odd_blowup(5, list(sizes)); gate("C5%s" % (sizes,), n, E, acc)
    print("C5 blow-ups done: rows=%d tailfail=%d" % (acc['rows'], acc['tailfail']), flush=True)
    for sizes in [(1,)*7,(2,1,1,1,1,1,1),(1,1,1,1,1,1,2)]:
        if sum(sizes) <= 13:
            n, E = odd_blowup(7, list(sizes)); gate("C7%s" % (sizes,), n, E, acc)
    print("C7 blow-ups done: rows=%d tailfail=%d" % (acc['rows'], acc['tailfail']), flush=True)
    # glued islands
    n5, E5 = 5, Cn(5); n7, E7 = 7, Cn(7); n9, E9 = 9, Cn(9)
    for (a, b, br) in [((n5,E5),(n7,E7),[(0,5)]), ((n5,E5),(n7,E7),[(0,5),(2,8)]),
                       ((n5,E5),(n9,E9),[(0,5)]), ((n7,E7),(n7,E7),[(0,7)])]:
        n, E = union_disjoint(a, b); E = E + br
        gate("glue", n, E, acc)
    print("glued islands done: rows=%d tailfail=%d" % (acc['rows'], acc['tailfail']), flush=True)
    n, E = dec("H?AFBo]"); gate("thw-H", n, E, acc)
    print("="*60)
    print("TOTAL rows:", acc['rows'])
    print("IDENTITY fails:", acc['idfail'], acc['idex'])
    print("POINTWISE fails:", acc['ptfail'])
    print("TAIL dominance fails:", acc['tailfail'], acc['tailex'])
    print("VERDICT:", "TAIL DOMINANCE HOLDS (exact) on full battery" if acc['tailfail']==0 and acc['idfail']==0
          else "FAILURE -- see exemplars")

if __name__ == "__main__":
    main()
