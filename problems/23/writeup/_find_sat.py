"""Find graphs with a saturated underloaded vertex (T[q]=N) at small N and dump the first few."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _cond1_proof import build_K

def has_sat(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    sat=[q for q in Q if T[q]==F(N)]
    return (sat,O,N) if sat else None

if __name__=="__main__":
    found=[]
    for nn in (9,10):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=has_sat(info)
            if r:
                found.append((g6,nn,r[0],r[1]))
                if len(found)>=8: break
        if len(found)>=8: break
    for g6,nn,sat,O in found:
        print(f"{g6} N={nn} sat={sat} O={O}")
