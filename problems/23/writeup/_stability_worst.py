"""Dump worst-row equality geometry for the gamma-min R1/R2 stability gates (Codex 397).
   R1_k=(L/5)D_k-Tax_k>=0  -> worst = max Tax_k/((L/5)D_k);  R2_k overload -> max 25max(0,-B_k)/((4L/5)D_k).
   Report full data for the worst R1, worst R2, and worst at k=0, incl ell_g, a_g(P), E_k, delta_P.
"""
import subprocess
from fractions import Fraction as F
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _trunc_verify import chi_profile as endpt_chi
from _interval_drain_gate import interval_of
from _wf_deficit_farkas import flip, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def upd(acc,key,ratio,data):
    if acc[key] is None or ratio>acc[key][0]: acc[key]=(ratio,data)

def run(name,n,adj,E,acc):
    adj2,cuts=gmins(n,E); Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj2,side): continue
        st=struct_for_side(n,adj2,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); em0=ell_map(n,adj2,side)
        pg={}
        for g in M:
            Q=cyc[g]; cnt={}
            for path in Q:
                for v in path: cnt[v]=cnt.get(v,0)+1
            kk=len(Q); pg[g]={v:F(cnt[v],kk) for v in cnt}
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj2,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                a_g={g:sum(pg[g].get(P[i],F(0)) for i in range(L)) for g in M}
                ells=sorted(ell[g] for g in M)
                for k in range(n):
                    Gamma_k=sum(max(0,ell[g]**2-k*k) for g in M)
                    A_k=sum(a_g[g]*max(0,ell[g]-k) for g in M)
                    D_k=N*N-k*k-Gamma_k
                    B_k=L*(N-k)-A_k
                    Ek=sum((2*r+1)*chiP[r] for r in range(k,n))
                    Tax=Ek+deltaP*max(0,L*L-k*k)
                    data=dict(name=name,N=n,f=f,P=tuple(P),k=k,L=L,D_k=str(D_k),Tax=str(Tax),Ek=str(Ek),
                              dP=str(deltaP),Gk=str(Gamma_k),Ak=str(A_k),Bk=str(B_k),ells=ells,
                              a_g=[str(a_g[g]) for g in sorted(M)])
                    if D_k>0:
                        r1=Tax/(F(L,5)*D_k); upd(acc,'R1',r1,data)
                        if k==0: upd(acc,'R1_k0',r1,data)
                        if B_k<0:
                            r2=25*(-B_k)/(F(4*L,5)*D_k); upd(acc,'R2',r2,data)
                            if k==0: upd(acc,'R2_k0',r2,data)

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    run(name,n,adj,E,acc)

def main():
    acc=dict(R1=None,R2=None,R1_k0=None,R2_k0=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d-%s"%(nn,g6),n,E,acc)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw-"+g6,n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(1,1,1,1,1),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    import json
    for key in ['R1','R1_k0','R2','R2_k0']:
        v=acc[key]
        print("="*60)
        if v is None: print(key,": none"); continue
        print("%s worst ratio = %s = %.5f"%(key,str(v[0]),float(v[0])))
        print("  ", json.dumps(v[1]))

if __name__=="__main__":
    main()
