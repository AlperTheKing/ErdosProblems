# band9 — r=4 KTT census for the weight band W = |nu| in [91,140]

Hunter 9 of 12, Reeve-dimension sweep, 2026-07-21.
Target: a triple (lam,mu,nu), |lam|+|mu|=|nu|, whose stretched LR polynomial
P(n) = c(n nu; n lam, n mu) has a strictly NEGATIVE coefficient (King–Tollu–Toumazet 2004).

**No counterexample was found. This proves nothing about the conjecture and is not
evidence for it; it closes the enumerated windows and nothing more.**

## 0. Size of the band

Number of r=4 triples (lam,mu,nu each with at most 4 parts, |lam|+|mu|=|nu|) with
|nu| in [91,140]:

    sum_{W=91}^{140} p4(W) * sum_{a=0}^{W} p4(a) p4(W-a)  =  171 496 406 264 085  ~ 1.715e14

so a literally exhaustive triple-by-triple census of the band is out of reach. The band
IS however exactly coordinatised by a 9-dimensional moduli space (below), and exhaustive
sub-censuses of that space are feasible and are what is reported here.

## 1. Band <-> gap-moduli dictionary (exact, and the reason the census is possible)

Gaps a=(l1-l2,l2-l3,l3-l4), b=(m1-m2,m2-m3,m3-m4), c=(n1-n2,n2-n3,n3-n4);
Aw = a1+2a2+3a3, Bw, Cw likewise; D = Cw-Aw-Bw.

* Q(lam,mu,nu) depends on the triple only through (a,b,c), up to lattice translation of R^3
  (the two "add a full column" symmetries (lam,nu)->(lam+1^4,nu+1^4) and
  (mu,nu)->(mu+1^4,nu+1^4) act on the hive as translations). Hence L(n), V, h*, P and a1
  depend only on (a,b,c). RE-VERIFIED IN THIS RUN at band scale: 40 random dim-3 triples
  with |nu| in [91,140] and arbitrary (lam4,mu4,nu4) matched the canonical representative
  exactly on (L1,L2,L3,6a1,V) — 40/40, 0 mismatches (hive4.py vs the fast evaluator).
* (a,b,c) is realised by partitions iff 4 | D; then |lam| = 4 l4 + Aw, |mu| = 4 m4 + Bw,
  |nu| = 4 n4 + Cw with l4+m4-n4 = D/4 and l4,m4,n4 >= 0.
* **A gap vector with 4|D is realised by SOME triple with |nu| in [91,140] iff
  Aw+Bw <= 140 and Cw <= 140.**
  (=>) Aw+Bw <= |lam|+|mu| = W <= 140 and Cw <= |nu| = W <= 140.
  (<=) take n4 in [max(0, -D/4, ceil((91-Cw)/4)), floor((140-Cw)/4)]; this interval is
       nonempty because the band is 50 >= 4 wide and Aw+Bw <= 140 forces -D/4 <= (140-Cw)/4;
       then l4+m4 = D/4+n4 >= 0 can be split arbitrarily.
  So **the band is exactly the gap region R = {Aw+Bw <= 140, Cw <= 140, 4|D}**,
  |R| = 7 820 553 811 824 gap classes.

Every gap class is therefore a *band* object, and an exhaustive scan of a sub-region of R
is an exhaustive statement about a well-defined finite sub-family of
the band (the exact number of band triples covered is reported for each scan).

## 2. Negativity criterion used (all integer arithmetic)

deg P <= 3 and P(0) = 1 whenever Q is nonempty, so from L(1),L(2),L(3):

    6 a1 = -11 + 18 L1 - 9 L2 + 2 L3 ,   V = 6 a3 = L3 - 3 L2 + 3 L1 - 1 ,
    a2 = 1 + (h*1-h*3)/2 ,  h*1 = L1 - 4  (dim 3) ,  a0 = 1 .

a3 = V/6 > 0 and a0 = 1 > 0 always; a2 >= 0 whenever h*3 <= h*1. **The only Reeve-type
coefficient is a1**, and KTT fails in this cell iff 6a1 < 0, i.e. iff

    h*2  >  11 + 2 h*1 + 2 h*3

(the Reeve tetrahedron T_q has h* = (1,0,q-1,0), crossing at q = 13).

## 3. Scans run (all exhaustive over the stated gap region; all exact integer arithmetic)

