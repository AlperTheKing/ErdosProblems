#!/usr/bin/env python3
"""
Verify Q13 eq (17) — the local charging certificate identity — and probe the reformulated CF target.
For a 1-opt-stable labeling phi (stable under changing any single vertex):
  cost(phi) = (1/8) sum_v ( 3 d_v - sum_i |s_{v,i}| + 2 eps_v m_v ),   s_{v,i}=sum_{u in N(v)} sigma_i(phi(u)).
This is an EXACT identity at stability (each edge counted at both endpoints; per-vertex incident cost =
min-extension cost by Lemma 1). We verify it, and measure the reformulated CF inequality slack:
  cost(phi) <= RHS  <=>  sum_v sum_i |s_{v,i}| - 2 sum_v eps_v m_v  >=  10 e - 4 N^2/5.
"""
import random
random.seed(41)
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
def sig(A, i): return -1 if (A >> i) & 1 else 1
def cost(a, b): return (4 - bin(a ^ b).count('1')) // 2

def stable_label(N, A, restarts=30):
    """Return a 1-opt-stable labeling (local min under single-vertex changes) of lowest cost found."""
    nbr = [list(A[v]) for v in range(N)]; best = None; bestlab = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]; imp = True; sw = 0
        while imp and sw < 60:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc: bc, bl = c, L
                if bl != lab[u]: lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best: best = tot; bestlab = lab[:]
    return bestlab, best

def charging_terms(N, A, lab):
    total = 0
    for v in range(N):
        s = [sum(sig(lab[u], i) for u in A[v]) for i in range(5)]
        if all(x != 0 for x in s):
            prod = 1
            for x in s: prod *= -(1 if x > 0 else -1)
            eps = 1 if prod == -1 else 0
        else:
            eps = 0
        m = min(abs(x) for x in s) if s else 0
        d = len(A[v])
        total += 3*d - sum(abs(x) for x in s) + 2*eps*m
    return total  # = 8 * cost(phi) if stable

def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def C5(): return 5, [(i,(i+1)%5) for i in range(5)]
def myc(N, E):
    z=2*N; E2=list(E)
    for u,v in E: E2.append((u+N,v)); E2.append((u,v+N))
    for v in range(N): E2.append((z,v+N))
    return 2*N+1, E2
def rand_trifree(N):
    A=[set() for _ in range(N)]; ps=[(u,v) for u in range(N) for v in range(u+1,N)]; random.shuffle(ps)
    for u,v in ps:
        if A[u]&A[v]: continue
        A[u].add(v); A[v].add(u)
    return A
def is_stable(N, A, lab):
    for u in range(N):
        cur = sum(cost(lab[u], lab[w]) for w in A[u])
        for L in labels:
            if sum(cost(L, lab[w]) for w in A[u]) < cur: return False
    return True

print("(eq 17) charging identity: 8*cost(phi) == sum_v(3d_v - sum|s_vi| + 2 eps_v m_v) at 1-opt-stable phi")
bad = 0; tested = 0
for _ in range(300):
    N = random.randint(5, 13); A = rand_trifree(N)
    lab, c = stable_label(N, A, 12)
    if not is_stable(N, A, lab): continue
    tested += 1
    if charging_terms(N, A, lab) != 8*c: bad += 1
print(f"   identity holds at stable phi: violations={bad}/{tested}")

print("\nReformulated CF slack at stable phi (want LHS>=RHS_reform):  "
      "LHS=sum|s_vi|-2 sum eps_v m_v,  RHS_reform=10e-4N^2/5")
def report(tag, N, A):
    e = sum(len(A[v]) for v in range(N))//2
    lab, c = stable_label(N, A, 40)
    # LHS = sum|s_vi| - 2 sum eps m ; note 8 cost = 6e - LHS  => cost = (6e-LHS)/8; want cost<=RHS
    lhs = 0
    for v in range(N):
        s=[sum(sig(lab[u],i) for u in A[v]) for i in range(5)]
        if all(x!=0 for x in s):
            prod=1
            for x in s: prod*=-(1 if x>0 else -1)
            eps=1 if prod==-1 else 0
        else: eps=0
        m=min(abs(x) for x in s) if s else 0
        lhs += sum(abs(x) for x in s) - 2*eps*m
    rhs_ref = 10*e - 4*N*N/5
    rhs = (N*N/5.0 - e)/2.0
    print(f"   {tag:18s} N={N:3d} e={e:4d} cost(phi)={c:3d} RHS={rhs:6.1f} cost<=RHS={int(c<=rhs+1e-9)}  "
          f"| LHS={lhs} RHS_reform={rhs_ref:.1f} slack={lhs-rhs_ref:.1f}")
n,e=C5(); n2,e2=myc(n,e); n3,e3=myc(n2,e2)
report("M(M(C5))", n3, adj(n3,e3))
n4,e4=myc(n3,e3); report("M^3(C5)", n4, adj(n4,e4))
print("DONE")
