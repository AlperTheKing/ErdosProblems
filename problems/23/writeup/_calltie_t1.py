"""C-alltie transport experiment #1.
We probe the LOCAL-CHARGE candidate and the exact structure at a saturated vertex
in a Q-only K-component that has a dead B-neighbor.

Definitions per K-component C (disjoint from O) [all exact Fraction]:
  T(v)=sum_f ell(f) p_f(v);  deficit(C)=N|C|-Gamma_C, Gamma_C=sum_{v in C}T(v).
  crossdeg_B(v,C) = # B-edges from v that LEAVE C.
  intdeg_B(v,C)   = # B-edges from v that STAY in C.
  D(v)=sum_{f: v endpoint} ell(f).   handshake: sum_{e at v,B} mu(e)=2T(v)-D(v).

CLAIM-A (local charge):  N - T(v) >= crossdeg_B(v,C)   for v in a Q-only comp C.
CLAIM-B (key for C-alltie): a saturated v (T=N) in a Q-only comp C has crossdeg_B(v,C)=0.
  [CLAIM-A => CLAIM-B trivially.]  But a dead B-neighbor z of v is K-isolated (T=0),
  so z is NOT in C, hence vz is a crossing B-edge => crossdeg>=1 => contradicts CLAIM-B.
  => no saturated v in a Q-only comp has a dead B-neighbor => C-alltie.

So C-alltie <== CLAIM-A.  We test CLAIM-A exactly over census + blowups + Mycielskians,
and dump every saturated-vertex local profile to see WHAT makes CLAIM-A hold.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def crossdeg(v, Cs, Bset):
    c=0
    for (a,b) in Bset:
        if a==v and b not in Cs: c+=1
        elif b==v and a not in Cs: c+=1
    return c
def intdeg(v, Cs, Bset):
    c=0
    for (a,b) in Bset:
        if a==v and b in Cs: c+=1
        elif b==v and a in Cs: c+=1
    return c

def scan(Nmin,Nmax,stride=1):
    tot=0; failA=0; satcnt=0; satdead=0; minslack=None; failwit=None
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); K=B['K']; T=B['T']; N=B['N']; O=B['O']; Bset=B['Bset']
            comps=components(K,n)
            for C in comps:
                Cs=set(C)
                if Cs&O: continue
                if len(C)==1 and T[C[0]]==0: continue
                for v in C:
                    tot+=1
                    cd=crossdeg(v,Cs,Bset)
                    slack=(F(N)-T[v])-cd
                    if minslack is None or slack<minslack[0]:
                        minslack=(slack,g6,v,float(T[v]),cd)
                    if slack<0:
                        failA+=1
                        if failwit is None: failwit=(g6,v,float(T[v]),cd,sorted(C)[:8])
                    if T[v]==N:
                        satcnt+=1
                        dead=[w for w in range(n) if (min(v,w),max(v,w)) in Bset and T[w]==0]
                        if dead:
                            satdead+=1
        print(f"  N={nn}: vert-in-Qonly-comp={tot} CLAIM-A FAIL={failA} sat={satcnt} sat-with-deadnb={satdead}",flush=True)
    print(f"TOTAL CLAIM-A: vertices={tot} fail={failA} witness={failwit} min(N-T-crossdeg)={minslack}")

if __name__=="__main__":
    print("=== CLAIM-A local charge: N-T(v) >= crossdeg_B(v,C) on Q-only comps ===")
    scan(5,11,1)
