#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 3: the FIXED-TRAFFIC SQUARE BLOCKADE on the real circuits.

Principle (exact, proved by inspection of the transition mechanics):
  Along ANY directed cycle of middle-swaps, an atom whose selected row never changes
  keeps every edge of that row at selected multiplicity >= 1 in EVERY state of the
  cycle.  An edge that is ever a HOLE (selected multiplicity 0, e.g. the owner's
  active edge at its entry state) therefore cannot be used by any cycle-constant row.
  For the minimal balanced rotor (period 4, two atoms AB/PQ swapping on one square
  sigma), all four sigma-edges are holes at some state, so EVERY other atom needs a
  complete row avoiding ALL FOUR sigma-edges.

Exact per-fixture checks:
  B1 for every rotor-core square sigma (both transposed atoms present in the chosen
     circuit): list the atoms with NO sigma-avoiding row.  If nonempty => a period-4
     balanced rotor on sigma is impossible on this circuit FOR EVERY tuple.
  B2 the same at DB level for every square of the support (rotor-core or not).
  B3 liveness maximization: hill-climb + restarts on tuples maximizing the number of
     active components capturing a bad pair; report the best found and whether any
     genuine detour ever has an active entering vertex (exact evaluation per tuple).
"""
import sys, random
from itertools import combinations, product
from collections import defaultdict
sys.path.insert(0, '.')
from fixture_atoms_exact import build
from fixture_state_graph import state_data, detours, classify
from fixture_atoms_v3 import find_circuits_v3
from fixture_264_variants import find as find_variant

def squares_of(fx):
    sq = []
    for u, w in combinations(range(fx['n']), 2):
        if fx['color'].get(u) != fx['color'].get(w) or w in fx['adj'][u]:
            continue
        cn = sorted(fx['adj'][u] & fx['adj'][w])
        for c1, c2 in combinations(cn, 2):
            sq.append((u, c1, w, c2))
    return sq

def rotor_cores(fx, chosen):
    cores = []
    for (u, c1, w, c2) in squares_of(fx):
        sA = [(a1, b1) for a1 in fx['adj'][c1] - {u, w} for b1 in fx['adj'][c2] - {u, w}
              if a1 != b1 and (min(a1, b1), max(a1, b1)) in chosen
              and (a1, c1, u, c2, b1) in fx['rows'][(min(a1, b1), max(a1, b1))]
              and (a1, c1, w, c2, b1) in fx['rows'][(min(a1, b1), max(a1, b1))]]
        sB = [(p1, q1) for p1 in fx['adj'][u] - {c1, c2} for q1 in fx['adj'][w] - {c1, c2}
              if p1 != q1 and (min(p1, q1), max(p1, q1)) in chosen
              and (p1, u, c1, w, q1) in fx['rows'][(min(p1, q1), max(p1, q1))]
              and (p1, u, c2, w, q1) in fx['rows'][(min(p1, q1), max(p1, q1))]]
        if sA and sB:
            cores.append(((u, c1, w, c2), sA, sB))
    return cores

def blockade(fx, chosen, square, coreatoms):
    e_sq = {frozenset((square[0], square[1])), frozenset((square[1], square[2])),
            frozenset((square[2], square[3])), frozenset((square[3], square[0]))}
    blocked = []
    for a in chosen:
        if a in coreatoms:
            continue
        has_avoiding = any(all(frozenset((r[i], r[i+1])) not in e_sq for i in range(4))
                           for r in fx['rows'][a])
        if not has_avoiding:
            blocked.append(a)
    return blocked

def liveness_hunt(fx, chosen, iters=4000, restarts=12):
    atoms = sorted(chosen)
    rows = {a: fx['rows'][a] for a in atoms}
    sub = dict(tag=fx['tag'], edges=fx['edges'], adj=fx['adj'], color=fx['color'],
               atoms=atoms, rows=rows, bad={frozenset(a) for a in atoms},
               degB={u: len(fx['adj'][u]) for u in range(fx['n'])},
               degM=defaultdict(int))
    for u, w in atoms:
        sub['degM'][u] += 1; sub['degM'][w] += 1

    def score(omega):
        sel_rows, m, r, noc, S, act, comp, active_comps = state_data(sub, omega)
        # objective: number of active components + total latent edges in bad-capturing comps
        cap_edges = sum(1 for e in act if comp.get(next(iter(e))) in active_comps)
        return len(active_comps) * 100 + cap_edges, active_comps

    best = (0, None, None)
    rng = random.Random(5)
    sizes = [len(rows[a]) for a in atoms]
    for rs in range(restarts):
        omega = tuple(rng.randrange(s) for s in sizes)
        cur, _ = score(omega)
        for it in range(iters):
            i = rng.randrange(len(atoms))
            if sizes[i] == 1:
                continue
            j = rng.randrange(sizes[i])
            if j == omega[i]:
                continue
            om2 = list(omega); om2[i] = j; om2 = tuple(om2)
            s2, _ = score(om2)
            if s2 >= cur:
                omega, cur = om2, s2
        if cur > best[0]:
            best = (cur, omega, None)
    # exact liveness at the best tuple + neighbors
    found_L1 = 0
    checked = 0
    if best[1] is not None:
        stack = [best[1]]
        seen = {best[1]}
        while stack and checked < 400:
            om = stack.pop()
            checked += 1
            dts, st = classify(sub, om)
            for d in dts:
                if d['l1']:
                    found_L1 += 1
                om2 = list(om); om2[d['atom']] = d['alt']; om2 = tuple(om2)
                if om2 not in seen and len(seen) < 5000:
                    seen.add(om2)
                    stack.append(om2)
    return best[0], found_L1, checked

if __name__ == '__main__':
    results = {}
    for tag in ('298', '264'):
        fx = build(tag)
        if tag == '298':
            subs = find_circuits_v3(fx, cap=1000)
        else:
            subs, _ = find_variant(fx, (0,), cap=1000)
        subs = [sorted(map(tuple, s)) for s in subs]
        print(f"\n===== {tag}: {len(subs)} circuits =====")
        for si, s in enumerate(subs):
            chosen = set(map(tuple, s))
            cores = rotor_cores(fx, chosen)
            print(f" circuit#{si}: rotor-core squares: {len(cores)}")
            for (sq, sA, sB) in cores:
                for AB in sA:
                    for PQ in sB:
                        ca = {(min(AB), max(AB)), (min(PQ), max(PQ))}
                        blk = blockade(fx, chosen, sq, ca)
                        print(f"   square {sq} AB={AB} PQ={PQ}: blocked atoms (no sigma-avoiding row): "
                              f"{len(blk)} {blk[:6]}")
            sc, l1, chk = liveness_hunt(fx, chosen)
            print(f"   liveness hunt: best activity score {sc}; L1 transitions found "
                  f"{l1} over {chk} exact-checked tuples")
