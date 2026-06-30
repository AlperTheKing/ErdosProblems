"""Gate Codex 455 COLLATZ-WIELANDT SUPERVECTOR form of CSM-SPEC:  K2 * T <= N * T  vertexwise.
   K2[v,w]=sum_f #{Q in cyc[f]: v,w in Q}/|cyc[f]|.  K2*1 = T (each Q has |Q|=ell_f).  T>=0.
   K2 T <= N T (vertexwise), T>=0  =>  rho(K2)<=N (Collatz-Wielandt)  =>  rho(K)<=N (K<=K2 Jensen)
   => Gamma=1^T K 1 <= rho(K) N <= N^2 => beta<=N^2/25.
   ALSO verify the overload-cancellation identity:  (K2 T)[v]-N T[v] == sum_f (1/|cyc[f]|) sum_{Q in cyc[f], v in Q} Over(Q),
   Over(Q)=sum_{u in Q} T[u] - N*ell_f.  Exact Fraction.  Full battery incl N=23 guardrail.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _csmspec import build_K2

def test_cut(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    K2=build_K2(n,M,cyc)
    acc['cuts']+=1
    # K2 * T
    for v in range(n):
        k2t=sum(K2[v][w]*T[w] for w in range(n))
        # overload-cancellation identity RHS
        rhs=F(0)
        for f in M:
            wgt=F(1,len(cyc[f]))
            for Q in cyc[f]:
                if v in Q:
                    Over=sum(T[u] for u in Q)-N*ell[f]
                    rhs+=wgt*Over
        if k2t-N*T[v] != rhs:
            acc['id_fail']+=1
            if acc['id_ex'] is None: acc['id_ex']=(name,n,v,str(k2t-N*T[v]),str(rhs))
        marg=N*T[v]-k2t
        if marg<0:
            acc['fail']+=1
            if acc['ex'] is None: acc['ex']=(name,n,''.join(map(str,side)),v,str(marg))
        else:
            if marg==0: acc['tightv']+=1
            if acc['minmarg'] is None or marg<acc['minmarg']: acc['minmarg']=marg

def gfam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception: return
    for side in cuts: test_cut(name,n,adj,side,acc)

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
    acc=dict(cuts=0,fail=0,id_fail=0,tightv=0,minmarg=None,ex=None,id_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
        print("census N=%d: cuts=%d fail=%d id_fail=%d"%(nn,acc['cuts'],acc['fail'],acc['id_fail']),flush=True)
    grN,grE=mycielski(5,Cn(5)); gfam("Grotzsch",grN,grE,acc)
    m2N,m2E=mycielski(grN,grE)
    adj=[set() for _ in range(m2N)]
    for x,y in m2E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(m2N,adj)
    if Bconn(m2N,adj,side): test_cut("MycGrotzsch_N23",m2N,adj,side,acc)
    print("after Grotzsch+Myc23: cuts=%d fail=%d %s"%(acc['cuts'],acc['fail'],acc['ex'] or ''),flush=True)
    for q in range(2,16):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): test_cut("chain_q%d"%q,n,adj,side,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=27: gfam("blow%s"%(sizes,),nn,EE,acc)
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    nn,EE=union_disjoint(isl,g15); nn,EE=add_edges((nn,EE),[(0,5)])
    gfam("isl",nn,EE,acc)
    print("after chains+blowups+islands: cuts=%d fail=%d %s"%(acc['cuts'],acc['fail'],acc['ex'] or ''),flush=True)
    rng=random.Random(7); made=0; tries=0
    while made<200 and tries<60000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        EE=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not EE or not is_triangle_free(nn,EE): continue
        adj=[set() for _ in range(nn)]
        for a,b in EE: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; gfam("rand%d"%made,nn,EE,acc)
    print("="*55)
    print("gamma-min cuts tested:",acc['cuts']," (random N11/12 graphs:",made,")")
    print("overload-cancellation IDENTITY failures:",acc['id_fail'],acc['id_ex'] or '')
    print("K2*T <= N*T (Collatz-Wielandt) VIOLATIONS:",acc['fail'],acc['ex'] or '')
    print("tight vertices (margin 0):",acc['tightv'],"  min margin (exact):",str(acc['minmarg']))
    print("VERDICT:", "K2T<=NT HOLDS exact on full battery incl N=23 => rho(K2)<=N => Gamma<=N^2 (CW route LIVE)" if acc['fail']==0 and acc['id_fail']==0 else "FAILS")

if __name__=="__main__":
    main()
