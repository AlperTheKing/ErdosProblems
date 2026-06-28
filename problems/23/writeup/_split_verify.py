"""Exact-test Codex's SPLIT certificate for ROWSUM-O (block 120). Per bad edge f, L=ell(f), layers I_i(f) (geodesic
   position i), A_i(f)=sum_{v in I_i} p_f(v) S(v), S=sum_g p_g.  SPLIT: exists t in [1,m] with
     OUT_t = sum_{i<t} A_i + sum_{i>=L-t} A_i <= 2tN/L,   CEN_t = sum_{t<=i<=L-1-t} A_i <= (L-2t)N/L.
   (sum = ROWSUM-O <= N.)  Test on (a) standard gate via struct, (b) LARGE blow-up quotient gate (A_i = P_{pi(i)})
   -- the regime where every prior certificate died."""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _stark1 import gmins

def split_ok_from_A(A, N):
    """A = list of A_i (i=0..L-1, Fraction). Return True if SPLIT holds for some t."""
    L=len(A); m=(L-1)//2
    for t in range(1,m+1):
        out=sum(A[i] for i in range(t)) + sum(A[i] for i in range(L-t,L))
        cen=sum(A[i] for i in range(t,L-t))
        if out<=F(2*t*N,L) and cen<=F((L-2*t)*N,L):
            return True
    return False

def standard_gate(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    # S(v) = sum_g p_g(v)
    S=[F(0)]*n
    pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    fails=0; rowsum_fail=0
    for f in M:
        L=ell[f]; Ps=cyc[f]; k=len(Ps); a=f[0]
        d=pf[f]
        # layer of each geodesic vertex = its position (index in path)
        A=[F(0)]*L
        # accumulate p_f(v)*S(v) into the layer = position of v (consistent across geodesics for shortest path)
        layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        for v,pv in d.items():
            A[layer[v]] += pv*S[v]
        rowsum=sum(A)
        if rowsum>N: rowsum_fail+=1
        if not split_ok_from_A(A,N): fails+=1
    return dict(nbad=len(M), split_fail=fails, rowsum_fail=rowsum_fail)

def run(nm,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        d=standard_gate(adj,s,n)
        if d is None: continue
        acc['tot']+=d['nbad']; acc['split']+=d['split_fail']; acc['rowsum']+=d['rowsum_fail']

# --- quotient (large blow-up) SPLIT: A_i = P_{part at geodesic-position i} ---
def split_quotient(m, n):
    N=sum(n)
    prods=[(n[i]*n[(i+1)%m],i) for i in range(m)]; pmin,a=min(prods); b=(a+1)%m; nbad=n[a]*n[b]
    def Pi(i):
        if i==a: return F(n[b])
        if i==b: return F(n[a])
        return F(nbad,n[i])
    # geodesic path of bad edge: a -> a-1 -> ... -> b (around cycle avoiding edge a-b). L=m. positions 0..m-1.
    # position 0 = part a, position m-1 = part b, going a, a-1, a-2, ..., b (i.e. parts a, (a-1)%m, ...)
    order=[(a - k) % m for k in range(m)]   # a, a-1, ..., b  (length m, ends at b=(a+1)%m? check)
    # going backward from a by 1 each step for m-1 steps reaches a-(m-1) = a+1 = b (mod m). good.
    A=[Pi(order[i]) for i in range(m)]
    return split_ok_from_A(A,N), sum(A), F(N)

if __name__=="__main__":
    print("=== SPLIT certificate for ROWSUM-O: standard gate + LARGE blow-up quotient ===",flush=True)
    # standard gate
    G11=mycielski(5,Cn(5)); G23=mycielski(*G11); M15=mycielski(7,Cn(7))
    accm={'tot':0,'split':0,'rowsum':0}
    for nm,g in [("Grotzsch11",G11),("MycC7_15",M15)]: run(nm,g[0],g[1],accm)
    print(f"  Mycielskians(11,15): bad-edges={accm['tot']} SPLIT-FAIL={accm['split']} ROWSUM-FAIL={accm['rowsum']}",flush=True)
    accg={'tot':0,'split':0,'rowsum':0}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}",n,E,accg)
    print(f"  glued battery: bad-edges={accg['tot']} SPLIT-FAIL={accg['split']} ROWSUM-FAIL={accg['rowsum']}",flush=True)
    for nnn in (9,10,11):
        outg=subprocess.run([GENG,"-tc",str(nnn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'split':0,'rowsum':0}; ng=0
        for g6 in outg:
            ng+=1
            if nnn==11 and ng>4000: break
            n,E=dec(g6); run(g6,n,E,acc)
        print(f"  census N={nnn}{' (first 4000)' if nnn==11 else ''}: bad-edges={acc['tot']} SPLIT-FAIL={acc['split']} ROWSUM-FAIL={acc['rowsum']}",flush=True)
    # LARGE blow-up quotient sweep (the decisive regime)
    print("--- LARGE blow-up quotient SPLIT sweep ---",flush=True)
    rng=random.Random(31415)
    for m in (5,7,9,11):
        sf=0; rf=0; tot=0; worst=None
        for _ in range(60000):
            n=[rng.choice([1,2,3,5,7,12,30,100,300,700,1500]) for _ in range(m)]
            if sum(n)>4000 or sum(n)<m: continue
            ok,rs,N=split_quotient(m,n)
            tot+=1
            if rs>N: rf+=1
            if not ok: sf+=1
        print(f"  C{m} large blow-ups: tested={tot} SPLIT-FAIL={sf} ROWSUM-FAIL={rf}",flush=True)
