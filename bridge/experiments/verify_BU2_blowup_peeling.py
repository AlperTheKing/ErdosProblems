#!/usr/bin/env python3
"""
BU2 (blow-up peeling lemma), FULL test toward a proof.

Setup: C5[m], m=(m0..m4) in Z>=0, sum=5n. beta(C5[m]) = P := min_i m_i*m_{i+1}
(BU1, proved). Removing s_i vertices from class i (sum s = 5, 0<=s_i<=m_i) yields
C5[m-s] with beta = min_i (m_i-s_i)(m_{i+1}-s_{i+1}) =: P'(s).

Peeling drop  Delta(s) = P - P'(s).  Want: exists s with Delta(s) <= 2n-1.

This script, for each composition m of 5n into 5 POSITIVE parts:
  - P, regime flag (P <= 2n-1  => trivially OK since Delta<=P)
  - Delta_allones  (s=(1,1,1,1,1))           -> tests the clean all-ones route
  - Delta_best = P - max_s P'(s) over ALL s (compositions of 5 into 5 nonneg,
    clamped by s_i<=m_i)                       -> tests the LEMMA itself
Reports:
  - any LEMMA violation (Delta_best > 2n-1)         [would DISPROVE BU2]
  - any all-ones failure (Delta_allones > 2n-1)     [all-ones insufficient, need adaptive s]
  - the worst-case witnesses

Full enumeration for n=7..16; adversarial sampling (tiny-class + heavy-pair
danger zone) for larger n.
"""
import itertools, sys

def products_min(m):
    return min(m[i]*m[(i+1)%5] for i in range(5))

# all s = compositions of 5 into 5 nonneg parts (126 of them)
S_ALL = [s for s in itertools.product(range(6), repeat=5) if sum(s)==5]

def delta_best(m, P):
    bestPp = -1
    for s in S_ALL:
        if any(s[i] > m[i] for i in range(5)):
            continue
        mm = tuple(m[i]-s[i] for i in range(5))
        Pp = min(mm[i]*mm[(i+1)%5] for i in range(5))
        if Pp > bestPp:
            bestPp = Pp
    return P - bestPp

def delta_allones(m, P):
    if any(mi < 1 for mi in m):
        return None
    mm = tuple(mi-1 for mi in m)
    Pp = min(mm[i]*mm[(i+1)%5] for i in range(5))
    return P - Pp

def compositions_positive(total, parts):
    # ordered compositions of `total` into `parts` POSITIVE integers
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - (parts-1) + 1):
        for rest in compositions_positive(total-first, parts-1):
            yield (first,)+rest

def best_s(m, P):
    """return (bestPp, argmax s) over all valid s."""
    bestPp, args = -1, None
    for s in S_ALL:
        if any(s[i] > m[i] for i in range(5)):
            continue
        mm = tuple(m[i]-s[i] for i in range(5))
        Pp = min(mm[i]*mm[(i+1)%5] for i in range(5))
        if Pp > bestPp:
            bestPp, args = Pp, s
    return bestPp, args

def check_full(n):
    twonm1 = 2*n-1
    lemma_viol = []
    allones_fail = []        # (m,P,da, optimal s) — all-ones insufficient but lemma holds
    worst_best = (-1, None)
    cnt = 0
    nontrivial = 0           # P >= 2n cases (the only ones needing work)
    for m in compositions_positive(5*n, 5):
        cnt += 1
        P = products_min(m)
        if P <= twonm1:
            continue          # Delta <= P <= 2n-1 trivially; skip expensive part
        nontrivial += 1
        bestPp, sopt = best_s(m, P)
        db = P - bestPp
        if db > worst_best[0]:
            worst_best = (db, m, sopt)
        if db > twonm1:
            lemma_viol.append((m, P, db, sopt))
        da = delta_allones(m, P)
        if da is not None and da > twonm1:
            allones_fail.append((m, P, da, sopt))
    return cnt, nontrivial, lemma_viol, allones_fail, worst_best

def main():
    print("== FULL enumeration n=7..20 (regime P>=2n only is nontrivial) ==")
    af_examples = []
    for n in range(7, 21):
        cnt, ntriv, lv, af, wb = check_full(n)
        print(f"n={n:2d} 5n={5*n:3d} comps={cnt:8d} P>=2n:{ntriv:6d} 2n-1={2*n-1:3d} | "
              f"LEMMA_viol={len(lv)} allones_fail={len(af)} | "
              f"worst Delta_best={wb[0]} @m={wb[1]} s={wb[2]}")
        if lv:
            print("  !!! LEMMA VIOLATIONS:", lv[:5]); sys.exit(2)
        af_examples += af[:3]
    print("\nSample all-ones failures (lemma still holds via adaptive s; note s avoids size-1 classes):")
    for (m,P,da,sopt) in af_examples[:12]:
        print(f"  m={m} P={P} Delta_allones={da} -> optimal s={sopt} (Delta_best={P-min((m[i]-sopt[i])*(m[(i+1)%5]-sopt[(i+1)%5]) for i in range(5))})")
    print("\nNO LEMMA VIOLATIONS through n=20: BU2 holds (Delta_best <= 2n-1) on all blow-ups.")

if __name__ == "__main__":
    main()
