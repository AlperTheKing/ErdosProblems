"""Census sweep of the counting-entropy sub-lemma sum_v L^2 <= N*Gamma.
Tests on the gamma-min max cut (as the strategy specifies). Reports worst ratio + any violations.
Also tests the per-edge form W_e <= N*h_e."""
import sys
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos, gamma_of, maxcut_value, Bconnected
from flag_engine import enumerate_graphs

def ratios_for_cut(N,adj,side,G,M):
    he=[]; a=[]
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None  # bad edge with no B-geodesic (B disconnected for this pair)
        g=len(geos); h=len(geos[0]); he.append(h)
        cnt={}
        for P in geos:
            for w in P: cnt[w]=cnt.get(w,0)+1
        a.append({w:c/g for w,c in cnt.items()})
    L=[0.0]*N
    for ei in range(len(M)):
        for w,frac in a[ei].items(): L[w]+=he[ei]*frac
    sumL2=sum(x*x for x in L); rhs=N*G
    r2=sumL2/rhs if rhs>0 else 0.0
    worstWe=0.0
    for ei in range(len(M)):
        We=sum(frac*L[w] for w,frac in a[ei].items())
        rr=We/(N*he[ei]) if he[ei]>0 else 0.0
        if rr>worstWe: worstWe=rr
    return sumL2,rhs,r2,worstWe

def main(maxN, all_cuts=False):
    worst2=0.0; worstWe=0.0; viol=0; total=0; worstg=None
    for N in range(5,maxN+1):
        graphs=enumerate_graphs(N,triangle_free=True)
        for (n,A) in graphs:
            adj=[set(j for j in range(n) if A[i]>>j&1) for i in range(n)] if isinstance(A[0],int) else None
            # A is bitmask rows from _decode_g6? handle list-of-int adjacency-bitmask
            adj=[set() for _ in range(n)]
            for i in range(n):
                row=A[i]
                for j in range(n):
                    if (row>>j)&1: adj[i].add(j)
            E=edges_of(adj)
            if not E: continue
            if all_cuts:
                mc=maxcut_value(n,E);
                cuts=[]
                for mask in range(1<<(n-1)):
                    c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
                    if c!=mc: continue
                    side=[(mask>>u)&1 for u in range(n)]
                    if not Bconnected(n,adj,side): continue
                    Gv,Mv=gamma_of(n,adj,side)
                    if Gv is None: continue
                    cuts.append((side,Gv,Mv))
                if not cuts: continue
            else:
                res,mc=gamma_min_cut(n,adj,E)
                if res is None: continue
                cuts=[res]
            for (side,G,M) in cuts:
                if not M: continue
                out=ratios_for_cut(n,adj,side,G,M)
                if out is None: continue
                sumL2,rhs,r2,we=out
                total+=1
                if r2>worst2: worst2=r2; worstg=(n,A,G,len(M))
                if we>worstWe: worstWe=we
                if sumL2>rhs+1e-7: viol+=1; print("VIOLATION N=%d G=%d sumL2=%.4f rhs=%d"%(n,G,sumL2,rhs))
    print("maxN=%d all_cuts=%s | instances=%d worst sumL2/(N*G)=%.6f worst W_e/(N h_e)=%.6f violations=%d"%(
        maxN,all_cuts,total,worst2,worstWe,viol))
    if worstg: print("  worst-ratio graph: N=%d Gamma=%d beta=%d"%(worstg[0],worstg[2],worstg[3]))

if __name__=="__main__":
    mx=int(sys.argv[1]) if len(sys.argv)>1 else 9
    ac = len(sys.argv)>2 and sys.argv[2]=="allcuts"
    main(mx, ac)
