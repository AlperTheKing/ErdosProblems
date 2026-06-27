"""Find the tightest (binding) graphs for each sandwich link, to understand fragility/structure.
Link I:  U_over <= HV_B          slack1 = HV_B - U_over
Link II: HV_B  <= U_under        slack2 = U_under - HV_B
Report the min-slack graphs (excluding the trivial U_over=0 cases for link I) at each N,
plus their load vector and overload set, for census N<=11."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def info_quants(info):
    n=info['n']; T=info['T']; N=n
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u)
    HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    return Uo,Uu,HVB

def run(Nmax,Nmin=8):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        best1=None; best2=None  # (slack, g6, Uo,Uu,HVB)
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            Uo,Uu,HVB=info_quants(info)
            if Uo>0:
                s1=HVB-Uo
                if best1 is None or s1<best1[0]: best1=(s1,g6,Uo,Uu,HVB)
            s2=Uu-HVB
            if (HVB>0) and (best2 is None or s2<best2[0]): best2=(s2,g6,Uo,Uu,HVB)
        if best1:
            s1,g6,Uo,Uu,HVB=best1
            n,E=dec(g6); info=loads(n,E)
            print(f"  N={nn} LINK-I tightest (HVB-Uover): slack={float(s1):.4f} @ {g6} | Uo={float(Uo):.3f} HVB={float(HVB):.3f} Uu={float(Uu):.3f} T={[float(t) for t in info['T']]}")
        if best2:
            s2,g6,Uo,Uu,HVB=best2
            n,E=dec(g6); info=loads(n,E)
            print(f"  N={nn} LINK-II tightest (Uunder-HVB): slack={float(s2):.4f} @ {g6} | Uo={float(Uo):.3f} HVB={float(HVB):.3f} Uu={float(Uu):.3f} T={[float(t) for t in info['T']]}")

if __name__=="__main__":
    run(11,8)
