"""Full-battery test of the user's GPM (geodesic-measure majorization) route for (A).  Reuses _gpm_lp.test_row.
   GPM averaged + optional PATHWISE (PGPM).  census N<=10 gamma-min + Grotzsch + Myc(Grotzsch) N=23 + glued chains
   + overloaded blow-ups + glued-island + random N=11/12.  Usage: python _gpm_battery.py [--pathwise]
"""
import sys, subprocess, random
from _gpm_lp import run_graph
from _h import dec, GENG, Bconn
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _wf_deficit_farkas import odd_blowup
from _Klocal_gate import glued_c5_chain

def maxcut_ls(n,adj,seeds=80):
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
    pw='--pathwise' in sys.argv
    print("MODE:", "PATHWISE (PGPM)" if pw else "averaged (GPM)")
    acc=dict(rows=0,feas=0,infeas=0,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); run_graph("cen%d"%nn,n,E,acc,pathwise=pw)
        print("census N=%d: rows=%d feas=%d infeas=%d %s"%(nn,acc['rows'],acc['feas'],acc['infeas'],acc['ex'] or ''),flush=True)
    grN,grE=mycielski(5,Cn(5)); run_graph("Grotzsch",grN,grE,acc,pathwise=pw)
    m2N,m2E=mycielski(grN,grE)
    adj=[set() for _ in range(m2N)]
    for x,y in m2E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(m2N,adj)
    if Bconn(m2N,adj,side): run_graph("MycGrotzsch_N23",m2N,m2E,acc,cuts=[side],pathwise=pw)
    print("after Grotzsch+Myc23: rows=%d feas=%d infeas=%d %s"%(acc['rows'],acc['feas'],acc['infeas'],acc['ex'] or ''),flush=True)
    for q in range(2,14):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): run_graph("chain_q%d"%q,n,E,acc,cuts=[side],pathwise=pw)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=20: run_graph("blow%s"%(sizes,),nn,EE,acc,pathwise=pw)
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    nn,EE=union_disjoint(isl,g15); nn,EE=add_edges((nn,EE),[(0,5)])
    run_graph("isl",nn,EE,acc,pathwise=pw)
    print("after chains+blowups+islands: rows=%d feas=%d infeas=%d %s"%(acc['rows'],acc['feas'],acc['infeas'],acc['ex'] or ''),flush=True)
    rng=random.Random(7); made=0; tries=0
    while made<150 and tries<40000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        EE=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not EE or not is_triangle_free(nn,EE): continue
        adj=[set() for _ in range(nn)]
        for a,b in EE: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; run_graph("rand%d"%made,nn,EE,acc,pathwise=pw)
    print("="*55)
    print("rows=%d FEASIBLE=%d INFEASIBLE=%d  (random N11/12: %d)"%(acc['rows'],acc['feas'],acc['infeas'],made))
    print("VERDICT:", "GPM%s FEASIBLE on FULL battery incl N=23 -- convex route proves (A)" % (" PATHWISE" if pw else "") if acc['infeas']==0 and acc['feas']>0 else "INFEASIBLE: %s"%(acc['ex'],))

if __name__=="__main__":
    main()
