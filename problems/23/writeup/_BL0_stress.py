"""STRESS TEST the STANDALONE per-row inequality (BL0) on HARD large witnesses:
   (BL0)  B_L(P) := L*(N^2-Gamma) + 25*(L*N - sum_i T[x_i]) - (S^2 - L^2 q)  >= 0
   over odd-L shortest blue geodesics of a (single) good max cut.

Witnesses: Grotzsch=Myc(C5) N=11, Myc(Grotzsch) N=23, Myc(C7) N=15, Myc(Myc(C7)) N=31,
           C5/C7/C9 balanced + lopsided blow-ups up to N~45.
For each graph we pick ONE max cut (greedy improve from a structural 2-coloring; verify it is
locally optimal i.e. a true gamma-min would need full search, but a single good cut already
exercises the inequality - we ONLY need NO violation). ALL exact Fraction.
"""
import sys
from fractions import Fraction as F
from _h import Bconn, geos
from _bdef_construct import Cn, mycielski, is_triangle_free

def odd_blowup(m, sizes):
    nn=sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]): E.append((start[i]+a,start[j]+b))
    return nn,E

def adjof(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def cutsize(n,adj,side):
    c=0
    for u in range(n):
        for v in adj[u]:
            if v>u and side[u]!=side[v]: c+=1
    return c

def greedy_maxcut(n,adj,seed_side=None):
    import random
    best=None
    for trial in range(40):
        if seed_side is not None and trial==0:
            side=list(seed_side)
        else:
            random.seed(trial); side=[random.randint(0,1) for _ in range(n)]
        improved=True
        while improved:
            improved=False
            for v in range(n):
                same=sum(1 for w in adj[v] if side[w]==side[v])
                diff=sum(1 for w in adj[v] if side[w]!=side[v])
                if same>diff:
                    side[v]^=1; improved=True
        cs=cutsize(n,adj,side)
        if best is None or cs>best[0]: best=(cs,side)
    return best[1]

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    if not Bconn(n,adj,side): return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    return M,ell,T,cyc

def test_graph(name,n,E):
    if not is_triangle_free(n,E):
        return (name,n,"NOT-TRIFREE",None)
    adj=adjof(n,E)
    # seed: 2-color via BFS parity (works for blow-ups), else random
    side=greedy_maxcut(n,adj)
    st=struct(n,adj,side)
    if st is None: return (name,n,"no-struct/B-disconn",None)
    M,ell,T,cyc=st
    N=F(n); Gamma=sum(T)
    minB=None; nrows=0
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            nrows+=1
            Ti=[T[P[i]] for i in range(L)]
            h=[Ti[i]/N for i in range(L)]; S=sum(h)
            q=min(h[i]*h[(i+1)%L] for i in range(L))
            B_L=L*(N*N-Gamma)+25*(L*N-sum(Ti))-(S*S-(L*L)*q)
            if minB is None or B_L<minB[0]: minB=(B_L,L,Gamma)
    return (name,n,"rows=%d Gamma=%s N^2=%d"%(nrows,Gamma,n*n), minB)

def main():
    wit=[]
    g=mycielski(5,Cn(5)); wit.append(("Grotzsch(MycC5)",)+g)
    gg=mycielski(*g); wit.append(("Myc(Grotzsch)N23",)+gg)
    c7=(7,Cn(7)); m7=mycielski(*c7); wit.append(("MycC7 N15",)+m7)
    for sizes in [(1,1,1,1,1),(3,3,3,3,3),(4,4,4,4,4),(5,5,5,5,5),(8,8,8,8,8),
                  (4,3,4,3,4),(6,2,6,2,6),(2,1,2,1,1)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=45: wit.append(("C5%s"%(sizes,),n,E))
    for sizes in [(1,)*7,(3,)*7,(5,)*7,(3,2,3,2,3,2,3)]:
        n,E=odd_blowup(7,list(sizes))
        if n<=49: wit.append(("C7%s"%(sizes,),n,E))
    for sizes in [(1,)*9,(3,)*9,(4,)*9]:
        n,E=odd_blowup(9,list(sizes))
        if n<=45: wit.append(("C9%s"%(sizes,),n,E))

    anyviol=False
    for w in wit:
        name=w[0]; n=w[1]; E=w[2]
        try:
            res=test_graph(name,n,E)
        except Exception as ex:
            print("%-22s N=%d ERROR %s"%(name,n,ex)); continue
        nm,nn,info,minB=res
        if minB is None:
            print("%-22s N=%d  %s"%(nm,nn,info)); continue
        B,L,G=minB
        flag="" if B>=0 else "  <<< VIOLATION"
        if B<0: anyviol=True
        print("%-22s N=%d  %s | min B_L=%s (L=%d)%s"%(nm,nn,info,str(B),L,flag))
    print("="*60)
    print("ANY VIOLATION:", anyviol)

if __name__=="__main__":
    main()
