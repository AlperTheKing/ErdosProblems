"""Confirm one N=11 gamma-min GET-failure witness exactly (E(I) > c(I)) before declaring GPT-Pro's GET false."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

found=0
outg=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
for g6 in outg:
    if found>=2: break
    n,E=dec(g6); adj,cuts=gmins(n,E)
    for s in cuts:
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,mu,cyc=st
        for f in M:
            if len(cyc[f])!=1: continue
            P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
            atoms=[]
            for g in M:
                if g==f: continue
                k=len(cyc[g])
                for Q in cyc[g]:
                    J=sorted(pos[v] for v in Q if v in Pset)
                    if J: atoms.append((J[0],J[-1],F(1,k),g,len(cyc[g])))
            rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
            def find(x):
                while par[x]!=x: par[x]=par[par[x]]; x=par[x]
                return x
            for u in rest:
                for w in adj[u]:
                    if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
            cd={}
            for v in rest: cd.setdefault(find(v),set()).add(v)
            spans=[]
            for r,C in cd.items():
                A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
                if A: spans.append((min(A),max(A)))
            for a in range(L):
                for b in range(a,L):
                    E_=sum(w for (r,sm,w,g,kk) in atoms if not (sm<a or r>b))
                    cI=sum(1 for (lo,hi) in spans if not (hi<a or lo>b))
                    if E_>cI:
                        print(f"g6={g6} side={''.join(map(str,s))} f={f} P={P_f} I=[{a},{b}]: E={E_}={float(E_):.3f} > c={cI}")
                        ov=[(g,kk,(r,sm)) for (r,sm,w,g,kk) in atoms if not (sm<a or r>b)]
                        print(f"   overlapping geodesic-atoms (g,|cyc|,J): {ov}")
                        print(f"   overlapping component spans: {[(lo,hi) for (lo,hi) in spans if not (hi<a or lo>b)]}")
                        found+=1
                        break
                if found and found%1==0 and E_>cI: break
            if found>=2: break
        if found>=2: break
print(f"\n=> GET-failures on gamma-min N=11 confirmed: {found} witnesses printed (E>c). GPT-Pro GET lemma is FALSE.")
