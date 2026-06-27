import subprocess
import sys
sys.path.insert(0,"E:/Projects/ErdosProblems/problems/23/writeup")
from verify_iii_independent import dec, check
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
f_ge=0; f_lt=0; ntot=0; tight_ct=0; examples=[]
for g6 in out:
    n,E=dec(g6); r=check(n,E)
    if r is None or r[0]=='nopeel': continue
    G,n2,iii,Ap,lep,tight,d=r; ntot+=1
    ok=iii and Ap and lep
    if not ok:
        if G>=n2*n2: f_ge+=1
        else:
            f_lt+=1
            if len(examples)<6: examples.append((g6,G,iii,Ap,lep,d['ov']))
    if tight: tight_ct+=1
print(f"N=11: configs={ntot} | fails at Gamma>=N^2 = {f_ge} (MUST be 0) | fails at Gamma<N^2 = {f_lt} | tight={tight_ct}")
for ex in examples: print("   Gamma<N^2 fail:",ex)
print("DONE N=11 independent gate")
