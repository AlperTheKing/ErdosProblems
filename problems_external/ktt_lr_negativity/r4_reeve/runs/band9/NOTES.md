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
  depend only on (a,b,c). RE-VERIFIED at band scale: 40 random dim-3 triples
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
| **Aw+Bw <= 72, Cw <= 72** | **26 908 223 405** | **4 912 171 172 063** | 4 326 631 435 | 1 274 602 651 | **0** |
| **Aw <= 32, Bw <= 32, Cw <= 140** | **31 499 271 576** | **4 693 735 006 992** | 516 693 093 | 131 182 996 | **0** |
| Aw+Bw <= 64, Cw <= 64 (subsumed by S=72) | 10 083 075 463 | 2 058 732 232 122 | 1 624 780 265 | 410 849 132 | **0** |
| Aw <= 44, Bw <= 44, Cw <= 44 | 6 563 857 152 | 1 115 329 664 832 | 2 081 546 042 | 745 185 809 | **0** |
| Aw <= 20, Bw <= 20, Cw <= 140 | 2 630 178 432 | 483 244 514 936 | 11 976 471 | 1 343 705 | **0** |
| Aw <= 20, Bw <= 20, Cw <= 60 (re-run, +histogram) | 227 808 076 | 64 355 214 188 | 11 976 471 | 1 343 705 | **0** |
| Aw <= 140, Bw <= 8, Cw <= 8 | 30 808 696 | 1 883 620 354 | 17 646 | 61 | **0** |
| Aw <= 8, Bw <= 140, Cw <= 8 | 30 808 696 | 1 883 620 354 | 17 646 | 61 | **0** |
| Aw <= 8, Bw <= 8, Cw <= 140 | 34 530 120 | 7 546 854 100 | 17 646 | 61 | **0** |

(The 20/20/60 line reproduces the 20/20/140 line's Q-nonempty and dim-3 counts EXACTLY —
independent evidence that every nonempty class in that box already has Cw <= 60.)

plus non-exhaustive probes of the whole band (uniform random; the assigned volume-steered
single-box hill climb at fixed small c, two seeds; a c=4-restricted climb; and a NEW
a1-steered descent) — see section 5 and manifest.json.

**Union of the exhaustive regions** — computed independently in exact integer arithmetic by
`union_count.py` (which reproduces the scanner's own `bandTriplesCovered` counter for EVERY
region and the band totals 7 820 553 811 824 / 171 496 406 264 085):

    56 043 104 209 gap classes   =   8 846 458 835 872 band triples
    out of   7 820 553 811 824 gap classes  =  171 496 406 264 085 band triples
    i.e. 0.717 % of the gap classes and 5.158 % of the triples of the band.

**The band as a whole is NOT exhausted.** What is exhausted is the union of the gap
regions listed above, and that statement is exact.

Total direct engine evaluations across all scans (exhaustive + probes, overlaps counted
once per scan): **78 935 116 996**, of which 3 159 405 761 landed on 3-dimensional Q.

Detector unit tests, both passed:
* `reeve_detector_check.log`: on T_q the integer criterion returns 6a1 = 12-q and V = q for
  q = 1..40, firing NEGATIVE exactly for q >= 13 — 0 failures.
* `hive4.py --reeve 20` (exact Fraction Ehrhart, independent of the integer criterion):
  h* = (1,0,q-1,0), a1 = 2 - q/6, NEG=True exactly for q >= 13. **REEVE UNIT TEST: PASS.**
  The detector demonstrably detects the textbook negative case.

## 4. Records (every one re-verified exactly by hive4.py, and by BOTH LR engines)

* min a1 over dim-3 = **11/6**, attained at the unimodular simplex h* = (1,0,0,0),
  e.g. lam=(15,14,13,12) mu=(35,2,1) nu=(49,16,14,13), W = 92, c = 4, V = 1,
  P = 1 + (11/6)n + n^2 + (1/6)n^3.  (Engines A and B: 4,10,20 at n=1,2,3.)
  Also attained at lam=(23,21,10,8) mu=(14,11,5,1) nu=(35,25,17,16), W = 93 — the state the
  NEW a1-steered descent converged to (engines A and B: 4,10,20 at n=1,2,3; identical P).
* min a1 over ALL strata = 0, attained only on 0-dimensional Q where P is the constant 1
  (there is no negative coefficient there; the polynomial is 1).
* max V over the whole band (volume-steered climb, seed 20260722, W = 139) = **2850** at
  lam=(34,20,9) mu=(38,26,12) nu=(52,40,28,19), c = 638, h* = (1,634,1865,350),
  P = 1 + 19n + 143n^2 + 475n^3, a1 = 19 > 0.
  (Engines A and B: 638, 4411 at n = 1,2; hive4.py verified with held-out P(4),P(5);
  max vertex denominator 1; volume cross-check True.)  Previous best 2817.
* max V over an EXHAUSTIVE region = **926** (Aw,Bw,Cw <= 44).  Within the new S=72 cone
  max V = 539 at lam=(24,16,10,5) mu=(19,12,6) nu=(34,26,19,13), c = 147, h* = (1,143,341,54),
  P = 1 + (32/3)n + (91/2)n^2 + (539/6)n^3, a1 = 32/3 > 0 (engines A and B: 147, 923).
* **max V among h*1 = 0 (c = dim+1 = 4, the Reeve shape) = 1 in EVERY scan, exhaustive or
  not, including a climb run that was RESTRICTED to c <= 4.**
  i.e. every dim-3 r=4 hive polytope with exactly 4 lattice points that was seen anywhere in
  this band is UNIMODULAR (q = 1), against the q >= 13 needed for the Reeve mechanism.
  Also max V at c = 5 is 3 and at c = 6 is 4 in every scan.

