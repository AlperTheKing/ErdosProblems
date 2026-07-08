"""
Realizability experiment for the m=9 double-star LocalObstruction:
21-vertex candidate graph with K3,3 mono cluster, 2-edge waist u-w-v, anchor webs.
Brute-force exact max cut (2^20), then Gamma-min analysis + Hall check at Gamma-min max cuts.
Also: C5[t] blow-up Hall-slack computation (t=2,3) as the 'wide waist' contrast.
"""
from collections import deque, Counter
from itertools import combinations

def build():
    # vertices: l=0,1,2  r=3,4,5  u=6 w=7 v=8  aL=9,10,11 aR=12,13,14  zL=15,16,17 zR=18,19,20
    E = []
    for l in (0,1,2):
        for r in (3,4,5):
            E.append((l,r))            # K3,3 mono cluster (intended bad)
    for l in (0,1,2): E.append((l,6))  # l-u
    E += [(6,7),(7,8)]                 # waist u-w, w-v
    for r in (3,4,5): E.append((8,r))  # v-r
    for a in (9,10,11):
        for l in (0,1,2): E.append((a,l))
        for z in (15,16,17): E.append((a,z))
    for b in (12,13,14):
        for r in (3,4,5): E.append((b,r))
        for z in (18,19,20): E.append((b,z))
    return 21, E

def check_triangle_free(n, E):
    adj = [set() for _ in range(n)]
    for (i,j) in E: adj[i].add(j); adj[j].add(i)
    for (i,j) in E:
        if adj[i] & adj[j]: return False
    return True

def bfs(adjL, n, s):
    d = [-1]*n; d[s]=0; q=deque([s])
    while q:
        x=q.popleft()
        for y in adjL[x]:
            if d[y]<0: d[y]=d[x]+1; q.append(y)
    return d

def analyze_cut(n, E, mask):
    """Return (gamma or None, atoms, supports, Eshort_by_subsetcheck)"""
    blue=[]; mono=[]
    adjB=[[] for _ in range(n)]
    for (i,j) in E:
        if ((mask>>i)&1)!=((mask>>j)&1):
            blue.append((i,j)); adjB[i].append(j); adjB[j].append(i)
        else: mono.append((i,j))
    dist={}
    gamma=0; atoms=[]
    for (u,v) in mono:
        if u not in dist: dist[u]=bfs(adjB,n,u)
        d=dist[u][v]
        if d<0: return None, [], [], None
        gamma += (d+1)**2
        if d==4: atoms.append((u,v))
    sups=[]
    for (u,v) in atoms:
        if u not in dist: dist[u]=bfs(adjB,n,u)
        if v not in dist: dist[v]=bfs(adjB,n,v)
        du,dv=dist[u],dist[v]
        S=frozenset((x,y) for (x,y) in blue
                    if (du[x]>=0 and dv[y]>=0 and du[x]+1+dv[y]==4) or
                       (du[y]>=0 and dv[x]>=0 and du[y]+1+dv[x]==4))
        sups.append(S)
    return gamma, atoms, sups, None

def hall_violations(atoms, sups):
    k=len(atoms)
    viol=[]
    if k==0 or k>18: return viol
    U=[frozenset()]*(1<<k)
    U=[None]*(1<<k); U[0]=frozenset()
    for s in range(1,1<<k):
        low=(s&-s).bit_length()-1
        U[s]=U[s&(s-1)]|sups[low]
        if bin(s).count('1')>len(U[s]):
            viol.append((s, bin(s).count('1'), len(U[s])))
    return viol

def main():
    n,E = build()
    print("n=",n," edges=",len(E)," triangle-free:", check_triangle_free(n,E))
    adjm=[0]*n
    for (i,j) in E: adjm[i]|=1<<j; adjm[j]|=1<<i
    nmask=(1<<n)-1
    best=-1; bestmasks=[]
    for m2 in range(1<<(n-1)):
        mask=m2<<1
        cut=0; mm=mask
        while mm:
            v=(mm&-mm).bit_length()-1
            cut+=bin(adjm[v]&~mask&nmask).count("1")
            mm&=mm-1
        if cut>best: best=cut; bestmasks=[mask]
        elif cut==best: bestmasks.append(mask)
    intended = 0
    for v in (6,8,9,10,11,12,13,14): intended |= 1<<v
    # intended: Y = {u,v,anchors}; complement equivalent; normalize bit0=0 side
    icut=0; mm=intended
    while mm:
        v=(mm&-mm).bit_length()-1
        icut+=bin(adjm[v]&~intended&nmask).count("1")
        mm&=mm-1
    print("MAX CUT =", best, " #maxcut masks =", len(bestmasks), " intended cut value =", icut)
    # Gamma-min analysis over max cuts
    gmin=None; results=[]
    for mask in bestmasks:
        g,atoms,sups,_=analyze_cut(n,E,mask)
        results.append((mask,g,atoms,sups))
        if g is not None and (gmin is None or g<gmin): gmin=g
    print("Gamma-min over max cuts =", gmin)
    tot_viol=0; ell5tot=0
    for (mask,g,atoms,sups) in results:
        if g==gmin:
            v=hall_violations(atoms,sups)
            tot_viol+=len(v)
            ell5tot+=len(atoms)
            if v: print("HALL VIOLATION at gmin mask",mask,"atoms",atoms,"viol",v[:3])
    print("gamma-min cuts:", sum(1 for r in results if r[1]==gmin),
          " total ell5 atoms across them:", ell5tot, " hall violations:", tot_viol)
    # show one gamma-min cut structure
    for (mask,g,atoms,sups) in results:
        if g==gmin:
            print("example gmin mask:",mask,"sideY:",[i for i in range(n) if (mask>>i)&1])
            print(" atoms:",atoms)
            for a,S in zip(atoms,sups): print("  ",a,"|P|=",len(S))
            break

def c5blowup(t):
    # classes V0..V4, edges between consecutive classes (blow-up of C5)
    n=5*t
    def V(c): return list(range(c*t,(c+1)*t))
    E=[]
    for c in range(5):
        for x in V(c):
            for y in V((c+1)%5): E.append((min(x,y),max(x,y)))
    # canonical max cut: X = V0 u V1? standard: sides {V0,V2} vs {V1,V3,V4}: bad pair V3-V4
    mask=0
    for x in V(1)+V(3)+V(4): mask|=1<<x
    g,atoms,sups,_=analyze_cut(n,E,mask)
    if atoms:
        Esh=frozenset().union(*sups)
        print(f"C5[{t}]: atoms={len(atoms)} |E_short(all)|={len(Esh)} slack={len(Esh)/len(atoms):.2f} gamma={g}")
        viol=hall_violations(atoms,sups) if len(atoms)<=18 else []
        print(f"   hall violations: {len(viol)}")

if __name__=="__main__":
    main()
    for t in (2,3): c5blowup(t)
