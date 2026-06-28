"""Re-scan CLAIM-A failures, splitting by O empty vs nonempty.
KEY QUESTION: do ALL local-charge / sat-with-deadnb-in-Qonly failures have O EMPTY?
If so, C-alltie (which assumes O nonempty) is never witnessed-violated and the
real content is: when O nonempty, the saturated-with-dead config forces O-meet.
Exact Fraction over census N=5..11."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components

def crossdeg(v, Cs, Bset):
    c=0
    for (a,b) in Bset:
        if a==v and b not in Cs: c+=1
        elif b==v and a not in Cs: c+=1
    return c

def scan(Nmin,Nmax):
    # count, among Q-only comps, saturated v with dead B-neighbor, split by O empty/nonempty
    Oempty_satdead=0; Ononempty_satdead=0; wit=None
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']; Bset=B['Bset']
            comps=components(K,n)
            for C in comps:
                Cs=set(C)
                if Cs&O: continue   # only Q-only comps (disjoint from O)
                for v in C:
                    if T[v]!=N: continue
                    dead=[w for w in range(n) if (min(v,w),max(v,w)) in Bset and T[w]==0]
                    if not dead: continue
                    if O:
                        Ononempty_satdead+=1
                        if wit is None: wit=(g6,v,sorted(C),sorted(O))
                    else:
                        Oempty_satdead+=1
        print(f"  N={nn}: sat-with-dead in Q-only: O-EMPTY={Oempty_satdead} O-NONEMPTY={Ononempty_satdead}",flush=True)
    print(f"TOTAL sat-with-dead in Q-only comp: O-empty={Oempty_satdead} O-nonempty={Ononempty_satdead} (loads cut) witness_Ononempty={wit}")

if __name__=="__main__":
    print("=== sat-with-dead-neighbor in Q-only comp, split by O empty/nonempty (loads cut) ===")
    scan(5,11)
