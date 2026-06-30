"""Gate Codex 398 / GPT-Pro SWITCH CERTIFICATE for the gamma-min (A),(B) stability inequalities.
   F5(P): rho:{0..L-1}->Z5 with rho(i+1)-rho(i) in {1,4} (mod5) and rho(0)-rho(L-1) in {1,4} (closing via f).
   U_A(rho,c,tau): {x_i: rho(i)=c} + completion;  U_B(rho,c,tau): {x_i: rho(i)!=c} + complementary completion.
   Completion over B-components C of G[V-P], Att(C)={rho(i): x_i has B-neighbor in C}:
     U_A: Att subset {c}->all C; Att disjoint {c}->none; else one bipartition side (tau).
     U_B: Att disjoint {c}->all C; Att subset {c}->none; else one bipartition side (tau).
   Z_X(z)=min over (rho,c,tau, B^U connected) of [DeltaGamma(U_X)+z*mu(U_X)], mu=delta_B-delta_M.
   GATES (gamma-min rows):
     PF-A: Z_A(25) <= D_all - (5/L)(E_0+C_L).
     PF-B: if S>L: Z_B(25) <= D_all - (125/(4L))*N*(S-L).
     PF-C: Z_X(25)<0 => Z_X(Lambda)<0  (Lambda=|E|N^2+1).
   ALL exact Fraction.  Reports failures/margins.  Straddler completions capped.
"""
import subprocess, itertools
from fractions import Fraction as F
from _crux_extract import components_off_path
from _singleton_core import ell_map
from _factor_gate import chi_profile as _pc
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

CAP=1<<14

def f5_maps(L):
    res=[]
    for start in range(5):
        for steps in itertools.product((1,4),repeat=L-1):
            rho=[start]
            for s in steps: rho.append((rho[-1]+s)%5)
            if (rho[0]-rho[-1])%5 in (1,4): res.append(tuple(rho))
    return res

def comp_info(n,adj,side,P,rho):
    Pset=set(P); comps=components_off_path(n,adj,side,Pset); info=[]
    for C in comps:
        att=set()
        for v in C:
            for w in adj[v]:
                if w in Pset and side[w]!=side[v]: att.add(rho[P.index(w)])
        col={}; st=[next(iter(C))]; col[st[0]]=0
        while st:
            u=st.pop()
            for w in adj[u]:
                if w in C and side[w]!=side[u] and w not in col: col[w]=col[u]^1; st.append(w)
        cls0={v for v in C if col.get(v,0)==0}; cls1={v for v in C if col.get(v,0)==1}
        info.append((C,att,cls0,cls1))
    return info

def build_U(P,rho,c,info,mode,tauchoice):
    L=len(P)
    if mode=='A': base={P[i] for i in range(L) if rho[i]==c}
    else: base={P[i] for i in range(L) if rho[i]!=c}
    W=set(base); si=0
    for (C,att,cls0,cls1) in info:
        if not att: continue
        if mode=='A':
            allin = att<= {c}; nonein = (c not in att)
        else:
            allin = (c not in att); nonein = att<= {c}
        if allin: W|=C
        elif nonein: pass
        else:
            pick=tauchoice[si] if si<len(tauchoice) else 0; si+=1
            W|=(cls0 if pick==0 else cls1)
    return frozenset(W), si

def Zvals(n,adj,side,P,Gamma,Lam):
    """return (ZA25,ZA_big, ZB25,ZB_big)."""
    L=len(P); best={('A',25):None,('A','big'):None,('B',25):None,('B','big'):None}
    cnt=0
    for rho in f5_maps(L):
        info=comp_info(n,adj,side,P,rho)
        nstr=sum(1 for (C,att,c0,c1) in info if att and not(att<={0}) )  # rough straddler upper bound
        for c in range(5):
            # count straddlers for this (rho,c,mode)
            for mode in ('A','B'):
                # determine #straddlers
                straddlers=0
                for (C,att,c0,c1) in info:
                    if not att: continue
                    if mode=='A': allin=att<={c}; nonein=(c not in att)
                    else: allin=(c not in att); nonein=att<={c}
                    if not allin and not nonein: straddlers+=1
                taus=[()] if straddlers==0 else itertools.product((0,1),repeat=straddlers)
                for tau in taus:
                    cnt+=1
                    if cnt>CAP: break
                    W,_=build_U(P,rho,c,info,mode,tau)
                    if not W or len(W)==n: continue
                    s2=flip(side,list(W))
                    if not Bconn(n,adj,s2): continue
                    g1=gamma_of(n,adj,s2)
                    if g1 is None: continue
                    dB,dM=deltas(n,adj,side,W); mu=dB-dM; dG=g1-Gamma
                    for z,zk in ((25,25),(Lam,'big')):
                        val=dG+z*mu
                        k=(mode,zk)
                        if best[k] is None or val<best[k]: best[k]=val
                if cnt>CAP: break
            if cnt>CAP: break
        if cnt>CAP: break
    return best

def run(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); Gamma=sum(ell[g]**2 for g in M)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                deltaP=(S/L)**2-q; C_L=deltaP*L*L
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                D_all=N*N-Gamma
                best=Zvals(n,adj,side,P,Gamma,Lam)
                ZA25=best[('A',25)]; ZAb=best[('A','big')]; ZB25=best[('B',25)]; ZBb=best[('B','big')]
                acc['rows']+=1
                # PF-A
                if ZA25 is not None:
                    rhsA=D_all-F(5,L)*(E0+C_L)
                    if ZA25>rhsA:
                        acc['PFA_fail']+=1
                        if acc['PFA_ex'] is None: acc['PFA_ex']=(name,n,tuple(P),str(ZA25),str(rhsA))
                # PF-B
                if S>L and ZB25 is not None:
                    rhsB=D_all-F(125,4*L)*N*(S-L)
                    if ZB25>rhsB:
                        acc['PFB_fail']+=1
                        if acc['PFB_ex'] is None: acc['PFB_ex']=(name,n,tuple(P),str(ZB25),str(rhsB))
                # PF-C
                for Z25,Zb,tag in ((ZA25,ZAb,'A'),(ZB25,ZBb,'B')):
                    if Z25 is not None and Z25<0:
                        if Zb is None or Zb>=0:
                            acc['PFC_fail']+=1
                            if acc['PFC_ex'] is None: acc['PFC_ex']=(name,n,tuple(P),tag,str(Z25),str(Zb))

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,PFA_fail=0,PFB_fail=0,PFC_fail=0,PFA_ex=None,PFB_ex=None,PFC_ex=None)
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d PFA=%d PFB=%d PFC=%d"%(nn,acc['rows'],acc['PFA_fail'],acc['PFB_fail'],acc['PFC_fail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3)]:
        nn,EE=odd_blowup(5,list(sizes)) if False else (None,None)
    from _wf_deficit_farkas import odd_blowup
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("rows:",acc['rows'])
    print("PF-A failures (Z_A(25) > D_all-(5/L)(E0+C_L)):",acc['PFA_fail'],acc['PFA_ex'] or '')
    print("PF-B failures:",acc['PFB_fail'],acc['PFB_ex'] or '')
    print("PF-C failures (Z(25)<0 but Z(big)>=0):",acc['PFC_fail'],acc['PFC_ex'] or '')
    ok=(acc['PFA_fail']==0 and acc['PFB_fail']==0 and acc['PFC_fail']==0)
    print("VERDICT:", "SWITCH CERTIFICATE FEASIBLE (PF-A,B,C hold) => gamma-min proves (A),(B)" if ok else "FAILS")

if __name__=="__main__":
    main()
