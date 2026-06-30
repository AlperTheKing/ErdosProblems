"""Gate Codex 407 / GPT-Pro no-port A-compression cone on gamma-min NO-PORT rows.
   A_r = (L/5)*d_r - e_r - c_r,  d_r=(2r+1)(1-m_r), e_r=(2r+1)chiP[r], c_r=(2r+1)delta_P*1_{r<L}.
   port profiles p_{i,r}=(2r+1)chi_i[r] (+ Lambda*mu_i at r=0); sum_r p_{i,r}=H_i (>=0 on no-port).
   A-cone: exists alpha_i>=0, u_r>=0 (u_N=0) with A_r = u_r - u_{r+1} + sum_i alpha_i p_{i,r}.
   Equivalently u_r = TailA_r - sum_i alpha_i Tailp_{i,r} >= 0 for all r, alpha>=0  (LP feasibility).
   If feasible => DGsum+C_L <= (L/5)(N^2-Gamma) = (A).  Report feasible/infeasible per no-port row;
   also the simple alpha=0 case (TailA_r>=0 for all r).  Float LP for feasibility (infeasibility reliable).
"""
import subprocess
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile as port_chi
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def run(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); em0=ell_map(n,adj,side); Gamma=sum(ell[g]**2 for g in M)
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
                # singleton ports (no-port => all H_i>=0); build profiles
                ports=[]  # (Hi, p_vector)
                noport=True
                for i in range(L):
                    Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or W is None: continue
                    if Hi<0: noport=False; break
                    em1=ell_map(n,adj,flip(side,W))
                    chi=port_chi(em0,em1,n)
                    dB,dM=deltas(n,adj,side,W); mu=dB-dM
                    pv=[(2*r+1)*chi[r] for r in range(n)]
                    pv[0]+=Lam*mu
                    ports.append((Hi,pv))
                if not noport: continue
                # A-vector
                m=[sum(1 for g in M if ell[g]>r) for r in range(n)]
                d=[(2*r+1)*(1-m[r]) for r in range(n)]
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                e=[(2*r+1)*chiP[r] for r in range(n)]
                c=[(2*r+1)*deltaP if r<L else F(0) for r in range(n)]
                A=[F(L,5)*d[r]-e[r]-c[r] for r in range(n)]
                # tails
                TailA=[sum(A[s] for s in range(r,n)) for r in range(n)]
                Tailp=[[sum(pv[s] for s in range(r,n)) for r in range(n)] for (_,pv) in ports]
                acc['rows']+=1
                # alpha=0 case
                if all(TailA[r]>=0 for r in range(n)):
                    acc['alpha0']+=1; continue
                # LP feasibility: exists alpha>=0 with sum_i alpha_i Tailp[i][r] <= TailA[r] for all r
                if not ports:
                    acc['infeas']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,tuple(P),'no ports & TailA<0 somewhere')
                    continue
                Amat=np.array([[float(Tailp[i][r]) for i in range(len(ports))] for r in range(n)],float)
                bvec=np.array([float(TailA[r]) for r in range(n)],float)
                res=linprog(np.zeros(len(ports)),A_ub=Amat,b_ub=bvec,bounds=[(0,None)]*len(ports),method="highs")
                if res.success: acc['feas_alpha']+=1
                else:
                    acc['infeas']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,tuple(P),'LP infeasible')

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,alpha0=0,feas_alpha=0,infeas=0,ex=None)
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d alpha0=%d feas=%d infeas=%d"%(nn,acc['rows'],acc['alpha0'],acc['feas_alpha'],acc['infeas']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("no-port rows:",acc['rows'])
    print("A-cone feasible via alpha=0 (TailA_r>=0 all r):",acc['alpha0'])
    print("A-cone feasible via alpha>0 (LP):",acc['feas_alpha'])
    print("A-cone INFEASIBLE:",acc['infeas'],acc['ex'] or '')
    print("VERDICT:", "A-COMPRESSION CONE FEASIBLE (proves (A) on no-port)" if acc['infeas']==0 and acc['rows']>0 else "INFEASIBLE on some no-port row")

if __name__=="__main__":
    main()
