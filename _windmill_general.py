import networkx as nx
# Friendship graph F_k = windmill(k,3): k triangles sharing a hub. n=2k+1.
# Closed forms:
#   edges: hub-blade = 2k edges deg(8?) hub deg=2k, blade deg=2; blade-blade = k edges deg(2,2)
#   H = 2k * 2/(2k+2) + k * 2/(2+2) = 4k/(2k+2) + k/2 = 2k/(k+1) + k/2
#   mu*: hub matched to >=0; to be maximal each triangle needs a covered vertex.
#        Optimal: match hub into ONE triangle (covers that triangle's blade-blade is free though).
#        Known: mu*(F_k) = ? brute force below + formula guess k+1? Let's compute.
def mmm(G):
    from itertools import combinations
    edges=list(G.edges()); best=None
    for r in range(0,len(edges)+1):
        if best is not None and r>=best: break
        for S in combinations(edges,r):
            used=set(); ok=True
            for u,v in S:
                if u in used or v in used: ok=False;break
                used.add(u);used.add(v)
            if not ok: continue
            if all((a in used or b in used) for a,b in edges):
                best=r; break
        if best==r: break
    return best
def H(G): return sum(2.0/(G.degree(u)+G.degree(v)) for u,v in G.edges())
print("k   n   mu*   H        H_formula   margin(H-mu*)")
for k in range(2,8):
    G=nx.windmill_graph(k,3)
    mm=mmm(G); h=H(G)
    hf = 2*k/(k+1) + k/2.0
    print("%-3d %-3d %-4d %-8.4f %-10.4f %.4f"%(k,2*k+1,mm,h,hf,h-mm))
print()
print("As k->inf: H ~ k/2 + 2, mu* ~ k  =>  mu* - H ~ k/2 -> +inf. Margin DIVERGES; counterexample family is robust.")
