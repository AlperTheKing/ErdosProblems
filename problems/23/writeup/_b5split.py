"""Gate Codex 447 B5 traffic split on pure length-5 whole-component positive-overload rows.
   tau(e) = sum_g (1/|cyc[g]|) #{Q in cyc[g]: e is a consecutive blue edge of Q}.
   I(P)=sum_g (1/|cyc[g]|) sum_Q |V(P) cap V(Q)|;  Def=N^2-25|M|;  D2=(2/75)Def.
   E(P)=sum_{i=0..3} tau({x_i,x_{i+1}}) - 4.
   R(P)=2(N-4) - tau(delta_B(P)) - sum_{v in P} d_M(v),  tau(delta_B(P))=sum over blue edges e with |e cap V(P)|=1 of tau(e).
   (1) I(P)-N == E(P)-R(P)/2 ;  (2) R(P)>=0 ;  (3) E(P) <= (4/75)Def = 2 D2.   Exact.
"""
import subprocess, random
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski

def Kcomp(n,M,cyc,Pset):
    adjK=[set() for _ in range(n)]
    for g in M:
        for Q in cyc[g]:
            for a in Q:
                for b in Q:
                    if a!=b: adjK[a].add(b)
    seen=set(Pset); dq=deque(Pset)
    while dq:
        u=dq.popleft()
        for w in adjK[u]:
            if w not in seen: seen.add(w); dq.append(w)
    return seen

def tau_edge(e,M,cyc):
    """e=frozenset of 2 vertices; tau(e)=sum_g (1/|cyc[g]|) #{Q: e consecutive in Q}."""
    tot=F(0)
    for g in M:
        Q_list=cyc[g]; k=len(Q_list); c=0
        for Q in Q_list:
            for i in range(len(Q)-1):
                if frozenset((Q[i],Q[i+1]))==e: c+=1
        tot+=F(c,k)
    return tot

def scan(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    dM=[0]*n
    for g in M:
        a,b=g; dM[a]+=1; dM[b]+=1
    for f in M:
        L=ell[f]
        if L!=5: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            Over=sum(T[P[i]] for i in range(L))-L*N
            if Over<=0: continue
            C=Kcomp(n,M,cyc,set(P))
            if len(C)!=n: continue
            if set(ell[g] for g in M if any(set(Q)<=C for Q in cyc[g]))!={5}: continue
            Pset=set(P)
            I=sum(F(1,len(cyc[g]))*sum(len(Pset & set(Q)) for Q in cyc[g]) for g in M)
            Def=N*N-25*len(M); D2=F(2,75)*Def
            # E(P): row blue-edge traffic (consecutive path edges) minus 4
            E=sum(tau_edge(frozenset((P[i],P[(i+1)%L])),M,cyc) for i in range(4)) - 4   # i=0..3 (4 path edges)
            # tau(delta_B(P)): blue (cut) edges with exactly one endpoint in P
            tauB=F(0)
            for u in range(n):
                for v in adj[u]:
                    if v<=u: continue
                    if side[u]!=side[v]:   # blue (cut) edge
                        if (u in Pset) ^ (v in Pset):
                            tauB+=tau_edge(frozenset((u,v)),M,cyc)
            R=2*(N-4) - tauB - sum(dM[v] for v in P)
            acc['rows']+=1
            if I-N != E - R/2:
                acc['id_fail']+=1
                if acc['id_ex'] is None: acc['id_ex']=(name,n,tuple(P),str(I-N),str(E-R/2))
            if R<0:
                acc['R_fail']+=1
                if acc['R_ex'] is None: acc['R_ex']=(name,n,tuple(P),str(R))
            if E > F(4,75)*Def:
                acc['E_fail']+=1
                if acc['E_ex'] is None: acc['E_ex']=(name,n,tuple(P),str(E),str(F(4,75)*Def))

def gfam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception: return
    for side in cuts: scan(name,n,adj,side,acc)

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
    acc=dict(rows=0,id_fail=0,R_fail=0,E_fail=0,id_ex=None,R_ex=None,E_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
    grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): scan("Myc23",n,adj,side,acc)
    print("pure-C5 whole-component Over>0 rows:",acc['rows'])
    print("  (1) identity I-N == E-R/2  fail=%d %s"%(acc['id_fail'],acc['id_ex'] or ''))
    print("  (2) port capacity R>=0     fail=%d %s"%(acc['R_fail'],acc['R_ex'] or ''))
    print("  (3) row-edge defect E<=(4/75)Def  fail=%d %s"%(acc['E_fail'],acc['E_ex'] or ''))
    print("VERDICT:", "B5 TRAFFIC SPLIT (1)(2)(3) HOLD" if acc['id_fail']==acc['R_fail']==acc['E_fail']==0 else "FAIL")

if __name__=="__main__":
    main()
