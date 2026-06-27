"""Test the candidate chain  2*U_over <= HV_B <= U_under  (=> COUPLE 2U_over<=U_under).
HV_B = sum_{xy in B} |o(x)-o(y)|, o=(T-N)+.  Also test underload isoperimetry and a few
variants. All exact rational, census N<=11."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def quants(info):
    n=info['n']; T=info['T']; N=n; G=info['G']
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u)
    HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    HVB_u=sum(abs(u[a]-u[b]) for (a,b) in info['Bset'])
    return Uo,Uu,HVB,HVB_u,N*N-G

def run_census(Nmax,Nmin=5):
    print("--- chain 2U_over<=HV_B<=U_under  + variants ---")
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nt=0
        c_2U_le_HVB=c_HVB_le_Uu=c_chain=0
        c_HVBu_le=0
        worst_2U_HVB=None; worst_HVB_Uu=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; Uo,Uu,HVB,HVBu,N2mG=quants(info)
            a = 2*Uo<=HVB
            b = HVB<=Uu
            if a: c_2U_le_HVB+=1
            if b: c_HVB_le_Uu+=1
            if a and b: c_chain+=1
            g1=2*Uo-HVB
            if worst_2U_HVB is None or g1>worst_2U_HVB: worst_2U_HVB=g1
            g2=HVB-Uu
            if worst_HVB_Uu is None or g2>worst_HVB_Uu: worst_HVB_Uu=g2
        print(f"  N={nn}: cfg={nt} | 2U_over<=HV_B:{c_2U_le_HVB}/{nt} (max 2U-HVB={float(worst_2U_HVB):+.3f}) | HV_B<=U_under:{c_HVB_le_Uu}/{nt} (max HVB-Uu={float(worst_HVB_Uu):+.3f}) | BOTH(chain):{c_chain}/{nt}",flush=True)

if __name__=="__main__":
    run_census(11,5)
