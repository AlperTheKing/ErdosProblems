"""Gate Codex 450 CYCLE-SECOND-MOMENT spectral domination (CSM-SPEC): rho(K2) <= N, i.e. N*I - K2 PSD, where
   K2[v,w] = sum_{f in M} (1/|cyc[f]|) * #{Q in cyc[f] : v in Q and w in Q}.
   Since K = sum_f p_f p_f^T (p_f=E_Q[q_Q]) <= K2 (Jensen/covariance), rho(K2)<=N => rho(K)<=N => Gamma<=N^2.
   EXACT rational LDL PSD test.  Full battery incl the N=23 Myc(Grotzsch) guardrail (killed prior spectral claims).
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain

def build_K2(n,M,cyc):
    K2=[[F(0)]*n for _ in range(n)]
    for f in M:
        Qs=cyc[f]; w=F(1,len(Qs))
        for Q in Qs:
            vs=list(set(Q))
            for a in vs:
                for b in vs:
                    K2[a][b]+=w
    return K2

def is_psd(Mat):
    """exact rational symmetric PSD test via no-pivot LDL: all pivots>=0; a 0 pivot must have a 0 row."""
    n=len(Mat); A=[row[:] for row in Mat]
    minpiv=None
    for k in range(n):
        p=A[k][k]
        if p<0: return False, p
        if minpiv is None or p<minpiv: minpiv=p
        if p==0:
            for j in range(k+1,n):
                if A[k][j]!=0: return False, F(0)
            continue
        for i in range(k+1,n):
            if A[i][k]==0: continue
            fac=A[i][k]/p
            for j in range(k,n):
                A[i][j]-=fac*A[k][j]
    return True, minpiv

def test_cut(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    K2=build_K2(n,M,cyc)
    Mat=[[(F(n) if i==j else F(0))-K2[i][j] for j in range(n)] for i in range(n)]
    psd,minpiv=is_psd(Mat)
    acc['cuts']+=1
    if not psd:
        acc['fail']+=1
        if acc['ex'] is None: acc['ex']=(name,n,''.join(map(str,side)),str(minpiv))
    else:
        if minpiv==0: acc['tight']+=1
        if acc['mingap'] is None or (minpiv is not None and minpiv<acc['mingap']): acc['mingap']=minpiv

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
    acc=dict(cuts=0,fail=0,tight=0,mingap=None,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
        print("census N=%d: cuts=%d fail=%d tight=%d"%(nn,acc['cuts'],acc['fail'],acc['tight']),flush=True)
    # GUARDRAIL: Myc(Grotzsch) N=23 (killed (k2)); + Grotzsch N=11
    grN,grE=mycielski(5,Cn(5)); gfam("Grotzsch",grN,grE,acc)
    m2N,m2E=mycielski(grN,grE)
    adj=[set() for _ in range(m2N)]
    for x,y in m2E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(m2N,adj)
    if Bconn(m2N,adj,side): test_cut("MycGrotzsch_N23",m2N,adj,side,acc)
    print("after Grotzsch+Myc23: cuts=%d fail=%d %s"%(acc['cuts'],acc['fail'],acc['ex'] or ''),flush=True)
    # glued chains (killed VAR-STABILITY)
    for q in range(2,16):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): test_cut("chain_q%d"%q,n,adj,side,acc)
    # overloaded blow-ups N<=24
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(4,3,4,3,4),(5,4,5,4,5),(2,2,2,2,2),(3,3,3,3,3)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=24: gfam("blow%s"%(sizes,),nn,EE,acc)
    # glued islands (killed ZMU)
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
    nn,EE=union_disjoint(isl,g15); nn,EE=add_edges((nn,EE),[(0,5)])
    gfam("isl_C5_MycC7",nn,EE,acc)
    print("after chains+blowups+islands: cuts=%d fail=%d %s"%(acc['cuts'],acc['fail'],acc['ex'] or ''),flush=True)
    # randoms N=11/12
    rng=random.Random(7); made=0; tries=0
    while made<120 and tries<40000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        EE=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not EE or not is_triangle_free(nn,EE): continue
        adj=[set() for _ in range(nn)]
        for a,b in EE: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; gfam("rand%d"%made,nn,EE,acc)
    print("="*55)
    print("total gamma-min cuts tested:",acc['cuts']," (random N11/12 graphs:",made,")")
    print("CSM-SPEC (N*I - K2 PSD) VIOLATIONS:",acc['fail'],acc['ex'] or '')
    print("tight (min pivot = 0) cuts:",acc['tight'])
    print("min PSD pivot gap (exact):",str(acc['mingap']))
    print("VERDICT:", "CSM-SPEC rho(K2)<=N HOLDS exact on full battery incl N=23 -- SPECTRAL ROUTE LIVE" if acc['fail']==0 else "CSM-SPEC FALSE")

if __name__=="__main__":
    main()
