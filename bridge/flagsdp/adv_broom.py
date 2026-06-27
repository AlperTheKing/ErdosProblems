#!/usr/bin/env python3
"""Adversarial broom-clustered attack on the safe-peel lemma (Erdos #23, delta=0).

Angle: inflate mass(M_C) = sum over bad edges incident to a peel-cycle C of (d_B+1)^2.
Build a small core (a short B-path or a C5 transversal) that carries MANY long odd ears
(high-ell bad edges) all sharing the SAME few vertices, so peeling the shortest geodesic
removes a huge Gamma-mass -> tries to violate (iii) L <= 2|C|N - |C|^2.

We rely on peel_check.check_instance (it auto-picks the max cut MINIMIZING Gamma).
Report ONLY harness-verified instances. An obstruction = ok & triangle_free & B_connected
& ge_n2 & m>=2 & has_safe_peel False.
"""
import sys
from peel_check import check_instance, maxcut_all, Bconnected, gamma_of

def mk(n):
    return [set() for _ in range(n)]

def add(adj,u,v):
    if u!=v:
        adj[u].add(v); adj[v].add(u)

def summarize(name, n, adj, verbose=True):
    r = check_instance(n, adj)
    obstruction = (r.get("ok") and r.get("triangle_free") and r.get("B_connected")
                   and r.get("ge_n2") and (r.get("m") or 0)>=2 and r.get("has_safe_peel") is False)
    near = False
    if r.get("ok") and r.get("B_connected") and (r.get("m") or 0)>=2:
        g=r.get("gamma"); n2=r.get("n2")
        if g is not None and n2 and g >= n2 - max(2, n2//50):  # within ~2% of tight
            near = True
    tag = "*** OBSTRUCTION ***" if obstruction else ("near-tight" if near else "")
    if verbose or obstruction or near:
        print(f"[{name}] N={r.get('N')} tf={r.get('triangle_free')} Bconn={r.get('B_connected')} "
              f"m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} tight={r.get('tight')} "
              f"ge_n2={r.get('ge_n2')} safe_peel={r.get('has_safe_peel')} {tag}")
        if not r.get("ok") or not r.get("B_connected"):
            print(f"      detail: {r.get('detail')}")
    return r, obstruction, near

# ---- Building blocks --------------------------------------------------------
# C5[q] balanced blow-up backbone (the tight family). Parts 0..4, each size q.
def c5_blowup(qs):
    """qs = list of 5 part sizes. Returns (n, adj, parts) where parts[i] = list of vertex ids."""
    parts=[]; nxt=0
    for q in qs:
        parts.append(list(range(nxt,nxt+q))); nxt+=q
    n=nxt; adj=mk(n)
    for i in range(5):
        for u in parts[i]:
            for v in parts[(i+1)%5]:
                add(adj,u,v)
    return n,adj,parts

if __name__=="__main__":
    print("=== sanity: balanced C5[q] (tight, should have safe peel) ===")
    for q in (2,3,4):
        n,adj,parts=c5_blowup([q]*5)
        summarize(f"C5[{q}]", n, adj)
