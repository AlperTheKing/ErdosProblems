"""Exact-test Codex's MIN-BUFFER form (block 125), the cleanest {1,2} fractional-SPLIT sub-target.
   Per bad edge f, L=ell(f): E=A_0+A_{L-1}, U=A_1+A_{L-2}, C=A_2+...+A_{L-3}, T0=2N/L, H=min(U,T0).
     (MB1)  E + H <= 4N/L
     (MB2)  C + H <= (L-2)N/L
   Adding (with H) implies ROWSUM-O. Also report whether {1,2} suffices vs the rare t>=3 cases at L>=7."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import gmins

def mb_ok(A, N):
    L=len(A);
    if L<5: return True, True   # not applicable (ell>=5 always)
    E=A[0]+A[L-1]; U=A[1]+A[L-2]; C=sum(A[i] for i in range(2,L-2))
    T0=F(2*N,L); H=min(U,T0)
    ok = (E+H <= 2*T0) and (C+H <= F((L-2)*N, L))
    rowsum_ok = sum(A) <= N
    return ok, rowsum_ok

def standard(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    mbfail=0; rsfail=0
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]
        layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        ok,rsok=mb_ok(A,N)
        if not rsok: rsfail+=1
        if not ok: mbfail+=1
    return len(M), mbfail, rsfail

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=standard(adj,s,n)
        if d is None: continue
        acc['tot']+=d[0]; acc['mb']+=d[1]; acc['rs']+=d[2]

def mb_quotient(m,n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    order=[(a-k)%m for k in range(m)]; A=[Pi(order[i]) for i in range(m)]
    return mb_ok(A,N)

if __name__=="__main__":
    print("=== MIN-BUFFER form (E+H<=4N/L, C+H<=(L-2)N/L, H=min(U,2N/L)) ===",flush=True)
    G11=mycielski(5,Cn(5)); M15=mycielski(7,Cn(7))
    accm={'tot':0,'mb':0,'rs':0}
    for nm,g in [("Grotzsch11",G11),("MycC7_15",M15)]: run(nm,g[0],g[1],accm)
    print(f"  Mycielskians: bad-edges={accm['tot']} MB-FAIL={accm['mb']} ROWSUM-FAIL={accm['rs']}",flush=True)
    accg={'tot':0,'mb':0,'rs':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: bad-edges={accg['tot']} MB-FAIL={accg['mb']} ROWSUM-FAIL={accg['rs']}",flush=True)
    for nnn in (9,10,11):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'mb':0,'rs':0}; ng=0
        for g6 in outg:
            ng+=1
            if nnn==11 and ng>4000: break
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn} (ALL gamma-min cuts): bad-edges={acc['tot']} MB-FAIL={acc['mb']} ROWSUM-FAIL={acc['rs']}",flush=True)
    print("--- LARGE blow-up quotient MIN-BUFFER (incl L>=7 where t>=3 can occur) ---",flush=True)
    rng=random.Random(161803)
    for m in (5,7,9,11,13):
        mf=0; rf=0; tot=0
        for _ in range(70000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            ok,rsok=mb_quotient(m,n); tot+=1
            if not rsok: rf+=1
            if not ok: mf+=1
        print(f"  C{m}: tested={tot} MB-FAIL(={'{1,2} insufficient' if mf else 'ok'})={mf} ROWSUM-FAIL={rf}",flush=True)
