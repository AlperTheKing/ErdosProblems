"""For a g6, enumerate ALL gamma-min connected-B max cuts and report worst maxT vs K. Independent impl."""
from fractions import Fraction
import _synth_verify as S

def all_gmin_maxT(g6):
    n, adj, edges = S.dec_g6(g6)
    best, cuts = S.all_max_cuts(n, edges)
    # collect all connected-B cuts with bad edges, find min Gamma
    cand=[]
    minG=None
    for side in cuts:
        bedges=S.B_edges(edges, side)
        if not S.B_connected_spanning(n, side, bedges): continue
        bad=S.bad_edges(edges, side)
        if not bad: continue
        ell={}; ok=True
        for (u,v) in bad:
            d,_=S.bfs_dist_and_geos(n, bedges, u, v)
            if d==-1: ok=False; break
            ell[(u,v)]=d+1
        if not ok: continue
        G=sum(e*e for e in ell.values())
        cand.append((G, side, bad, ell, bedges))
        if minG is None or G<minG: minG=G
    if minG is None: return None
    worst=None; allT=[]
    for (G, side, bad, ell, bedges) in cand:
        if G!=minG: continue
        T=S.T_uniform(n, bad, ell, bedges)
        mT=max(T)
        allT.append(mT)
        if worst is None or mT>worst: worst=mT
    K=n+(n*n-minG)
    return n, minG, K, worst, len(allT), worst>K

if __name__=="__main__":
    for g6 in ['K?ABBBwerwBw','L?`DAboU`w@{hS','DUW','I?rFf_{N?','G?`F`w','H?bB@_W','J?AEB?oE?W?']:
        print(g6, all_gmin_maxT(g6))
