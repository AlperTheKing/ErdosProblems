"""Independent exact-stress of Codex's |O|=1 STAR-O1 sublemma (block 90), the cleanest cond3 sub-target.
   For a gamma-min connected-B max cut with O={o} a singleton (T(o)>N, all others T<=N):
     a_w = omega({o,w}),  R_w = N-T(w),  LB1(o) = sum_{w: a_w>0, R_w>0} a_w*R_w/(a_w+R_w).
   STAR-O1:  LB1(o) >= T(o)-N.   (Rayleigh: C_eff(o<->ground) >= LB1; (CAP)|O1 <=> C_eff >= T(o)-N.)
   Exact Fraction. Reports min ratio LB1/(T(o)-N) + witness; any fail -> term list."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _cond1_audit import omega_dict
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _superphi import blow

def star_o1(adj, side, n):
    """Return list of (ok, ratio, T(o)-N, terms) for each singleton-O occurrence; None if not applicable."""
    r=omega_dict(adj,side,n)
    if r is None: return None
    M,ell,T,mu,cyc,omega=r; N=n
    O=[v for v in range(n) if T[v]>N]
    if len(O)!=1: return None
    o=O[0]; Do=T[o]-N
    if Do<=0: return None
    LB1=F(0); terms=[]
    for w in range(n):
        if w==o: continue
        aw=omega.get(frozenset((o,w)),F(0))
        Rw=F(N)-T[w]
        if aw>0 and Rw>0:
            t=aw*Rw/(aw+Rw); LB1+=t; terms.append((w,aw,Rw,t))
    ok = LB1>=Do
    ratio = (LB1/Do) if Do!=0 else None
    return (ok, ratio, Do, LB1, o, terms)

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

def run(nm,n,E,report=True,acc=None):
    adj,cuts=gmins(n,E)
    tot=0; fails=0; minr=None; wit=None; firstfail=None
    for s in cuts:
        d=star_o1(adj,s,n)
        if d is None: continue
        ok,ratio,Do,LB1,o,terms=d; tot+=1
        if not ok:
            fails+=1
            if firstfail is None: firstfail=(nm,s,o,Do,LB1,terms)
        if ratio is not None and (minr is None or ratio<minr): minr=ratio; wit=(nm,o)
    if acc is not None:
        acc['tot']+=tot; acc['fails']+=fails
        if minr is not None and (acc['minr'] is None or minr<acc['minr']): acc['minr']=minr; acc['wit']=wit
        if firstfail and acc['firstfail'] is None: acc['firstfail']=firstfail
    if report:
        rr=float(minr) if minr is not None else None
        print(f"  {nm} N={n}: |O|=1 cuts={tot} STAR-O1-FAILS={fails} min-ratio={rr} wit={wit}",flush=True)
    return tot,fails,minr,firstfail

if __name__=="__main__":
    print("=== |O|=1 STAR-O1: LB1(o) >= T(o)-N (independent, exact) ===",flush=True)
    cur=(5,Cn(5))
    for nm in ["Grotzsch=N11","Myc2(C5)=N23"]:
        cur=mycielski(*cur); run(nm,cur[0],cur[1])
    cur=(7,Cn(7)); cur=mycielski(*cur); run("Myc(C7)=N15",cur[0],cur[1])
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("G?bF`w",3)]:
        nn,EE=blow(g6,t); run(f"{g6}[{t}]",nn,EE)
    print("--- glued battery ---",flush=True)
    acc={'tot':0,'fails':0,'minr':None,'wit':None,'firstfail':None}
    g15=mycielski(7,Cn(7)); gr=mycielski(5,Cn(5))
    for iN,iE in [(5,Cn(5)),(7,Cn(7))]:
        for gN,gE in [g15,gr]:
            for br in [[(0,0)],[(0,1)],[(0,2)],[(0,0),(2,3)]]:
                if any(j>=gN for _,j in br): continue
                n,E=union_disjoint((iN,iE),(gN,gE))
                for (i,j) in br: E=E+[(i,iN+j)]
                if n>22 or not is_triangle_free(n,E): continue
                run(f"isl{iN}+gad{gN}{br}",n,E,report=False,acc=acc)
    print(f"  glued battery: |O|=1 cuts={acc['tot']} STAR-O1-FAILS={acc['fails']} min-ratio={float(acc['minr']) if acc['minr'] else None}",flush=True)
    if acc['firstfail']: print(f"    FIRSTFAIL {acc['firstfail'][:5]}")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        acc={'tot':0,'fails':0,'minr':None,'wit':None,'firstfail':None}
        for g6 in outg:
            n,E=dec(g6); run(g6,n,E,report=False,acc=acc)
        ff=f" FIRSTFAIL {acc['firstfail'][:5]}" if acc['firstfail'] else ""
        print(f"  census N={nn}: |O|=1 cuts={acc['tot']} STAR-O1-FAILS={acc['fails']} min-ratio={float(acc['minr']) if acc['minr'] else None} wit={acc['wit']}{ff}",flush=True)
