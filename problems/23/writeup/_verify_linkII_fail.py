"""VERIFY the apparent link-II failure on J???E?pNu\\?[2] (N=22). Dump full details + scan more
blow-ups to see how widespread link-II failure is. If link II genuinely fails at N>=12, the
sandwich route is INVALID (link II is not universal). Check both links + the CONCLUSION U_over<=U_under."""
from fractions import Fraction as F
from _h import dec, loads

def blowup(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t):
                EE.append((a*t+i,b*t+j))
    return nn,EE

def full(label,n,E):
    info=loads(n,E)
    if info is None: print(f"{label}: skip"); return
    N=n; T=info['T']; G=info['G']
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u); HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    print(f"=== {label} N={n} Gamma={G} N^2={N*N} (Gamma<=N^2: {G<=N*N}) ===")
    print(f"  U_over={float(Uo):.3f} HV_B={float(HVB):.3f} U_under={float(Uu):.3f}")
    print(f"  link I  U_over<=HV_B : {Uo<=HVB}")
    print(f"  link II HV_B<=U_under: {HVB<=Uu}   {'<<< LINK II FAILS' if not HVB<=Uu else ''}")
    print(f"  CONCLUSION U_over<=U_under (=Gamma<=N^2): {Uo<=Uu}")
    print(f"  distinct T values: {sorted(set(float(t) for t in T))}")

if __name__=="__main__":
    # the suspected violator
    n,E=dec("J???E?pNu\\?")
    full("J???E?pNu\\?[1]",n,E)
    nn,EE=blowup(n,E,2); full("J???E?pNu\\?[2]",nn,EE)
    # scan blow-ups of several N<=11 graphs to count link-II failures at larger N
    print("\n--- scan: link-II failures among blow-ups (t=2) of assorted N=10,11 graphs ---")
    import subprocess
    from _h import GENG
    tested=0; II_fail=0; concl_fail=0; egs=[]
    out=subprocess.run([GENG,"-tc","10"],capture_output=True,text=True).stdout.split()
    for g6 in out[:200]:
        n,E=dec(g6)
        nn,EE=blowup(n,E,2)
        if nn>20: continue
        info=loads(nn,EE)
        if info is None: continue
        N=nn; T=info['T']
        o=[(T[z]-N if T[z]>N else F(0)) for z in range(nn)]
        u=[(N-T[z] if T[z]<N else F(0)) for z in range(nn)]
        Uo=sum(o); Uu=sum(u); HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
        tested+=1
        if not HVB<=Uu: II_fail+=1; egs.append(g6)
        if not Uo<=Uu: concl_fail+=1
    print(f"  tested {tested} blow-ups(t=2) of N=10 graphs | link-II fails:{II_fail} | conclusion(Gamma<=N^2) fails:{concl_fail}")
    print(f"  link-II-failing examples: {egs[:8]}")
