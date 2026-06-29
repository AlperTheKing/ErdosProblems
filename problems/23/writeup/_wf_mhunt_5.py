"""Family #5 adversarial hunt for a counterexample to LEMMA (M).
Exhaustive census extension N=10,11,12 (geng -tc, triangle-free).
For each graph: exact maxcut_all (GLOBAL max cuts only), keep connected-B cuts,
for each unique-geodesic bad edge f build P, find all P-contained chords, check
interior-overlap. A counterexample = an interior-overlap on a VERIFIED GLOBAL-max cut.

maxcut_all returns ONLY global-maximum cuts (it tracks `best`), so every overlap
found here is on a true global max cut -> it WOULD count as a counterexample.
We also separately scan ALL cuts (not just max) to count NEAR-MISSES (overlaps on
non-global-max connected-B cuts) for honesty.

EXACT integer/Fraction arithmetic; no floats in any pass/fail decision."""
import sys, subprocess
from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side

def cutsize(n,adj,s):
    return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def chords_overlaps(n,adj,s):
    """Return list of (f,P,chord_i,chord_j) interior-overlaps on connected-B cut s.
    Uses struct_for_side: cyc[f]=B-geodesics; P-contained chord = a bad edge g!=f
    with some geodesic that is a contiguous subpath of P (consecutive positions)."""
    if not Bconn(n,adj,s): return []
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    out=[]
    for f in M:
        if len(cyc[f])!=1: continue   # unique-geodesic only
        P_f=cyc[f][0]; L=len(P_f)
        pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1:  # contiguous on P
                        chords.append((pp[0],pp[-1],g)); break
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                p1,q1,gi=chords[i]; p2,q2,gj=chords[j]
                if p1>p2: p1,q1,gi,p2,q2,gj=p2,q2,gj,p1,q1,gi
                # interior-overlap: p2 < min(q1,q2)  (share more than one position)
                if p2 < min(q1,q2):
                    out.append((f,tuple(P_f),(p1,q1,gi),(p2,q2,gj)))
    return out

def scan_graph(g6, do_near=True):
    """Return (n_globalmax_overlaps_list, near_miss_count).
    global-max overlaps are the real counterexamples."""
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    # exact global max cuts (maxcut_all reuses the per-cut sweep already)
    best=-1; maxcuts=[]; allcuts=[]
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    for m in range(1<<(n-1)):
        s=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if s[u]!=s[v])
        allcuts.append((c,s))
        if c>best: best=c; maxcuts=[s]
        elif c==best: maxcuts.append(s)
    truemax=best
    gm_over=[]
    for s in maxcuts:
        ovs=chords_overlaps(n,adj,s)
        for ov in ovs:
            gm_over.append((g6,''.join(map(str,s)),truemax,ov))
    near=0
    if do_near:
        for c,s in allcuts:
            if c==truemax: continue
            if chords_overlaps(n,adj,s): near+=1
    return gm_over, near, truemax

def run(nmin,nmax,near_max_n=11):
    grand_gm=[]; grand_near=0; total_graphs=0
    for nn in range(nmin,nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        ng=len(outg); total_graphs+=ng
        do_near=(nn<=near_max_n)
        gm_here=0; near_here=0; first=None
        for idx,g6 in enumerate(outg):
            gm,near,_=scan_graph(g6,do_near)
            if gm:
                gm_here+=len(gm)
                if first is None: first=gm[0]
            near_here+=near
            if (idx & 0x3FF)==0:
                print(f"    N={nn} {idx}/{ng} ... gm_over={gm_here} near={near_here}",flush=True)
        grand_gm.extend([] if gm_here==0 else [first])
        grand_near+=near_here
        print(f"  census N={nn}: graphs={ng} GLOBAL-MAX overlaps={gm_here} (FIRST={first}) near-misses={near_here}",flush=True)
    print(f"\nTOTAL graphs scanned N={nmin}..{nmax}: {total_graphs}",flush=True)
    print(f"GLOBAL-MAX interior-overlaps (COUNTEREXAMPLES): {sum(1 for x in grand_gm if x)} first-per-N={grand_gm}",flush=True)
    print(f"near-misses (overlap on non-global-max connected-B cut): {grand_near}",flush=True)
    if any(grand_gm):
        print("!!! COUNTEREXAMPLE TO LEMMA (M) FOUND !!!",flush=True)
    else:
        print("=== NO counterexample: lemma (M) holds on all global-max connected-B cuts in census ===",flush=True)

if __name__=="__main__":
    a=int(sys.argv[1]) if len(sys.argv)>1 else 10
    b=int(sys.argv[2]) if len(sys.argv)>2 else 12
    run(a,b)
