"""Pinned Wagner gadget (Codex block 92 / GPT-Pro): N=26, kills the BROAD constant-load bridge/SELFCAP.
   Add to the standing gate (anchored geodesically-idle pins -- census+glued+Mycielskians MISS these).
   O is empty here (lambda=25/2 < N=26), so GCD/cond3/SAT-ZMU-CONN are vacuous; sanity-check H>=0 anyway."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _gcd import build_H, is_psd_exact, run_gmin

WAGNER_N=26
WAGNER_E=[(0,1),(0,4),(0,7),(0,10),(1,2),(1,5),(1,12),(2,3),(2,6),(2,14),(3,4),(3,7),(3,16),
          (4,5),(4,18),(5,6),(5,20),(6,7),(6,22),(7,24),(8,9),(8,11),(8,15),(8,19),(8,23),
          (9,13),(9,17),(9,21),(9,25),(10,11),(12,13),(14,15),(16,17),(18,19),(20,21),(22,23),(24,25)]
WAGNER_SIDE=[0,1,0,1,0,1,0,1,1,0,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1]

if __name__=="__main__":
    n,E=WAGNER_N,WAGNER_E
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=WAGNER_SIDE
    # sanity: triangle-free, cut connected, bad edges
    tf=all(not (adj[u]&adj[v]) for u in range(n) for v in adj[u] if v>u)
    print(f"triangle_free={tf} Bconn={Bconn(n,adj,side)}")
    r=build_H(adj,side,n)
    if r is None:
        print("build_H None");
    else:
        H,T,N=r
        O=[v for v in range(n) if T[v]>N]
        print(f"|O|={len(O)} (expect 0)  H>=0 (exact PSD)={is_psd_exact(H,n)}  maxT={float(max(T)):.4f} N={N}")
    # also run via run_gmin (the gate entry point)
    res=run_gmin(n,E)
    if res:
        bad=sum(1 for x in res if not x[0])
        print(f"run_gmin: gamma-min cuts tested={len(res)} BOTH-PSD-FAILS={bad}")
    else:
        print("run_gmin: None (chosen cut may not be the gamma-min connected maxcut via this entry)")
