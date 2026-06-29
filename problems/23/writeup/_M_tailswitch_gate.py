"""Exact-test Codex block-187 TAIL-SWITCH proof of lemma (M).
For unique-path f, two P-contained bad rows g,h with position intervals [p1,q1],[p2,q2] (p1<=p2) that
INTERIOR-overlap (p2 < r:=min(q1,q2)): claim one of
  S_L = {x_0,...,x_{p2}},   S_R = {x_r,...,x_{L-1}}
strictly increases cutsize (delta_M(S) > delta_B(S)). => interior-overlap impossible on a max cut => (M).
Battery: census N<=9 ALL connected-B cuts + N=26 path+detour chord layouts (nested/crossing/chaining) +
glued islands + Mycielskians (gamma-min). Report overlaps caught/missed; first miss with both tail gains."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def boundary_gain(n,adj,s,Sset):
    dB=0; dM=0
    for u in Sset:
        for w in adj[u]:
            if w in Sset: continue
            if s[u]!=s[w]: dB+=1
            else: dM+=1
    return dM-dB  # >0 => flipping S increases cut
def boundary_dB(n,adj,s,Sset):
    return sum(1 for u in Sset for w in adj[u] if w not in Sset and s[u]!=s[w])
def build_pd(pend, chords):
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for (a,b) in chords: E.append((min(a,b),max(a,b)))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))
def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def check_cut(n,adj,s,name,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
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
                r=min(b1,b2)
                if a2<r:  # interior-overlap
                    acc['ov']+=1
                    SL=set(P_f[0:a2+1]); SR=set(P_f[r:L])
                    gL=boundary_gain(n,adj,s,SL); gR=boundary_gain(n,adj,s,SR)
                    if gL>0 or gR>0: acc['caught']+=1
                    else:
                        acc['miss']+=1
                        if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,(a1,b1),(a2,b2),gL,gR)
                    ssum=gL+gR
                    if ssum<acc['minsum']: acc['minsum']=ssum; acc['minsumrec']=(name,f,(a1,b1),(a2,b2),gL,gR)
                    if ssum<2: acc['sumlt2']+=1
                    # block-189 positive-extra: non-path cut-edge crossings of S_L,S_R = (dB-1) each (path edge is the 1)
                    extra=(boundary_dB(n,adj,s,SL)-1)+(boundary_dB(n,adj,s,SR)-1)
                    if extra>acc['maxextra']: acc['maxextra']=extra; acc['maxextrarec']=(name,f,(a1,b1),(a2,b2),extra)
                    if extra>2: acc['extragt2']+=1

def run():
    acc={'ov':0,'caught':0,'miss':0,'first':None,'minsum':10**9,'minsumrec':None,'sumlt2':0,'maxextra':-10,'maxextrarec':None,'extragt2':0}
    # census N<=9 ALL connected-B cuts
    for nn in range(6,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        o0=acc['ov']; m0=acc['miss']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for m in range(1<<(n-1)):
                s=[(m>>v)&1 for v in range(n)]
                check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} all connB: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    # N=26 path+detour layouts (parity cut): nested/crossing/chaining
    for name,pend,chords in [("nested",12,[(0,8),(2,6)]),("crossing",12,[(0,6),(2,8)]),
                             ("nested2",16,[(0,12),(2,10),(4,8)]),("chain",12,[(0,4),(4,8),(8,12)]),
                             ("nested-c6",18,[(0,12),(3,9)])]:
        n,E=build_pd(pend,chords); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not tri_free(n,adj): print(f"  {name} n={n}: not tri-free",flush=True); continue
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,[v%2 for v in range(n)],name,acc)
        print(f"  {name} N={n} parity: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    # glued + Mycielskians (gamma-min)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                        ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); o0=acc['ov']; m0=acc['miss']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    print(f"\n  TOTAL interior-overlaps={acc['ov']} CAUGHT(some tail switch gains cut)={acc['caught']} MISS={acc['miss']}",flush=True)
    print(f"  block-188 gain(S_L)+gain(S_R)>=2: violations(sum<2)={acc['sumlt2']}; MIN SUM={acc['minsum']} at {acc['minsumrec']}",flush=True)
    print(f"  block-189 positive-extra (non-path cut crossings of S_L,S_R) <=2: viol(extra>2)={acc['extragt2']}; MAX EXTRA={acc['maxextra']} at {acc['maxextrarec']}",flush=True)
    if acc['first']: print(f"  first MISS: {acc['first']}",flush=True)
    print(f"  === {'TAIL-SWITCH proof of (M) FAILS (miss)' if acc['miss'] else 'TAIL-SWITCH proves (M): every P-contained interior-overlap has a cut-increasing tail switch => impossible on max cut'} ===",flush=True)

if __name__=="__main__": run()
