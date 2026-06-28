"""Independent exact-test of Codex's CONSTANT-LOAD-COMPONENT-BRIDGE (block 85).
   For a gamma-min connected-B max cut, take a PROPER positive K/omega component C (carries bad edges, |C|<n)
   with T constant on C. Claim: the induced cut side_C on G[C] is itself a gamma-min connected-B MAX cut of G[C]:
     (i)  side_C is a maximum cut of G[C];
     (ii) among connected-B max cuts of G[C], side_C minimizes Gamma_C;
     (iii) [needed for induction] B restricted to C is connected.
   If true, induction Gamma_C<=|C|^2 + identity Gamma_C=sum_{v in C}T(v)=lambda|C| forces lambda<=|C|; the
   dangerous case lambda=N with |C|<N is impossible => GCD-cond1.  INDEPENDENT impl (not Codex's file)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def gamma_of_cut(n, adj, s):
    """Gamma = sum ell(f)^2 over same-side edges with finite B-geodesic; None if some bad edge has no B-path."""
    Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
    G=0
    for (u,v) in Mb:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G, len(Mb)

def gmin_connected_maxcuts(n, adj):
    """All connected-B max cuts, and the gamma-min value + the gamma-min cuts."""
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        g=gamma_of_cut(n,adj,s)
        if g is None: continue
        cand.append((s,g[0]))
    if not cand: return None,None,[]
    gm=min(g for _,g in cand)
    return cuts, gm, [s for s,g in cand if g==gm]

def induced(adj, C):
    """induced subgraph on vertex set C (sorted), relabeled 0..|C|-1; return (m, adjC, idx)."""
    Cs=sorted(C); idx={v:i for i,v in enumerate(Cs)}; m=len(Cs)
    adjC=[set() for _ in range(m)]
    for v in Cs:
        for u in adj[v]:
            if u in idx: adjC[idx[v]].add(idx[u])
    return m, adjC, idx, Cs

def maxcut_value(m, adjC):
    best=-1
    for s in maxcut_all(m, adjC):  # maxcut_all already returns maximum cuts; value = #cut edges
        cutedges=sum(1 for u in range(m) for v in adjC[u] if v>u and s[u]!=s[v])
        if cutedges>best: best=cutedges
    return best

def cut_value(m, adjC, s):
    return sum(1 for u in range(m) for v in adjC[u] if v>u and s[u]!=s[v])

def check_graph(nm, n, E, report=True):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    _,gm,gmins=gmin_connected_maxcuts(n,adj)
    if not gmins:
        if report: print(f"  {nm} N={n}: no connected-B max cut with bad edges")
        return 0,0,0
    ncomp=0; bad=0; tested=0
    for s in gmins:
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,mu,cyc=st
        kc,_=kcomponents(n,cyc)
        # bad-edge endpoints per component (positive component = contains a bad edge)
        for root,C in kc.items():
            if len(C)<2 or len(C)>=n: continue          # proper, nontrivial
            badin=[f for f in M if f[0] in C and f[1] in C]
            if not badin: continue                        # positive = carries bad edges
            Tvals={T[v] for v in C}
            if len(Tvals)!=1: continue                    # T constant on C
            lam=next(iter(Tvals))
            ncomp+=1; tested+=1
            # induced G[C]
            m, adjC, idx, Cs = induced(adj, C)
            sC=[s[v] for v in Cs]
            # (iii) B restricted to C connected
            biii = Bconn(m, adjC, sC)
            # (i) side_C is a maximum cut of G[C]
            mcv = maxcut_value(m, adjC)
            ci = (cut_value(m, adjC, sC)==mcv)
            # (ii) among connected-B max cuts of G[C], side_C minimizes Gamma_C
            _, gmC, _ = gmin_connected_maxcuts(m, adjC)
            gC = gamma_of_cut(m, adjC, sC)
            cii = (ci and biii and gC is not None and gmC is not None and gC[0]==gmC)
            # also verify the load identity Gamma_C == sum_{v in C} T(v) == lam*|C|
            sumT = sum(T[v] for v in C)
            ident = (gC is not None and gC[0]==sumT==lam*len(C))
            ok = (ci and cii and biii and ident)
            if not ok:
                bad+=1
                if report and bad<=3:
                    print(f"    !! {nm} comp|C|={len(C)} lam={lam} N={n}: (i)max={ci} (ii)gammin={cii} (iii)Bconn={biii} ident={ident} Gamma_C={gC[0] if gC else None} sumT={sumT}")
    if report:
        print(f"  {nm} N={n}: const-load proper positive comps tested={tested} BRIDGE-FAILS={bad}",flush=True)
    return tested,bad,0

if __name__=="__main__":
    print("=== CONSTANT-LOAD-COMPONENT-BRIDGE exact audit (independent) ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); check_graph(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); check_graph("Myc(C7)=N15",cur[0],cur[1])
    print("--- glued-island battery ---",flush=True)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); gtot=0; gbad=0
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                t,b,_=check_graph(f"isl{iN}+gad{gN}{br}",n,E,report=False); gtot+=t; gbad+=b
    print(f"  glued battery: const-load comps tested={gtot} BRIDGE-FAILS={gbad}",flush=True)
    # FULL census N=7..11 all gamma-min cuts
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; bad=0
        for g6 in outg:
            n,E=dec(g6)
            t,b,_=check_graph(g6,n,E,report=False); tot+=t; bad+=b
        print(f"  census N={nn}: const-load proper positive comps tested={tot} BRIDGE-FAILS={bad}",flush=True)
