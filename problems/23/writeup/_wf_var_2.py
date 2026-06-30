"""Explore the FAN-AVERAGING variance inequality N(N-row_f) >= var_f for nonunique bad edges f.
EXACT Fraction. Gathers structural facts: identities, range of S, var decomposition,
Bhatia-Davis style bounds, and the relation row_f<=N. Hunts counterexamples to sub-lemmas
on the standing gate (census N<=11 ALL gamma-min cuts, Mycielskians, blow-ups, glued)."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def per_side(n, adj, s):
    """Return list of dicts, one per nonunique bad edge f, with all the quantities."""
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    # p_g(v) and S(v)
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    out=[]
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
        mean=row/ll; var=sum(d[v]*(S[v]-mean)**2 for v in d)
        # support of f and its S-values
        supp=sorted(d.keys())
        Svals=[S[v] for v in supp]
        out.append(dict(n=n,f=f,d=d,ll=ll,row=row,mean=mean,var=var,
                        margin=F(n)*(F(n)-row)-var, supp=supp, Svals=Svals,
                        Smax=max(Svals), Smin=min(Svals), S=S, pf=pf, cyc=cyc, M=M))
    return out

def gms(n,E):
    adj,cuts=gmins(n,E); return adj,cuts

# ---- sub-lemma checks ----
# (A) identity var = sum p_f S^2 - row^2/ell  (sanity)
# (B) row_f <= N  (the conclusion; we want to (re)derive)
# (C) Smax <= N ?  and per-vertex S(v)<=N ?
# (D) Bhatia-Davis: var <= ll*(Smax-mean)(mean-Smin); is ll*(Smax-mean)(mean-Smin) <= N(N-row)?
# (E) crude: var <= ll * (Smax - Smin)^2 / 4 ; compare.
# (F) KEY candidate: var <= ll*(N - mean)*mean  (variance of [0,N]-bounded var times mass)... test
# (G) candidate: N(N-row) - var = N^2 - N row - sum p S^2 + row^2/ll
#     Want to show >=0. Equivalent: sum_v p_f(v)[ N^2/ll - ??? ]. Let's just probe signs of pieces.

def checks(rec):
    n=F(rec['n']); d=rec['d']; S=rec['S']; ll=rec['ll']; row=rec['row']; mean=rec['mean']; var=rec['var']
    res={}
    # (A)
    var2=sum(d[v]*S[v]**2 for v in d) - row**2/ll
    res['A_identity']= (var2==var)
    # (B)
    res['B_row_le_N']= (row<=n)
    # (C) global S<=N at f-support, and globally
    res['C_S_le_N_supp']= all(S[v]<=n for v in d)
    res['C_S_le_N_all']= all(sv<=n for sv in S)
    res['Smax_supp']=max(S[v] for v in d)
    # (D) Bhatia-Davis on support range
    Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
    bd=ll*(Smax-mean)*(mean-Smin)
    res['D_var_le_BD']=(var<=bd)
    res['D_BD_le_target']=(bd<=n*(n-row))
    # (F) var <= ll*(N-mean)*mean ?
    res['F_var_le_llNmean']=(var<=ll*(n-mean)*mean)
    res['F_target_ge']=(ll*(n-mean)*mean<=n*(n-row))  # = ll*(N-mean)*mean<=N(N-row)?
    # (H) candidate sum_v p_f(v)*S(v)*(N - S(v)) >= 0 trivially if S<=N; relate
    # margin = N^2 - N row - sum p S^2 + row^2/ll
    #        = N^2(1) ... write as sum over support of p with weights? use ll = sum p.
    # N^2 - N row = sum_v p_f(v)*(N^2/ll? ) no. Let's use: N*row? Actually N*row = N*sum p S.
    # margin = N^2 - sum_v p_f(v)*(N*S(v)) ... no N row = N sum p S. and sum p S^2.
    # margin = N^2 - N*row - var. With var= sum p S^2 - row^2/ll.
    # margin = N^2 - N row - sum p S^2 + row^2/ll.
    # Try: = sum_v p_f(v)*[ N*(N-S(v)) ]  - (N row - row^2/ll) ... check:
    #   sum p N(N-S) = N^2 ll - N row. Not matching (has ll factor).
    return res

def collect(name, n, E, agg, firsts):
    adj,cuts=gms(n,E)
    for s in cuts:
        for rec in per_side(n,adj,s):
            r=checks(rec)
            for k,v in r.items():
                if isinstance(v,bool):
                    agg.setdefault(k,[0,0])
                    agg[k][0]+= (1 if v else 0); agg[k][1]+=1
                    if not v and firsts.get(k) is None:
                        firsts[k]=(name,rec['f'],str(rec['row']),str(rec['var']),str(rec['margin']))
            # record worst margin sign
            agg.setdefault('MARGIN_neg',[0,0])
            agg['MARGIN_neg'][1]+=1
            if rec['margin']<0:
                agg['MARGIN_neg'][0]+=1
                if firsts.get('MARGIN_neg') is None: firsts['MARGIN_neg']=(name,rec['f'])

if __name__=="__main__":
    agg={}; firsts={}
    print("=== census N=7..11 ALL gamma-min cuts ===",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); collect(g6,n,E,agg,firsts)
        print(f"  done N={nn}",flush=True)
    def blowup(parts):
        m=len(parts); off=[0]*(m+1)
        for i in range(m): off[i+1]=off[i]+parts[i]
        nn=off[m]; EE=[]
        for i in range(m):
            j=(i+1)%m
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,EE
    extra=[("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),
           ("Grotzsch",)+mycielski(5,Cn(5)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C5[2]",)+blowup([2,2,2,2,2]),
           ("C5[3]",)+blowup([3,3,3,3,3]),
           ("C5unbal",)+blowup([1,5,2,2,5]),
           ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
           ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6])]
    print("=== extra battery ===",flush=True)
    for it in extra:
        collect(it[0],it[1],it[2],agg,firsts); print(f"  done {it[0]}",flush=True)
    print("\n=== AGGREGATE (pass/total) ===")
    for k in sorted(agg):
        p,t=agg[k]; print(f"  {k}: {p}/{t}"+("  FIRSTFAIL "+str(firsts[k]) if firsts.get(k) else ""))
