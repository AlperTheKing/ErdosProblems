#!/usr/bin/env python3
"""Broaden the (16) audit: test the min-signature private-cycle congestion lemma on ALL 2-connected
edge-critical triangle-free atoms N<=9. (16): min-max private-cycle congestion kappa* <= n^2/(25 tau)."""
import numpy as np
from collections import deque
from scipy.optimize import linprog
import flag_engine as fe
import verify_D25_lemma16 as L

def is_2connected(N, adj):
    if N < 3: return False
    # connected and no cut vertex
    def conn(skip):
        seen = set(); start = next((v for v in range(N) if v != skip), None)
        if start is None: return True
        st = [start]; seen.add(start)
        while st:
            u = st.pop()
            for v in adj[u]:
                if v != skip and v not in seen: seen.add(v); st.append(v)
        return len(seen) == N - (1 if skip is not None else 0)
    if not conn(None): return False
    for w in range(N):
        if not conn(w): return False
    return True

def tau_of(N, adj):
    mc, _ = L.maxcut(N, adj)
    e = sum(len(adj[u]) for u in range(N))//2
    return e - mc

def is_edge_critical(N, A, adj, tau):
    edges = [(u, v) for u in range(N) for v in adj[u] if v > u]
    for (u, v) in edges:
        A2 = [A[i] for i in range(N)]
        A2[u] &= ~(1 << v); A2[v] &= ~(1 << u)
        adj2 = L.adjset(N, A2)
        if tau_of(N, adj2) >= tau: return False
    return True

def lemma16_val(N, A):
    """returns (kappa*, target, tau) or None."""
    adj = L.adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges) - mc
    if tau == 0: return None
    sigs = L.min_signatures(N, adj, edges, tau)
    cyc = L.all_odd_cycles_v(N, adj)
    varlist = []
    for si, S in enumerate(sigs):
        for e in S:
            for ci, C in enumerate(cyc):
                inter = C & S
                if len(inter) == 1 and (e in inter): varlist.append((si, e, ci))
    if not varlist: return ('nosel', tau)
    nv = len(varlist); nS = len(sigs); KAP = nv+nS; nvar = nv+nS+1
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    row = np.zeros(nvar)
    for s in range(nS): row[nv+s] = 1.0
    A_eq.append(row); b_eq.append(1.0)
    se = {}
    for vi, (si, e, ci) in enumerate(varlist): se.setdefault((si, e), []).append(vi)
    for (si, e), vis in se.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        row[nv+si] = -1.0
        A_eq.append(row); b_eq.append(0.0)
    A_ub = []; b_ub = []
    for a in edges:
        row = np.zeros(nvar)
        for vi, (si, e, ci) in enumerate(varlist):
            if a in cyc[ci]: row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=[(0, None)]*nvar, method="highs")
    return (res.fun if res.success else float('inf'), N*N/(25.0*tau), tau)

if __name__ == "__main__":
    print("=== (16) over all 2-connected edge-critical triangle-free atoms N<=9 ===", flush=True)
    worst = 0.0; viol = 0; natoms = 0; nosel = 0
    for N in [5, 6, 7, 8, 9]:
        states = fe.enumerate_graphs(N, triangle_free=True); cnt = 0; wN = 0.0
        for (n, A) in states:
            adj = L.adjset(n, A)
            if not is_2connected(n, adj): continue
            tau = tau_of(n, adj)
            if tau == 0: continue
            if not is_edge_critical(n, A, adj, tau): continue
            r = lemma16_val(n, A)
            if r is None: continue
            if r[0] == 'nosel': nosel += 1; continue
            kappa, target, t = r; cnt += 1; natoms += 1
            ratio = kappa/target if target > 0 else 9
            if kappa > target + 1e-6: viol += 1; print(f"  VIOLATION N={n} tau={t} kappa*={kappa:.4f} target={target:.4f}", flush=True)
            wN = max(wN, ratio); worst = max(worst, ratio)
        print(f"N={N}: {cnt} critical atoms tested, worst kappa*/target={wN:.4f}", flush=True)
    print(f">>> total {natoms} atoms, (16) VIOLATIONS={viol}, overall worst kappa*/target={worst:.4f}, no-selector={nosel}", flush=True)
    print("DONE", flush=True)
