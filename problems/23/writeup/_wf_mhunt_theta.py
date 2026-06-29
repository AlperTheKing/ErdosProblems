"""M-HUNT theta/multi-odd-cycle family: triangle-free graphs with MANY bad-edge geodesics able to
lie on a common P (so P-contained chords genuinely occur), verified GLOBAL max via maxcut_all (N<=24).

Builders:
  (T) generalized theta: two hubs s,t joined by k internally-disjoint paths of given lengths (parities
      chosen so several s-t paths are odd => bad edges on a cut), + optional extra rungs.
  (L) a long odd cycle C_{2g+1} PLUS several even-length 'shortcut' chord-paths (a-w-b via fresh w)
      that on the natural cut become bad edges whose geodesics are contiguous arcs of the cycle -> chords.
A hit = connected-B GLOBAL max cut with P-contained interior-overlap. Sub-max overlaps = near-miss.
EXACT. Run from .../problems/23/writeup."""
import itertools
from _h import maxcut_all
from _wf_mhunt_1 import find_overlaps_on_cut, cutsize
from _wf_mhunt_census import adj_of

def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def theta(path_lens):
    """Two hubs 0,1 joined by len(path_lens) internally-disjoint paths; lengths = #edges (>=2 to avoid
    parallel edges/triangles). Returns n,E."""
    E=[]; nxt=2; s,t=0,1
    for L in path_lens:
        if L==1:
            E.append((s,t)); continue
        prev=s
        for k in range(L-1):
            w=nxt; nxt+=1; E.append((min(prev,w),max(prev,w))); prev=w
        E.append((min(prev,t),max(prev,t)))
    return nxt, sorted(set(E))

def cycle_with_shortcuts(g, shorts):
    """Odd cycle C_{2g+1} on 0..2g, plus shortcuts (a,b) realized as a-w-b via fresh w (keeps tri-free).
    Returns n,E."""
    L=2*g+1; E=[(i,(i+1)%L) for i in range(L)]; E=[(min(a,b),max(a,b)) for a,b in E]
    nxt=L
    for (a,b) in shorts:
        w=nxt; nxt+=1; E.append((min(a,w),max(a,w))); E.append((min(b,w),max(b,w)))
    return nxt, sorted(set(E))

def scan(n,E,name,acc,Ncap=20):
    if n>Ncap: return
    adj=adj_of(n,E)
    if not tri_free(n,adj): return
    cuts=maxcut_all(n,adj); tm=cutsize(n,adj,cuts[0])
    for m in range(1<<(n-1)):
        s=[(m>>v)&1 for v in range(n)]
        c=cutsize(n,adj,s)
        st,ov=find_overlaps_on_cut(n,adj,s)
        if st!='ok' or not ov: continue
        if c==tm:
            acc['glob']+=1
            if acc['witness'] is None:
                acc['witness']=dict(name=name,n=n,side=s[:],truemax=tm,
                                    edges=sorted((min(a,b),max(a,b)) for a,b in E),
                                    rec=ov[0],allrecs=ov)
        else:
            acc['sub']+=1

if __name__=="__main__":
    print("=== M-HUNT theta/multi-odd-cycle family (exact global-max, N<=24) ===",flush=True)
    acc={'glob':0,'sub':0,'witness':None}
    tested=0
    # (T) generalized thetas: 3-4 paths, mixed parities, lengths 2..7
    plans=[]
    for k in (3,4):
        for lens in itertools.product(range(2,8),repeat=k):
            if sum(L-1 for L in lens)+2>20: continue
            if k==4 and sum(lens)>18: continue
            plans.append(("theta",tuple(sorted(lens))))
    plans=list({p for p in plans})
    print(f"  theta plans: {len(plans)}",flush=True)
    for _,lens in plans:
        n,E=theta(list(lens)); scan(n,E,f"theta{lens}",acc); tested+=1
        if acc['witness']: break
        if tested%200==0: print(f"    ...theta tested {tested} glob={acc['glob']} sub={acc['sub']}",flush=True)
    print(f"  theta done: tested={tested} overlap-on-GLOBAL={acc['glob']} overlap-on-SUB(nearmiss)={acc['sub']}",flush=True)

    # (L) odd cycle + even-gap shortcuts (these create P-contained chords on the cycle's long-arc geodesics)
    if acc['witness'] is None:
        t2=0
        for g in (4,5,6,7,8):  # cycle length 9..17
            L=2*g+1
            evens=[(a,b) for a in range(L) for b in range(a+2,L) if (b-a)%2==0]
            for combo in itertools.combinations(evens, 2):
                n,E=cycle_with_shortcuts(g,list(combo))
                if n>20: continue
                scan(n,E,f"C{L}+sc{combo}",acc); t2+=1
                if acc['witness']: break
            if acc['witness']: break
            for combo in itertools.combinations(evens, 3):
                if sum(b-a for a,b in combo)>14: continue
                n,E=cycle_with_shortcuts(g,list(combo))
                if n>20: continue
                scan(n,E,f"C{L}+sc{combo}",acc); t2+=1
                if acc['witness']: break
            if acc['witness']: break
            print(f"    C{L}: cumulative shortcut-tested={t2} glob={acc['glob']} sub={acc['sub']}",flush=True)
        print(f"  cycle+shortcut done: tested={t2}",flush=True)

    print(f"\n  TOTAL overlap-on-GLOBAL={acc['glob']}  overlap-on-SUB(nearmiss)={acc['sub']}",flush=True)
    if acc['witness']:
        w=acc['witness']
        print(f"  *** WITNESS {w['name']} N={w['n']} truemax={w['truemax']}",flush=True)
        print(f"  side={w['side']}",flush=True)
        print(f"  edges={w['edges']}",flush=True)
        print(f"  rec f={w['rec']['f']} P={w['rec']['P']} c1={w['rec']['c1']} c2={w['rec']['c2']}",flush=True)
    else:
        print("  NO verified-global-max P-contained interior-overlap (theta/cycle+shortcut family).",flush=True)
