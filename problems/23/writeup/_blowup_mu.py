"""KEY test: do blow-ups of the mu(e)>N graphs have mu(e)<=N for t>=2?
If yes => mu(e)<=N holds in the blow-up regime; since Gamma/N^2 is blow-up invariant
(Gamma(G[t])=t^2 Gamma(G), N(G[t])=tN), proving (L)/link I/Gamma<=N^2 in the large-t regime
(where mu<=N is clean) TRANSFERS to the base graph. Tests the violators H?AFBo], J???E?pNu\\?.
Also confirms the sandwich + (L) hold on these blow-ups."""
from fractions import Fraction as F
from _h import dec, loads
from _edgeload import edge_loads

def blowup(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t):
                EE.append((a*t+i,b*t+j))
    return nn,EE

def report(label,n,E):
    if n>22: print(f"  {label:18} N={n}: skip (maxcut too big)"); return
    info=loads(n,E)
    if info is None: print(f"  {label:18} N={n}: skip (no good cut)"); return
    mu,Ev=edge_loads(info); N=n
    mx=max(mu.values()) if mu else F(0)
    T=info['T']; o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u); HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    vals=sorted(set(v for v in o if v>0)); Lok=True
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        dB=sum(1 for (a,b) in info['Bset'] if (a in A)!=(b in A))
        if sum(T[z] for z in A) > N*dB: Lok=False
    print(f"  {label:18} N={n} G={info['G']} | max mu/N={float(mx/N):.4f} | (L):{Lok} | sandwich U_o={float(Uo):.2f}<=HVB={float(HVB):.2f}<=U_u={float(Uu):.2f}: {Uo<=HVB<=Uu}")

if __name__=="__main__":
    for g6 in ["H?AFBo]","J???E?pNu\\?","H?AFBo]"]:
        pass
    print("=== violators at t=1 vs blow-ups ===")
    for g6 in ["H?AFBo]","J???E?pNu\\?"]:
        n,E=dec(g6)
        report(f"{g6} t1",n,E)
        for t in (2,):
            nn,EE=blowup(n,E,t)
            report(f"{g6} t{t}",nn,EE)
