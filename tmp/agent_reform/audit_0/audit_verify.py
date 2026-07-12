# INDEPENDENT adversarial re-verification of the pivotal-pentagon report claims.
# Written from scratch (different algorithms from battery.py where feasible). Exact ints/Fractions.
import sys
from fractions import Fraction
from itertools import combinations

def mkgraph(n, edges):
    E = sorted(set((min(u,v),max(u,v)) for u,v in edges))
    adj = [set() for _ in range(n)]
    for u,v in E:
        assert u!=v
        adj[u].add(v); adj[v].add(u)
    for u,v in E:
        assert not (adj[u] & adj[v]), "TRIANGLE"
    return n, E, adj

def pent_list(n, E, adj):
    # independent C5 enumeration: for each edge ab, count paths a-c-d-e-b of length 4? simpler: 5-subsets
    out = []
    for S in combinations(range(n),5):
        # count hamilton cycles on S
        a,b,c,d,e = S
        import itertools
        for p in itertools.permutations([b,c,d,e]):
            if p[0] > p[-1]: continue
            cyc = (a,)+p
            if all(cyc[(i+1)%5] in adj[cyc[i]] for i in range(5)):
                out.append(cyc)
    return out

def trA5(n, adj):
    A = [[1 if j in adj[i] else 0 for j in range(n)] for i in range(n)]
    def mm(X,Y):
        return [[sum(X[i][k]*Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    A2=mm(A,A); A4=mm(A2,A2); A5=mm(A4,A)
    return sum(A5[i][i] for i in range(n))

def beta_exhaustive(n, E):
    best = None
    for m in range(1<<(n-1)):
        mono = 0
        for u,v in E:
            if ((m>>u)&1)==((m>>v)&1): mono += 1
        if best is None or mono < best: best = mono
    return best

def maxcut(n,E):
    return len(E) - beta_exhaustive(n,E)

def R_pathcount(n, E, adj, m):
    tot = 0
    for u,v in E:
        if ((m>>u)&1)!=((m>>v)&1): continue
        side = (m>>u)&1
        X = [x for x in adj[u] if ((m>>x)&1)!=side]
        Y = [y for y in adj[v] if ((m>>y)&1)!=side]
        assert not (set(X)&set(Y)), "cross-neighborhoods intersect: triangle!"
        for x in X:
            for y in Y:
                tot += len(adj[x] & adj[y])   # z's; z in {u,v} impossible (checked below)
    return tot

def R_anchor(n, pents, m):
    # direct: anchors per pentagon, assert <=1
    tot = 0
    for cyc in pents:
        s = [(m>>x)&1 for x in cyc]
        mono = [i for i in range(5) if s[i]==s[(i+1)%5]]
        assert len(mono)%2==1, "parity fail"
        anc = [i for i in mono if (i-1)%5 not in mono and (i+1)%5 not in mono]
        assert len(anc)<=1, "ANCHOR UNIQUENESS FAILS"
        tot += len(anc)
    return tot

def audit(name, n, E, allcut_R=True, expect=None):
    n,E,adj = mkgraph(n,E)
    pents = pent_list(n,E,adj)
    t5 = trA5(n,adj)
    assert t5 == 10*len(pents), (name,"trA5 mismatch",t5,len(pents))
    beta = beta_exhaustive(n,E)
    mc = len(E)-beta
    deg = [len(adj[i]) for i in range(n)]
    delta = min(deg)
    win = 25*delta > 4*n-2
    Rb = 0
    propA_ok = True
    if allcut_R:
        for m in range(1<<(n-1)):
            r1 = R_pathcount(n,E,adj,m)
            r2 = R_anchor(n,pents,m)
            assert r1==r2, (name,"R formula vs anchor mismatch at cut",m,r1,r2)
            if r1 > len(pents): propA_ok = False
            if r1 > Rb: Rb = r1
    x = Fraction(25*beta, n*n); y = Fraction(3125*Rb, n**5)
    kap = None
    if x < 1 and beta >= 0:
        kap = (1-y)/(1-x)
    print(f"{name}: N={n} e={len(E)} maxcut={mc} beta={beta} #C5={len(pents)} Rbest(ALLcuts)={Rb} delta={delta} win={int(win)} x={x} y={y} forced_kappa={kap} PropA={'OK' if propA_ok else 'VIOLATED'}")
    if expect:
        for k,v in expect.items():
            got = {"e":len(E),"maxcut":mc,"beta":beta,"C5":len(pents),"R":Rb,"kappa":kap,"x":x,"y":y}[k]
            assert got==v, (name,k,"expected",v,"got",got)
        print(f"  expectations {list(expect.keys())} ALL MATCH")
    return dict(n=n,beta=beta,C5=len(pents),R=Rb,x=x,y=y,kap=kap,win=win)

def circulant(k,D):
    return [(i,(i+d)%k) for i in range(k) for d in D]

def blowup(nb, Eb, sizes):
    ofs=[]; t=0
    for s in sizes: ofs.append(t); t+=s
    E=[(ofs[u]+i, ofs[v]+j) for (u,v) in Eb for i in range(sizes[u]) for j in range(sizes[v])]
    return t,E

def hom_to_C5(n, adj):
    # backtracking: map vertices to Z5, edges must map to (i,i+-1 mod5)
    col = [-1]*n
    order = sorted(range(n), key=lambda v:-len(adj[v]))
    def bt(i):
        if i==n: return True
        v = order[i]
        for c in range(5):
            ok=True
            for w in adj[v]:
                if col[w]!=-1 and col[w] not in ((c+1)%5,(c-1)%5):
                    ok=False; break
            if ok:
                col[v]=c
                if bt(i+1): return True
                col[v]=-1
        return False
    return bt(0)

print("=== independent audit_verify ===")
# 1. Petersen
PE = [(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+[(5,7),(7,9),(9,6),(6,8),(8,5)]
r = audit("Petersen",10,PE,expect={"e":15,"maxcut":12,"beta":3,"C5":12,"R":12,
        "kappa":Fraction(5,2),"x":Fraction(3,4),"y":Fraction(3125*12,10**5)})
# 2. C13(1,5)
r13 = audit("C13(1,5)",13,circulant(13,[1,5]),expect={"beta":6,"C5":52,"R":50,
        "kappa":Fraction(215043,41743),"x":Fraction(150,169)})
n13,E13,adj13 = mkgraph(13,circulant(13,[1,5]))
print("  C13(1,5) hom->C5 exists?", hom_to_C5(13,adj13), "(report claims NOT hom-C5 -> expect False)")
# 3. Groetzsch
GE = [(i,(i+1)%5) for i in range(5)]
for j in range(5): GE += [(5+j,(j-1)%5),(5+j,(j+1)%5),(5+j,10)]
rg = audit("Groetzsch",11,GE)
# 4. C5[t] doubly tight t=1,2,3
Eb5 = [(i,(i+1)%5) for i in range(5)]
for t in (1,2,3):
    N,E = blowup(5,Eb5,(t,)*5)
    rt = audit(f"C5[{t}]",N,E, allcut_R=(N<=15))
    assert rt["beta"]==t*t and rt["C5"]==t**5, "tightness fail"
    if N<=15: assert rt["R"]==t**5, "R_best != t^5"
    print(f"  C5[{t}]: beta=t^2, #C5=t^5, Rbest=t^5 (allcuts)  -> (x,y)=(1,1) doubly tight CONFIRMED")
# 5. base case N<=5: enumerate all TF graphs on 5 vertices, check beta<=1
import itertools as it
cnt=0; bad=0
for k in range(11):
    for Es in it.combinations(list(it.combinations(range(5),2)),k):
        adj=[set() for _ in range(5)]; tri=False
        for u,v in Es:
            if adj[u]&adj[v]: tri=True; break
            adj[u].add(v); adj[v].add(u)
        if tri: continue
        cnt+=1
        b = beta_exhaustive(5,list(Es))
        if b>1: bad+=1
print(f"base case: {cnt} TF graphs on N=5 enumerated, beta>1 count={bad} (expect 0)")
print("=== audit_verify DONE ===")
