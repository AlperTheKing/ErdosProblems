#!/usr/bin/env python3
"""Targeted near-tight FAMILY search for the safe-peel lemma (Erdos #23 delta=0).
Construct non-C5[q] families that should push Gamma/N^2 high:
  - unbalanced C5 blow-ups C5[q1..q5]
  - odd-cycle blow-ups C7[q], C9[q]
  - C5[q] with a few edges deleted/added (perturbations)
  - "prisms"/Mobius-type triangle-free graphs
Rank by Gamma/N^2 among m>=2 connected-B; report safe-peel status; flag obstructions."""
import itertools
from peel_check import check_instance

def Cm_blowup(parts):
    """Blow-up of cycle C_len with given part sizes (complete bipartite links between consecutive)."""
    L=len(parts); n=sum(parts); off=[0]*(L+1)
    for i in range(L): off[i+1]=off[i]+parts[i]
    adj=[set() for _ in range(n)]
    def vid(i,a): return off[i]+a
    for i in range(L):
        j=(i+1)%L
        for a in range(parts[i]):
            for b in range(parts[j]):
                u=vid(i,a); v=vid(j,b)
                adj[u].add(v); adj[v].add(u)
    return n,adj

def report(name, n, adj, collect):
    r=check_instance(n,adj)
    ok = r.get("ok") and r.get("B_connected") and r.get("m",0)>=2 and r.get("gamma") is not None
    if not ok:
        return
    ratio=r["gamma"]/r["n2"]
    collect.append((ratio, n, r["m"], r["gamma"], r["has_safe_peel"], name, r))
    flag = " <-- OBSTRUCTION" if (r["has_safe_peel"] is False and r["gamma"]>=r["n2"]) else (" NOPEEL" if r["has_safe_peel"] is False else "")
    print(f"{name}: N={n} m={r['m']} gamma={r['gamma']} n2={r['n2']} ratio={ratio:.5f} tight={r['tight']} safe_peel={r['has_safe_peel']}{flag}")

def main():
    collect=[]
    # Balanced C5[q] baseline
    for q in range(2,5):
        n,adj=Cm_blowup([q]*5); report(f"C5[{q}]", n, adj, collect)
    # Unbalanced C5 blow-ups: vary part sizes, keep N<=26 (keep<=22 for peel CD on shortest geodesic)
    print("--- unbalanced C5 blow-ups ---")
    seen=set()
    for parts in itertools.product(range(1,6),repeat=5):
        if sum(parts)>22: continue
        # canonical under rotation+reflection to cut dupes
        rots=[]
        for s in range(5):
            r1=parts[s:]+parts[:s]; rots.append(r1); rots.append(r1[::-1])
        canon=min(rots)
        if canon!=list(parts) and tuple(canon) in seen: continue
        seen.add(tuple(canon))
        if min(parts)==max(parts): continue  # skip balanced (already done)
        n,adj=Cm_blowup(list(parts))
        report(f"C5{parts}", n, adj, collect)
    # C7, C9 blow-ups
    print("--- C7 / C9 blow-ups ---")
    for q in range(1,4):
        n,adj=Cm_blowup([q]*7)
        if n<=24: report(f"C7[{q}]", n, adj, collect)
    for q in range(1,3):
        n,adj=Cm_blowup([q]*9)
        if n<=24: report(f"C9[{q}]", n, adj, collect)
    # unbalanced C7 (one part bigger)
    for big in range(2,5):
        for pos in range(1):
            parts=[1]*7; parts[0]=big
            n,adj=Cm_blowup(parts)
            if n<=22: report(f"C7{tuple(parts)}", n, adj, collect)

    # ---- C5[q] perturbations: delete a single bad-creating? No, delete a cross edge ----
    print("--- C5[q] with one cross-edge deleted ---")
    for q in (3,4):
        n,base=Cm_blowup([q]*5)
        # delete one edge between part0[0] and part1[0]
        import copy
        adj=[set(s) for s in base]
        adj[0].discard(q); adj[q].discard(0)   # vid(1,0)=q
        report(f"C5[{q}]-1edge", n, adj, collect)

    # rank
    collect.sort(key=lambda x:-x[0])
    print("\n=== TOP 20 family instances by ratio ===")
    for (ratio,n,m,gamma,sp,name,r) in collect[:20]:
        print(f"  ratio={ratio:.5f} N={n} m={m} gamma={gamma} tight={gamma==n*n} safe_peel={sp} {name}")
    obstr=[c for c in collect if c[4] is False and c[3]>=c[1]*c[1]]
    nopeel=[c for c in collect if c[4] is False]
    print(f"\nNOPEEL count (any ratio): {len(nopeel)}; OBSTRUCTIONS (tight,no-peel): {len(obstr)}")
    for (ratio,n,m,gamma,sp,name,r) in obstr[:5]:
        print(f"  OBSTRUCTION {name}: N={n} m={m} gamma={gamma}")

if __name__=="__main__":
    main()
