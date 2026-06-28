"""Test the GENERAL component bridge (enables induction reducing SPEC to the irreducible case):
   for EVERY proper positive K/omega component C (any load, |C|<n, carries a bad edge), is the induced cut
   on G[C] a gamma-min connected-B MAXIMUM cut of G[C]?  If yes for all proper components, then by K being
   block-diagonal over K-components (rho(K)=max_i rho(K_{C_i})) and the IH (SPEC for G[C], |C|<n => rho(K_C)
   <=|C|<=n), SPEC reduces to the IRREDUCIBLE case (single K-component spanning all positive-load vertices).
   Independent impl, exact. (Codex's CLCB was the CONSTANT-LOAD restriction of this.)"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _clcb_audit import induced, maxcut_value, cut_value, gmin_connected_maxcuts, gamma_of_cut

def gmins(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
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

def check(n,E):
    adj,cuts=gmins(n,E)
    proper=0; maxbad=0; gminbad=0; bconnbad=0; constload=0
    for s in cuts:
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,mu,cyc=st
        kc,_=kcomponents(n,cyc)
        for root,C in kc.items():
            if len(C)<2 or len(C)>=n: continue
            if not any(f[0] in C and f[1] in C for f in M): continue  # positive
            proper+=1
            if len({T[v] for v in C})==1: constload+=1
            m, adjC, idx, Cs = induced(adj, C)
            sC=[s[v] for v in Cs]
            # (i) induced cut is a MAX cut of G[C]
            if cut_value(m,adjC,sC)!=maxcut_value(m,adjC): maxbad+=1; continue
            # (iii) B|_C connected
            if not Bconn(m,adjC,sC): bconnbad+=1; continue
            # (ii) gamma_C is the gamma-min among connected-B max cuts of G[C]
            _,gmC,_=gmin_connected_maxcuts(m,adjC)
            gC=gamma_of_cut(m,adjC,sC)
            if gC is None or gmC is None or gC[0]!=gmC: gminbad+=1
    return proper, maxbad, bconnbad, gminbad, constload

def run(nm,n,E,report=True):
    p,mb,bb,gb,cl=check(n,E)
    if report:
        print(f"  {nm} N={n}: proper-pos-comps={p} (constload={cl}) NOT-maxcut={mb} B|C-disconn={bb} NOT-gammin={gb}",flush=True)
    return p,mb,bb,gb

if __name__=="__main__":
    print("=== GENERAL component bridge (all proper positive comps): induced cut = gamma-min conn maxcut of G[C]? ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    print("--- glued battery ---",flush=True)
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5)); P=0;MB=0;BB=0;GB=0
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                p,mb,bb,gb=run(f"isl{iN}+gad{gN}{br}",n,E,report=False); P+=p;MB+=mb;BB+=bb;GB+=gb
    print(f"  glued battery: proper-pos-comps={P} NOT-maxcut={MB} B|C-disconn={BB} NOT-gammin={GB}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        P=0;MB=0;BB=0;GB=0
        for g6 in outg:
            n,E=dec(g6); p,mb,bb,gb=run(g6,n,E,report=False); P+=p;MB+=mb;BB+=bb;GB+=gb
        print(f"  census N={nn}: proper-pos-comps={P} NOT-maxcut={MB} B|C-disconn={BB} NOT-gammin={GB}",flush=True)