## 5. Non-exhaustive probes of the whole band

| probe | evaluations | Q nonempty | dim 3 | NEGATIVE | min 6a1 (dim3) | max V | max V at c=4 |
|---|---|---|---|---|---|---|---|
| uniform random band triples | 60 000 000 | 534 | 233 | **0** | 11 | 600 | 1 |
| volume-steered climb, seed 909 (c <= 6) | 540 129 489 | 480 358 374 | 379 252 198 | **0** | 11 | 2817 | 1 |
| volume-steered climb, seed 20260722 (c <= 6) | 77 267 272 | 68 715 835 | 54 231 316 | **0** | 11 | **2850** | 1 |
| volume-steered climb RESTRICTED to c <= 4 | 147 752 132 | 122 082 306 | 95 721 021 | **0** | 11 | 2837 | **1** |
| **a1-steered descent (NEW mode `--aclimb`)** | 101 406 487 | 83 644 771 | 65 692 812 | **0** | **11** | 368 | 1 |

The uniform-random line is worth recording on its own: a uniformly random triple of
4-part partitions with |lam|+|mu|=|nu| in [91,140] has c(nu;lam,mu) > 0 only about
534/60 000 000 ~ 9e-6 of the time, which is why the census had to be run in gap-moduli
coordinates and why the climbs had to be seeded there too.

The assigned method (volume-steered hill climb: repeatedly single-box perturb toward
larger V at fixed small c) raised V to 2850 when c was free, but at c = 4 (h*_1 = 0, the
Reeve shape) it never moved V off 1 — **every c = 4 dim-3 r=4 hive polytope it reached was
unimodular**, including in a run whose acceptance rule FORBADE leaving c <= 4.
Against the Reeve requirement q >= 13 that is a margin of a factor 13 in V.

`--aclimb` is a new mode added in this session (`bandscan9d.cpp` -> `bandscan9e.exe`) that
descends the actual objective 6a1 = 11 + 2h*1 - h*2 + 2h*3 directly instead of maximising V.
It is a strictly better-targeted search than the volume climb, and it also bottoms out at
6a1 = 11 and never once goes below.

## 6. Exact distribution of 6a1 (new this session)

The scanner mode `--whist` histograms 6a1 over all dim-3 polytopes of an exhaustive region.

* Aw<=20, Bw<=20, Cw<=60 (1 343 705 dim-3 polytopes): 6a1 takes values in **[11, 38]**;
  296 384 of them sit exactly at the floor 11; **0 below 11**, 0 negative.
* Aw<=32, Bw<=32, Cw<=140 (131 182 996 dim-3 polytopes): 6a1 takes values in **[11, 62]**;
  15 752 928 sit exactly at 11; **0 below 11**, 0 negative.

Two structural facts fall out and are worth recording, because they say *how far* the band
is from the Reeve mechanism rather than merely that no hit was found:

1. The floor is 11, i.e. a1 >= 11/6 on every dim-3 hive polytope enumerated, equivalently
   **h*_2 <= 2 h*_1 + 2 h*_3 always held** — the h*-vector never bulges in the middle.
   Negativity needs h*_2 > 11 + 2h*_1 + 2h*_3, so the observed gap is at least 11.
2. The value 6a1 = 12 is extremely rare (819 out of 131 182 996; 140 out of 1 343 705)
   while 11, 13, 15 carry most of the mass — the low end of the spectrum is nearly
   supported on odd values, i.e. a1 has a strong half-integrality bias near the floor.

Neither fact is a proof of anything. Both are exact counts over the stated regions.

## 7. Cross-engine validation done in this session (round 2)

`xcheck2.py` / `xcheck2.json`: 8 FRESH random dim-3 band gap classes (drawn independently of
every record above), each pushed through four engines —

* the fast integer scanner (`--one`),
* `hive4.py` exact Fraction Ehrhart (with held-out P(4), P(5) verification),
* LR engine A `lr_hive.exe`,
* LR engine B `engineB_lrrule.py` (classical LR rule),

compared at stretch n = 1 and n = 2, plus L3 and V scanner-vs-hive4:
**8/8 agreement, 0 mismatches.**  (A first pass reported 8/8 "mismatch" purely because the
LR engines take comma-separated partitions and were being fed space-separated ones; the
invocation was fixed and re-run. Recorded here so the failure is not silently lost.)

Additionally re-verified by BOTH LR engines this session:
* new max-V record lam=(34,20,9) mu=(38,26,12) nu=(52,40,28,19): A = 638, 4411; B = 638, 4411.
* S=72 max-V record lam=(24,16,10,5) mu=(19,12,6) nu=(34,26,19,13): A = 147, 923; B = 147, 923.
* a1-descent floor state lam=(23,21,10,8) mu=(14,11,5,1) nu=(35,25,17,16): A = 4,10,20; B = 4,10,20.

And the coverage bookkeeping itself was re-derived independently: `union_count.py` (pure
Python integers, no C++) reproduces the scanner's `bandTriplesCovered` counter exactly for
all nine regions and reproduces the two band totals exactly.

## 8. Honest statement of what this run establishes

It establishes that the King–Tollu–Toumazet conjecture has **no r=4 counterexample inside
the union of the gap regions of section 3**, i.e. inside 8 846 458 835 872 of the
171 496 406 264 085 triples of the weight band 91 <= |nu| <= 140 (5.158 %), and that no
counterexample was produced by a further 926 555 380 directed (non-exhaustive) evaluations
spread over the whole band.

It establishes **nothing whatever** about the conjecture in general, and it is not evidence
for it. The remaining 94.8 % of the band is untouched, and so is every other band.
