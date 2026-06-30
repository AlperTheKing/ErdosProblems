"""All-connected-B-cuts stress of WITNESS-ANCHORED-TAIL (independent strong check of Codex's 111962/0-miss)."""
import subprocess
from itertools import product
from _witness_tail_gate import run_side
from _h import dec, GENG
acc=dict(deficits=0,pos=0,miss=0,first=None)
for nn in range(7,10):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6)
        for bits in product((0,1),repeat=n-1):
            side=[0]+list(bits)
            run_side("acut%s"%g6,n,E,side,acc)
    print("  all-cuts N=%d: deficits=%d pos=%d miss=%d"%(nn,acc['deficits'],acc['pos'],acc['miss']),flush=True)
print("WITNESS-ANCHORED-TAIL all-connected-B-cuts N<=9: deficits=%d positive=%d MISSES=%d %s"%(acc['deficits'],acc['pos'],acc['miss'],acc['first'] or ''),flush=True)
