"""Family #5 FAST global-max-only hunter for lemma (M), census N=12 (and beyond).
Gray-code incremental max-cut sweep (exact, integer) to find ALL global-max cuts,
then run the P-contained interior-overlap test (struct_for_side) ONLY on those.
This is the genuine counterexample test: every cut tested for overlaps is a VERIFIED
exact global maximum cut. Near-miss counting is omitted here (done exhaustively at
N<=11 in _wf_mhunt_5.py). EXACT integer arithmetic for the cut sizes."""
import sys, subprocess
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def chords_overlaps(n,adj,s):
    if not Bconn(n,adj,s): return []
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    out=[]
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f)
        pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
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
                p1,q1,gi=chords[i]; p2,q2,gj=chords[j]
                if p1>p2: p1,q1,gi,p2,q2,gj=p2,q2,gj,p1,q1,gi
                if p2 < min(q1,q2):
                    out.append((f,tuple(P_f),(p1,q1,gi),(p2,q2,gj)))
    return out

def maxcuts_fast(n,nbr):
    """Clean: Smask bit u = side1 membership of vertex u, vertex0 fixed 0.
    Iterate s over odd-free space via gray code on bits 1..n-1."""
    free=n-1
    full=1<<free
    # current cut value, maintained incrementally
    cut=0
    Smask=0  # all side0
    best=0; maxmasks=[0]
    prev=0
    for k in range(1, full):
        g=k ^ (k>>1)
        diff=g ^ prev
        b=diff.bit_length()-1
        v=b+1
        prev=g
        # flip vertex v in Smask; update cut by (neighbors now-crossing - neighbors now-same)
        # before flip: count neighbors of v on opposite side = crossing contributed by v
        nb=nbr[v]
        # neighbors on side1 (Smask) and side0
        same_side_before = nb & (Smask if (Smask>>v)&1 else ~Smask)
        # simpler: compute crossing edges from v before and after
        side_v = (Smask>>v)&1
        opp_mask = (~Smask) if side_v else Smask
        cross_before = bin(nb & opp_mask & ((1<<n)-1)).count("1")
        # flip
        Smask ^= (1<<v)
        side_v2 = (Smask>>v)&1
        opp_mask2 = (~Smask) if side_v2 else Smask
        cross_after = bin(nb & opp_mask2 & ((1<<n)-1)).count("1")
        cut += (cross_after - cross_before)
        if cut>best: best=cut; maxmasks=[Smask]
        elif cut==best: maxmasks.append(Smask)
    sides=[[(m>>u)&1 for u in range(n)] for m in maxmasks]
    return best, sides

def scan_graph(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    nbr=[0]*n
    for a,b in E:
        adj[a].add(b); adj[b].add(a); nbr[a]|=(1<<b); nbr[b]|=(1<<a)
    best,maxsides=maxcuts_fast(n,nbr)
    gm_over=[]
    for s in maxsides:
        ovs=chords_overlaps(n,adj,s)
        for ov in ovs:
            gm_over.append((g6,''.join(map(str,s)),best,ov))
    return gm_over

def run(nn):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    ng=len(outg); gm_here=0; first=None
    for idx,g6 in enumerate(outg):
        gm=scan_graph(g6)
        if gm:
            gm_here+=len(gm)
            if first is None: first=gm[0]; print("  !!! GM-OVERLAP:",first,flush=True)
        if (idx & 0x3FFF)==0:
            print(f"    N={nn} {idx}/{ng} gm_over={gm_here}",flush=True)
    print(f"  census N={nn}: graphs={ng} GLOBAL-MAX interior-overlaps={gm_here} FIRST={first}",flush=True)
    if gm_here: print("!!! COUNTEREXAMPLE TO LEMMA (M) FOUND !!!",flush=True)
    else: print(f"=== N={nn}: NO counterexample; lemma (M) holds on all global-max connected-B cuts ===",flush=True)

if __name__=="__main__":
    run(int(sys.argv[1]))
