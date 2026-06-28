"""Decisive gamma-minimality test for A-alltie.
Take graphs KNOWN to have saturated vertices (from census: graphs where loads() gives T(u)=N).
For each, enumerate ALL connected max cuts, compute Gamma for each, and test A-alltie per cut.
Report: does any NON-gamma-min connected max cut have a sat-zero-mu A-alltie VIOLATION?
If yes -> gamma-minimality ESSENTIAL. If A-alltie holds on ALL connected max cuts -> it's cut-robust.
Exact Fraction. Source graphs: scan census N=10,11 for saturated loads-cut graphs."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def Acheck_side(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    c=0; v=0
    for e,val in mu.items():
        if val!=0: continue
        a0,b0=e
        for (a,b) in ((a0,b0),(b0,a0)):
            if T[a]==N:
                c+=1
                if T[b]!=0: v+=1
    return c,v

def all_conn_maxcuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); out=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: out.append((side,G))
    return adj,out

if __name__=="__main__":
    print("=== gamma-minimality essential? A-alltie on gamma-min vs ALL connected max cuts (saturated graphs) ===")
    g_gmin_c=0; g_gmin_v=0; g_non_c=0; g_non_v=0; nonwit=None; nsat_graphs=0
    for nn in [10,11]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            if not any(t==info['n'] for t in info['T']): continue  # only saturated graphs
            nsat_graphs+=1
            adj,cand=all_conn_maxcuts(n,E)
            if not cand: continue
            gm=min(G for _,G in cand)
            for side,G in cand:
                r=Acheck_side(n,adj,side)
                if r is None: continue
                c,v=r
                if G==gm: g_gmin_c+=c; g_gmin_v+=v
                else:
                    g_non_c+=c; g_non_v+=v
                    if v>0 and nonwit is None: nonwit=(g6,float(G),float(gm))
        print(f"  after N={nn}: sat-graphs={nsat_graphs} | GMIN cases={g_gmin_c} viol={g_gmin_v} | NONMIN cases={g_non_c} viol={g_non_v}"+(f" NONMIN-WIT {nonwit}" if nonwit else ""), flush=True)
    print(f"\nCONCLUSION: NONMIN A-alltie cases={g_non_c} violations={g_non_v}")
    print("  if NONMIN cases>0 and viol=0 => A-alltie is CUT-ROBUST (holds on non-min cuts too) => NOT dependent on gamma-min")
    print("  if NONMIN viol>0 => gamma-minimality ESSENTIAL")
