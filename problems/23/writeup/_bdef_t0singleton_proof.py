"""PARTIAL PROOF of boundary-deficit for the ONLY components that occur in the relevant regime.

Empirical fact (this leg, exact): over the full triangle-free census N<=11 (and every other family
tested), EVERY K-component C disjoint from O with O!=empty is an isolated T=0 singleton {v}
(K-row of v identically zero). For such a singleton:
    deficit({v}) = N - T[v] = N - 0 = N,
    dB({v})      = #B-edges incident to v = (B-degree of v) <= deg(v) <= N-1.
Hence deficit - dB = N - dB >= N - (N-1) = 1 > 0: boundary-deficit holds with slack >= 1,
PROVABLY, with NO census needed for these components.

This script EXACT-verifies, over the full census N<=11 (and witnesses), the two structural facts the
partial proof rests on:
 (F1) every Q-only K-component coexisting with O!=empty is a singleton {v} with T[v]==0 and K-row(v)==0;
 (F2) for such v, dB(v) <= deg(v) <= N-1 < N, so deficit - dB >= 1.
If (F1) holds with 0 exceptions, boundary-deficit's relevant-regime content is the trivial (F2)."""
import sys, subprocess
sys.path.insert(0,r"E:\Projects\ErdosProblems\problems\23\writeup")
from fractions import Fraction as F
from _bdef_stress2 import pf_K_T, K_components
from _h import dec, GENG, loads

def check(g6):
    n,E=dec(g6); info=loads(n,E)
    if info is None: return None
    K,T,nn=pf_K_T(info); N=nn
    O=set(v for v in range(n) if T[v]>N)
    if not O: return ('noO',)
    Bset=info['Bset']
    comps=K_components(K,n)
    out=[]
    for C in comps:
        Cs=set(C)
        if Cs & O: continue
        # is it a T0 singleton with zero K-row?
        if len(C)==1:
            v=C[0]
            krow_zero = all(K[v][w]==0 for w in range(n))
            t0 = (T[v]==0)
            dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
            deg=len(info['adj'][v])
            f1 = (t0 and krow_zero)
            f2 = (dB<=deg<=N-1) and (N-dB>=1)
            out.append(('singleton',f1,f2,dB,deg,N))
        else:
            # NON-singleton Q-only comp coexisting with O: would BREAK (F1)
            mass=sum(T[v] for v in C)
            dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
            out.append(('NONSINGLETON_WITH_O',len(C),float(mass),dB,float(N*len(C)-mass)))
    return ('withO',out)

def census(Nmax):
    for nn in range(7,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nG=0; nWithO=0; nComp=0; f1_fail=0; f2_fail=0; nonsingle=0; minslack=None
        for g6 in out:
            r=check(g6)
            if r is None or r[0]=='noO': continue
            nG+=1; nWithO+=1
            for rec in r[1]:
                nComp+=1
                if rec[0]=='singleton':
                    _,f1,f2,dB,deg,N=rec
                    if not f1: f1_fail+=1
                    if not f2: f2_fail+=1
                    slack=N-dB
                    if minslack is None or slack<minslack: minslack=slack
                else:
                    nonsingle+=1
        print(f"  census N={nn}: with-O graphs={nWithO} | Q-only comps={nComp} "
              f"(F1-singleton-T0-Krow0 FAILS={f1_fail}, NON-singleton-with-O={nonsingle}) "
              f"| F2 fails={f2_fail} | min(deficit-dB)=N-dB min = {minslack}", flush=True)

if __name__=="__main__":
    print("=== T0-singleton partial proof: (F1) every Q-only-with-O comp is T0 singleton, (F2) slack>=1 ===", flush=True)
    census(11)
