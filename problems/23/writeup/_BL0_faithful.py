"""FAITHFULNESS check: the standalone atom B_L>=0 must FAIL on graphs WITH triangles
   (odd-girth-3, where Gamma can exceed N^2), proving B_L>=0 is NOT a free algebraic fact
   and genuinely encodes odd-girth>=5 / Gamma<=N^2.  Also confirm: does per-row B_L>=0 for
   ALL bad edges imply Gamma<=N^2 (non-circularity)?  We test the SUMMED implication:
     sum over one chosen geodesic per bad edge of  B_L/L = (N^2-Gamma) + 25(N - (1/L)sum T_i) - (S^2-L^2q)/L
   and more directly we just check whether B_L<0 occurs once triangles are allowed.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos

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

def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<n):
        side=[(mask>>i)&1 for i in range(n)]
        c=cutsize(n,adj,side)
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return cuts

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

def rows_minB(n,E):
    adj=adjof(n,E)
    minB=None; gammas=[]
    for side in all_maxcuts(n,adj):
        st=struct(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st; N=F(n); Gamma=sum(T); gammas.append(Gamma)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                Ti=[T[P[i]] for i in range(L)]
                h=[Ti[i]/N for i in range(L)]; S=sum(h)
                q=min(h[i]*h[(i+1)%L] for i in range(L))
                B=L*(N*N-Gamma)+25*(L*N-sum(Ti))-(S*S-(L*L)*q)
                if minB is None or B<minB: minB=B
    return minB, gammas

def main():
    # graphs WITH triangles, small N, connected. Use geng WITHOUT -t.
    print("=== TRIANGLE-CONTAINING graphs (expect B_L<0 somewhere) ===")
    sawneg=False; sawgammahi=False
    for nn in range(5,9):
        outg=subprocess.run([GENG,"-c",str(nn)],capture_output=True,text=True).stdout.split()
        cntneg=0; cnt=0
        for g6 in outg:
            n,E=dec(g6)
            adj=adjof(n,E)
            # only graphs that actually contain a triangle
            tri=any((adj[a]&adj[b]) for (a,b) in E)
            if not tri: continue
            cnt+=1
            mb,gms=rows_minB(n,E)
            if mb is not None and mb<0: cntneg+=1; sawneg=True
            if gms and max(gms)>n*n: sawgammahi=True
        print("N=%d: %d triangle graphs, %d with some B_L<0"%(nn,cnt,cntneg))
    print("saw B_L<0 on triangle graphs:", sawneg)
    print("saw Gamma>N^2 on triangle graphs:", sawgammahi)

if __name__=="__main__":
    main()
