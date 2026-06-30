"""Clean verification of BD-TARGET (the Bhatia-Davis reduction of the fan-averaging variance inequality).
For every NONUNIQUE bad edge f (|cyc(f)|>=2) on a gamma-min connected-B max cut:
  row_f = sum_v p_f(v)S(v),  ell_f=sum_v p_f(v),  mu=row_f/ell_f,  M=max_{v in supp p_f} S(v), m=min S(v).
  BD (theorem): var_f = ell_f*Var_pi(S) <= ell_f*(M-mu)(mu-m).
  BD-TARGET (the remaining inequality):  ell_f*(M-mu)(mu-m) <= N*(N-row_f).
  => N(N-row_f) >= var_f (fan-averaging). Verify BD-TARGET 0-violation + min margin on the FULL gate,
  INCLUDING obstruction-style CP-SAT-max blow-ups + redundant detours (the class that broke scalar NET)."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges

def recs_for(n,adj,s):
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu_,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    out=[]
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d); mu=row/ll
        Sv=[S[v] for v in d]; Mx=max(Sv); mn=min(Sv)
        var=sum(d[v]*(S[v]-mu)**2 for v in d)
        bd=ll*(Mx-mu)*(mu-mn); target=F(n)*(F(n)-row)
        out.append((n,f,var,bd,target,row))
    return out

def run_cut_set(name,n,adj,cuts,acc):
    for s in cuts:
        for (nn,f,var,bd,target,row) in recs_for(n,adj,s):
            acc['rows']+=1
            # sanity: BD theorem var<=bd
            if var>bd: acc['bd_thm_fail']+=1
            margin=target-bd
            if margin<acc['minmargin'][0]: acc['minmargin']=(margin,name,f,str(bd),str(target))
            if margin<0:
                acc['bdt_viol']+=1
                if acc['first'] is None: acc['first']=(name,f,str(bd),str(target),str(row))
            # also direct variance check
            if F(nn)*(F(nn)-row)<var: acc['direct_viol']+=1

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

if __name__=="__main__":
    acc={'rows':0,'bd_thm_fail':0,'bdt_viol':0,'direct_viol':0,'minmargin':(F(10**9),'','','',''),'first':None}
    print("=== BD-TARGET gate: ell(M-mu)(mu-m) <= N(N-row) for nonunique f (gamma-min) ===",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        r0=acc['rows']; v0=acc['bdt_viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            run_cut_set(g6,n,adj,cuts,acc)
        print(f"  census N={nn} gmin: rows(+{acc['rows']-r0}) BDT-viol(+{acc['bdt_viol']-v0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    named=[("M(C7)",)+mycielski(7,Cn(7)),("M(C9)",)+mycielski(9,Cn(9)),("M(Grotzsch)N23",)+mycg,
           ("C7|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C5[2]",)+blowup([2,2,2,2,2]),("C5[3]",)+blowup([3,3,3,3,3]),
           ("C5unbal",)+blowup([1,5,2,2,5]),("C7unbal",)+blowup([1,4,2,4,2,4,2])]
    for it in named:
        name,nn,E=it; adj,cuts=gmins(nn,E); r0=acc['rows']; v0=acc['bdt_viol']
        run_cut_set(name,nn,adj,cuts,acc)
        print(f"  {name} N={nn} gmin: rows(+{acc['rows']-r0}) BDT-viol(+{acc['bdt_viol']-v0})",flush=True)
    # obstruction-style: blow-ups + redundant detour, gamma-min
    for parts in [[2,2,2,2,2],[3,3,3,3,3]]:
        n,E=blowup(parts)
        # add a redundant cut-detour between two same-class verts under a max cut: use gmins cut to pick
        adj0,cuts0=gmins(n,E)
        if cuts0:
            s=cuts0[0]
            import itertools as it2
            pair=None; A=adj_from_edges(n,E)
            for u,v in it2.combinations(range(n),2):
                if s[u]==s[v] and v not in A[u]: pair=(u,v); break
            if pair:
                u,v=pair; n2,E2,side2=add_cut_path(n,list(E),list(s),u,v,6)
                adj2=adj_from_edges(n2,sorted(set(E2)))
                from _h import Bconn
                if Bconn(n2,adj2,side2):
                    r0=acc['rows']; v0=acc['bdt_viol']
                    run_cut_set("C%d%s+detour"%(len(parts),parts),n2,adj2,[side2],acc)
                    print(f"  C{len(parts)}{parts}+detour N={n2}: rows(+{acc['rows']-r0}) BDT-viol(+{acc['bdt_viol']-v0})",flush=True)
    print(f"\n  TOTAL nonunique rows={acc['rows']}  BD-theorem-fail={acc['bd_thm_fail']} (must be 0)  BD-TARGET-viol={acc['bdt_viol']}  direct-variance-viol={acc['direct_viol']}",flush=True)
    print(f"  MIN BD-TARGET margin (target-bd) = {float(acc['minmargin'][0])} at {acc['minmargin'][1:]}",flush=True)
    if acc['first']: print(f"  first BD-TARGET violation: {acc['first']}",flush=True)
    print(f"  === {'BD-TARGET VIOLATED (reduction has a real gap)' if acc['bdt_viol'] else 'BD-TARGET HOLDS: ell(M-mu)(mu-m)<=N(N-row) => fan-averaging variance proven modulo BD-TARGET'} ===",flush=True)
