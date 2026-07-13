#!/usr/bin/env python3
"""AGENT-HOMOLOGY Check 9: finite verification of the MOVER-CLOCK LEMMA.

Lemma (rotor mechanics, t-uniform):
  In any balanced live rotor, fix a vertex u that is ever inserted or expelled
  ("mover").  Its row-count r(u) changes along the rotor cycle by:
    +1 exactly at u's OWNER events (u inserted; the full profile at that state
       forces the PRE-value r(u) = t),
    -1 exactly at u's PARTNER events (u expelled; no pre-condition),
     0 otherwise.
  Cyclic closure (r returns to its start after the period).

Claim: for every consistent cyclic assignment with at least one owner event,
  (a) r(u) is confined to {t, t+1} at all times;
  (b) owner and partner events strictly alternate around the cycle;
  (c) every partner event has pre-value exactly t+1.

Finite verification: enumerate ALL cyclic event words w in {O, P, N}^L for
L <= 9 and ALL start values r0 in [t-4, t+4] (t = 7 as neutral offset; the
lemma is translation-invariant so one t suffices; also run t = 3).
A word+start is CONSISTENT iff every O step has pre-value exactly t and the
total delta is 0 (cyclic closure).  For every consistent pair with >= 1 O,
check (a),(b),(c).  Also verify consistent words with >= 1 P but 0 O exist
only when they'd violate closure (sum must be 0 => #O = #P, so 0 O => 0 P;
pure-N words are trivially consistent).
"""
from itertools import product

def run(t):
    viol = []
    n_consistent = 0
    for L in range(1, 10):
        for word in product('OPN', repeat=L):
            nO = word.count('O')
            nP = word.count('P')
            if nO != nP:
                continue  # cyclic closure impossible
            for r0 in range(t - 4, t + 5):
                # simulate
                r = r0
                ok = True
                vals = [r0]
                for ev in word:
                    if ev == 'O':
                        if r != t:
                            ok = False
                            break
                        r += 1
                    elif ev == 'P':
                        r -= 1
                    vals.append(r)
                if not ok or r != r0:
                    continue
                n_consistent += 1
                if nO == 0:
                    continue
                # (a) confinement
                conf = all(v in (t, t + 1) for v in vals)
                # (b) strict alternation of O/P around the cycle
                evs = [(i, e) for i, e in enumerate(word) if e in 'OP']
                alt = all(evs[k][1] != evs[(k + 1) % len(evs)][1]
                          for k in range(len(evs)))
                # (c) partner pre-value = t+1
                r = r0
                pre_ok = True
                for ev in word:
                    if ev == 'P' and r != t + 1:
                        pre_ok = False
                    if ev == 'O':
                        r += 1
                    elif ev == 'P':
                        r -= 1
                if not (conf and alt and pre_ok):
                    viol.append((word, r0, conf, alt, pre_ok))
    return n_consistent, viol

if __name__ == '__main__':
    allok = True
    for t in (3, 7):
        n, viol = run(t)
        print(f"t={t}: consistent cyclic (word,start) pairs checked: {n}; "
              f"violations of (a)/(b)/(c): {len(viol)}")
        for v in viol[:5]:
            print("   VIOLATION:", v)
        allok &= not viol
    print("VERDICT:", "ALL PASS (clock lemma verified on all cyclic words "
          "len<=9, both t)" if allok else "FAIL")
