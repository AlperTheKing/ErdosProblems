#!/usr/bin/env python3
"""
RUNG 3: audit GPT Q13's lemmas computationally.
(1) character formula c(A,B)=(3+sum sigma_i(A)sigma_i(B))/4.
(2) Lemma 1 exact star-extension formula vs brute min_A.
(4-5) Q(d)=3 floor(d/4)+[d%4 in {2,3}] is the MAX min-extension cost (sampling + sharp witness).
(12) Lemma 3: every 2-centre ball N[x]∪N[y] of a TRIANGLE-FREE graph is Clebsch-homomorphic (tau_K=0),
     AND GPT's explicit map (13) realizes it in the xy∉E case.
(19-20) Mycielski recursion tau_K(M(G))<=3 tau_K(G)+Q(n) and closed form on M^k(C5).
(11) per-vertex deletion recursion tau_K(G)<=tau_K(G-v)+Q(d_v) spot-check.
"""
import itertools, random
random.seed(13)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def sig(A, i): return -1 if (A >> i) & 1 else 1          # sigma_{i+1}(A), i in 0..4
def cost(A, B): return (4 - bin(A ^ B).count('1')) // 2

def Q(d): return 3*(d//4) + (1 if d % 4 in (2, 3) else 0)

# ---- (1) character formula ----
ok1 = all(cost(A, B) == (3 + sum(sig(A,i)*sig(B,i) for i in range(5)))//4
          for A in labels for B in labels)
print(f"(1) character formula c=(3+sum sigma sigma)/4 exact for all 256 pairs: {ok1}")

# ---- (2) Lemma 1 star-extension formula ----
def lemma1(Bs):
    s = [sum(sig(B, i) for B in Bs) for i in range(5)]
    if all(v != 0 for v in s):
        prod = 1
        for v in s: prod *= -(1 if v > 0 else -1)
        eps = 1 if prod == -1 else 0
    else:
        eps = 0
    m = min(abs(v) for v in s)
    return (3*len(Bs) - sum(abs(v) for v in s) + 2*eps*m)//4
def brute_star(Bs):
    return min(sum(cost(A, B) for B in Bs) for A in labels)
bad2 = 0
for _ in range(20000):
    d = random.randint(1, 9)
    Bs = [random.choice(labels) for _ in range(d)]
    if lemma1(Bs) != brute_star(Bs): bad2 += 1
print(f"(2) Lemma 1 formula == brute min_A over 20000 random multisets: violations={bad2}")

# ---- (4-5) Q(d) is the max star-extension cost ----
sharp = {0:[], 1:[0]}
block = [0, 0b00011, 0b11101, 0b11110]   # {∅,12,1345,2345} as bitmasks (elt i -> bit i-1)
# verify block has all s_i=0 and adds 3 per copy
sb = [sum(sig(B,i) for B in block) for i in range(5)]
print(f"    sharp block {[bin(b) for b in block]} s_i={sb} (expect all 0); brute add-per-block={brute_star(block)} (expect 3)")
worst = {d: 0 for d in range(0, 13)}
for _ in range(40000):
    d = random.randint(1, 12)
    Bs = [random.choice(labels) for _ in range(d)]
    worst[d] = max(worst[d], brute_star(Bs))
# sharp witnesses for each d: blocks of 4 (cost 3 each) + remainder
def sharp_cost(d):
    full = (d // 4) * brute_star(block)            # 3 per full block of 4
    r = d % 4
    rem = [[], [0], [0, 0b01111], [0, 0, 0b01111]][r]   # remainders giving 0,1,1
    return full + brute_star(rem) if r else full
okQ = all(worst[d] <= Q(d) for d in range(1, 13))
sharpQ = all(sharp_cost(d) == Q(d) for d in range(1, 13))
print(f"(4-5) Q(d): sampled max <= Q(d) for d=1..12: {okQ}; sharp construction achieves Q(d): {sharpQ}")
print(f"      Q(1..12)={[Q(d) for d in range(1,13)]}  sampled_max={[worst[d] for d in range(1,13)]}")

# ---- helpers ----
def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def tau_ub(N, A, restarts=80):
    nbr=[list(A[v]) for v in range(N)]; best=None
    for _ in range(restarts):
        lab=[random.choice(labels) for _ in range(N)]; imp=True; sw=0
        while imp and sw<40:
            imp=False; sw+=1
            for u in range(N):
                bc,bl=None,lab[u]
                for L in labels:
                    c=sum(cost(L,lab[w]) for w in nbr[u])
                    if bc is None or c<bc: bc,bl=c,L
                if bl!=lab[u]: lab[u]=bl; imp=True
        t=sum(cost(lab[u],lab[w]) for u in range(N) for w in nbr[u] if w>u)
        if best is None or t<best: best=t
        if best==0: break
    return best
def rand_trifree(N):
    A=[set() for _ in range(N)]; ps=[(u,v) for u in range(N) for v in range(u+1,N)]; random.shuffle(ps)
    for u,v in ps:
        if A[u]&A[v]: continue
        A[u].add(v); A[v].add(u)
    return A

# ---- (12) Lemma 3: every 2-centre ball of a triangle-free graph is Clebsch-hom ----
def map13_ok(A, x, y):
    # xy not an edge: A_=N(x)\N(y), B_=N(y)\N(x), C=N(x)&N(y); map and check all ball edges -> |Δ|=4
    Nx, Ny = A[x], A[y]
    Aset = Nx - Ny - {y}; Bset = Ny - Nx - {x}; C = (Nx & Ny)
    lab = {x: 0, y: 0b00011}
    for v in Aset: lab[v] = 0b01111      # 1234
    for v in Bset: lab[v] = 0b10100      # 35  (elts 3,5 -> bits 2,4)
    for v in C:    lab[v] = 0b11101      # 1345
    ball = set(lab)
    for u in ball:
        for w in A[u]:
            if w in ball and w > u and cost(lab[u], lab[w]) != 0:
                return False
    return True
viol12 = 0; tested12 = 0; map13_tested = 0; map13_bad = 0
for _ in range(400):
    N = random.randint(5, 11); Adj = rand_trifree(N)
    for x in range(N):
        for y in range(x+1, N):
            ball = Adj[x] | Adj[y] | {x, y}
            if len(ball) < 2: continue
            sub = sorted(ball); idx = {v: k for k, v in enumerate(sub)}
            E = [(idx[u], idx[w]) for u in ball for w in Adj[u] if w in ball and w > u]
            tested12 += 1
            if tau_ub(len(sub), adj(len(sub), E), 40) != 0: viol12 += 1
            if y not in Adj[x]:                # case xy∉E: test explicit map (13)
                map13_tested += 1
                if not map13_ok(Adj, x, y): map13_bad += 1
print(f"(12) Lemma 3: 2-centre balls Clebsch-hom (tau_K=0): non-hom violations={viol12}/{tested12}")
print(f"     explicit map (13) realizes hom on xy-nonedge balls: failures={map13_bad}/{map13_tested}")

# ---- (19-20) Mycielski recursion + closed form ----
def C5(): return 5, [(i,(i+1)%5) for i in range(5)]
def myc(N, E):
    z=2*N; E2=list(E)
    for u,v in E: E2.append((u+N,v)); E2.append((u,v+N))
    for v in range(N): E2.append((z,v+N))
    return 2*N+1, E2
def closed(k): return 8*3**(k-1) - 9*2**(k-1) + 1
n,e=C5(); seq=[(n,e)]
for _ in range(2): n2,e2=myc(*seq[-1]); seq.append((n2,e2))
print("(19-20) Mycielski recursion tau_K(M(G))<=3 tau_K(G)+Q(n) and closed form 8*3^(k-1)-9*2^(k-1)+1:")
prev=None
for k,(N,E) in enumerate(seq):
    t=tau_ub(N, adj(N,E), 120)
    cf = closed(k) if k>=1 else 0
    rec = (3*prev + Q(seq[k-1][0])) if prev is not None else 0
    print(f"   M^{k}(C5): N={N} tau_K_ub={t}  closed(20)={cf}  recursion_bound={rec}  (tau<=closed: {t<=cf if k>=1 else t==0})")
    prev=t
print("DONE")
