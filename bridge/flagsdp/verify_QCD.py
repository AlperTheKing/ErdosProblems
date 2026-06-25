#!/usr/bin/env python3
"""AUDIT GPT's QCD certificate (chat 6a3b5aba) for the Connected-B Gamma Lemma:
Does there exist cut weights a_S >= 0 with coverage h_a(e)=sum_{S: e in delta_M(S)} a_S = ell_e (=d_B(e)+1)
for every bad edge e, AND  sum_{S,T} a_S a_T min{b(S),b(T)} <= N^2 ?
If yes, QCD gives Gamma = sum ell_e^2 = sum h_a(e)^2 <= sum a_S a_T min{b(S),b(T)} <= N^2 => the lemma.
min{b,b} is a PSD kernel => convex QP: min a^T Q a s.t. C a = ell, a>=0. Tight expected at C5[q].
Cuts restricted to boundary b(S) <= Bmax (aligns with GPT's elementary theta cuts; harder constraint).
"""
import itertools
import numpy as np
from collections import deque

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]
def maxcut(N, adj):
    best = -1; bs = None
    for m in range(1 << (N-1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and s[u] != s[v])
        if c > best: best = c; bs = s
    return best, bs
def bdist(N, adjB, s):
    d = [-1]*N; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v in adjB[u]:
            if d[v] < 0: d[v] = d[u]+1; q.append(v)
    return d

def solve_QP(Q, C, ell):
    """min a^T Q a s.t. C a = ell, a>=0. Try cvxpy; else scipy SLSQP."""
    n = Q.shape[0]
    try:
        import cvxpy as cp
        a = cp.Variable(n, nonneg=True)
        prob = cp.Problem(cp.Minimize(cp.quad_form(a, cp.psd_wrap(Q))), [C @ a == ell])
        val = prob.solve(solver=cp.OSQP, max_iter=200000, eps_abs=1e-7, eps_rel=1e-7)
        return val, a.value
    except Exception as ex:
        from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint
        cons = [LinearConstraint(C, ell, ell)]
        res = minimize(lambda a: a@Q@a, np.ones(n)*0.1, jac=lambda a: 2*Q@a,
                       bounds=[(0, None)]*n, constraints=cons, method="SLSQP",
                       options={"maxiter": 2000, "ftol": 1e-10})
        return res.fun, res.x

def audit(N, A, label, Bmax=8):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    M = [(u, v) for (u, v) in edges if side[u] == side[v]]
    Bset = [(u, v) for (u, v) in edges if side[u] != side[v]]
    adjB = [set() for _ in range(N)]
    for (u, v) in Bset: adjB[u].add(v); adjB[v].add(u)
    # ell_e
    ell = []
    for (u, v) in M:
        d = bdist(N, adjB, u); ell.append(d[v]+1)
    ell = np.array(ell, float); m = len(M)
    if m == 0: print(f"{label}: bipartite, skip"); return
    # enumerate cuts S subset {1..N-1} (fix vertex 0 out), boundary b(S)<=Bmax
    cuts = []; bvals = []; Crows = []  # Crows[e] -> list of cut indices separating e
    sepC = [[] for _ in range(m)]
    for mask in range(1 << (N-1)):
        S = set(u+1 for u in range(N-1) if (mask >> u) & 1)
        if not S: continue
        b = sum(1 for (u, v) in Bset if (u in S) != (v in S))
        if b == 0 or b > Bmax: continue
        ci = len(cuts); cuts.append(S); bvals.append(b)
        for ei, (u, v) in enumerate(M):
            if (u in S) != (v in S): sepC[ei].append(ci)
    nc = len(cuts)
    if nc == 0: print(f"{label}: no cuts with b<=Bmax"); return
    bvals = np.array(bvals, float)
    Q = np.minimum.outer(bvals, bvals)
    C = np.zeros((m, nc))
    for ei in range(m):
        for ci in sepC[ei]: C[ei, ci] = 1.0
    # feasibility of C a = ell, a>=0: each bad edge must be separable by some small cut
    if any(len(sepC[ei]) == 0 for ei in range(m)):
        print(f"{label}: some bad edge not separated by any b<=Bmax cut (raise Bmax)"); return
    val, a = solve_QP(Q, C, ell)
    Gamma = float(np.sum(ell**2))
    print(f"{label:14s} N={N:3d} m={m:3d} #cuts(b<={Bmax})={nc:5d} Gamma={Gamma:.1f} QCD_obj_min={val:.2f} "
          f"N^2={N*N} QCD<=N^2:{val <= N*N+1e-3} (Gamma<=obj always)", flush=True)

# builders
def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A
def c5paths20():
    N = 20; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    x = lambda i: i % 5; y = lambda i: 5+(i % 5); z = lambda i: 10+(i % 5); w = lambda i: 15+(i % 5)
    for i in range(5):
        add(x(i), x(i+1)); add(x(i), y(i)); add(y(i), z(i)); add(z(i), w(i)); add(w(i), x(i+1))
    return N, A
def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

if __name__ == "__main__":
    print("=== AUDIT QCD certificate: min sum a_S a_T min{b,b} s.t. h_a(e)=ell_e, a>=0;  <= N^2 ? ===", flush=True)
    audit(*c5n(1), "C5", Bmax=4)
    audit(*c5n(2), "C5[2]", Bmax=8)
    audit(*petersen(), "Petersen", Bmax=8)
    audit(*gpt_k23(), "K23-N13", Bmax=8)
    audit(*c5paths20(), "theta-N20", Bmax=6)
    print("DONE", flush=True)
