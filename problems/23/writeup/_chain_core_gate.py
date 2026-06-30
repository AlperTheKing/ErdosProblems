"""Due-diligence after the VAR-STABILITY battery gap: verify the CORE results (atom Tail_0>=0, (A), (B),
   levelwise R1_r>=0) hold on the glued C5 CHAINS q=2..18 (supplied cut) -- the family that broke global
   VAR-STABILITY. If the core also fails here, the reduction itself is battery-gapped; if it holds, only the
   global-variance auxiliary was wrong.  Exact Fraction.
"""
from fractions import Fraction as F
from _Klocal_gate import glued_c5_chain
from _singleton_core import ell_map, Hi_and_best
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import flip
from _h import Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def main():
    atom_fail=0; A_fail=0; B_fail=0; R1_fail=0; rows=0; noport_rows=0; ex=[]
    for q in range(2,19):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if not Bconn(n,adj,side): continue
        Lam=len(E)*n*n+1
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        N=F(n); Gamma=sum(ell[g]**2 for g in M); em0=ell_map(n,adj,side)
        pg={}
        for g in M:
            Q=cyc[g];cnt={}
            for path in Q:
                for v in path: cnt[v]=cnt.get(v,0)+1
            kk=len(Q); pg[g]={v:F(cnt[v],kk) for v in cnt}
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                noport=True
                for i in range(L):
                    Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is not None and Hi<0: noport=False; break
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                Tail0=sum((2*r+1)*Z[r] for r in range(n))
                rows+=1
                if noport: noport_rows+=1
                if Tail0<0: atom_fail+=1; ex.append(('atom',q,tuple(P),str(Tail0)))
                # (A),(B)
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); qq=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-qq; C_L=deltaP*L*L
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                D_all=N*N-Gamma; D_path=N*(L-S)
                if E0+C_L > F(L,5)*D_all: A_fail+=1; ex.append(('A',q,tuple(P),str(E0+C_L),str(F(L,5)*D_all)))
                if 25*max(0,-D_path) > F(4*L,5)*D_all: B_fail+=1; ex.append(('B',q,tuple(P)))
                # R1_k all k
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(L)) for g in M}
                for k in range(n):
                    Gamma_k=sum(max(0,ell[g]**2-k*k) for g in M)
                    D_k=N*N-k*k-Gamma_k
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    Tax=Ek+deltaP*max(0,L*L-k*k)
                    if F(L,5)*D_k-Tax<0: R1_fail+=1; ex.append(('R1',q,tuple(P),k)); break
        print("chain q=%d (N=%d): rows so far=%d atom_fail=%d A=%d B=%d R1=%d"%(q,n,rows,atom_fail,A_fail,B_fail,R1_fail),flush=True)
    print("="*55)
    print("glued-chain rows:",rows," (no-port:",noport_rows,")")
    print("atom Tail_0>=0 fails:",atom_fail)
    print("(A) fails:",A_fail)
    print("(B) fails:",B_fail)
    print("levelwise R1_k>=0 fails:",R1_fail)
    print("examples:",ex[:5])
    print("VERDICT:", "CORE (atom/(A)/(B)/R1) ROBUST on glued chains (only global VAR-STAB was gapped)" if atom_fail==0 and A_fail==0 and B_fail==0 and R1_fail==0 else "CORE BATTERY-GAP: a core result FAILS on chains")

if __name__=="__main__":
    main()
