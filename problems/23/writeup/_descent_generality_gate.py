"""GENERALITY test for Part B (singleton Gamma-descent), beyond the synthetic k-chord family.
Over ALL connected-B max cuts of every triangle-free census graph (N<=11), find every unique-path
interval-Hall failure demand(I)>cap(I), and test the descent lemma:
  STRONG: EVERY max-load vertex x* (argmax d_i in I) has a cut-tight (cut unchanged), B-connected,
          Gamma-DECREASING singleton flip.
  Also record hub structure B: internal, dB=2, dM=2, B-nbrs = path nbrs, bad-nbrs P-contained.
If STRONG holds on every census max-cut failure, the descent is not a k-chord artifact. Report first
obstruction (failure where some max-load vertex does NOT descend) and structure stats. Exact Fraction.
NOTE: tests NON-gamma-min max cuts too (that is the point -- gamma-min cuts do not fail, so the failure
mechanism can only be stressed on cuts that DO fail)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

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
def descends(n,adj,s,x,base_cut,G0):
    s2=s[:]; s2[x]^=1
    if cutsize(n,adj,s2)!=base_cut or not Bconn(n,adj,s2): return False
    g2=gamma_of(n,adj,s2)
    return g2 is not None and g2<G0

def check_cut(n,adj,s,name,acc):
    base_cut=cutsize(n,adj,s); G0=gamma_of(n,adj,s)
    if G0 is None: return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        Ps=cyc[g]; k=len(Ps)
        for P in Ps:
            for v in P: S[v]+=F(1,k)
    Pcontained=set()
    for g in M:
        if any(set(Q)<=set(cyc[f][0]) for f in M if len(cyc[f])==1 for Q in cyc[g]): pass
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        Pcont=set()
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset: Pcont.add(g); break
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
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                m=max(dvec[i] for i in range(a,b+1))
                H=[i for i in range(a,b+1) if dvec[i]==m]
                desc=[descends(n,adj,s,P_f[i],base_cut,G0) for i in H]
                if not all(desc):
                    acc['strongfail']+=1
                    if acc['first'] is None:
                        acc['first']=(name,''.join(map(str,s)),f,(a,b),str(m),[P_f[i] for i in H],desc)
                if not any(desc):
                    acc['weakfail']+=1
                # hub structure on max-load vertices
                for i in H:
                    x=P_f[i]; acc['hub']+=1
                    dB=sum(1 for w in adj[x] if s[w]!=s[x]); dM=sum(1 for w in adj[x] if s[w]==s[x])
                    internal=0<i<L-1
                    bnb=set(w for w in adj[x] if s[w]!=s[x])
                    pathnb={P_f[i-1],P_f[i+1]} if internal else set()
                    mnb=[(min(x,w),max(x,w)) for w in adj[x] if s[w]==s[x]]
                    mn_contained=all(e in Pcont for e in mnb)
                    if internal and dB==2 and dM==2 and bnb==pathnb and mn_contained: acc['Bok']+=1
                    else:
                        acc['Bother']+=1
                        if acc['firstB'] is None:
                            acc['firstB']=(name,f,i,internal,dB,dM,bnb==pathnb,len(mnb),mn_contained)

if __name__=="__main__":
    import sys
    NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 11
    print(f"=== Part-B GENERALITY gate: descent on ALL connected-B max cuts of census N<={NMAX} (exact) ===",flush=True)
    acc={'fail':0,'strongfail':0,'weakfail':0,'hub':0,'Bok':0,'Bother':0,'first':None,'firstB':None,'cuts':0}
    for nn in range(5,NMAX+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        f0=acc['fail']; sf0=acc['strongfail']; c0=acc['cuts']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for s in maxcut_all(n,adj):
                if not Bconn(n,adj,s): continue
                acc['cuts']+=1
                check_cut(n,adj,list(s),g6,acc)
        print(f"  N={nn}: connB-maxcuts={acc['cuts']-c0} interval-Hall-failures={acc['fail']-f0} STRONG-fail={acc['strongfail']-sf0}",flush=True)
    print(f"\n  TOTAL connB-maxcuts={acc['cuts']} failures={acc['fail']} STRONG-fail={acc['strongfail']} WEAK-fail={acc['weakfail']}",flush=True)
    print(f"  hub-checks={acc['hub']} B-struct-OK={acc['Bok']} B-struct-OTHER={acc['Bother']}",flush=True)
    if acc['firstB']: print(f"  first non-(dB=dM=2) hub: {acc['firstB']}",flush=True)
    print(f"  === {'DESCENT OBSTRUCTION: '+str(acc['first']) if acc['first'] else 'STRONG descent holds on EVERY census max-cut interval-Hall failure (not a k-chord artifact)'} ===",flush=True)
