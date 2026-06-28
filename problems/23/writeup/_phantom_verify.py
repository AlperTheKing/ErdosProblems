"""Exact-test Codex's REPAIRED phantom-capacity row-Hall (block 113), which adds the global idle bank
   idle_o = N - |U_o| (U_o = union of active bad-edge supports) to fix the support-Hall failure I found.
     (PH)  PHANTOM-HALL:      sum_{f in H} c_f(o) <= |union_{f in H} supp(p_f)| + idle_o
     (TPH) TRUNCATED-PHANTOM: sum_{f in H} c_f(o) <= sum_v min(1, A_H(v)) + idle_o
   Full subset enum, small |M|. Includes the N=9 witness H?AFBo] that killed the plain support-Hall."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import odd_blowup, gmins

def pf_dict(cyc, f):
    Ps=cyc[f]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    return d

def verify(adj, side, n, maxM=15):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T2,mu,cyc=st
    if len(M)>maxM: return dict(skip='bigM', nbad=len(M))
    K,T=build_K(adj,side,n); N=n
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip='Oempty')
    pf={f:pf_dict(cyc,f) for f in M}
    supp={f:set(pf[f].keys()) for f in M}
    Xf={f:sum(pf[f].get(o,F(0)) for o in O) for f in M}
    s={q:sum(K[o][q] for o in O) for q in Q}
    res={'O':len(O),'nbad':len(M),'PH_fail':0,'TPH_fail':0,'plainRH_fail':0}
    Ml=list(M)
    for o in O:
        psi={q:(K[o][q]/(F(N)-T[q]+s[q])) for q in Q if (F(N)-T[q]+s[q])>0}
        cf={f: Xf[f]*(pf[f].get(o,F(0)) + sum(psi.get(q,F(0))*pf[f].get(q,F(0)) for q in Q)) for f in M}
        active=[f for f in M if cf[f]>0]
        Uo=set().union(*[supp[f] for f in active]) if active else set()
        idle_o=F(N)-len(Uo)
        for r in range(1,1<<len(Ml)):
            H=[Ml[i] for i in range(len(Ml)) if r>>i&1]
            dem=sum(cf[f] for f in H)
            unionsupp=len(set().union(*[supp[f] for f in H]))
            AH={}
            for f in H:
                for v,pv in pf[f].items(): AH[v]=AH.get(v,F(0))+Xf[f]*pv
            tmcap=sum(min(F(1),AH.get(v,F(0))) for v in AH)
            if dem>unionsupp: res['plainRH_fail']+=1
            if dem>unionsupp+idle_o: res['PH_fail']+=1
            if dem>tmcap+idle_o: res['TPH_fail']+=1
    return res

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=verify(adj,s,n)
        if d is None or d.get('skip'): continue
        acc['tot']+=1
        acc['PH']+=d['PH_fail']; acc['TPH']+=d['TPH_fail']; acc['plainRH']+=d['plainRH_fail']
        acc['maxO']=max(acc['maxO'],d['O'])

if __name__=="__main__":
    print("=== PHANTOM-HALL / TRUNCATED-PHANTOM (idle-bank repair), exact ===",flush=True)
    # the N=9 witness that killed support-Hall
    n,E=dec("H?AFBo]"); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    d=verify(adj,[0,0,0,1,1,1,1,0,0],n)
    print(f"  N=9 witness H?AFBo] o-side: plainRH-FAIL={d['plainRH_fail']} PH-FAIL={d['PH_fail']} TPH-FAIL={d['TPH_fail']}",flush=True)
    G11=mycielski(5,Cn(5)); G23=mycielski(*G11); M15=mycielski(7,Cn(7))
    for nm,g in [("Grotzsch11",G11),("MycC7_15",M15)]:
        a={'tot':0,'PH':0,'TPH':0,'plainRH':0,'maxO':0}; run(nm,g[0],g[1],a)
        print(f"  {nm}: O-cuts={a['tot']} plainRH-FAIL={a['plainRH']} PH-FAIL={a['PH']} TPH-FAIL={a['TPH']} maxO={a['maxO']}",flush=True)
    ab={'tot':0,'PH':0,'TPH':0,'plainRH':0,'maxO':0}
    for sizes in [[1,3,2,2,3],[2,3,2,2,3],[1,4,3,2,4],[2,4,2,3,4],[1,5,3,2,5],[1,3,1,2,3]]:
        n,E,adj,side=odd_blowup(5,sizes); run(f"C5{sizes}",n,E,ab)
    print(f"  small non-uniform C5: O-cuts={ab['tot']} plainRH-FAIL={ab['plainRH']} PH-FAIL={ab['PH']} TPH-FAIL={ab['TPH']} maxO={ab['maxO']}",flush=True)
    ag={'tot':0,'PH':0,'TPH':0,'plainRH':0,'maxO':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,ag)
    print(f"  glued battery: O-cuts={ag['tot']} plainRH-FAIL={ag['plainRH']} PH-FAIL={ag['PH']} TPH-FAIL={ag['TPH']} maxO={ag['maxO']}",flush=True)
    for nnn in (9,10,11):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'PH':0,'TPH':0,'plainRH':0,'maxO':0}; skip=0; ng=0
        for g6 in outg:
            ng+=1
            if nnn==11 and ng>6000: break
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}{' (first 6000)' if nnn==11 else ''}: O-cuts={acc['tot']} plainRH-FAIL={acc['plainRH']} PH-FAIL={acc['PH']} TPH-FAIL={acc['TPH']} maxO={acc['maxO']}",flush=True)
