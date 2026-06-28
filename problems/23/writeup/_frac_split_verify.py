"""Exact-test Codex's FRACTIONAL shell-crossing SPLIT certificate (block 122, tie-invariant).
   Per bad edge f, L=ell(f), A_i layer loads, R=ROWSUM-N, B_t=OUT_t-2tN/L (t=1..m).
   FRAC condition: R<=0 AND min_t B_t <= 0 AND max_t B_t >= R   (conv{B_t} intersects [R,0]) => ROWSUM-O.
   (Weaker than integer split, which needed a single B_t in [R,0].) Test ALL gamma-min cuts + large blow-ups."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import gmins
from _split_verify import split_quotient  # reuse A_i quotient builder indirectly

def frac_ok(A, N):
    L=len(A); m=(L-1)//2; R=sum(A)-F(N)
    if R>0: return False, True   # ROWSUM-O itself fails
    Bs=[ (sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L))) - F(2*t*N,L) for t in range(1,m+1)]
    ok = (min(Bs)<=0) and (max(Bs)>=R)
    return ok, False

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
    fails=0; rowsumfail=0
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]
        layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        ok,rsf=frac_ok(A,N)
        if rsf: rowsumfail+=1
        if not ok: fails+=1
    return len(M), fails, rowsumfail

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=standard(adj,s,n)
        if d is None: continue
        acc['tot']+=d[0]; acc['frac']+=d[1]; acc['rs']+=d[2]

def frac_quotient(m, n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    order=[(a-k)%m for k in range(m)]; A=[Pi(order[i]) for i in range(m)]
    return frac_ok(A,N)

if __name__=="__main__":
    print("=== FRACTIONAL shell-crossing SPLIT (tie-invariant) -- all gamma-min cuts + large blow-ups ===",flush=True)
    G11=mycielski(5,Cn(5)); M15=mycielski(7,Cn(7))
    accm={'tot':0,'frac':0,'rs':0}
    for nm,g in [("Grotzsch11",G11),("MycC7_15",M15)]: run(nm,g[0],g[1],accm)
    print(f"  Mycielskians: bad-edges={accm['tot']} FRAC-FAIL={accm['frac']} ROWSUM-FAIL={accm['rs']}",flush=True)
    accg={'tot':0,'frac':0,'rs':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: bad-edges={accg['tot']} FRAC-FAIL={accg['frac']} ROWSUM-FAIL={accg['rs']}",flush=True)
    for nnn in (9,10,11):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'frac':0,'rs':0}; ng=0
        for g6 in outg:
            ng+=1
            if nnn==11 and ng>4000: break
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}{' (first 4000, ALL gamma-min cuts)' if nnn==11 else ' (ALL gamma-min cuts)'}: bad-edges={acc['tot']} FRAC-FAIL={acc['frac']} ROWSUM-FAIL={acc['rs']}",flush=True)
    print("--- LARGE blow-up quotient FRAC sweep ---",flush=True)
    rng=random.Random(2718)
    for m in (5,7,9,11,13):
        ff=0; rf=0; tot=0
        for _ in range(70000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            ok,rsf=frac_quotient(m,n); tot+=1
            if rsf: rf+=1
            if not ok: ff+=1
        print(f"  C{m} large blow-ups: tested={tot} FRAC-FAIL={ff} ROWSUM-FAIL={rf}",flush=True)
