#!/usr/bin/env python3
"""Adversarial referee of STRATEGY F (theta-decomposition / SP reduction) for D25.
Self-contained: re-derives t, nu*, and the obstruction kappa* from scratch (no reliance on
the colleague's modules) so any bug in their code does not propagate.

Three independent checks:
  (A) Re-verify nu*, t for theta/C5/C5[2]/K23; confirm where 25 is tight (only C5[q]) vs slack (theta).
  (B) THE KEY-LEMMA CLAIM: is (t, nu*) additive across an odd-cycle-straddling 2-cut? Build the
      glue explicitly and recompute on the merged graph. If additivity holds in straddling cases,
      Strategy F could glue; if it fails, the induction is unsound (the colleague's claim).
  (C) THE OBSTRUCTION: directly compute the saddle kappa* = max_w min_S sum_e min_C w(C) on K23,
      and the FIXED-signature value (no rotation). Then ask: does Strategy F's SP machinery ever
      face this max_w/min_S saddle, or does it pass it untouched into the 3-connected leaf?
"""
import itertools
from fractions import Fraction as F
from scipy.optimize import linprog
import numpy as np

# ---------- graph primitives ----------
def adjset(N, E):
    adj = [set() for _ in range(N)]
    for (u, v) in E:
        adj[u].add(v); adj[v].add(u)
    return adj

def maxcut(N, E):
    adj = adjset(N, E)
    best = -1; bs = None
    for mask in range(1 << (N - 1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for (u, v) in E if side[u] != side[v])
        if c > best: best = c; bs = side
    return best, bs

def tau_of(N, E):
    mc, _ = maxcut(N, E)
    return len(E) - mc

def all_odd_cycles(N, E):
    adj = adjset(N, E)
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i + 1) % len(path)])) for i in range(len(path)))
                if es not in seen:
                    seen.add(es); out.append((es, frozenset(path)))
            elif w not in ps and w > start and len(path) < N:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N):
        dfs(s, s, [s], {s})
    return out

def nu_star(N, E):
    cyc = all_odd_cycles(N, E)
    if not cyc: return 0.0
    Eset = [frozenset(e) for e in E]
    nC = len(cyc)
    c = -np.ones(nC)
    A_ub = []; b_ub = []
    for a in Eset:
        row = [1.0 if a in C[0] else 0.0 for C in cyc]
        A_ub.append(row); b_ub.append(1.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * nC, method="highs")
    return -res.fun if res.success else 0.0

# ---------- builders ----------
def c5n(k):
    N = 5 * k; part = lambda v: v // k; E = []
    for u in range(N):
        for v in range(u + 1, N):
            if (part(u) - part(v)) % 5 in (1, 4): E.append((u, v))
    return N, E

def theta_atom(l1, l2):
    E = [(0, 1)]; nxt = 2; prev = 0
    for _ in range(l1 - 1):
        E.append((prev, nxt)); prev = nxt; nxt += 1
    E.append((prev, 1)); prev = 0
    for _ in range(l2 - 1):
        E.append((prev, nxt)); prev = nxt; nxt += 1
    E.append((prev, 1))
    return nxt, E

def gpt_k23():
    N = 13; E = []
    for i in (0, 1):
        for j in (2, 3, 4): E.append((i, j))
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt + 1; nxt += 2
        E.append((x, a)); E.append((a, b)); E.append((b, y))
    return N, E

def two_sum_straddle(N1, E1, c1, N2, E2, c2, delete_shared):
    """identify c1=(x1,y1) with c2=(x2,y2); relabel K2."""
    x1, y1 = c1; x2, y2 = c2
    newid = {x2: x1, y2: y1}; nxt = N1
    for v in range(N2):
        if v in (x2, y2): continue
        newid[v] = nxt; nxt += 1
    es = set((min(u, v), max(u, v)) for (u, v) in E1)
    for (u, v) in E2:
        uu, vv = newid[u], newid[v]; e = (min(uu, vv), max(uu, vv))
        if delete_shared and e == (min(x1, y1), max(x1, y1)): continue
        es.add(e)
    return nxt, list(es)

# ---------- (C) the saddle kappa* on K23 directly ----------
def min_signatures(N, E, tau):
    mc, side = maxcut(N, E)
    M0 = set(frozenset((u, v)) for (u, v) in E if side[u] == side[v])
    Eset = [frozenset(e) for e in E]
    sigs = set()
    for wm in range(1 << N):
        W = [(wm >> u) & 1 for u in range(N)]
        sig = frozenset(e for e in Eset if (W[min(e)] ^ W[max(e)]) ^ (e in M0))
        if len(sig) == tau: sigs.add(sig)
    return list(sigs)

def kappa_saddle(N, E):
    """kappa* = max_{w>=0,sum=1} min_S sum_{e in S} min_{C odd, C cap S={e}} w(C).
    Solve as an LP in w with the inner min_S handled by: for the TRUE kappa* we need
    min over S of a concave-in-w function, which is itself the LP-dual congestion value.
    We instead solve the primal congestion LP (same as lemma16) which equals kappa* by LP duality:
       min kappa s.t. sum_S p_S=1; sum_C w_{S,e,C}=p_S; sum_{(S,e,C): a in C} w <= kappa.
    """
    tau = tau_of(N, E)
    Eset = [frozenset(e) for e in E]
    sigs = min_signatures(N, E, tau)
    cyc = all_odd_cycles(N, E)
    varlist = []
    for si, S in enumerate(sigs):
        for e in S:
            for ci, C in enumerate(cyc):
                inter = C[0] & S
                if len(inter) == 1 and e in inter:
                    varlist.append((si, e, ci))
    nv = len(varlist); nS = len(sigs)
    KAP = nv + nS; nvar = nv + nS + 1
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    row = np.zeros(nvar)
    for s in range(nS): row[nv + s] = 1.0
    A_eq.append(row); b_eq.append(1.0)
    se = {}
    for vi, (si, e, ci) in enumerate(varlist): se.setdefault((si, e), []).append(vi)
    for (si, e), vis in se.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        row[nv + si] = -1.0
        A_eq.append(row); b_eq.append(0.0)
    A_ub = []; b_ub = []
    for a in Eset:
        row = np.zeros(nvar)
        for vi, (si, e, ci) in enumerate(varlist):
            if a in cyc[ci][0]: row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq),
                  b_eq=np.array(b_eq), bounds=[(0, None)] * nvar, method="highs")
    return (res.fun if res.success else float('inf')), nS, len(cyc)

