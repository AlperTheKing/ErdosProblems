"""Verify GPT-Pro's two foundational claims for the (A) proof strategy (calibrated dual-price coarea):
   (L) LINEARIZATION (Euler):  L^2*delta = (1/2) sum_i a_i h_i,  a_i = 2S - L^2(h_{r+1}1_{i=r}+h_r 1_{i=r+1}),
       r = argmin_i h_i h_{i+1}.  Also (ECPI): E_0 + delta*L^2 <= (L/5)(N^2-Gamma)  <=>  sum_v pi(v)T(v)+E_0 <= (L/5)N^2,
       pi(v)=L/5 + (a_i/(2N))1_{v=x_i}.
   (E) E_0 CONVENTION (GPT-Pro's definitional trap): the gate's E_0 (chi_profile) is RENORMALIZED -- on the balanced
       C5[t] blow-up E_0 = 0, whereas the RAW post-flip Gamma change (flip {x_0,x_{L-1}}, recompute Gamma) is != 0.
   Exact Fraction.  theta H?AFBo] + census N<=8 (linearization) + C5[2],C5[3] blow-ups (E_0 convention).
"""
import subprocess
from fractions import Fraction as F
from _singleton_core import ell_map
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def lin_check(name,n,adj,side,acc):
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
            h=[T[P[i]]/N for i in range(L)]; S=sum(h)
            prods=[h[i]*h[(i+1)%L] for i in range(L)]
            q=min(prods); r=prods.index(q)
            D=S*S-L*L*q   # = L^2 * delta
            a=[2*S - L*L*((h[(r+1)%L] if i==r else 0)+(h[r] if i==(r+1)%L else 0)) for i in range(L)]
            lin=F(1,2)*sum(a[i]*h[i] for i in range(L))
            acc['rows']+=1
            if lin!=D:
                acc['lin_fail']+=1
                if acc['lin_ex'] is None: acc['lin_ex']=(name,tuple(P),str(lin),str(D))

def main():
    acc=dict(rows=0,lin_fail=0,lin_ex=None)
    # linearization on theta + census N<=8 gamma-min
    n,E=dec("H?AFBo]"); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    _,cuts=gmins(n,E)
    for side in cuts: lin_check("thw",n,adj,side,acc)
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            try: _,cuts=gmins(n,E)
            except Exception: continue
            for side in cuts: lin_check("cen%d"%nn,n,adj,side,acc)
    print("(L) LINEARIZATION L^2*delta == (1/2)sum a_i h_i (Euler):  rows=%d  fail=%d %s"%(acc['rows'],acc['lin_fail'],acc['lin_ex'] or ''))

    # (E) E_0 convention on balanced C5[t] blow-ups
    print("(E) E_0 convention on balanced C5[t] blow-ups (gate E_0 should be 0; raw flip != 0):")
    for t in (2,3):
        n,E=odd_blowup(5,[t,t,t,t,t])
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        _,cuts=gmins(n,E)
        done=False
        for side in cuts:
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,cyc=st[0],st[1],st[2],st[4]
            if not M: continue
            Gamma=sum(ell[g]**2 for g in M)
            for f in M:
                L=ell[f]
                if L%2: pass
                else: continue
                for P in cyc[f]:
                    if len(P)!=L: continue
                    chiP=[0]*n
                    for end in (P[0],P[-1]):
                        ch=endpt_chi(n,adj,side,end,M,n)
                        for rr in range(n): chiP[rr]+=ch[rr]
                    E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
                    # raw flip of {x_0, x_{L-1}}
                    s2=flip(side,{P[0],P[-1]})
                    graw=gamma_of(n,adj,s2)
                    raw=(graw-Gamma) if graw is not None else None
                    print("   C5[%d] N=%d L=%d Gamma=%d: gate E_0=%s ; raw flip{x0,xL-1} dGamma=%s"%(t,n,L,Gamma,str(E0),str(raw)))
                    done=True; break
                if done: break
            if done: break

if __name__=="__main__":
    main()
