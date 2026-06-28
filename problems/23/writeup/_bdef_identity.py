"""Verify the clean reframing: for a K-component C disjoint from O,
   sum_{v in C} T[v] = Gamma_C := sum_{bad edge f with geodesic support inside C} ell(f)^2,
so deficit(C) = N|C| - Gamma_C, and BOUNDARY-DEFICIT <=> N|C| >= Gamma_C + dB(C). Exact Fraction."""
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact
from _bdef import components

def gamma_C(Cset,P,M,ell):
    g=F(0)
    for f,d in enumerate(P):
        supp=set(d.keys())
        if supp and supp<=Cset:
            g+=F(ell[M[f]])**2
    return g

for g6 in ["J?AEB?oE?W?","DUW","G?bF`w","I?rFf_{N?","H?bB@_W"]:
    n,E=dec(g6); info=loads(n,E)
    P,M,ell,nn=pf_exact(info); N=nn
    K=[[F(0)]*nn for _ in range(nn)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(nn)) for v in range(nn)]
    O=set(v for v in range(nn) if T[v]>N)
    for C in components(K,nn):
        Cs=set(C)
        if Cs&O: continue
        mass=sum(T[v] for v in C)
        gC=gamma_C(Cs,P,M,ell)
        defi=F(N*len(C))-mass
        dB=sum(1 for (a,b) in info['Bset'] if (a in Cs)^(b in Cs))
        print(f"{g6:14} |C|={len(C)} N={N}: mass={float(mass):.2f} Gamma_C={float(gC):.2f} match={mass==gC} "
              f"deficit={float(defi):.2f}=(N|C|-Gamma_C={float(F(N*len(C))-gC):.2f}) dB={dB} N|C|>=Gamma_C+dB:{N*len(C)>=gC+dB}")
