## On the M5-cycle CD-valid instance: does a FRACTIONAL layering exist?
## We want phi:V->R with (i) |phi(a)-phi(b)|<=1 for B-edges (1-Lipschitz),
## (ii) |phi(u)-phi(v)|=4 for bad edges (forced by d_B=4 and Lipschitz: actually <=4 always,
##      and =4 only if the geodesic is "straight"). The coarea identity then gives
##      4|M| = sum_M|drop| <= sum_B|drop| <= |B|. Linear bound 4|M|<=|B|. Check it holds here.
import networkx as nx
def build_M5():
    B=nx.Graph(); M=[]; Xset=set(); Yset=set()
    ms=[f"m{i}" for i in range(5)]; Xset|=set(ms)
    edges=[(ms[i],ms[(i+1)%5]) for i in range(5)]
    for (u,v) in edges:
        a=f"a_{u}_{v}"; w=f"w_{u}_{v}"; b=f"b_{u}_{v}"
        Yset|={a,b}; Xset|={w}
        for e in [(u,a),(a,w),(w,b),(b,v)]: B.add_edge(*e)
        M.append((u,v))
    B.add_nodes_from(Xset|Yset)
    return B,M,Xset,Yset
B,M,X,Y=build_M5()
print("|B|=",B.number_of_edges(),"|M|=",len(M),"4|M|<=|B|?",4*len(M)<=B.number_of_edges())
# A fractional phi making EVERY bad edge drop=4 and every B-edge drop<=1 simultaneously is
# again a {0,4}-2-coloring of M up to scaling => impossible for odd M-cycle. So even FRACTIONAL
# straight layering fails. The coarea bound only gives, per single phi, sum_M|drop|<=|B|, and we
# canNOT force every M-drop to 4 at once. Confirm: max over phi of min bad-edge drop.
# LP: maximize t s.t. exists phi, |phi(a)-phi(b)|<=1 on B, |phi(u)-phi(v)|>=t on M (with signs free).
# Sign-free abs makes it nonconvex; the obstruction is exactly the odd cycle (frustration).
print("=> No single 1-Lipschitz phi can give all 5 bad edges drop 4 (odd M-cycle frustration).")
print("=> Confirms: the coarea/single-potential route is structurally insufficient in general;")
print("   the bound must use the FULL family of CD flips, not one foliation.")
