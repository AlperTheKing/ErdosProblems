"""Independent exhaustive census: worst maxT over ALL gamma-min cuts, N=5..10. No census_GPI import."""
import subprocess, sys
from fractions import Fraction
import _synth_verify as S
import _synth_allgmin as A

GENG=r"E:\Projects\ErdosProblems\bridge\flagsdp\nauty2_8_9\geng.exe"
import census_GPI as C
GENG=C.GENG  # reuse path

def run(nmax):
    grand_viol=[]
    minslack_overall=None
    for n in range(5, nmax+1):
        out=subprocess.run([GENG,'-tc',str(n)],capture_output=True,text=True).stdout.split()
        nchk=0; viol=0; minslack=None; tight=[]
        for g6 in out:
            if not S.is_triangle_free(*S.dec_g6(g6)[:2]):  # adj as matrix-ish; use own
                pass
            r=A.all_gmin_maxT(g6)
            if r is None: continue
            nn, G, K, worst, ncuts, isviol = r
            nchk+=1
            slack=K-worst
            if isviol:
                viol+=1; grand_viol.append((g6, nn, G, K, worst))
            if minslack is None or slack<minslack:
                minslack=slack
            if slack==0:
                tight.append(g6)
        print(f"N={n}: checked={nchk} viol={viol} minslack(K-worstmaxT)={minslack} tight0_count={len(tight)} tight_examples={tight[:3]}")
        if minslack_overall is None or (minslack is not None and minslack<minslack_overall):
            minslack_overall=minslack
        sys.stdout.flush()
    print("GRAND violations:", grand_viol)
    print("overall min slack:", minslack_overall)

if __name__=="__main__":
    nmax=int(sys.argv[1]) if len(sys.argv)>1 else 10
    run(nmax)