| region | gap classes tested | band triples covered | Q nonempty | dim 3 | NEGATIVE |
|---|---|---|---|---|---|
| Aw+Bw <= 64, Cw <= 64 | 10 083 075 463 | 2 058 732 232 122 | 1 624 780 265 | 410 849 132 | **0** |
| Aw <= 20, Bw <= 20, Cw <= 140 | 2 630 178 432 | 483 244 514 936 | 11 976 471 | 1 343 705 | **0** |
| Aw <= 140, Bw <= 8, Cw <= 8 | 30 808 696 | 1 883 620 354 | 17 646 | 61 | **0** |
| Aw <= 8, Bw <= 140, Cw <= 8 | 30 808 696 | 1 883 620 354 | 17 646 | 61 | **0** |
| Aw <= 8, Bw <= 8, Cw <= 140 | 34 530 120 | 7 546 854 100 | 17 646 | 61 | **0** |
| Aw <= 44, Bw <= 44, Cw <= 44 | 6 563 857 152 | 1 115 329 664 832 | 2 081 546 042 | 745 185 809 | **0** |

plus non-exhaustive probes of the whole band (uniform random, and the assigned
volume-steered single-box hill climb at fixed small c) — see manifest.json.

Union of the exhaustive regions (computed independently in Python from the partition
generating function, and matching the scanner's own counters exactly on the S=64 cone):

    16 204 103 249 gap classes   =   2 986 675 964 834 band triples
    out of   7 820 553 811 824 gap classes  =  171 496 406 264 085 band triples
    i.e. 0.21 % of the gap classes and 1.74 % of the triples of the band.

**The band as a whole is NOT exhausted.** What is exhausted is the union of the six gap
regions above, and that statement is exact.

Detector unit test (`reeve_detector_check.log`): on the Reeve family T_q, whose Ehrhart
polynomial is P(n) = (q/6)n^3 + n^2 + (2-q/6)n + 1, the integer criterion used here returns
6a1 = 12-q and V = q for q = 1..40, firing NEGATIVE exactly for q >= 13 — 0 failures. The
detector demonstrably detects the textbook negative case.

## 4. Records (every one re-verified exactly by hive4.py, and by BOTH LR engines)

* min a1 over dim-3 = **11/6**, attained by the unimodular simplex h* = (1,0,0,0),
  e.g. lam=(15,14,13,12) mu=(35,2,1) nu=(49,16,14,13), W = 92, c = 4, V = 1,
  P = 1 + (11/6)n + n^2 + (1/6)n^3.  (Engines A and B: c(n nu;n lam,n mu) = 4,10,20 at n=1,2,3.)
* min a1 over ALL strata = 0, attained only on 0-dimensional Q where P is the constant 1
  (there is no negative coefficient there; the polynomial is 1).
* max V (exhaustive S=64) = **375** at lam=(24,18,12,7) mu=(16,10,5) nu=(32,26,20,14),
  c = 108, h* = (1,104,234,36), P = 1 + (19/2)n + 35n^2 + (125/2)n^3, a1 = 19/2 > 0.
  (Engines A and B: 108, 660, 2032 at n = 1,2,3.)
* max V over the whole band (volume-steered climb, W = 130) = **2817** at
  lam=(34,21,9) mu=(37,22,7) nu=(54,38,24,14), c = 636, h* = (1,632,1843,341),
  P = 1 + 19n + (293/2)n^2 + (939/2)n^3, a1 = 19 > 0.  (Engines A and B: 636, 4381 at n=1,2.)
  max V over the 60M uniform-random band census = 600 (h*2 = 377, 6a1 = 78 > 0).
* **max V among h*1 = 0 (c = dim+1 = 4, the Reeve shape) = 1 in EVERY scan.**
  i.e. every dim-3 r=4 hive polytope with exactly 4 lattice points that was seen in the
  band is UNIMODULAR (q = 1), against the q >= 13 needed for the Reeve mechanism.
  Also max V at c = 5 is 3 and at c = 6 is 4.

## 5. Non-exhaustive probes of the whole band

| probe | evaluations | Q nonempty | dim 3 | NEGATIVE | min 6a1 (dim3) | max V | max V at c=4 |
|---|---|---|---|---|---|---|---|
| uniform random band triples | 60 000 000 | 534 | 233 | **0** | 11 | 600 | 1 |
| volume-steered single-box climb (c <= 6) | 540 129 489 | 480 358 374 | 379 252 198 | **0** | 11 | 2817 | 1 |

The uniform-random line is worth recording on its own: a uniformly random triple of
4-part partitions with |lam|+|mu|=|nu| in [91,140] has c(nu;lam,mu) > 0 only about
534/60 000 000 ~ 9e-6 of the time, which is why the census had to be run in gap-moduli
coordinates and why the climb had to be seeded there too.

The assigned method (volume-steered hill climb: repeatedly single-box perturb toward
larger V at fixed small c) was run for 780 s over 32 threads from gap-seeded starts.
It raised V to 2817 when c was free, but at c = 4 (h*_1 = 0, the Reeve shape) it never
moved V off 1: **every c = 4 dim-3 r=4 hive polytope it reached was unimodular.**
Against the Reeve requirement q >= 13 this is a margin of a factor 13 in V, and the
exact criterion 6a1 = 11 + 2h*1 - h*2 + 2h*3 was never below 11 in any of the
~2.0e10 evaluations of this run.
