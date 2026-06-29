"""(B*) MECHANISM lemma test: on a GLOBAL max connected-B cut, do two P-contained bad chords ever
INTERIOR-overlap (open position-intervals (a,b),(c,d) share a point but the chords do NOT merely meet at a
shared endpoint)? Hypothesis: interior-overlap (incl. nesting) of P-contained chords => NOT global max.
[Because load>=2 at a position needs 2 chords covering it; if they may only share endpoints (chain), the
high-load vertex is a bracket junction => (B*).]
For census N<=9 ALL connected-B cuts: for each unique-path f, collect P-contained chords as position
intervals; flag interior-overlap; record whether the cut is global max. Report: interior-overlap on a
GLOBAL MAX cut = COUNTEREXAMPLE to the mechanism. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def interior_overlap(intervals):
    # intervals = list of (p,q) p<q position-intervals. Return True if two INTERIOR-overlap:
    # they share an interior point and are not just endpoint-touching (q1==p2) nor identical.
    for i in range(len(intervals)):
        p1,q1=intervals[i]
        for j in range(i+1,len(intervals)):
            p2,q2=intervals[j]
            lo=max(p1,p2); hi=min(q1,q2)
            if lo<hi:  # overlap of length>=1 (share more than a single endpoint)
                # endpoint-touch is lo==hi (one shared point); lo<hi means they overlap on a segment
                # but allow shared-endpoint chaining: q1==p2 gives lo==hi==q1 (not <). nesting/crossing => lo<hi
                return (p1,q1,p2,q2)
    return None

def check_cut(n,adj,s,name,is_max,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            # P-contained chord: a geodesic that is a subpath of P
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q);
                    if pp[-1]-pp[0]==len(pp)-1:  # contiguous = subpath
                        chords.append((pp[0],pp[-1])); break
        ov=interior_overlap(chords)
        if ov:
            acc['overlap']+=1
            if is_max:
                acc['overlap_on_max']+=1
                if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,chords,ov)
            else:
                acc['overlap_on_nonmax']+=1

def run():
    acc={'overlap':0,'overlap_on_max':0,'overlap_on_nonmax':0,'first':None}
    for nn in range(6,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        o0=acc['overlap']; m0=acc['overlap_on_max']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            mx=cutsize(n,adj,list(maxcut_all(n,adj)[0]))
            for m in range(1<<(n-1)):
                s=[(m>>v)&1 for v in range(n)]
                is_max=(cutsize(n,adj,s)==mx)
                check_cut(n,adj,s,g6,is_max,acc)
        print(f"  census N={nn}: contained-chord interior-overlaps(+{acc['overlap']-o0}) of which ON GLOBAL-MAX(+{acc['overlap_on_max']-m0})",flush=True)
    print(f"\n  total interior-overlaps={acc['overlap']}  on-global-max={acc['overlap_on_max']}  on-nonmax={acc['overlap_on_nonmax']}",flush=True)
    if acc['first']: print(f"  *** interior-overlap ON GLOBAL MAX (counterexample to mechanism): {acc['first']} ***",flush=True)
    print(f"  === {'MECHANISM HOLDS: P-contained chords interior-overlap ONLY on non-max cuts (global-max => chords meet only at endpoints => high-load vtx is a junction)' if acc['overlap_on_max']==0 else 'MECHANISM FALSE: interior-overlap occurs on a global max cut'} ===",flush=True)

if __name__=="__main__": run()
