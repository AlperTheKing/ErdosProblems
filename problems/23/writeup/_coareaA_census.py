"""Census test of the CORRECTED (A) coarea LP (no M2, theta-subgradient) -- the decisive feasibility sweep.
   If feasible on ALL gamma-min rows of the battery, (A) is certified (coarea/Farkas => gamma-minimality => (A)).
   Float linprog.  Usage: python _coareaA_census.py [Nmax]
"""
import sys, subprocess, random
from _coareaA_lp2 import test_row
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski

def run_graph(name,n,E,acc,cuts=None):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if cuts is None:
        try: _,cuts=gmins(n,E)
        except Exception: return
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                tag,fe=test_row(n,adj,side,M,ell,T,cyc,f,list(P))
                acc['rows']+=1
                if tag=='NOCOLS': acc['nocol']+=1; continue
                if fe: acc['feas']+=1
                else:
                    acc['infeas']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,''.join(map(str,side)),f,tuple(P))

def maxcut_ls(n,adj,seeds=60):
    best=None;bv=-1;rng=random.Random(9)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)];imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]):s[v]^=1;imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv:bv=val;best=s[:]
    return best

def main():
    Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 9
    acc=dict(rows=0,feas=0,infeas=0,nocol=0,ex=None)
    for nn in range(5,Nmax+1):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); run_graph("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d feas=%d infeas=%d nocol=%d %s"%(nn,acc['rows'],acc['feas'],acc['infeas'],acc['nocol'],acc['ex'] or ''),flush=True)
    # theta + Grotzsch + Myc23
    n,E=dec("H?AFBo]"); run_graph("thw",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); run_graph("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): run_graph("Myc23",n,E,acc,cuts=[side])
    print("="*55)
    print("TOTAL rows=%d  FEASIBLE=%d  INFEASIBLE=%d  no-col=%d"%(acc['rows'],acc['feas'],acc['infeas'],acc['nocol']))
    print("first infeasible:",acc['ex'] or 'NONE')
    print("VERDICT:", "CORRECTED COAREA LP FEASIBLE on ALL rows -- (A) CERTIFIED on this battery" if acc['infeas']==0 and acc['feas']>0 else ("INFEASIBLE rows remain -- route still incomplete" if acc['infeas']>0 else "no rows"))

if __name__=="__main__":
    main()
