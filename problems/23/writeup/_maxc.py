"""Decisive: does a single UNIVERSAL c make HALF-c [sum_f p_f(o)H_f >= c N^2 (T-4S)] close k2 for all o?
For overloaded o with T(o)>4S(o):
  c_needed(o) = (T(o)-N)/(T(o)-4S(o))   [c >= this closes k2 at o]
  c_o         = (sum_f p_f(o)H_f)/(N^2 (T(o)-4S(o)))   [HALF-c holds at o iff c <= c_o]
o closed by universal c iff c_needed(o) <= c <= c_o. Universal c exists iff max_o c_needed <= min_o c_o.
(o with T<=4S are auto: c_needed<=0, c_o=+inf.) Report max c_needed, min c_o, gap = min c_o - max c_needed (>=0 => a
universal c works => HALF-c with that c proves k2 entirely). EXACT Fraction."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _half import analyze
from _superphi import blow
from _schur_spec import pf_exact

def graph_cstats(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    u={q:F(N)-T[q] for q in Q}
    W={q:sum(K[q][q2]*u[q2] for q2 in Q) for q in Q}
    psi={q:F(N)*u[q]+W[q] for q in Q}
    maxneed=None; minco=None
    for o in O:
        S_o=sum(d.get(o,F(0)) for d in P)
        den=T[o]-4*S_o
        if den<=0: continue  # auto
        c_need=(T[o]-N)/den
        lhs=sum(K[o][q]*psi[q] for q in Q)   # sum_f p_f(o)H_f
        c_o=lhs/(F(N*N)*den)
        if maxneed is None or c_need>maxneed: maxneed=c_need
        if minco is None or c_o<minco: minco=c_o
    return maxneed,minco,N

def run(Nmax,Nmin=8,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        worstgap=None; wg=None; nhi=0; nbad=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            mn,mc,N=graph_cstats(info)
            if mn is None: continue   # no high-regime o
            nhi+=1
            gap=mc-mn
            if gap<0: nbad+=1
            if worstgap is None or gap<worstgap: worstgap=gap; wg=(g6,float(mn),float(mc))
        print(f"  N={nn}(str{stride}): graphs-with-high-regime-o={nhi} | universal-c FAILS(min c_o<max c_need):{nbad} | worst gap(min c_o - max c_need)={float(worstgap) if worstgap is not None else 'na'}@{wg}",flush=True)

if __name__=="__main__":
    print("=== universal-c for HALF-c: gap = min_o c_o - max_o c_needed (>=0 => single c closes k2) ===")
    for g6 in ["I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?","G?bF`w"]:
        n,E=dec(g6); info=loads(n,E); mn,mc,N=graph_cstats(info)
        if mn is None: print(f"  {g6}: no high-regime o"); continue
        print(f"  {g6:13} N={n}: max c_needed={float(mn):.4f} min c_o={float(mc):.4f} gap={float(mc-mn):+.4f} {'OK' if mc>=mn else 'NO universal c'}")
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("J?`@C_W{Ck?",2)]:
        nn,EE=blow(g6,t)
        if nn>22: continue
        info=loads(nn,EE)
        if info is None: continue
        mn,mc,N=graph_cstats(info)
        if mn is None: print(f"  {g6}[{t}]: no high-regime o"); continue
        print(f"  {g6}[{t}] N={nn}: max c_needed={float(mn):.4f} min c_o={float(mc):.4f} gap={float(mc-mn):+.4f} {'OK' if mc>=mn else 'NO'}")
    run(9,8,1); run(10,10,4); run(11,11,15)