def kappa_fixed_sig(N, E, S):
    """congestion using ONLY the single fixed signature S (no rotation): the min-max private-cycle
    congestion restricted to p concentrated on S."""
    Eset = [frozenset(e) for e in E]
    cyc = all_odd_cycles(N, E)
    Sset = frozenset(frozenset(e) for e in S)
    varlist = []
    for e in Sset:
        for ci, C in enumerate(cyc):
            inter = C[0] & Sset
            if len(inter) == 1 and e in inter:
                varlist.append((e, ci))
    nv = len(varlist); KAP = nv; nvar = nv + 1
    grp = {}
    for vi, (e, ci) in enumerate(varlist): grp.setdefault(e, []).append(vi)
    # sanity: every edge of S must have at least one private cycle, else S0 invalid for this LP
    if len(grp) != len(Sset):
        return ("INVALID: S has %d edges but only %d have private cycles" % (len(Sset), len(grp)))
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    for e, vis in grp.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        A_eq.append(row); b_eq.append(1.0)  # each bad edge routes a full unit private cycle
    A_ub = []; b_ub = []
    for a in Eset:
        row = np.zeros(nvar)
        for vi, (e, ci) in enumerate(varlist):
            if a in cyc[ci][0]: row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub, dtype=float), b_ub=np.array(b_ub, dtype=float),
                  A_eq=np.array(A_eq, dtype=float), b_eq=np.array(b_eq, dtype=float),
                  bounds=[(0, None)] * nvar, method="highs")
    return res.fun if res.success else float('inf')

if __name__ == "__main__":
    print("=== (A) tight vs slack: where does 25 live? ===")
    for lab, (N, E) in [("C5", c5n(1)), ("C5[2]", c5n(2)), ("theta(4,6)", theta_atom(4, 6)),
                        ("theta(4,4)", theta_atom(4, 4)), ("K23-N13", gpt_k23())]:
        t = tau_of(N, E); nu = nu_star(N, E); tgt = 25 * t * t / (N * N)
        tight = abs(nu - tgt) < 1e-6
        print(f"  {lab:11s} n={N:2d} t={t} nu*={nu:.4f} 25t^2/n^2={tgt:.4f} TIGHT={tight}")

    print("\n=== (B) additivity of (t,nu*) across an odd-cycle-STRADDLING 2-cut ===")
    cases = []
    N1, E1 = c5n(2); N2, E2 = theta_atom(4, 6)
    cases.append(("C5[2] (+) theta46 @straddle bad edge", two_sum_straddle(N1, E1, (0, 5), N2, E2, (0, 1), True),
                  (N1, E1), (N2, E2)))
    Na, Ea = theta_atom(4, 6); Nb, Eb = theta_atom(4, 6)
    cases.append(("theta46 (+) theta46 @ bad edge", two_sum_straddle(Na, Ea, (0, 1), Nb, Eb, (0, 1), False),
                  (Na, Ea), (Nb, Eb)))
    Nc, Ec = c5n(1); Nd, Ed = c5n(1)
    cases.append(("C5 (+) C5 @ pure B-edge 2-cut", two_sum_straddle(Nc, Ec, (0, 2), Nd, Ed, (0, 2), False),
                  (Nc, Ec), (Nd, Ed)))
    for lab, (Nm, Em), (Na, Ea), (Nb, Eb) in cases:
        t1, t2, tm = tau_of(Na, Ea), tau_of(Nb, Eb), tau_of(Nm, Em)
        nu1, nu2, num = nu_star(Na, Ea), nu_star(Nb, Eb), nu_star(Nm, Em)
        print(f"  {lab}")
        print(f"     t: {t1}+{t2}={t1+t2} vs merged {tm}  ADDITIVE={tm==t1+t2}")
        print(f"     nu*: {nu1:.3f}+{nu2:.3f}={nu1+nu2:.3f} vs merged {num:.3f}  ADDITIVE={abs(num-(nu1+nu2))<1e-6}")

    print("\n=== (C) the saddle (rotation) obstruction on K23-N13 ===")
    N, E = gpt_k23(); t = tau_of(N, E)
    # fixed natural signature S0 = the 4 'bad' chord edges (0,1),(2,3),(2,4),(3,4)
    S0 = [(0, 1), (2, 3), (2, 4), (3, 4)]
    kf = kappa_fixed_sig(N, E, S0)
    print(f"  fixed-signature S0 congestion (no rotation) = {kf:.4f}  (expect 4/3={4/3:.4f})")
    ks, nS, nC = kappa_saddle(N, E)
    print(f"  saddle kappa* (rotation over {nS} min sigs, {nC} odd cycles) = {ks:.4f}  (expect 6/5={6/5:.4f})")
    print(f"  floor n^2/(25t) = {N*N/(25*t):.4f}")
    print(f"  ROTATION GAP: fixed {kf:.4f} -> rotated {ks:.4f} (drop = {kf-ks:.4f})")
    print("DONE", flush=True)
