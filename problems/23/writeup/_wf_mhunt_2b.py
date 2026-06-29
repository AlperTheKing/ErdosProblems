"""Focused follow-up to _wf_mhunt_2: characterize the 2420 near-misses (battery C: Grotzsch+pins)
and try to PROMOTE a near-miss overlap-cut to GLOBAL max by adding more idle B-pins / tuning the
pendant so the rest of the graph's max cut cannot exceed the overlap cut.

For each Grotzsch+pin graph: among connected-B cuts that HAVE an interior-overlap, record the gap
(truemax - cutsize). The closer to 0 the better. gap==0 would be a counterexample. We sweep many
pin layouts (multiple pendants, longer chains, even-length chains that flip parity) to minimize the gap.
EXACT integer arithmetic. Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import itertools
from _h import Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, is_triangle_free

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:
        if a!=b: adj[a].add(b); adj[b].add(a)
    return adj

def overlaps_on_cut(n,adj,s):
    if not Bconn(n,adj,s): return None
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    res=[]
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1: chords.append((pp[0],pp[-1])); break
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                a1,b1=chords[i]; a2,b2=chords[j]
                if a1>a2: a1,b1,a2,b2=a2,b2,a1,b1
                if a2<min(b1,b2): res.append((f,tuple(P_f),(a1,b1),(a2,b2)))
    return res

def analyze(name,n,E,acc,NCAP=21):
    if n-1>NCAP: return
    if not is_triangle_free(n,E): return
    adj=adj_of(n,E)
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    acc['graphs']+=1
    best=-1; bycut={}
    for m in range(1<<(n-1)):
        c=0
        for u,v in edges:
            if ((m>>u)^(m>>v))&1: c+=1
        if c>best: best=c
        bycut.setdefault(c,[]).append(m)
    mx=best
    # find all connected-B cuts (any size) with an interior-overlap; record min gap
    for c,masks in bycut.items():
        for m in masks:
            s=[(m>>u)&1 for u in range(n)]
            ov=overlaps_on_cut(n,adj,s)
            if ov:
                gap=mx-c
                if gap<acc['min_gap']:
                    acc['min_gap']=gap
                    acc['min_gap_rec']=dict(name=name,n=n,cut=c,truemax=mx,gap=gap,
                                            f=ov[0][0],c1=ov[0][2],c2=ov[0][3],
                                            side=''.join(map(str,s)))
                if gap==0:
                    acc['gmax']+=1
                    acc['witnesses'].append(dict(name=name,n=n,E=list(E),side=list(s),
                                                 f=ov[0][0],P=ov[0][1],c1=ov[0][2],c2=ov[0][3],
                                                 cutsize=c,truemax=mx))

def add_pendants(nE, pins):
    n,E=nE; E=list(E)
    for (anchor,clen) in pins:
        prev=anchor
        for _ in range(clen):
            E.append((prev,n)); prev=n; n+=1
    return n,E

if __name__=="__main__":
    print("=== battery C-deep: Grotzsch + multi-pin, minimize (truemax - overlap-cut) ===",flush=True)
    grot=mycielski(5,Cn(5))  # N=11
    acc=dict(graphs=0,gmax=0,min_gap=10**9,min_gap_rec=None,witnesses=[])
    # single pins, chains 1..5
    for a in range(grot[0]):
        for cl in range(1,6):
            n,E=add_pendants(grot,[(a,cl)])
            analyze(f"Grot+pin@{a}len{cl}",n,E,acc)
    print(f"  single-pin sweep: graphs={acc['graphs']} min_gap={acc['min_gap']} rec={acc['min_gap_rec']}",flush=True)
    # double pins on two distinct anchors (idle B-pins on both sides)
    cfgs=0
    for a in range(grot[0]):
        for b in range(a+1,grot[0]):
            for cla in (1,2,3):
                for clb in (1,2,3):
                    n,E=add_pendants(grot,[(a,cla),(b,clb)])
                    if n-1<=21:
                        analyze(f"Grot+pin@{a}len{cla}+@{b}len{clb}",n,E,acc); cfgs+=1
    print(f"  double-pin sweep: configs={cfgs} graphs={acc['graphs']} gmax={acc['gmax']} min_gap={acc['min_gap']} rec={acc['min_gap_rec']}",flush=True)
    # triple pins (more idle mass) -- N grows, cap chains short
    cfgs=0
    for combo in itertools.combinations(range(grot[0]),3):
        for cls in itertools.product((1,2),repeat=3):
            n,E=add_pendants(grot,[(combo[i],cls[i]) for i in range(3)])
            if n-1<=21:
                analyze(f"Grot+3pin{combo}{cls}",n,E,acc); cfgs+=1
    print(f"  triple-pin sweep: configs={cfgs} graphs={acc['graphs']} gmax={acc['gmax']} min_gap={acc['min_gap']} rec={acc['min_gap_rec']}",flush=True)

    print(f"\n  === min_gap over all = {acc['min_gap']} (0 => COUNTEREXAMPLE); gmax-overlaps={acc['gmax']} ===",flush=True)
    if acc['witnesses']:
        for w in acc['witnesses'][:5]:
            print(f"    CE: {w['name']} N={w['n']} f={w['f']} c1={w['c1']} c2={w['c2']} cut={w['cutsize']}==max={w['truemax']} side={''.join(map(str,w['side']))} E={w['E']}",flush=True)
    else:
        print("  NO gap==0 overlap -- lemma (M) holds; closest near-miss above.",flush=True)
