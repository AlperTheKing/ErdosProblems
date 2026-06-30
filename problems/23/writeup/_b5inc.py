"""Verify Codex 444 B5 incidence reformulation on pure length-5 whole-component rows (Over>0):
   I(P)=sum_g (1/|cyc[g]|) sum_{Q in cyc[g]} |V(P) cap V(Q)|.
   Claims: sum_{v in P} T[v] = 5*I(P);  Gamma=25|M|; Def_C=N^2-25|M|;
   B5 (15*Over<=2*Def_C)  <=>  75*(I(P)-N) <= 2*(N^2-25|M|).  Exact.  census N<=10 (incl Petersen) + N=23.
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

def scan(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            Over=sum(T[P[i]] for i in range(L))-L*N
            if Over<=0: continue
            C=Kcomp(n,M,cyc,set(P))
            # pure length-5 whole-component check (precondition)
            if len(C)!=n or L!=5: acc['precond_fail']+=1; continue
            Pset=set(P)
            I=sum(F(1,len(cyc[g]))*sum(len(Pset & set(Q)) for Q in cyc[g]) for g in M)
            acc['rows']+=1
            sumTP=sum(T[P[i]] for i in range(L))
            if sumTP != 5*I:
                acc['id_fail']+=1
                if acc['id_ex'] is None: acc['id_ex']=(name,n,tuple(P),str(sumTP),str(5*I))
            # equivalence B5 <=> 75(I-N) <= 2(N^2-25|M|)
            Def=N*N-25*len(M)
            lhs_b5=15*Over; rhs_b5=2*Def
            lhs_inc=75*(I-N); rhs_inc=2*(N*N-25*len(M))
            if (lhs_b5<=rhs_b5) != (lhs_inc<=rhs_inc):
                acc['equiv_fail']+=1
            if lhs_inc>rhs_inc:
                acc['inc_fail']+=1
                if acc['inc_ex'] is None: acc['inc_ex']=(name,n,tuple(P),str(lhs_inc),str(rhs_inc))

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
    acc=dict(rows=0,precond_fail=0,id_fail=0,equiv_fail=0,inc_fail=0,id_ex=None,inc_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
    grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): scan("Myc23",n,adj,side,acc)
    print("pure-C5 whole-component Over>0 rows:",acc['rows'])
    print("  identity sum_P T == 5*I(P)  fail=%d %s"%(acc['id_fail'],acc['id_ex'] or ''))
    print("  B5 <=> incidence equivalence fail=%d"%acc['equiv_fail'])
    print("  incidence 75(I-N)<=2(N^2-25|M|) fail=%d %s"%(acc['inc_fail'],acc['inc_ex'] or ''))
    print("VERDICT:", "B5 INCIDENCE FORM EXACT" if acc['id_fail']==acc['equiv_fail']==acc['inc_fail']==0 else "MISMATCH")

if __name__=="__main__":
    main()
