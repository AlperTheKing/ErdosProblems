"""Mechanism: WHY does O nonempty force a single loaded K-component?
Per loaded K-component C (K-closed), record:
  sz=|C|, GammaC=sum T, maxT=max_{v in C} T(v), deficit=N|C|-GammaC,
  hasO = (maxT>N), Gamma_C/sz (avg load), Gamma_C/sz^2.
Test on the GLUED instances (where O vanished) and the standalone overloaded gadgets
(where O present, single component). Look for the invariant distinguishing them.

Hypothesis to test exactly:
  (H_sep) A loaded K-component C that is SEPARATED (its own component, with another loaded
          component present) always has maxT <= N (i.e. cannot contribute to O).
  Equivalently: if a vertex is overloaded (T>N), its K-component is the UNIQUE loaded one.

Also examine the C5[t] blowup family: single component, T==N uniform (boundary case),
and how gluing two blowups behaves.
"""
from fractions import Fraction as F
from _h import dec, loads
from _calltie_glue import components_from_info, C

def percomp(name,n,E,quiet=False):
    info=loads(n,E)
    if info is None:
        print(f"{name}: loads None"); return None
    T=info['T']; N=info['n']
    comps=components_from_info(info)
    loaded=[Cc for Cc in comps if sum(T[v] for v in Cc)>0]
    rows=[]
    for Cc in loaded:
        gc=sum(T[v] for v in Cc); mx=max(T[v] for v in Cc); sz=len(Cc)
        rows.append(dict(sz=sz,GammaC=gc,maxT=mx,deficit=N*sz-gc,hasO=(mx>N)))
    nloaded=len(loaded)
    if not quiet:
        print(f"{name}: N={N} loaded={nloaded}")
        for r in rows:
            print(f"    sz={r['sz']} GammaC={r['GammaC']} maxT={r['maxT']}({float(r['maxT']):.3f}) "
                  f"deficit={r['deficit']} GammaC/sz={float(r['GammaC']/r['sz']):.3f} "
                  f"GammaC/sz^2={float(F(r['GammaC'],r['sz']**2)):.3f} hasO={r['hasO']}")
    return N, rows, nloaded

if __name__=="__main__":
    print("=== H_sep: a SEPARATED loaded comp (>=2 loaded comps) never has maxT>N ? ===")
    # standalone overloaded (single comp, has O)
    print("--- standalone overloaded gadgets (single loaded comp, O present) ---")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); percomp(g6,n,E)
    # glued (two loaded comps) -- check maxT of each
    print("--- glued (two loaded comps): does any comp have maxT>N? ---")
    n1,E1=dec("I?BD@g]Qo"); base=n1
    E2=[(base+i, base+(i+1)%5) for i in range(5)]
    E=list(E1)+list(E2); E.append((0,base+5)); E.append((base+5,base));
    percomp("I?BD@g]Qo+C5 bridge2", base+6, E)
    for (a,b) in [(5,7),(5,9),(7,7)]:
        Ec=C(a); E2=[(a+i,a+(i+1)%b) for i in range(b)]; Ec=Ec+E2; nn=a+b
        Ec.append((0,nn)); Ec.append((nn,a)); nn+=1
        percomp(f"C{a}+C{b}", nn, Ec)
    # exhaustive small check: does any census/glue ever give maxT>N in a multi-loaded-comp config?
    print("--- exhaustive: scan many glue widths for maxT>N with >=2 loaded comps ---")
    import subprocess
    from _h import GENG
    bad=0; tot=0
    # systematic: glue two arbitrary census graphs by an even bridge
    for nn in range(7,9):
        gs=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in gs[:200]:
            na,Ea=dec(g6)
            # self-glue with a C5 via even bridge
            base=na; E2=[(base+i,base+(i+1)%5) for i in range(5)]
            E=list(Ea)+list(E2)+[(0,base+5),(base+5,base)]
            r=percomp(f"x",base+6,E,quiet=True)
            if r is None: continue
            N,rows,nloaded=r
            if nloaded>=2:
                tot+=1
                if any(rr['maxT']>N for rr in rows):
                    bad+=1; print(f"   VIOLATION {g6}+C5: a separated comp has maxT>N: {rows}")
    print(f"   scanned multi-loaded-comp configs={tot}, with a separated overloaded comp (maxT>N)={bad}")
