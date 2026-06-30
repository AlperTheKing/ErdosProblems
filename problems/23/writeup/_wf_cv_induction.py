"""ROUTE INDUCTION on bad edges within a K-component => (CV).

(CV) target, per K-component c:   sum_{v in c} T(v)^2 <= (N + N^2/25 - beta) * sum_{v in c} T(v).

Order the component's bad edges f_1..f_r. After t edges the partial load is
   T_t(v) = sum_{s<=t} w_{f_s} p_{f_s}(v),   w_f = ell_f/|cyc_f|,  p_f(v)=#geodesics of f thru v.
Adding f_t:  Delta T_t = w_{f_t} p_{f_t}.
   Delta(sum_v T^2) = 2 sum_v T_{t-1}(v) Delta T_t(v) + sum_v Delta T_t(v)^2      [STEP_t]
   Delta Gamma_c    = sum_v w_{f_t} p_{f_t}(v) = ell_{f_t}^2                        [exact]

We GATE the per-step inequality in TWO forms:
  (F)  STEP_t <= (N + eta_r) * ell_{f_t}^2        [FINAL budget eta_r = N^2/25 - r ; telescopes EXACTLY to (CV)]
  (R)  STEP_t <= (N + eta_t) * ell_{f_t}^2        [RUNNING budget eta_t = N^2/25 - t ; weaker telescope]
Form (F) is the load-bearing one: sum_t STEP_t = sum_v T_r^2 (telescopes), sum_t ell^2 = Gamma_c,
so (F) for every step and every order  =>  (CV).  We test multiple edge orders and report the WORST step.

All exact Fraction. Full standing battery (model on _cv_gate.py)."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def comp_edges(n, adj, side):
    """Return per-component data: for each K-component, list of (f, w_f, pf_vec) over the n vertices,
    plus the component's vertex set and ell_f per edge. pf_vec[v] = #geodesics of f through v (integer)."""
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    if not M: return None
    beta = len(M)
    comp_map, find = kcomponents(n, cyc)
    cid = [find(u) for u in range(n)]
    # group bad edges by component (geodesic vertices all share a component)
    comp_bad = {}
    for f in M:
        Ps = cyc[f]
        c = find(Ps[0][0])
        pf = [0]*n
        for P in Ps:
            for v in P: pf[v] += 1
        wf = F(ell[f], len(Ps))
        comp_bad.setdefault(c, []).append((f, wf, pf, ell[f]))
    comps = {}
    for v in range(n): comps.setdefault(cid[v], []).append(v)
    return beta, comps, comp_bad, T

def step_terms(prefixT, wf, pf, vs):
    """STEP_t = 2*sum_v T_{t-1}(v)*(wf*pf[v]) + sum_v (wf*pf[v])^2, over component vertices vs."""
    cross = F(0); sq = F(0)
    for v in vs:
        dT = wf * pf[v]
        if dT == 0: continue
        cross += prefixT[v] * dT
        sq += dT * dT
    return 2*cross + sq

def chk(name, n, adj, side, acc, orders):
    if not Bconn(n, adj, side): return
    res = comp_edges(n, adj, side)
    if res is None: return
    beta, comps, comp_bad, T = res
    N = n
    etaR = F(N*N, 25) - beta                # FINAL budget (uses total beta)
    AfinalFull = F(N) + etaR               # N + eta_r  (used in form F, with total beta)
    for c, badlist in comp_bad.items():
        if not badlist: continue
        vs = comps[c]
        r = len(badlist)
        Gamma_c = sum(wf*sum(pf) for (f,wf,pf,l) in badlist)   # = sum ell_f^2
        # final-eta for THIS component's reduction uses global beta (eta_r = N^2/25 - beta)
        Afin = AfinalFull
        for order_name, perm in orders(badlist):
            prefixT = [F(0)]*n
            tot = F(0)
            for t,(f,wf,pf,l) in enumerate(perm, start=1):
                step = step_terms(prefixT, wf, pf, vs)
                l2 = F(l*l)
                # form F: budget = N + eta_r (global)
                marginF = Afin*l2 - step
                # form R: running budget eta_t = N^2/25 - t  (t bad edges placed so far, global count irrelevant => use t)
                etaT = F(N*N,25) - t
                marginR = (F(N)+etaT)*l2 - step
                acc['nstep'] += 1
                if marginF < acc['minF'][0]:
                    acc['minF'] = (marginF, name, order_name, N, beta, len(vs), t, r, str(l))
                if marginR < acc['minR'][0]:
                    acc['minR'] = (marginR, name, order_name, N, beta, len(vs), t, r, str(l))
                if marginF < 0:
                    acc['violF'] += 1
                    if acc['firstF'] is None:
                        acc['firstF'] = (name, order_name, N, beta, t, r, str(marginF))
                if marginR < 0:
                    acc['violR'] += 1
                    if acc['firstR'] is None:
                        acc['firstR'] = (name, order_name, N, beta, t, r, str(marginR))
                # update prefix
                for v in vs:
                    prefixT[v] += wf*pf[v]
                tot += step
            # sanity: telescoped sum == sum_v T_c^2  and matches (CV) directly
            S2 = sum(prefixT[v]*prefixT[v] for v in vs)
            assert tot == S2, ("telescope mismatch", name, order_name, str(tot), str(S2))
            acc['ncomp'] += 1

def orders(badlist):
    """Yield (name, ordered list). Test: ell ascending, ell descending, and original."""
    asc = sorted(badlist, key=lambda x: x[3])
    desc = sorted(badlist, key=lambda x: -x[3])
    yield ("ell-asc", asc)
    yield ("ell-desc", desc)
    yield ("orig", list(badlist))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(nstep=0, ncomp=0, violF=0, violR=0, firstF=None, firstR=None,
             minF=(F(10**18),), minR=(F(10**18),))
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc,orders)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc,orders)
    print("  two-lane+k-lane: violF=%d violR=%d"%(acc['violF'],acc['violR']),flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc,orders)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc,orders)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc,orders)
    print("  blow-ups + Mycielskians + glued done (violF=%d violR=%d)"%(acc['violF'],acc['violR']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['violF']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc,orders)
        print("  census N=%d (violF+%d)"%(nn,acc['violF']-v0),flush=True)
    print("\n  steps tested=%d  components=%d"%(acc['nstep'],acc['ncomp']),flush=True)
    print("  FINAL-eta form:   violations=%d"%acc['violF'],flush=True)
    print("    MIN marginF = %s at (name,order,N,beta,|c|,t,r,ell)=%s"%(float(acc['minF'][0]),acc['minF'][1:]),flush=True)
    if acc['firstF']: print("    first F-violation: %s"%(acc['firstF'],),flush=True)
    print("  RUNNING-eta form: violations=%d"%acc['violR'],flush=True)
    print("    MIN marginR = %s at (name,order,N,beta,|c|,t,r,ell)=%s"%(float(acc['minR'][0]),acc['minR'][1:]),flush=True)
    if acc['firstR']: print("    first R-violation: %s"%(acc['firstR'],),flush=True)
    print("\n  === per-step (F) STEP_t <= (N+eta_r)ell^2  %s  => telescopes to (CV) ==="%("HOLDS" if not acc['violF'] else "FAILS"),flush=True)
    print("  === per-step (R) STEP_t <= (N+eta_t)ell^2  %s ==="%("HOLDS" if not acc['violR'] else "FAILS"),flush=True)
