"""ADVERSARIAL LOGIC AUDIT of the chain:
   boundary-deficit  =>  no critical K_QQ-component  =>  rho(K_QQ)<N  =>  cond(1)  =>  (w/ 2,3) SPEC.

We ASSUME boundary-deficit is TRUE (deficit(C)>=dB(C) for every FULL K-component C disjoint from O).
We scrutinize EVERY junction exactly (Fraction), on real census graphs + iterated Mycielskians:

J1 (K-closedness/applicability): is a *critical K_QQ-component* (connected comp of {q~q':K[q,q']>0}
    inside Q, with T=N & leak=0 on it) necessarily a FULL K-component of V (K-closed), so that the
    boundary-deficit lemma even APPLIES to it?  Re-derive K-closedness and TEST: enumerate every
    K_QQ-component on overloaded census graphs; check whether the leak=0 ones are K-closed in V
    (i.e. equal to a full K-component).  ALSO test the converse direction needed by the logic:
    a full K-component disjoint from O is automatically inside Q (so dB/deficit on it are comparable
    to the K_QQ-component decomposition).

J2 (deficit=0 <=> critical): show deficit(C)=0 AND C subset Q  <=>  T[v]=N for all v in C.
    Both directions, exactly, on every full-K-component-disjoint-from-O found.

J3 (dB(C)>0 for PROPER C): does B connected + O nonempty FORCE dB(C)>0 for a proper full K-component
    C disjoint from O?  Look for the gap: what if C is a *proper subset of V* but NO B-edge crosses it
    (B-closed)? Then dB=0 and the contradiction collapses even though deficit=0.  Enumerate, exactly,
    every full K-component disjoint from O and record (|C|, dB(C), whether C is B-closed, whether C=V,
    whether {T>0}=V).  A *B-closed proper C disjoint from O* would be the gap.

J4 (the final contradiction): for a HYPOTHETICAL critical component, plug deficit=0 + the dB value and
    see if 0>=dB>0 actually fires.  We never expect a real critical component (NO-Q-ONLY); the point
    is to confirm the LOGIC would fire IF one existed, and to find any config where it would NOT.

Run: python _bdef_logic.py
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact


def build_K(info):
    P, M, ell, n = pf_exact(info)
    K = [[F(0)] * n for _ in range(n)]
    for d in P:
        it = list(d.items())
        for a in range(len(it)):
            va, pa = it[a]
            for b in range(len(it)):
                vb, pb = it[b]
                K[va][vb] += pa * pb
    T = [sum(K[v][w] for w in range(n)) for v in range(n)]
    return K, T, n


def full_components(K, n):
    """connected comps of the K-graph {v~w: K[v][w]>0} on ALL of V."""
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        C = []
        while stack:
            v = stack.pop()
            C.append(v)
            for w in range(n):
                if w != v and not seen[w] and K[v][w] > 0:
                    seen[w] = True
                    stack.append(w)
        comps.append(sorted(C))
    return comps


def qq_components(K, n, Qset):
    """connected comps of the K-graph restricted to Q (the K_QQ-components)."""
    seen = {q: False for q in Qset}
    comps = []
    for s in Qset:
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        C = []
        while stack:
            v = stack.pop()
            C.append(v)
            for w in Qset:
                if w != v and not seen[w] and K[v][w] > 0:
                    seen[w] = True
                    stack.append(w)
        comps.append(sorted(C))
    return comps


def analyze(info, name="", verbose=False):
    K, T, n = build_K(info)
    N = n
    O = set(v for v in range(n) if T[v] > N)
    Q = set(v for v in range(n) if T[v] <= N)
    Bset = info['Bset']
    support = set(v for v in range(n) if T[v] > 0)

    # ---- J1: K_QQ-components, which are leak-free? are leak-free ones K-closed in V? ----
    qqcomps = qq_components(K, n, Q)
    j1_records = []
    for C in qqcomps:
        Cs = set(C)
        leak = {v: sum(K[v][o] for o in O) for v in C}
        leakfree = all(leak[v] == 0 for v in C)
        satur = all(T[v] == N for v in C)
        critical = leakfree and satur
        # K-closed in V?  no K-edge from C to V\C
        kclosed = all(K[v][w] == 0 for v in C for w in range(n) if w not in Cs)
        # is it a full K-component? (equal to one of the full comps)
        j1_records.append(dict(C=tuple(C), leakfree=leakfree, satur=satur,
                               critical=critical, kclosed=kclosed))
        # LOGIC CHECK: leakfree (=> claim says K-closed) MUST imply kclosed
        if leakfree and not kclosed:
            print(f"  [J1-VIOLATION] {name}: leak-free K_QQ-comp NOT K-closed! C={C}")

    # ---- full K-components disjoint from O: J2,J3,J4 ----
    fcomps = full_components(K, n)
    frecords = []
    for C in fcomps:
        Cs = set(C)
        if Cs & O:
            continue  # only those disjoint from O (boundary-deficit hypothesis)
        # J1-applicability: is C subset Q?  (full comp disjoint from O => should be in Q)
        inQ = Cs <= Q
        mass = sum(T[v] for v in C)
        deficit = F(N * len(C)) - mass
        dB = sum(1 for (a, b) in Bset if (a in Cs) ^ (b in Cs))
        allTN = all(T[v] == N for v in C)
        allT0 = all(T[v] == 0 for v in C)
        isV = (len(C) == n)
        bclosed = (dB == 0)
        # K-closed always true for a FULL K-component by construction; record for sanity
        kclosed = all(K[v][w] == 0 for v in C for w in range(n) if w not in Cs)
        # J3/J4 gap: a PROPER (not all V) full comp disjoint from O that is ALSO B-closed (dB=0)
        gap_J3 = (not isV) and bclosed
        frecords.append(dict(C=tuple(C), inQ=inQ, deficit=deficit, dB=dB,
                             allTN=allTN, allT0=allT0, isV=isV, bclosed=bclosed,
                             kclosed=kclosed, mass=mass, gap_J3=gap_J3))
    return dict(name=name, n=n, N=N, O=sorted(O), support=sorted(support),
                Bconn_all=(support, n), j1=j1_records, full=frecords, K=K, T=T)


def mycielski(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    N2 = 2 * n + 1
    E2 = list(E)
    for u in range(n):
        for v in adj[u]:
            if v > u:
                E2.append((u, n + v))
                E2.append((v, n + u))
    for u in range(n):
        E2.append((n + u, 2 * n))
    return N2, E2


def report(res, deep=False):
    name = res['name']
    O = res['O']
    n = res['n']
    # J1 summary
    j1 = res['j1']
    j1_leakfree = [r for r in j1 if r['leakfree']]
    j1_bad = [r for r in j1 if r['leakfree'] and not r['kclosed']]
    j1_critical = [r for r in j1 if r['critical']]
    # full-comp summary
    full = res['full']
    proper_disjoint = [r for r in full if not r['isV']]
    gaps = [r for r in full if r['gap_J3']]
    # J2 check: any full comp disjoint from O, in Q, deficit==0, but NOT allTN?
    j2_viol = [r for r in full if r['inQ'] and r['deficit'] == 0 and not r['allTN']]
    # also reverse: allTN but deficit!=0 (impossible by arithmetic, sanity)
    j2_viol2 = [r for r in full if r['allTN'] and r['deficit'] != 0]
    line = (f"  {name:24s} n={n} |O|={len(O)} | full-comps-disjoint-O={len(full)} "
            f"proper(not V)={len(proper_disjoint)} | K_QQ-comps={len(j1)} leakfree={len(j1_leakfree)} "
            f"critical={len(j1_critical)} | J1bad(leakfree-not-Kclosed)={len(j1_bad)} "
            f"| J2viol={len(j2_viol)+len(j2_viol2)} | J3gap(proper&Bclosed&disjointO)={len(gaps)}")
    print(line, flush=True)
    if deep or j1_bad or j2_viol or j2_viol2 or gaps:
        for r in gaps:
            print(f"      [J3-GAP] proper full K-comp disjoint-O with dB=0: |C|={len(r['C'])} "
                  f"C={r['C']} deficit={float(r['deficit'])} allTN={r['allTN']} allT0={r['allT0']} "
                  f"inQ={r['inQ']} mass={float(r['mass'])}")
        for r in j2_viol:
            print(f"      [J2-VIOL] inQ deficit=0 but not allTN: C={r['C']}")
        for r in j1_bad:
            print(f"      [J1-BAD] leakfree K_QQ-comp not K-closed: C={r['C']}")
    return dict(j1_bad=len(j1_bad), j2_viol=len(j2_viol) + len(j2_viol2),
                gaps=len(gaps), critical=len(j1_critical))


def run_census(Nmax, Nmin=5, stride=1):
    tot = dict(j1_bad=0, j2_viol=0, gaps=0, critical=0, graphs=0, withO=0)
    worst_gap_example = None
    for nn in range(Nmin, Nmax + 1):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()[::stride]
        cj = dict(j1_bad=0, j2_viol=0, gaps=0, critical=0, graphs=0, withO=0, gapprop=0)
        for g6 in outg:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            res = analyze(info, g6)
            cj['graphs'] += 1
            tot['graphs'] += 1
            if res['O']:
                cj['withO'] += 1
                tot['withO'] += 1
            # count gaps: proper full comp disjoint from O AND B-closed (dB=0)
            full = res['full']
            gaps = [r for r in full if r['gap_J3']]
            # we also want PROPER comps that are B-closed even if O empty? No: chain only invoked when O!=∅.
            # But J3 is about: GIVEN O!=∅ and B connected, does a proper comp force dB>0?
            # The dangerous case = proper comp disjoint-O with dB=0 AND O nonempty.
            gaps_withO = [r for r in gaps if res['O']]
            j1bad = [r for r in res['j1'] if r['leakfree'] and not r['kclosed']]
            j2v = [r for r in full if (r['inQ'] and r['deficit'] == 0 and not r['allTN'])
                   or (r['allTN'] and r['deficit'] != 0)]
            crit = [r for r in res['j1'] if r['critical']]
            cj['j1_bad'] += len(j1bad)
            cj['j2_viol'] += len(j2v)
            cj['gaps'] += len(gaps_withO)
            cj['critical'] += len(crit)
            tot['j1_bad'] += len(j1bad)
            tot['j2_viol'] += len(j2v)
            tot['gaps'] += len(gaps_withO)
            tot['critical'] += len(crit)
            if gaps_withO and worst_gap_example is None:
                worst_gap_example = (g6, [r['C'] for r in gaps_withO], res['O'])
        print(f"  census N={nn}(str{stride}): graphs={cj['graphs']} withO={cj['withO']} | "
              f"J1bad={cj['j1_bad']} J2viol={cj['j2_viol']} J3gaps(properBclosed disjointO,O!=∅)={cj['gaps']} "
              f"critical-comps={cj['critical']}", flush=True)
    print(f"  TOTAL: graphs={tot['graphs']} withO={tot['withO']} J1bad={tot['j1_bad']} "
          f"J2viol={tot['j2_viol']} J3gaps={tot['gaps']} critical={tot['critical']}")
    if worst_gap_example:
        print(f"  J3-GAP EXAMPLE: {worst_gap_example}")


if __name__ == "__main__":
    print("=== ADVERSARIAL LOGIC AUDIT: boundary-deficit => cond(1) chain ===")
    print("\n-- named overloaded graphs + iterated Mycielskians --")
    named = ["G?bF`w", "I?BD@g]Qo", "I?ABCc]}?", "J??CE?{{?]?", "J?AEB?oE?W?"]
    for g6 in named:
        n, E = dec(g6)
        info = loads(n, E)
        if info:
            report(analyze(info, g6), deep=False)
    # iterated Mycielskians
    C5 = (5, [(i, (i + 1) % 5) for i in range(5)])
    C7 = (7, [(i, (i + 1) % 7) for i in range(7)])
    n1, E1 = mycielski(*C5)
    n2, E2 = mycielski(n1, E1)
    n3, E3 = mycielski(n2, E2)
    m1, F1 = mycielski(*C7)
    m2, F2 = mycielski(m1, F1)
    chain = [("C5", C5), ("Grotzsch N=11", (n1, E1)),
             ("Myc(Grotzsch) N=23", (n2, E2)), ("Myc^3(C5) N=47", (n3, E3)),
             ("Myc(C7) N=15", (m1, F1)), ("Myc(Myc(C7)) N=31", (m2, F2))]
    print("\n-- iterated Mycielskians --")
    for nm, (nn, EE) in chain:
        info = loads(nn, EE)
        if info is None:
            print(f"  {nm}: loads=None")
            continue
        report(analyze(info, nm), deep=True)
    print("\n-- full census J1/J2/J3 audit --")
    run_census(11, 5, 1)
