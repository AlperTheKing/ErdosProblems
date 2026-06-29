"""EXACT Gamma-decomposition of the singleton hub-flip descent (Part B mechanism).
For each k-chord interval-Hall failure, max-load hub x*, compute Gamma(s)->Gamma(s') under flipping x*:
  Gamma = sum_{bad e} ell_s(e)^2,  ell_s(e)=bdist_restr(e)+1 (#vertices in shortest alternating path).
Classify the change exactly:
  ADDED bad edges (cut->bad at x*): the 2 path edges (x*,x_{i*-1}),(x*,x_{i*+1}).
  REMOVED bad edges (bad->cut at x*): the 2 incident bracket bad rows.
  RETAINED bad edges whose ell changed: ell_s'(e) vs ell_s(e).
Decompose: INCIDENT-EXCHANGE = sum(added ell'^2) - sum(removed ell^2);
           RETAINED-SHIFT     = sum_{retained} (ell_s'(e)^2 - ell_s(e)^2).
Total dGamma = INCIDENT-EXCHANGE + RETAINED-SHIFT. Report per-family: is INCIDENT-EXCHANGE==0 (neutral)?
is RETAINED-SHIFT<0 (strict)? which retained edge(s) shorten, by how much, and the odd-girth context.
Exact Fraction/int."""
from fractions import Fraction as F
from collections import deque
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def badset(n,adj,s): return set((u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v])
def ell(adj,s,e):
    d=bdist_restr(adj,s,e[0],e[1]); return None if d<0 else d+1

def analyze_failure(n,adj,s,P_f,i_star,acc,f=None):
    s2=s[:]; s2[P_f[i_star]]^=1
    if cutsize(n,adj,s2)!=cutsize(n,adj,s) or not Bconn(n,adj,s2):
        acc['notcuttight']+=1; return
    B0=badset(n,adj,s); B1=badset(n,adj,s2)
    added=B1-B0; removed=B0-B1; retained=B0&B1
    # exact ell on each side
    def G_of(bads, side):
        tot=0; lens={}
        for e in bads:
            L=ell(adj,side,e)
            if L is None: return None,None
            tot+=L*L; lens[e]=L
        return tot, lens
    G0,len0=G_of(B0,s); G1,len1=G_of(B1,s2)
    if G0 is None or G1 is None: acc['infell']+=1; return
    dG=G1-G0
    inc_exchange=sum(len1[e]**2 for e in added)-sum(len0[e]**2 for e in removed)
    ret_shift=sum(len1[e]**2-len0[e]**2 for e in retained)
    shortened=[(e,len0[e],len1[e]) for e in retained if len1[e]<len0[e]]
    lengthened=[(e,len0[e],len1[e]) for e in retained if len1[e]>len0[e]]
    acc['n']+=1
    acc['dG_neg'] += 1 if dG<0 else 0
    acc['incEx_zero'] += 1 if inc_exchange==0 else 0
    acc['retShift_neg'] += 1 if ret_shift<0 else 0
    acc['n_lengthened'] += len(lengthened)
    acc['n_shortened'] += len(shortened)
    # multiset of ell preserved across incident exchange?
    if sorted(len1[e] for e in added)==sorted(len0[e] for e in removed): acc['incEx_multiset_eq']+=1
    # is the (a) shortened edge set exactly {f}?  (b) does f shorten?
    if f is not None:
        fkey=(min(f),max(f)); short_keys={(min(e),max(e)) for (e,a,b) in shortened}
        if short_keys=={fkey}: acc['short_is_just_f']+=1
        if fkey in short_keys: acc['f_shortens']+=1
    # record a representative
    if acc['rep'] is None or (dG<0 and len(shortened)>=1 and acc['rep'][0]>=0):
        acc['rep']=(dG, inc_exchange, ret_shift, len(added), len(removed),
                    [(e,a,b) for (e,a,b) in shortened], [(e,a,b) for (e,a,b) in lengthened],
                    sorted(added), sorted(removed))
    # invariant checks
    if inc_exchange!=0: acc['incEx_nonzero_ex']=acc.get('incEx_nonzero_ex') or (i_star,inc_exchange,sorted(added),sorted(removed),len0,len1)
    if dG>=0: acc['dG_nonneg_ex']=acc.get('dG_nonneg_ex') or (i_star,dG)

