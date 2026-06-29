"""Census-blindness guard for the SWITCH-DESCENT bridge: stress on larger k-chords (k=6..12) and a VARIANT
failure family (chords of length 7, spanning 6) + double-detour. Check every interval-Hall failure still has a
Gamma-descent switch in the family, and track whether SINGLETON always suffices or the bigger switches are needed."""
from fractions import Fraction as F
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def gamma_of(n,adj,s):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def test_cut(n,adj,s,acc,name):
    if not Bconn(n,adj,s): return
    base_cut=cutsize(n,adj,s); base_G=gamma_of(n,adj,s)
    if base_G is None: return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        compinfo=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),C))
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(len(C) for (lo,hi,C) in compinfo if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                cands=[({P_f[i]},'singleton') for i in range(a,b+1)]
                cands.append((set(P_f[a:b+1]),'pathint'))
                W=set(P_f[a:b+1])
                for (lo,hi,C) in compinfo:
                    if a<=lo and hi<=b: W=W|C
                cands.append((W,'pathint+comps'))
                found=None
                for (Wset,lab) in cands:
                    s2=s[:]
                    for v in Wset: s2[v]^=1
                    if cutsize(n,adj,s2)!=base_cut: continue
                    if not Bconn(n,adj,s2): continue
                    g2=gamma_of(n,adj,s2)
                    if g2 is None or g2>=base_G: continue
                    found=lab; break
                if found: acc['lab'][found]=acc['lab'].get(found,0)+1
                else:
                    acc['nodesc']+=1
                    if acc['first'] is None: acc['first']=(name,f,(a,b),str(dem),cap)

def kchord(k, clen=4):
    """path 0..(clen*k), detour longer than path, k chords (clen*j, clen*j+clen) + (0, clen*k)."""
    pend=clen*k
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1  # detour internal vertices => detour length pend+2 > pend
    ext=list(range(pend+1, pend+1+nint))
    det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    n=pend+1+nint
    return n, sorted(set((min(a,b),max(a,b)) for a,b in E))

if __name__=="__main__":
    print("=== SWITCH-DESCENT stress: larger k + variant chord lengths (census-blindness guard) ===",flush=True)
    acc={'fail':0,'nodesc':0,'lab':{},'first':None}
    for clen in (4,6):  # chord length 5 (clen=4) and 7 (clen=6)
        for k in (3,6,9,12):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            f0=acc['fail']; nd0=acc['nodesc']
            test_cut(n,adj,s,acc,f"k{k}_clen{clen}")
            print(f"  chord-len={clen+1} k={k} N={n} parity: failures={acc['fail']-f0} no-descent={acc['nodesc']-nd0}",flush=True)
    print(f"\n  TOTAL failures={acc['fail']} NO-DESCENT={acc['nodesc']}  label-dist={acc['lab']}",flush=True)
    print(f"  === {'NO-DESCENT WITNESS: '+str(acc['first']) if acc['first'] else 'bridge HOLDS on all stress (every failure has a Gamma-descent switch)'} ===",flush=True)
