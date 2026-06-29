"""Exact-gate Codex block-179 SPARE-UNIT lemma: for unique bad row f, path P, every interval I with
D_noncont(I)>0 we require cap(I) - D_noncont(I) >= 1  (i.e. D_noncont(I)+1 <= cap(I)).
D_noncont(I) = sum over g!=f NOT P-contained of sum_{i in I} p_g(x_i). cap(I)=sum_{C: span hits I}|C|.
Battery: k-chord non-gamma parity + census N<=11 gamma-min + glued islands + STANDALONE iterated
Mycielskians (Grotzsch N=11, Myc(Grotzsch) N=23 = the standing gate that killed k2/ZMU). Exact Fraction.
Reports tested intervals with Dnc>0, GLOBAL MIN SLACK, and first spare-violation (slack<1) if any."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        noncont=[]
        for g in M:
            if g==f: continue
            contained = any(set(Q)<=Pset for Q in cyc[g])
            if not contained: noncont.append(g)
        nc_at=[F(0)]*L
        for g in noncont:
            d=pf[g]
            for v,pv in d.items():
                if v in Pset: nc_at[pos[v]]+=pv
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
        for a in range(L):
            for b in range(a,L):
                Dnc=sum(nc_at[i] for i in range(a,b+1))
                if Dnc<=0: continue
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                slack=F(cap)-Dnc
                acc['ints']+=1
                if acc['minslack'] is None or slack<acc['minslack']:
                    acc['minslack']=slack; acc['minrec']=(name,''.join(map(str,s)),f,(a,b),str(Dnc),cap)
                if slack<1:
                    acc['viol']+=1
                    if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,(a,b),str(Dnc),cap,str(slack))
                if slack==1:
                    acc['slack1']+=1
                    if L!=5:
                        acc['slack1_notC5']+=1
                        if acc['firstNotC5'] is None: acc['firstNotC5']=(name,''.join(map(str,s)),f,(a,b),L,str(Dnc),cap)
                # block 182: length-sensitive reserve cap - Dnc >= ell(f)-4 = L-4
                residual=F(cap)-Dnc-(L-4)
                if acc['minresid'] is None or residual<acc['minresid']:
                    acc['minresid']=residual; acc['minresidrec']=(name,f,(a,b),L,str(Dnc),cap)
                if residual<0:
                    acc['lenviol']+=1
                    if acc['firstlen'] is None: acc['firstlen']=(name,''.join(map(str,s)),f,(a,b),L,str(Dnc),cap,str(residual))

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

if __name__=="__main__":
    print("=== SPARE-UNIT lemma gate (block 179): Dnc>0 => cap - Dnc >= 1, exact ===",flush=True)
    acc={'ints':0,'viol':0,'first':None,'minslack':None,'minrec':None,'slack1':0,'slack1_notC5':0,'firstNotC5':None,
         'minresid':None,'minresidrec':None,'lenviol':0,'firstlen':None}
    for clen in (4,6):
        for k in (3,6,9):
            n,E=kchord(k,clen); s=[v%2 for v in range(n)]; i0=acc['ints']; v0=acc['viol']
            check_cut(n,adj_of(n,E),s,f"k{k}c{clen}-parity",acc)
            print(f"  kchord k={k} clen={clen} N={n} parity: intervals(Dnc>0)={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        i0=acc['ints']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} gamma-min: intervals(Dnc>0)={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    glued=[("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
           ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    for name,(nn,E) in glued:
        adj,cuts=gmins(nn,E); i0=acc['ints']; v0=acc['viol']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gamma-min: intervals(Dnc>0)={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    # STANDING GATE: iterated Mycielskians (Grotzsch N=11, Myc(Grotzsch) N=23)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); i0=acc['ints']; v0=acc['viol']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gamma-min ({len(cuts)} cuts): intervals(Dnc>0)={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL intervals(Dnc>0)={acc['ints']} SPARE-VIOL(slack<1)={acc['viol']}",flush=True)
    print(f"  GLOBAL MIN SLACK = {float(acc['minslack']) if acc['minslack'] is not None else 'na'} at {acc['minrec']}",flush=True)
    print(f"  SLACK==1 intervals = {acc['slack1']}; of those with |P_f|!=5 (ell(f)!=5) = {acc['slack1_notC5']}",flush=True)
    if acc['firstNotC5']: print(f"  first slack=1 non-C5: {acc['firstNotC5']}",flush=True)
    print(f"  === EQ-CLASS (block181): {'COUNTEREXAMPLE slack=1 with ell!=5' if acc['slack1_notC5'] else 'slack=1 => ell(f)=5 (C5 boundary) HOLDS'} ===",flush=True)
    print(f"  LENGTH-SENSITIVE (block182) cap-Dnc>=ell-4: LEN-VIOL={acc['lenviol']}; MIN RESIDUAL={float(acc['minresid']) if acc['minresid'] is not None else 'na'} at {acc['minresidrec']}",flush=True)
    if acc['firstlen']: print(f"  first length-violation: {acc['firstlen']}",flush=True)
    print(f"  === LEN-SENS (block182): {'VIOLATION' if acc['lenviol'] else 'cap-Dnc >= ell(f)-4 HOLDS (reserve=ell-4)'} ===",flush=True)
    print(f"  === {'SPARE-VIOLATION: '+str(acc['first']) if acc['first'] else 'SPARE-UNIT HOLDS: every noncontained-overrun interval leaves >=1 unit capacity spare'} ===",flush=True)
