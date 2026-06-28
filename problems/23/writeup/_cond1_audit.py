"""Audit Codex's GCD-cond1 grounding reduction (block 84) on the EXACT gate.
   H_QQ = L_{omega,QQ} + diag(ground),  ground(v) = (N-T(v)) + omega(v,O)   [standard grounded-Laplacian].
   => H_QQ PD  <=>  every Q omega-component has total ground > 0.   (linear-algebra fact, we verify it.)
   Codex's reduction to SAT-ZMU-CONN needs the hidden equivalences:
     (1) on B-edges: omega(e)>0  <=>  mu(e)>0   (positive cycle-traffic == positive geodesic traffic)
     (2) omega-components on positive-traffic vertices == K/traffic components used by SAT-ZMU-CONN
     (3) ADVERSARIAL: on the glued-island battery + Mycielskians with O nonempty, H_QQ is PD
         (no zero-ground Q omega-component) -- the glued islands killed prior cond1 forms (ZMU/O-K-SUPPORT)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _gcd import a_bar, is_psd_exact, build_H
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free

def omega_dict(adj, side, n):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    omega={}
    for f in M:
        ae=a_bar(ell[f]); Ps=cyc[f]; k=len(Ps)
        ef=frozenset(f); omega[ef]=omega.get(ef,F(0))+ae
        for P in Ps:
            for i in range(len(P)-1):
                e2=frozenset((P[i],P[i+1])); omega[e2]=omega.get(e2,F(0))+ae*F(1,k)
    return M,ell,T,mu,cyc,omega

def audit(adj, side, n):
    r=omega_dict(adj,side,n)
    if r is None: return None
    M,ell,T,mu,cyc,omega=r; N=n
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return dict(skip='O-empty')
    # (1) on B-edges (cut edges, side differ): omega>0 <=> mu>0
    mism=0; nB=0
    Bedges=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v]]
    for (u,v) in Bedges:
        nB+=1
        e=frozenset((u,v)); et=(min(u,v),max(u,v))  # mu is keyed by (u<v) tuples, omega by frozensets
        ow = omega.get(e,F(0))>0
        mw = mu.get(et,F(0))>0
        if ow!=mw: mism+=1
    # ground(v) for v in Q and Q-omega-components
    Qset=set(Q)
    # build omega-graph adjacency among Q (edges with omega>0, both endpoints in Q)
    gadj={v:set() for v in Q}
    for e,w in omega.items():
        if w<=0: continue
        a,b=tuple(e)
        if a in Qset and b in Qset: gadj[a].add(b); gadj[b].add(a)
    # components of Q under omega
    seen=set(); comps=[]
    for v in Q:
        if v in seen: continue
        stack=[v]; comp=[]; seen.add(v)
        while stack:
            x=stack.pop(); comp.append(x)
            for y in gadj[x]:
                if y not in seen: seen.add(y); stack.append(y)
        comps.append(comp)
    # ground(v) = (N-T(v)) + omega(v,O)
    def omega_vO(v):
        s=F(0)
        for u in O:
            s+=omega.get(frozenset((v,u)),F(0))
        return s
    minground=None; zero_comp=0
    for comp in comps:
        g=sum((F(N)-T[v])+omega_vO(v) for v in comp)
        if minground is None or g<minground: minground=g
        if g<=0: zero_comp+=1
    # cross-check H_QQ PD directly (exact)
    H,_,_=build_H(adj,side,n)
    qi={v:i for i,v in enumerate(Q)}
    HQQ=[[H[a][b] for b in Q] for a in Q]
    hqq_pd=is_psd_exact_strict(HQQ,len(Q))
    # (2) omega-components (FULL graph) vs K/traffic components (kcomponents)
    fulladj={v:set() for v in range(n)}
    for e,w in omega.items():
        if w<=0: continue
        a,b=tuple(e); fulladj[a].add(b); fulladj[b].add(a)
    seen2=set(); wcomp=[]
    for v in range(n):
        if v in seen2: continue
        st=[v]; cc=set([v]); seen2.add(v)
        while st:
            x=st.pop()
            for y in fulladj[x]:
                if y not in seen2: seen2.add(y); cc.add(y); st.append(y)
        wcomp.append(frozenset(cc))
    kc,_=kcomponents(n,cyc)
    # compare only on traffic-carrying vertices (positive omega-degree); isolated vtxs are singletons in both
    traffic={v for v in range(n) if fulladj[v]}
    wpart=frozenset(frozenset(c & traffic) for c in wcomp if (c & traffic))
    kpart=frozenset(frozenset(set(c) & traffic) for c in kc.values() if (set(c) & traffic))
    comp_equal = (wpart==kpart)
    return dict(O=len(O),Q=len(Q),nB=nB,omega_mu_mismatch=mism,
                ncomp=len(comps),zero_ground_comps=zero_comp,minground=minground,
                HQQ_PD=hqq_pd, grounding_matches=(zero_comp==0)==hqq_pd, comp_equal=comp_equal)

def is_psd_exact_strict(A,n):
    """PD (strict) test: all pivots > 0 (no zero pivot)."""
    M=[[A[i][j] for j in range(n)] for i in range(n)]
    used=[False]*n
    for _ in range(n):
        piv=-1; best=None
        for i in range(n):
            if used[i]: continue
            if best is None or M[i][i]>best: best=M[i][i]; piv=i
        if piv==-1: break
        d=M[piv][piv]
        if d<=0: return False   # PD requires strictly positive pivot
        used[piv]=True
        for i in range(n):
            if used[i] or M[i][piv]==0: continue
            fac=M[i][piv]/d
            for j in range(n):
                if not used[j]: M[i][j]-=fac*M[piv][j]
    return True

def gmin_cuts_with_O(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    from _h import maxcut_all, Bconn, bdist_restr
    cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
    cand=[]
    for s in cuts:
        Mb=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
        if not Mb: continue
        G=0; ok=True
        for (u,v) in Mb:
            d=bdist_restr(adj,s,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((s,G))
    if not cand: return adj,[]
    gm=min(g for _,g in cand)
    return adj,[s for s,g in cand if g==gm]

def run(nm,n,E):
    adj,cuts=gmin_cuts_with_O(n,E)
    tot=0; mism=0; zg=0; gmismatch=0; nO=0; cne=0
    for s in cuts:
        d=audit(adj,s,n)
        if d is None or d.get('skip'): continue
        tot+=1; nO+=1
        mism+=d['omega_mu_mismatch']; zg+=d['zero_ground_comps']
        if not d['grounding_matches']: gmismatch+=1
        if not d['comp_equal']: cne+=1
    if nO==0: print(f"  {nm} N={n}: (all gamma-min cuts O-empty)"); return
    print(f"  {nm} N={n}: O-cuts={nO} omega!=mu={mism} zero-ground-comp={zg} ground-vs-PD-mismatch={gmismatch} wcomp!=Kcomp={cne}",flush=True)

if __name__=="__main__":
    print("=== cond1 grounding audit (omega/mu support + H_QQ PD on glued battery) ===",flush=True)
    # Mycielskians
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    # GLUED-ISLAND BATTERY (the adversarial blind spot)
    print("--- glued-island battery ---",flush=True)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}{br}",n,E)
    # census N=7..9
    for nn in range(7,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot=0; mism=0; zg=0; gmismatch=0; cne=0
        for g6 in outg:
            n,E=dec(g6)
            adj,cuts=gmin_cuts_with_O(n,E)
            for s in cuts:
                d=audit(adj,s,n)
                if d is None or d.get('skip'): continue
                tot+=1; mism+=d['omega_mu_mismatch']; zg+=d['zero_ground_comps']
                if not d['grounding_matches']: gmismatch+=1
                if not d['comp_equal']: cne+=1
        print(f"  census N={nn}: O-cuts={tot} omega!=mu={mism} zero-ground-comp={zg} ground-vs-PD-mismatch={gmismatch} wcomp!=Kcomp={cne}",flush=True)