def run():
    print("=== EXACT descent Gamma-decomposition (Part B mechanism) ===",flush=True)
    acc={'n':0,'dG_neg':0,'incEx_zero':0,'retShift_neg':0,'rep':None,'notcuttight':0,'infell':0,
         'n_lengthened':0,'n_shortened':0,'incEx_multiset_eq':0,'short_is_just_f':0,'f_shortens':0}
    from fractions import Fraction as F
    for clen in (4,5,6,7):
        for k in (3,4,6):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            st=struct_for_side(n,adj,s)
            if st is None: continue
            M,elld,T,mu,cyc=st
            S=[F(0)]*n
            for g in M:
                kk=len(cyc[g])
                for P in cyc[g]:
                    for v in P: S[v]+=F(1,kk)
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
                comps=[]
                for r,C in cd.items():
                    A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
                    if A: comps.append((min(A),max(A),len(C)))
                seen=set()
                for a in range(L):
                    for b in range(a,L):
                        dem=sum(dvec[i] for i in range(a,b+1))
                        cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                        if dem<=cap: continue
                        m=max(dvec[i] for i in range(a,b+1))
                        for i in range(a,b+1):
                            if dvec[i]==m and i not in seen:
                                seen.add(i); analyze_failure(n,adj,s,P_f,i,acc,f=f)
    print(f"  hub-flip cases analyzed = {acc['n']}  (not-cut-tight skipped={acc['notcuttight']}, inf-ell={acc['infell']})",flush=True)
    print(f"  dGamma<0 (strict descent): {acc['dG_neg']}/{acc['n']}",flush=True)
    print(f"  INCIDENT-EXCHANGE == 0 (neutral): {acc['incEx_zero']}/{acc['n']}",flush=True)
    print(f"  RETAINED-SHIFT < 0 (strict source): {acc['retShift_neg']}/{acc['n']}",flush=True)
    print(f"  total LENGTHENED retained bad edges across all cases = {acc['n_lengthened']} (want 0); total shortened = {acc['n_shortened']}",flush=True)
    print(f"  INCIDENT-EXCHANGE ell-MULTISET preserved (added ells == removed ells): {acc['incEx_multiset_eq']}/{acc['n']}",flush=True)
    print(f"  shortened-set == {{f}} exactly: {acc['short_is_just_f']}/{acc['n']};  f itself shortens: {acc['f_shortens']}/{acc['n']}",flush=True)
    if acc.get('incEx_nonzero_ex'): print(f"  *** INCIDENT-EXCHANGE NONZERO witness: {acc['incEx_nonzero_ex']}",flush=True)
    if acc.get('dG_nonneg_ex'): print(f"  *** dGamma>=0 witness: {acc['dG_nonneg_ex']}",flush=True)
    r=acc['rep']
    if r:
        print(f"  representative: dGamma={r[0]} = incEx({r[1]}) + retShift({r[2]}); added={r[3]} removed={r[4]}",flush=True)
        print(f"    SHORTENED retained bad edges (e, ell_s, ell_s'): {r[5]}",flush=True)
        print(f"    LENGTHENED retained bad edges (e, ell_s, ell_s'): {r[6]}",flush=True)
        print(f"    added(path-edge) bad: {r[7]}  removed(bracket) bad: {r[8]}",flush=True)
    verdict = (acc['dG_neg']==acc['n'] and acc['incEx_zero']==acc['n'] and acc['retShift_neg']==acc['n'])
    print(f"  === {'CLEAN: every hub flip is cut-tight, INCIDENT-EXCHANGE neutral, RETAINED-SHIFT strictly negative => dGamma<0' if verdict else 'MIXED: see witnesses (decomposition not uniformly neutral+strict)'} ===",flush=True)

if __name__=="__main__": run()
