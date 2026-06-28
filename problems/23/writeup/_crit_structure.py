"""Explore the structure forbidding a CRITICAL component.
A critical component C subset Q: KQQ-connected, for all q in C: T[q]=N and leak[q]=sum_{o in O}K[q,o]=0.

leak[q]=0  <=>  for every bad edge f and o in O: p_f(q)p_f(o)=0
            <=>  no bad edge f has BOTH p_f(q)>0 and p_f(o)>0 for some o in O.
Let supp(f) = {v: p_f(v)>0} = vertices on some shortest a-b geodesic (the geodesic interval).
leak[q]=0 for all q in C means: for every f, if supp(f) meets C then supp(f) is DISJOINT from O.
Equivalently: every bad edge f with supp(f) ∩ C != empty has supp(f) ∩ O = empty.

Define M_C = { f : supp(f) ∩ C != empty } (bad edges 'touching' C).
For f in M_C: supp(f) ∩ O = empty, so supp(f) subset Q. Then sum_{v in supp(f)} p_f(v)=ell(f), all in Q.

T[q]=N for q in C. T[q] = sum_g ell(g) p_g(q). And N = T[q].

KEY computation: sum_{q in C} T[q] = N*|C|.   (saturation)
sum_{q in C} T[q] = sum_g ell(g) sum_{q in C} p_g(q) = sum_{g in M_C} ell(g) m_g  where
m_g := sum_{q in C} p_g(q) in (0, ell(g)] (mass of g's geodesic landing in C).
So  sum_{g in M_C} ell(g) m_g = N |C|.

Now bound: sum_{g in M_C} ell(g) m_g <= sum_{g in M_C} ell(g)^2? no. Let's just GATHER data:
 - does M_C ever leave C entirely inside Q (supp subset Q)?  yes by def.
 - what is |C|, |M_C|, and is there slack?
We DUMP, for each near/exact-critical-ish component (and for ALL components with all-r-small),
the numbers, to find the contradiction lever."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, reach_components
from _schur_spec import pf_exact

def supp_and_mass(info):
    P,M,ell,n=pf_exact(info)
    supp=[set(d.keys()) for d in P]  # support of each bad edge (vertices with p_f>0)
    return P,M,ell,supp,n

def analyze(info):
    P,M,ell,supp,n=supp_and_mass(info)
    K,T,O,Q,N,_=build_K(info)
    if not O: return None
    Oset=set(O); Qset=set(Q)
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    out=[]
    for c in range(ncomp):
        nodesIdx=[i for i in range(m) if comp[i]==c]
        Cset=set(Q[i] for i in nodesIdx)
        # is this component O-isolated (leak=0 for all)?
        leak0=all(sum(K[v][o] for o in O)==0 for v in Cset)
        rvals=[F(N)-T[v] for v in Cset]
        allsat=all(rv==0 for rv in rvals)
        # M_C
        MC=[fi for fi in range(len(M)) if supp[fi] & Cset]
        # do all M_C edges avoid O?
        MC_avoid_O = all(not (supp[fi] & Oset) for fi in MC)
        # mass landing in C
        massC=sum(ell[M[fi]]*sum(P[fi].get(v,F(0)) for v in Cset) for fi in MC)
        out.append(dict(c=c,sizeC=len(Cset),leak0=leak0,allsat=allsat,
                        minr=float(min(rvals)),MC=len(MC),MC_avoid_O=MC_avoid_O,
                        massC=float(massC),NcardC=float(N*len(Cset)),
                        Cset=sorted(Cset)))
    return dict(N=N,nO=len(O),ncomp=ncomp,comps=out)

if __name__=="__main__":
    # focus on graphs whose components are O-isolated (leak0) to study them
    for nn in range(7,12):
        cnt_iso=0; cnt_iso_sat=0; examples=[]
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            d=analyze(info)
            if d is None: continue
            for comp in d['comps']:
                if comp['leak0']:
                    cnt_iso+=1
                    if comp['minr']<=0.0+1e-9: pass
                    # record how close to saturation an O-isolated comp gets
                    if len(examples)<6 and comp['sizeC']>1:
                        examples.append((g6,comp['sizeC'],comp['minr'],comp['MC'],comp['MC_avoid_O'],comp['massC'],comp['NcardC']))
        print(f"N={nn}: O-isolated components={cnt_iso}; examples(size,minr,|MC|,MCavoidO,massC,N|C|)=")
        for e in examples: print("    ",e)
