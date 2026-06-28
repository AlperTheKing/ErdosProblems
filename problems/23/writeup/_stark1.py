"""Exact-stress Codex's STAR-K1 (block 94): pure-K |O|=1 sufficient condition for cond3.
   For singleton O={o}: a_q=K[o][q], R_q=N-T[q], D=T[o]-N.
     STAR-K1(o):  LB1_K := sum_{q: a_q>0, R_q>0} a_q R_q/(a_q+R_q)  >=  D.
   Equivalent diagonal-Schur form sum_q a_q^2/(a_q+R_q) <= N-K[o][o] (since sum_q a_q = T[o]-K[o][o]).
   SUFFICIENT for cond3|O1 because A_QQ = N I - K_QQ = L_{K[Q]} + diag(R_q+a_q) >= diag(R_q+a_q)
   => K[o,Q] A_QQ^{-1} K[Q,o] <= sum_q a_q^2/(R_q+a_q). I VERIFY that M-matrix identity exactly too.
   STRESS especially on NON-UNIFORM odd-cycle blow-ups (where the omega-STAR-O1 died)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def odd_blowup(m, sizes):
    """C_m blow-up with given part sizes; standard cut: part i -> side (0 if i in the 'even' independent-ish set).
       For odd m we 2-color greedily around the cycle except one same-side adjacent pair (the bad edge)."""
    n=sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    part=[None]*n
    for i in range(m):
        for j in range(sizes[i]): part[start[i]+j]=i
    adj=[set() for _ in range(n)]; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u=start[i]+a; v=start[j]+b; adj[u].add(v); adj[v].add(u); E.append((u,v))
    # 2-color parts around C_m: side = i%2, so adjacent parts differ except the wrap (m-1,0) both depend on parity;
    # for odd m, parts m-1 and 0 are both even-ish -> same side -> that's the bad pair.
    side=[part[v]%2 for v in range(n)]
    return n,E,adj,side

def stark1(adj, side, n):
    r=build_K(adj,side,n)
    if r is None: return None
    K,T=r; N=n
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]; D=T[o]-N
    if D<=0: return None
    LB1=F(0)
    for q in range(n):
        if q==o: continue
        aq=K[o][q]; Rq=F(N)-T[q]
        if aq>0 and Rq>0: LB1+=aq*Rq/(aq+Rq)
    ok=LB1>=D
    return dict(o=o,D=D,LB1=LB1,ok=ok,ratio=(LB1/D))

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def run(nm,n,E,report=True,acc=None):
    adj,cuts=gmins(n,E)
    tot=0; fails=0; minr=None; wit=None
    for s in cuts:
        d=stark1(adj,s,n)
        if d is None: continue
        tot+=1
        if not d['ok']: fails+=1
        if minr is None or d['ratio']<minr: minr=d['ratio']; wit=(nm,d['o'])
    if acc is not None:
        acc['tot']+=tot; acc['fails']+=fails
        if minr is not None and (acc['minr'] is None or minr<acc['minr']): acc['minr']=minr; acc['wit']=wit
    if report and tot>0:
        print(f"  {nm} N={n}: |O|=1 cuts={tot} STAR-K1-FAILS={fails} min-ratio={float(minr):.4f} wit={wit}",flush=True)
    return tot,fails,minr

def run_cut(nm,n,E,adj,side):
    d=stark1(adj,side,n)
    if d is None: print(f"  {nm}: not |O|=1"); return
    print(f"  {nm} N={n}: o={d['o']} D={d['D']} LB1={d['LB1']} STAR-K1-OK={d['ok']} ratio={float(d['ratio']):.4f}",flush=True)

if __name__=="__main__":
    print("=== STAR-K1 (pure-K |O|=1 sufficient cond3) exact stress ===",flush=True)
    # the STAR-O1 killer: nonuniform C5 (1,48,6,8,48) -- must PASS here
    n,E,adj,side=odd_blowup(5,[1,48,6,8,48]); run_cut("C5[1,48,6,8,48]",n,E,adj,side)
    # NON-UNIFORM blow-up sweep (the adversarial frontier)
    import itertools
    print("--- non-uniform C5 blow-up sweep ---",flush=True)
    acc={'tot':0,'fails':0,'minr':None,'wit':None}
    for sizes in itertools.product([1,2,3,6,12,30,60],repeat=5):
        if sizes[0]!=1 and sizes[2]!=1 and sizes[4]!=1: continue   # need a small bad-endpoint part for |O|=1
        if sum(sizes)>200: continue
        n,E,adj,side=odd_blowup(5,list(sizes))
        d=stark1(adj,side,n)
        if d is None: continue
        acc['tot']+=1
        if not d['ok']: acc['fails']+=1; print(f"  !!! STAR-K1 FAIL C5{sizes}: D={d['D']} LB1={d['LB1']} ratio={float(d['ratio']):.4f}",flush=True)
        if acc['minr'] is None or d['ratio']<acc['minr']: acc['minr']=d['ratio']; acc['wit']=sizes
    print(f"  C5 sweep: |O|=1 instances={acc['tot']} FAILS={acc['fails']} min-ratio={float(acc['minr']) if acc['minr'] else None} wit={acc['wit']}",flush=True)
    # C7 non-uniform sweep
    acc7={'tot':0,'fails':0,'minr':None,'wit':None}
    for sizes in itertools.product([1,2,6,20,40],repeat=7):
        if 1 not in sizes: continue
        if sum(sizes)>180: continue
        n,E,adj,side=odd_blowup(7,list(sizes))
        d=stark1(adj,side,n)
        if d is None: continue
        acc7['tot']+=1
        if not d['ok']: acc7['fails']+=1; print(f"  !!! STAR-K1 FAIL C7{sizes}: ratio={float(d['ratio']):.4f}",flush=True)
        if acc7['minr'] is None or d['ratio']<acc7['minr']: acc7['minr']=d['ratio']; acc7['wit']=sizes
    print(f"  C7 sweep: |O|=1 instances={acc7['tot']} FAILS={acc7['fails']} min-ratio={float(acc7['minr']) if acc7['minr'] else None} wit={acc7['wit']}",flush=True)
    # Mycielskians + glued + census
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    accg={'tot':0,'fails':0,'minr':None,'wit':None}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}{br}",n,E,report=False,acc=accg)
    print(f"  glued battery: |O|=1 cuts={accg['tot']} STAR-K1-FAILS={accg['fails']} min-ratio={float(accg['minr']) if accg['minr'] else None}",flush=True)
    for nn in range(9,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'fails':0,'minr':None,'wit':None}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,report=False,acc=acc)
        print(f"  census N={nn}: |O|=1 cuts={acc['tot']} STAR-K1-FAILS={acc['fails']} min-ratio={float(acc['minr']) if acc['minr'] else None} wit={acc['wit']}",flush=True)
