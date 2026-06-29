"""Exact-test Codex block-184 B* max-cut half:
For a connected-B cut, unique-path f, interval-Hall failure where NO vertex of P is a bracket-hub
(shared endpoint of two straddling P-contained bad rows), there exists a PATH-INTERVAL S={x_a..x_b}
whose flip strictly increases cutsize: delta_M(S) > delta_B(S)  (boundary bad-edges > boundary cut-edges).
=> no-bracket overload cannot occur on a GLOBAL max cut.
Battery: k-chord corpus (bracket control), chord-variant artifacts (nested/disjoint/single = no-bracket
non-max source), census N<=9 ALL connected-B cuts. Report no-bracket failures with NO cut-gain interval."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))
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

def has_cutgain_pathinterval(n,adj,s,P_f):
    L=len(P_f)
    for a in range(L):
        for b in range(a,L):
            Sset=set(P_f[a:b+1])
            dB=0; dM=0
            for u in Sset:
                for w in adj[u]:
                    if w in Sset: continue
                    if s[u]!=s[w]: dB+=1
                    else: dM+=1
            if dM>dB: return (a,b,dM,dB)
    return None

def check_cut(n,adj,s,name,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        k=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,k)
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
        # any interval failure?
        failed=None
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem>cap: failed=(a,b); break
            if failed: break
        if not failed: continue
        acc['fail']+=1
        # bracket hub present?
        hub=False
        for i in range(L):
            x=P_f[i]
            inc=[(min(x,w),max(x,w)) for w in adj[x] if s[w]==s[x] and w in pos and (min(x,w),max(x,w)) in Pcont]
            left=[e for e in inc if pos[e[0] if e[1]==x else e[1]]<i]
            right=[e for e in inc if pos[e[0] if e[1]==x else e[1]]>i]
            if left and right: hub=True; break
        if hub:
            acc['hub']+=1; return
        acc['nohub']+=1
        cg=has_cutgain_pathinterval(n,adj,s,P_f)
        if cg is None:
            acc['nohub_nocutgain']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,failed)
        else:
            acc['nohub_cutgain']+=1

def run():
    acc={'fail':0,'hub':0,'nohub':0,'nohub_cutgain':0,'nohub_nocutgain':0,'first':None}
    # k-chord (bracket control)
    for clen in (4,6):
        for k in (3,6):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            check_cut(n,adj,[v%2 for v in range(n)],f"kchord-k{k}c{clen}",acc)
    # chord-variant artifacts (no-bracket, non-max): test parity + a few random connected-B cuts
    variants=[("single-(2,10)",12,[(2,10)]),("single-(0,8)",12,[(0,8)]),
              ("disjoint",12,[(0,4),(8,12)]),("nested",12,[(0,8),(2,6)]),
              ("nested2",16,[(0,12),(2,10),(4,8)]),("overlap",12,[(0,6),(4,10)])]
    for name,pend,chords in variants:
        n,E=build_pd(pend,chords); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not tri_free(n,adj): continue
        check_cut(n,adj,[v%2 for v in range(n)],name,acc)
    print("  [k-chord + variant artifacts done]",flush=True)
    # census N<=9 ALL connected-B cuts
    for nn in range(5,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        f0=acc['fail']; nh0=acc['nohub']; ncg0=acc['nohub_nocutgain']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for m in range(1<<(n-1)):
                s=[(m>>v)&1 for v in range(n)]
                check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} ALL connB cuts: failures(+{acc['fail']-f0}) nohub(+{acc['nohub']-nh0}) nohub-NO-cutgain(+{acc['nohub_nocutgain']-ncg0})",flush=True)
    print(f"\n  total interval-Hall failures={acc['fail']}  bracket-hub={acc['hub']}  no-hub={acc['nohub']}",flush=True)
    print(f"  no-hub WITH cut-gain path-interval={acc['nohub_cutgain']}  no-hub WITHOUT cut-gain={acc['nohub_nocutgain']}",flush=True)
    if acc['first']: print(f"  *** COUNTEREXAMPLE (no-hub, no cut-gain): {acc['first']} ***",flush=True)
    print(f"  === {'COUNTEREXAMPLE to Codex B* max-cut lemma' if acc['nohub_nocutgain'] else 'Codex B* max-cut half HOLDS: every no-bracket interval-Hall failure has a cut-increasing path-interval flip (=> not global max)'} ===",flush=True)

if __name__=="__main__": run()
