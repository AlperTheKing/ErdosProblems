"""Verify the clean identity  deficit(C) = 1_C^T (N I - K) 1_C  for K-closed components C,
and study the relationship between boundary-deficit and ROWSUM-O.

Identities (exact Fraction):
  (Q) deficit(C) = N|C| - mass(C) = 1_C^T A 1_C  where A = N I - K.  [holds for ANY C since
       1_C^T K 1_C = sum_{v,w in C} K[v,w], and for K-closed C this = mass(C).]
  So boundary-deficit  <=>  1_C^T A 1_C >= dB(C).

Comparisons:
  (R1) Does ROWSUM-O restricted to F_C (belonging edges) imply Gamma_C <= N|C| (i.e. deficit>=0)? trivially
       deficit>=0 from T<=N, so look at strength.
  (R2) Is boundary-deficit (the +dB part) IMPLIED by ROWSUM-O? Test: among proper Q-only comps, does
       max over f in F_C of rowsumO(f)=sum_v p_f(v)S(v) relate to slack? We log both.
  (R3) Construct the converse direction qualitatively: does boundary-deficit hold whenever ROWSUM-O holds?
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def rowsumO(B):
    """ (O*1)_f = sum_v p_f(v) S(v) for each bad edge f. """
    P=B['P']; S=B['S']; M=B['M']
    out=[]
    for fi in range(len(M)):
        val=sum(P[fi].get(v,F(0))*S[v] for v in P[fi])
        out.append(val)
    return out

def check(info):
    B=build(info)
    K=B['K']; T=B['T']; N=B['N']; n=B['n']; O=B['O']; Bset=B['Bset']
    A=[[ (F(N) if i==j else F(0))-K[i][j] for j in range(n)] for i in range(n)]
    comps=components(K,n)
    ro=rowsumO(B)
    res=[]
    for C in comps:
        Cs=set(C)
        if Cs&O: continue
        d=analyze_one(B,C)
        # quadratic form 1_C^T A 1_C
        qf=sum(A[v][w] for v in C for w in C)
        ident=(qf==d['deficit'])
        # max rowsumO over belonging edges
        from _bdef_theory import build as _b
        supp=B['supp']
        FC=[fi for fi in range(len(B['M'])) if supp[fi] and supp[fi]<=Cs]
        maxro=max((ro[fi] for fi in FC),default=F(0))
        res.append(dict(sz=d['sz'],deficit=d['deficit'],dB=d['dB'],qf_ident=ident,
                        maxRowsumO=maxro,bd_ok=d['bd_ok'],
                        proper=(len(C)<n)))
    return res

if __name__=="__main__":
    print("=== deficit(C) = 1_C^T A 1_C  identity check + rowsumO link ===")
    bad_ident=0; tot=0
    for nn in range(5,10):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for r in check(info):
                tot+=1
                if not r['qf_ident']: bad_ident+=1
        print(f"  N={nn}: cumulative comps={tot} qf_identity_FAILS={bad_ident}",flush=True)
    print(f"identity deficit==1_C^T A 1_C : FAILS={bad_ident} / {tot}")
