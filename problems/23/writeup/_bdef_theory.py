"""THEORY exploration for BOUNDARY-DEFICIT lemma (Claude's leg).
Goal: prove or obstruct  deficit(C) = N|C| - mass(C) >= dB(C)  for K-component C disjoint from O.

KEY IDENTITIES we test exactly (Fraction):
 (M) mass(C) = sum_{v in C} T(v) = sum_{f in F_C} ell(f)^2 = Gamma_C,
     where F_C = {bad edges f : supp(p_f) subseteq C}.  (K-component is a union of geodesic supports.)
 So boundary-deficit  <=>  Gamma_C + dB(C) <= N|C|   for C disjoint from O.

Also explore relationship to ROWSUM-O:  for every bad edge f, sum_v p_f(v) S(v) <= N, S(v)=sum_g p_g(v).
And local relations between dB(C), |C|, the B-edges, and the geodesic structure.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact
from _superphi import blow

def build(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    supp=[]  # supp[fi] = set of vertices with p_f(v)>0
    for d in P:
        it=list(d.items())
        supp.append(set(v for v,_ in it))
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=set(v for v in range(n) if T[v]>N)
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    ellv=[ell[M[fi]] for fi in range(len(M))]  # ell of each bad edge
    return dict(P=P,M=M,ell=ell,ellv=ellv,n=n,N=N,K=K,T=T,O=O,S=S,supp=supp,Bset=info['Bset'])

def components(K,n):
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        stack=[s]; seen[s]=True; C=[]
        while stack:
            v=stack.pop(); C.append(v)
            for w in range(n):
                if w!=v and not seen[w] and K[v][w]>0:
                    seen[w]=True; stack.append(w)
        comps.append(sorted(C))
    return comps

def analyze_one(B,C):
    """Return dict with mass, Gamma_C (=sum ell^2 of belonging edges), deficit, dB, |C|, belonging edge count,
    K-closedness check (leak), and whether identity mass==Gamma_C holds."""
    K=B['K']; T=B['T']; N=B['N']; n=B['n']; supp=B['supp']; ellv=B['ellv']; Bset=B['Bset']
    Cs=set(C)
    mass=sum(T[v] for v in C)
    # belonging bad edges: supp subseteq C
    FC=[fi for fi in range(len(B['M'])) if supp[fi] and supp[fi]<=Cs]
    # partial: edges with supp intersecting C but not contained (should be NONE for a true K-component)
    partial=[fi for fi in range(len(B['M'])) if (supp[fi]&Cs) and not (supp[fi]<=Cs)]
    GammaC=sum(ellv[fi]**2 for fi in FC)
    deficit=F(N*len(C))-mass
    dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
    # leak: K mass from C to outside
    leak=sum(K[v][w] for v in C for w in range(n) if w not in Cs)
    return dict(mass=mass,GammaC=GammaC,deficit=deficit,dB=dB,sz=len(C),nFC=len(FC),
                partial=len(partial),leak=leak,identity=(mass==GammaC),
                bd_ok=(deficit>=dB))

def run(name,info):
    B=build(info)
    comps=components(B['K'],B['n'])
    out=[]
    for C in comps:
        if set(C)&B['O']: continue
        out.append((C,analyze_one(B,C)))
    return B,out

def census(Nmax,Nmin=5,stride=1,verbose=False):
    bad_ident=0; bad_partial=0; bad_bd=0; mincl=None; worst=None
    tot=0
    for nn in range(Nmin,Nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B,out=run(g6,info)
            for C,d in out:
                tot+=1
                if not d['identity']: bad_ident+=1
                if d['partial']>0: bad_partial+=1
                if d['leak']!=0:
                    if mincl is None: mincl=(g6,C,float(d['leak']))
                if not d['bd_ok']:
                    bad_bd+=1
                    if worst is None: worst=(g6,C,float(d['deficit']),d['dB'])
                slack=d['deficit']-d['dB']
                if worst is None or (isinstance(worst,tuple) and len(worst)==4): pass
        print(f"  N={nn}(str{stride}): comps(disjoint-O)~running tot={tot} bad_ident={bad_ident} bad_partial={bad_partial} bad_bd={bad_bd}",flush=True)
    print(f"TOTAL: tot={tot} bad_identity(mass!=GammaC)={bad_ident} bad_partial(supp straddles comp)={bad_partial} bad_boundary_deficit={bad_bd} leak_example={mincl} bd_violation={worst}",flush=True)

if __name__=="__main__":
    print("=== mass(C)=Gamma_C identity + boundary-deficit theory probe ===")
    # quick named check + identity
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]:
        n,E=dec(g6); B,out=run(g6,loads(n,E))
        for C,d in out:
            print(f"  {g6} C(sz{d['sz']}): mass={float(d['mass'])} GammaC={d['GammaC']} ident={d['identity']} "
                  f"partial={d['partial']} leak={float(d['leak'])} deficit={float(d['deficit'])} dB={d['dB']} bd_ok={d['bd_ok']} nFC={d['nFC']}")
    census(9,5,1)
