"""CRUX gate (GPT all-k Hall route + Codex 373 extraction family):
   On NON-gamma-min connected-B MAX cuts, does  Tail_k(P) < 0  for some k  IMPLY the existence of a
   neutral connected Gamma-DECREASING parity-completed interval switch W?  (The contrapositive on gamma-min
   cuts is exactly Tail_k>=0.)  Also: does Tail_k<0 even OCCUR on non-gamma-min max cuts?

   For each graph: enumerate ALL max cuts (2^(n-1)); among connected-B ones with bad edges, for each bad edge
   f and shortest geodesic P compute Tail_k (via _layer_gate.Zr_row).  Flag rows with min_k Tail_k < 0.
   For those, enumerate parity-completed interval switches W(I,choice) and test CutMargin(W)=0, Bconn,
   struct valid, DeltaGamma(W)<0.  Report whether every Tail_k<0 row yields such a W; any without one falsifies.
   ALL exact Fraction.  N<=12.
"""
import subprocess, itertools
from fractions import Fraction as F
from _layer_gate import Zr_row
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side

def all_max_cuts(n, adj, E):
    best = -1; cuts = []
    for bits in itertools.product((0,1), repeat=n-1):
        side = [0]+list(bits)
        val = sum(1 for (u,v) in E if side[u] != side[v])
        if val > best: best = val; cuts = [side]
        elif val == best: cuts.append(side)
    return best, cuts

def components_off_path(n, adj, side, Pset):
    """connected components of blue graph B with V(P) deleted."""
    seen = set(); comps = []
    for s in range(n):
        if s in Pset or s in seen: continue
        stack=[s]; comp=set([s]); seen.add(s)
        while stack:
            u=stack.pop()
            for w in adj[u]:
                if w in Pset or side[w]==side[u]: continue   # blue edges only
                if w not in seen: seen.add(w); comp.add(w); stack.append(w)
        comps.append(comp)
    return comps

def parity_interval_switches(n, adj, side, P):
    """Codex parity-completed interval family: for each interval I=[a,b] of path indices,
       W = {x_i:i in I} + forced components (Attach subset I -> all; Attach cap I empty -> none;
       straddling -> one bipartition class).  Yields candidate vertex sets W."""
    L = len(P); Pset = set(P)
    comps = components_off_path(n, adj, side, Pset)
    # attach + bipartition (by original side bit within comp via BFS 2-coloring on blue edges)
    info = []
    for C in comps:
        attach = set()
        for v in C:
            for w in adj[v]:
                if w in Pset and side[w] != side[v]:
                    attach.add(P.index(w))
        # bipartition C by blue-BFS parity
        col = {};
        start = next(iter(C)); col[start]=0; st=[start]
        while st:
            u=st.pop()
            for w in adj[u]:
                if w in C and side[w]!=side[u] and w not in col:
                    col[w]=col[u]^1; st.append(w)
        cls0 = {v for v in C if col.get(v,0)==0}; cls1 = {v for v in C if col.get(v,0)==1}
        info.append((C, attach, cls0, cls1))
    for a in range(L):
        for b in range(a, L):
            I = set(range(a, b+1))
            base = {P[i] for i in I}
            straddle = []
            forced = set(base)
            ok = True
            for (C, attach, cls0, cls1) in info:
                if not attach: continue
                if attach <= I: forced |= C
                elif attach & I: straddle.append((cls0, cls1))
                # else none
            choices = [()] if not straddle else itertools.product(*[(0,1)]*len(straddle))
            for ch in choices:
                W = set(forced)
                if straddle:
                    for sidx, pick in enumerate(ch):
                        W |= (straddle[sidx][0] if pick==0 else straddle[sidx][1])
                yield frozenset(W)

def test_extraction(n, adj, side, M, Gamma, P):
    """return True if some parity-interval W has CutMargin=0, Bconn, valid, dGamma<0."""
    seen=set()
    for W in parity_interval_switches(n, adj, side, P):
        if not W or W in seen: continue
        seen.add(W)
        dB, dM = deltas(n, adj, side, W)
        if dB != dM: continue
        s2 = flip(side, W)
        if not Bconn(n, adj, s2): continue
        g1 = gamma_of(n, adj, s2)
        if g1 is None: continue
        if g1 - Gamma < 0:
            return True, str(g1-Gamma), len(W)
    return False, None, None

def main():
    tot_negrows=0; extract_ok=0; extract_fail=0; failex=None
    neg_on_nonmin=0; tail_neg_occurs=0
    for nn in range(5, 13):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n, E = dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            mc, cuts = all_max_cuts(n, adj, E)
            # compute Gamma for each max cut to identify non-gamma-min
            structs=[]
            for side in cuts:
                if not Bconn(n, adj, side): continue
                st = struct_for_side(n, adj, side)
                if st is None: continue
                structs.append((side, st, sum(st[2])))
            if not structs: continue
            gmin = min(g for (_,_,g) in structs)
            for (side, st, G) in structs:
                M, ell, T, cyc = st[0], st[1], st[2], st[4]
                if not M: continue
                for f in M:
                    if ell[f]%2: pass
                    else: continue
                    for P in cyc[f]:
                        if len(P)!=ell[f]: continue
                        B_L, DGsum, Z, lhs, rhs = Zr_row(n, adj, side, M, ell, T, cyc, f, P)
                        mintail = min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                        if mintail < 0:
                            tail_neg_occurs += 1
                            if G > gmin: neg_on_nonmin += 1
                            tot_negrows += 1
                            ok, dg, sz = test_extraction(n, adj, side, M, G, P)
                            if ok: extract_ok += 1
                            else:
                                extract_fail += 1
                                if failex is None: failex=(g6, n, ell[f], tuple(P), str(mintail))
        print("through N=%d: Tail<0 rows=%d (non-min=%d) extract_ok=%d extract_fail=%d"
              % (nn, tot_negrows, neg_on_nonmin, extract_ok, extract_fail), flush=True)
    print("="*55)
    print("Tail_k<0 rows:", tot_negrows, " (on non-gamma-min cuts:", neg_on_nonmin, ")")
    print("extraction OK (found neutral dGamma<0 W):", extract_ok)
    print("extraction FAIL (no such W):", extract_fail, failex or '')
    print("VERDICT:", "EVERY Tail_k<0 row yields a neutral Gamma-decreasing switch (crux mechanism validated)"
          if extract_fail==0 and tot_negrows>0 else
          ("no Tail_k<0 rows found -- need bigger N / different cuts" if tot_negrows==0 else "EXTRACTION FALSIFIED"))

if __name__ == "__main__":
    main()
