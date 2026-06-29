"""Adversarial stress of (B*) / the descent route: build path+detour+f with CONFIGURABLE chord layouts
(chaining / nested / disjoint / mixed). For each that yields a connected-B max cut (parity) with a
unique-path f and an interval-Hall failure, test the ROBUST descent requirement:
   does SOME single-vertex flip exist that is cut-tight (cutsize preserved), B-connected, and Gamma-DECREASING?
Also report whether a shared-endpoint straddling P-contained chord vertex exists (the (B*) selector).
If a layout fails IH but has NO Gamma-descent flip, the descent route is BROKEN -> print it loudly.
Construction mirrors kchord: path 0..pend, detour ext-vertices 0->pend (forces f=(0,pend) geodesic=path),
edge (0,pend), plus an arbitrary list of chords [(a,b),...] with b-a even >=4 (triangle-free chord)."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def build(pend, chords):
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for (a,b) in chords: E.append((min(a,b),max(a,b)))
    E.append((0,pend))
    n=pend+1+nint
    return n, sorted(set((min(a,b),max(a,b)) for a,b in E))

def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gamma_of(n,adj,s):
    G=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v)
                if d<0: return None
                G+=(d+1)**2
    return G

def test_layout(name,pend,chords,acc):
    n,E=build(pend,chords); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if not tri_free(n,adj):
        acc['skip_tri']+=1; return
    s=[v%2 for v in range(n)]
    # parity must be a connected-B max cut
    mc_size=cutsize(n,adj,s)
    # is parity max? compare to maxcut_all only if n small enough; else use local-opt proxy
    is_max=True
    if n<=22:
        mcs=max(cutsize(n,adj,list(m)) for m in maxcut_all(n,adj))
        is_max=(mc_size==mcs)
    else:
        # local optimality proxy: no single flip improves
        for v in range(n):
            s2=s[:]; s2[v]^=1
            if cutsize(n,adj,s2)>mc_size: is_max=False; break
    if not (is_max and Bconn(n,adj,s)):
        acc['skip_notmax']+=1; return
    G0=gamma_of(n,adj,s)
    st=struct_for_side(n,adj,s)
    if st is None or G0 is None: acc['skip_struct']+=1; return
    M,elld,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        kk=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,kk)
    base=cutsize(n,adj,s)
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        Pcont=set()
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset: Pcont.add((min(g),max(g))); break
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        whole_dem=sum(dvec); whole_cap=sum(c for (_,_,c) in comps)
        # any interval failure?
        failed=False; failI=None
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem>cap: failed=True; failI=(a,b); break
            if failed: break
        if not failed: continue
        acc['failures']+=1
        # ROBUST descent: does SOME single flip lower Gamma (cut-tight + Bconn)?
        found=None
        for v in range(n):
            s2=s[:]; s2[v]^=1
            if cutsize(n,adj,s2)!=base or not Bconn(n,adj,s2): continue
            g2=gamma_of(n,adj,s2)
            if g2 is not None and g2<G0: found=v; break
        # shared-endpoint straddling P-contained chord vertex?
        chain_vtx=None
        for i in range(L):
            x=P_f[i]
            inc=[(min(x,w),max(x,w)) for w in adj[x] if s[w]==s[x] and w in pos and (min(x,w),max(x,w)) in Pcont]
            left=[e for e in inc if (pos[e[0] if e[1]==x else e[1]])<i]
            right=[e for e in inc if (pos[e[0] if e[1]==x else e[1]])>i]
            if left and right: chain_vtx=(i,x); break
        if found is None:
            acc['NO_DESCENT']+=1
            if acc['firstND'] is None: acc['firstND']=(name,chords,f,failI)
        else:
            acc['has_descent']+=1
        if chain_vtx is None: acc['no_chain']+=1
        else: acc['has_chain']+=1
        # is the descent flip a chain vertex?
        if found is not None and chain_vtx is not None and found==chain_vtx[1]: acc['descent_is_chain']+=1

def run():
    acc={'failures':0,'has_descent':0,'NO_DESCENT':0,'has_chain':0,'no_chain':0,'descent_is_chain':0,
         'skip_tri':0,'skip_notmax':0,'skip_struct':0,'firstND':None}
    layouts=[]
    # chaining (original k-chord style), clen=4
    layouts.append(("chain-c4-k3",12,[(0,4),(4,8),(8,12)]))
    layouts.append(("chain-c4-k2",8,[(0,4),(4,8)]))
    # disjoint spans
    layouts.append(("disjoint-c4",12,[(0,4),(8,12)]))
    layouts.append(("disjoint2-c4",16,[(0,4),(6,10),(12,16)]))
    # nested
    layouts.append(("nested-c4",12,[(0,8),(2,6)]))
    layouts.append(("nested2",16,[(0,12),(2,10),(4,8)]))
    # mixed
    layouts.append(("mixed",16,[(0,4),(4,8),(10,14)]))
    layouts.append(("overlap-noshare",12,[(0,6),(4,10)]))
    layouts.append(("chain-c6",18,[(0,6),(6,12),(12,18)]))
    layouts.append(("disjoint-c6",18,[(0,6),(12,18)]))
    layouts.append(("chain-mixed-len",14,[(0,4),(4,10)]))
    layouts.append(("star-share",12,[(0,4),(4,8),(4,10)]))
    for (name,pend,chords) in layouts:
        b0=acc['failures']; nd0=acc['NO_DESCENT']
        test_layout(name,pend,chords,acc)
        print(f"  {name}: chords={chords} -> failures(+{acc['failures']-b0}) NO_DESCENT(+{acc['NO_DESCENT']-nd0})",flush=True)
    print("\n=== chord-variant descent stress ===",flush=True)
    print(f"  total IH-failures={acc['failures']}  has-Gamma-descent={acc['has_descent']}  NO-DESCENT={acc['NO_DESCENT']}",flush=True)
    print(f"  shared-endpoint chain-vertex present={acc['has_chain']}  absent={acc['no_chain']}  (descent==chain-vtx: {acc['descent_is_chain']})",flush=True)
    print(f"  skips: tri={acc['skip_tri']} notmax={acc['skip_notmax']} struct={acc['skip_struct']}",flush=True)
    if acc['firstND']: print(f"  *** NO-DESCENT WITNESS: {acc['firstND']} ***",flush=True)
    print(f"  === {'DESCENT ROUTE BROKEN (IH-failure with no Gamma-descent flip)' if acc['NO_DESCENT'] else 'every IH-failure across diverse chord layouts admits a single-vertex Gamma-descent flip'} ===",flush=True)

if __name__=="__main__": run()
