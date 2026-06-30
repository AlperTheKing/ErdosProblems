"""EXACT reduction of the fan-averaging variance inequality to a single scalar inequality (BD-TARGET),
plus a stress of BD-TARGET and its tempting sub-lemmas on the standing gate
(census N<=11 ALL gamma-min cuts + iterated Mycielskians N<=23 + blow-ups + glued).

Chain (all EXACT, per nonunique bad edge f on a gamma-min connected-B max cut):
  var_f = ell_f * Var_{pi_f}(S),  pi_f(v)=p_f(v)/ell_f         [definition]
  (BD)   Var_{pi_f}(S) <= (M-mu)(mu-m)                         [Bhatia-Davis, UNCONDITIONAL THEOREM]
         where mu=mean_f, M=max_supp S, m=min_supp S
  =>     var_f <= ell_f (M-mu)(mu-m)
  (BD-TARGET)  ell_f (M-mu)(mu-m) <= N (N - row_f)             [the SINGLE remaining inequality]
  => N(N-row_f) >= var_f.   QED modulo BD-TARGET.

We (1) verify BD is exact-tight-or-slack and never violated (it's a theorem, sanity),
(2) verify BD-TARGET 0-violation on the full gate,
(3) probe whether BD-TARGET admits cheaper sufficient sub-lemmas, and hunt counterexamples to those
    (to expose the true residual gap honestly).
"""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def analyze_side(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu_,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    recs=[]
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
        mean=row/ll
        var=sum(d[v]*(S[v]-mean)**2 for v in d)
        Sv=[S[v] for v in d]; M_=max(Sv); m_=min(Sv)
        Vpi=var/ll
        recs.append(dict(n=n,f=f,ll=ll,row=row,mean=mean,var=var,
                         M=M_,m=m_,Vpi=Vpi,
                         target=F(n)*(F(n)-row),
                         bd=ll*(M_-mean)*(mean-m_),
                         Sa=S[f[0]],Sb=S[f[1]]))
    return recs

def gate_run(name,n,E,agg,firsts):
    adj,cuts=gmins(n,E)
    for s in cuts:
        for r in analyze_side(n,adj,s):
            checks={
              'BD_thm':          r['Vpi'] <= (r['M']-r['mean'])*(r['mean']-r['m']),
              'BD_TARGET':       r['bd'] <= r['target'],
              'FINAL_var':       r['var'] <= r['target'],
              # tempting cheaper sub-lemmas for BD-TARGET (hunt counterexamples):
              # (S1) ell*(M-mean) <= N - row + (N - M)? i.e. split as product of two N-row-ish terms
              'S1_M_le_N':       r['M'] <= F(n),
              # (S2) ell*(mean-m) <= N (mass-bounded spread below)
              'S2_llspread_le_N':r['ll']*(r['mean']-r['m']) <= F(n),
              # (S3) ell*(M-mean) <= N - row (upper spread bounded by deficit)
              'S3_upper':        r['ll']*(r['M']-r['mean']) <= F(n)-r['row'],
              # (S4) product form: (ell(M-mean))*(mean-m) <= (N-row)*N  via S3 & (mean-m)<=N
              'S4_meanm_le_N':   (r['mean']-r['m']) <= F(n),
              # (S3') via S2: bd=(M-mean)*[ell(mean-m)] <= (M-mean)*N; need M-mean <= N-row
              'S3p_upperdef':    (r['M']-r['mean']) <= F(n)-r['row'],
              # (S5) symmetric via S2-on-upper: ell(M-mean)<=N ? and then need (mean-m)<=N-row
              'S5a_llupper_leN': r['ll']*(r['M']-r['mean']) <= F(n),
              'S5b_lowerdef':    (r['mean']-r['m']) <= F(n)-r['row'],
              # (S6) the STRONG candidate from _wf_var_fast: row*(M+N-mean) <= N^2
              'S6_strong':       r['row']*(r['M']+F(n)-r['mean']) <= F(n)**2,
            }
            for k,v in checks.items():
                agg.setdefault(k,[0,0]); agg[k][1]+=1; agg[k][0]+=(1 if v else 0)
                if not v and firsts.get(k) is None:
                    firsts[k]=(name,r['f'],'row='+str(r['row']),'bd='+str(r['bd']),'tgt='+str(r['target']),
                               'M='+str(r['M']),'m='+str(r['m']),'mean='+str(r['mean']),'ll='+str(r['ll']))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

if __name__=="__main__":
    agg={}; firsts={}
    print("=== census N=7..11 ALL gamma-min cuts ===",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); gate_run(g6,n,E,agg,firsts)
        print(f"  done N={nn}",flush=True)
    extra=[("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),
           ("Grotzsch",)+mycielski(5,Cn(5)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           ("C5[2]",)+blowup([2,2,2,2,2]),
           ("C5[3]",)+blowup([3,3,3,3,3]),
           ("C5[4]",)+blowup([4,4,4,4,4]),
           ("C5unbal",)+blowup([1,5,2,2,5]),
           ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
           ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6]),
           ("C5[1,48,6,8,48]",)+blowup([1,48,6,8,48])]
    print("=== iterated-Mycielskian / glued / blow-up gate ===",flush=True)
    for it in extra:
        gate_run(it[0],it[1],it[2],agg,firsts); print(f"  done {it[0]}",flush=True)
    print("\n=== AGGREGATE (pass/total) ===")
    for k in ['BD_thm','BD_TARGET','FINAL_var','S1_M_le_N','S2_llspread_le_N','S3_upper','S4_meanm_le_N']:
        print(f"  {k}: {agg.get(k)}"+("   FIRSTFAIL "+str(firsts[k]) if firsts.get(k) else ""))
