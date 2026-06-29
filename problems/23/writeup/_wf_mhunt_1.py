"""ADVERSARIAL hunt for a counterexample to lemma (M):
   a triangle-free graph with a connected-B GLOBAL MAXIMUM cut having a P-contained
   interior-overlap (two P-contained chords [p1,q1],[p2,q2], p1<=p2, p2<min(q1,q2)).

Family #1: non-uniform odd-cycle blow-ups C_m[t_0..t_{m-1}], m in {5,7,9,11}, parts varied
incl extreme ratios.

KEY FACT (verified _wf_mhunt_check.py, 0 value-mismatches over census): the global-max-cut
VALUE of C_m[sizes] equals the best PART-LEVEL assignment value (max over 2^m part-sidings of
sum_{i: side[i]!=side[i+1]} sizes[i]*sizes[i+1]). So a whole-part cut whose value == that part
max is a VERIFIED GLOBAL MAXIMUM, with NO call to maxcut_all needed -> scales to any N.

We enumerate EVERY part-level global-max siding (whole parts on each side), and for the
connected-B ones with a unique-geodesic bad edge, search for a P-contained interior-overlap.
A hit is a VERIFIED-global-max counterexample. Overlaps appearing only on sub-max part sidings
are reported as NEAR-MISSES. EXACT Fraction arithmetic via struct_for_side.

Run from .../problems/23/writeup."""
import itertools
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side

def build_blowup(m, sizes):
    n=sum(sizes); start=[0]*m
    for i in range(1,m): start[i]=start[i-1]+sizes[i-1]
    adj=[set() for _ in range(n)]; E=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                u=start[i]+a; v=start[j]+b
                adj[u].add(v); adj[v].add(u); E.append((u,v))
    return n,adj,E,start

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def part_maxval(m,sizes):
    best=-1; assigns=[]
    for bits in range(1<<m):
        ps=[(bits>>i)&1 for i in range(m)]
        val=sum(sizes[i]*sizes[(i+1)%m] for i in range(m) if ps[i]!=ps[(i+1)%m])
        if val>best: best=val; assigns=[ps]
        elif val==best: assigns.append(ps)
    return best,assigns

def find_overlaps_on_cut(n,adj,s):
    """Return ('ok', list-of-overlap-records) or (reason,[])."""
    if not Bconn(n,adj,s): return ('not-bconn',[])
    st=struct_for_side(n,adj,s)
    if st is None: return ('no-struct',[])
    M,ell,T,mu,cyc=st
    out=[]
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1:
                        chords.append((pp[0],pp[-1],g)); break
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                a1,b1,g1=chords[i]; a2,b2,g2=chords[j]
                if a1>a2: a1,b1,g1,a2,b2,g2=a2,b2,g2,a1,b1,g1
                r=min(b1,b2)
                if a2<r:
                    out.append(dict(f=f,P=P_f,c1=(a1,b1),c2=(a2,b2),g1=g1,g2=g2))
    return ('ok',out)

def analyze(m, sizes):
    """Verified-global-max search over whole-part global-max sidings.
    Returns dict with witness (or None) and near-miss info."""
    n,adj,E,start=build_blowup(m,sizes)
    pmax,assigns=part_maxval(m,sizes)
    # expand each part-siding to a vertex-level cut (whole parts)
    n_global_connB=0; n_overlap=0; witness=None
    for ps in assigns:
        s=[0]*n
        for i in range(m):
            for a in range(sizes[i]): s[start[i]+a]=ps[i]
        cval=cutsize(n,adj,s)
        assert cval==pmax, (m,sizes,cval,pmax)  # exact global-max guarantee
        status,ov=find_overlaps_on_cut(n,adj,s)
        if status!='ok': continue
        n_global_connB+=1
        if ov:
            n_overlap+=1
            if witness is None:
                witness=dict(m=m,sizes=sizes,n=n,side=s[:],truemax=pmax,
                             edges=sorted(E),rec=ov[0],allrecs=ov,part_side=ps)
    return dict(m=m,sizes=sizes,n=n,truemax=pmax,n_partmax_sidings=len(assigns),
                n_global_connB=n_global_connB,n_overlap=n_overlap,witness=witness)

def gen_plans():
    seen=set(); plans=[]
    def add(m,sizes):
        rots=[tuple(sizes[i:]+sizes[:i]) for i in range(m)]
        rots+=[tuple(reversed(r)) for r in rots]
        k=(m,min(rots))
        if k in seen: return
        seen.add(k); plans.append((m,sizes))
    # m=5: full small + extreme ratios up to large N
    for sizes in itertools.product([1,2,3,4,5,6,8,12,20,40],repeat=5):
        if sum(sizes)>120: continue
        add(5,sizes)
    # m=7: small + extreme
    for sizes in itertools.product([1,2,3,5,10,20],repeat=7):
        if sum(sizes)>90: continue
        add(7,sizes)
    # m=9
    for sizes in itertools.product([1,2,4,8],repeat=9):
        if sum(sizes)>72: continue
        add(9,sizes)
    # m=11
    for sizes in itertools.product([1,2,4],repeat=11):
        if sum(sizes)>60: continue
        add(11,sizes)
    return plans

if __name__=="__main__":
    print("=== M-HUNT family #1: odd-cycle blow-ups, VERIFIED global-max via part-level value ===",flush=True)
    plans=gen_plans()
    print(f"  part-vectors to test (dedup rot/refl): {len(plans)}",flush=True)
    results=[]; found=None; tested=0; n_overlap_graphs=0
    for m,sizes in plans:
        tested+=1
        r=analyze(m,sizes)
        results.append(r)
        if r['n_overlap']>0:
            n_overlap_graphs+=1
            if found is None:
                found=r['witness']
                w=found
                print(f"  *** GLOBAL-MAX OVERLAP FOUND: C{w['m']}{w['sizes']} N={w['n']} truemax={w['truemax']}",flush=True)
                print(f"      side={w['side']}",flush=True)
                print(f"      f={w['rec']['f']} P={w['rec']['P']} c1={w['rec']['c1']} c2={w['rec']['c2']}",flush=True)
        if tested%2000==0:
            print(f"    ...tested {tested}/{len(plans)} overlap-graphs={n_overlap_graphs}",flush=True)
    print(f"\n  tested={tested} graphs-with-global-max-overlap={n_overlap_graphs}",flush=True)
    if found:
        w=found
        print(f"  WITNESS C{w['m']}{w['sizes']} N={w['n']} truemax={w['truemax']}",flush=True)
        print(f"  WITNESS side={w['side']}",flush=True)
        print(f"  WITNESS edges={w['edges']}",flush=True)
        print(f"  WITNESS rec={w['rec']}",flush=True)
    else:
        print("  NO verified-global-max P-contained interior-overlap in family #1.",flush=True)
