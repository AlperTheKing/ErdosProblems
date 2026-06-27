"""STRESS-TEST the sandwich  U_over <= HV_B <= U_under  (=> Gamma<=N^2 => #23) at LARGE N,
beyond census. Families: C(2k+1)[q] blowups, Mycielskians, random triangle-free graphs N up to ~24.
Also re-checks the per-level overload isoperimetry |A|<=dB(A). EXACT rational.
If ANY family violates either link => the sandwich is a small-N coincidence (kills the route).
Uses loads() which takes the Gamma-min connected-B max cut over ALL max cuts (exp in N) -- so for
large N we restrict to graphs with few vertices on one side OR pass a known good cut. For blowups we
can afford up to N~20 (maxcut_all is 2^(N-1)); beyond that we provide the natural balanced cut."""
from fractions import Fraction as F
import random
from collections import deque
from _h import dec, loads, geos, bdist_restr, Bconn

def quants_from_loads(info):
    n=info['n']; T=info['T']; N=n; G=info['G']
    o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    u=[(N-T[z] if T[z]<N else F(0)) for z in range(n)]
    Uo=sum(o); Uu=sum(u)
    HVB=sum(abs(o[a]-o[b]) for (a,b) in info['Bset'])
    # overload isoperimetry
    vals=sorted(set(v for v in o if v>0)); isobad=0
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        dB=sum(1 for (a,b) in info['Bset'] if (a in A)!=(b in A))
        if len(A)>dB: isobad+=1
    return Uo,Uu,HVB,N*N-G,isobad

def Cblow(k,q):
    """odd cycle C_{2k+1} blown up by q: N=(2k+1)q."""
    L=2*k+1; nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q):
                E.append((i*q+a, ((i+1)%L)*q+b))
    return nn,E

def mycielski(n,E):
    """Mycielskian: vertices 0..n-1 (orig), n..2n-1 (shadow), 2n (apex). Triangle-free preserved."""
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    E2=list(E); apex=2*n
    for u in range(n):
        for v in adj[u]:
            if v>u:
                E2.append((u, n+v)); E2.append((n+u, v))  # u'~v and v'~u (shadow to orig neighbors)
        E2.append((n+u, apex))
    return 2*n+1, E2

def rand_trifree(n,p,seed):
    rng=random.Random(seed); E=[]; adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]; rng.shuffle(pairs)
    for (i,j) in pairs:
        if rng.random()<p:
            # add only if no common neighbor (keeps triangle-free)
            if not (adj[i]&adj[j]):
                E.append((i,j)); adj[i].add(j); adj[j].add(i)
    return n,E

def test_one(label,n,E,maxcut_ok=True):
    if n>22:
        print(f"  {label:22} N={n}: SKIP (maxcut_all too big)"); return None
    info=loads(n,E)
    if info is None:
        print(f"  {label:22} N={n}: skip (no connected-B max cut / not tri-free-good)"); return None
    Uo,Uu,HVB,N2mG,isobad=quants_from_loads(info)
    L1 = Uo<=HVB; L2 = HVB<=Uu; gam=Uo<=Uu
    flag="" if (L1 and L2 and isobad==0) else "  <<<<< VIOLATION"
    print(f"  {label:22} N={n} G={info['G']} | U_over={float(Uo):7.3f} HV_B={float(HVB):7.3f} U_under={float(Uu):7.3f} N2-G={float(N2mG):6.1f} | I:{L1} II:{L2} iso_fail:{isobad} Gam<=N2:{gam}{flag}")
    return (L1,L2,isobad)

if __name__=="__main__":
    print("=== odd-cycle blowups C(2k+1)[q] (anchor; expect tight) ===")
    for k in (2,3,4):
        for q in range(1,5):
            n,E=Cblow(k,q)
            if n<=20: test_one(f"C{2*k+1}[{q}]",n,E)
    print("=== Mycielskians (triangle-free, high chromatic) ===")
    n,E=Cblow(2,1)  # C5
    n2,E2=mycielski(n,E); test_one("Myciel(C5)=Grotzsch",n2,E2)
    n,E=([7,[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,0)]][0], [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,0)])
    n3,E3=mycielski(7,E); test_one("Myciel(C7)",n3,E3)
    print("=== random triangle-free N=12..22 (multiple seeds/densities) ===")
    bad=0; tot=0
    for n in range(12,23,2):
        for p in (0.3,0.45,0.6):
            for seed in range(4):
                nn,E=rand_trifree(n,p,seed*100+n)
                r=test_one(f"rand n{n} p{p} s{seed}",nn,E)
                if r is not None:
                    tot+=1
                    if not(r[0] and r[1] and r[2]==0): bad+=1
    print(f"\nRANDOM SUMMARY: {tot} tested, {bad} violations of sandwich-or-isoperimetry")
