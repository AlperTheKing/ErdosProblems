"""Find the provable closing bound.  B_L = L*Dout + (L+25)*Din - disp,  disp=S^2-L^2 q,
S=sum h_i, h_i=T_i/N, q=min_cyclic h_i h_{i+1},  Din=sum(N-T_i)=N*(L - S),  Dout>=0.

Key algebra:  disp = S^2 - L^2 q.  Since q = min h_i h_{i+1} <= (1/L^2)(sum sqrt..)?  We test
the elementary bound coupling disp to S and to the spread.  Candidate CLOSERS (each exact-tested):

 (X1)  disp <= S^2 - (S/L)^2 ... no.  Test disp <= (L-1)/L * S^2 ? (since q>=0 => disp<=S^2; sharper?)
 (X2)  disp <= S*(L*max_i h_i - S)?
 (X3)  THE MAIN ONE: since Din = N(L-S), test whether
         L*Dout + (L+25)*Din >= disp
       is implied by the SIMPLER  (L+25)*Din >= disp - L*Dout, and whether disp <= (L+25)*(N*L - sum T_i)+L*Dout
       i.e. just re-confirm B_L>=0 but report, per row, the RATIO disp/(L*Dout+(L+25)*Din) when denom>0,
       and the worst (closest to 1) rows to see the true tightness structure.
 (X4)  Test disp <= 25*Din + L*Dout  (drop the L*Din, i.e. coefficient 25 not L+25 on Din) -- does the
       weaker-credit form hold? If yes, cleaner statement B_L' = L*Dout+25*Din - disp... but wait that's
       L*Dout+25*Din-disp = B_L - L*Din; since Din can be<0 this could fail. Test it.
 (X5)  scale-free: disp/N^2 <= (something).  disp = S^2 - L^2 q, all O(1).  Din/N = L-S, Dout/N>=0.
       Test  disp <= (L+25)*(L-S)*N + L*Dout, i.e. as N->inf with S,L fixed the RHS ~ N -> disp bounded.
       At tight blow-up S=L (all h_i=1), disp=L^2-L^2*1=0, Din=0, Dout=0: 0>=0 tight.
ALL exact. Report worst ratio + whether X1/X4 hold.
"""
import sys, subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos
from _bdef_construct import Cn, mycielski

def adjof(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<n):
        side=[(mask>>i)&1 for i in range(n)]; c=cutsize(n,adj,side)
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return cuts
def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M or not Bconn(n,adj,side): return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    return M,ell,T,cyc

def main():
    failX1=0; failX4=0; worstratio=None; worstrow=None
    rows=0
    minB=None
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj=adjof(n,E)
            for side in all_maxcuts(n,adj):
                st=struct(n,adj,side)
                if st is None: continue
                M,ell,T,cyc=st; N=F(n); Gamma=sum(T); Tall=N*N-Gamma
                for f in M:
                    L=ell[f]
                    if L%2==0: continue
                    for P in cyc[f]:
                        if len(P)!=L: continue
                        rows+=1
                        Ti=[T[i] for i in P]
                        Din=sum(N-t for t in Ti); Dout=Tall-Din
                        h=[t/N for t in Ti]; S=sum(h)
                        q=min(h[i]*h[(i+1)%L] for i in range(L))
                        disp=S*S-(L*L)*q
                        B=L*Dout+(L+25)*Din-disp
                        if minB is None or B<minB: minB=B
                        # X1: disp <= (L-1)/L * S^2
                        if disp > F(L-1,L)*S*S: failX1+=1
                        # X4: disp <= 25*Din + L*Dout
                        if disp > 25*Din + L*Dout: failX4+=1
                        denom=L*Dout+(L+25)*Din
                        if denom>0:
                            ratio=disp/denom
                            if worstratio is None or ratio>worstratio:
                                worstratio=ratio; worstrow=(nn,L,str(disp),str(Din),str(Dout),str(S),str(q))
    print("rows:",rows," min B_L:",str(minB))
    print("X1 disp<=(L-1)/L*S^2  fails:",failX1)
    print("X4 disp<=25*Din+L*Dout fails:",failX4,"  (if 0: cleaner form B_L>=L*Din i.e. 25Din+L Dout>=disp)")
    print("worst ratio disp/((L+25)Din+L Dout):",str(worstratio)," at (N,L,disp,Din,Dout,S,q)=",worstrow)

if __name__=="__main__":
    main()
