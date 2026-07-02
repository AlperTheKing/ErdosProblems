# C5-RS Layer-Set Subset Profile

Date: 2026-07-01

Claude exact-falsified the row-majorization reduction (RM). The live C5-RS route is therefore the direct tau-threshold layer-cake. This note records the finite subset form used for the next gate.

## Equivalent subset form

For a length-5 row `Q=(q0,...,q4)` in an all-length-5 K-component, set

```text
s_i = Tw_C(q_i)
tau = 5m/N
eta = N^2/25 - m
```

C5-RS is equivalent to the 31 subset inequalities

```text
sum_{i in A} (s_i - tau) <= (1 + 25/N) eta
```

for every nonempty `A subset {0,1,2,3,4}`. The left side maximized over `A` is exactly `sum_i max(0,s_i-tau)`.

The stronger local candidate C5-LIFT-PMS is equivalently the same subset family with budget

```text
(25/N + 2/3) eta.
```

## Diagnostic script

```text
problems/23/writeup/_codex_c5rs_subset_profile.py
```

It classifies nonempty masks by dihedral orbit on the 5-cycle:

```text
10000, 11000, 10100, 11100, 11010, 11110, 11111
```

and records exact minimum C5-RS and C5-LIFT margins by orbit.

## Local exact results

Named + census `N=8..10`, positive eta only:

```text
cuts: 18244
rows: 79840
over_rows: 36
subset_checks: 2475040
c5_fails: 0
lift_fails: 0
```

Minimum C5-LIFT margins by orbit:

```text
10000: 103/75
11000: 337/300
10100: 187/300
11100: 131/150
11010: 28/75
11110: 13/30
11111: 0
```

The unique local tight positive-eta C5-LIFT case is the full mask `11111` on the equality atom:

```text
I?BD@g]Qo, N=10, m=3, eta=1, tau=3/2,
s=[2,34/15,32/15,34/15,2], row_sum=32/3.
```

Census `N=11`, positive eta only:

```text
cuts: 171182
rows: 1045374
over_rows: 0
subset_checks: 32406594
c5_fails: 0
lift_fails: 0
```

Minimum C5-LIFT margins by orbit:

```text
10000: 873/550
11000: 773/550
10100: 304/275
11100: 254/275
11010: 254/275
11110: 204/275
11111: 14/25
```

## Interpretation

1. The false RM route tried to compare row loads to C5 class sizes. The subset profile avoids class majorization entirely.
2. In exact census, every proper mask has substantial positive C5-LIFT margin. Tightness is isolated in the full-mask active-all-five branch.
3. The next proof split should be:

```text
full mask 11111: row-sum stability / weighted pentagonal branch;
proper masks: direct level-set surplus bound, likely easier and independent of C5-hom majorization.
```

This is not a proof. It is a finite layer-set map for the next exact gate.

## Weighted quotient subset-orbit check

The same proper-mask/full-mask split was checked on the two C5-hom quotient seeds with positive eta, qmax cuts only, length-5 rows only, exhaustive weights in `{1,2}`.

Script:

```text
problems/23/writeup/_codex_c5lift_quotient_subset_profile.py
```

Equality seed `I?BD@g]Qo`:

```text
checked_weights: 1024
checked_rows: 45710
subset_checks: 1417010
first_c5_fail: None
first_lift_fail: None
min C5-LIFT by orbit:
10000: 79/44
11000: 175/132
10100: 83/66
11100: 26/33
11010: 61/66
11110: 5/11
11111: 0
```

Sibling seed `I?`FAo]]?`:

```text
checked_weights: 1024
checked_rows: 43286
subset_checks: 1341866
first_c5_fail: None
first_lift_fail: None
min C5-LIFT by orbit:
10000: 19/11
11000: 169/132
10100: 157/132
11100: 49/66
11010: 113/132
11110: 9/22
11111: 1/3
```

This supports a sharper split:

```text
PROPER-MASK LIFT: for every nonempty proper A subset {0,...,4},
  sum_{i in A}(s_i-tau) <= (25/N + 2/3) eta.

FULL-MASK ROW-SUM: for A={0,...,4}, prove the necessary row-sum bound separately.
```

If PROPER-MASK LIFT is universal, then any C5-LIFT failures at scale must occur only at the full mask, and C5-RS reduces in the L=5 branch to row-sum stability.

## Selected non-C5-hom scale stress

I added a selected larger-graph wrapper:

```text
problems/23/writeup/_codex_c5rs_selected_scale_profile.py
```

It reuses the exact subset-profile arithmetic but feeds heuristic connected max cuts for larger examples where gmins is not feasible.

Petersen[2], 300 local-search seeds:

```text
n: 20
heuristic_best_cut_edges: 48
connected_best_cuts_used: 5
rows: 1920
subset_checks: 59520
c5_fails: 0
lift_fails: 0
min C5-LIFT by every orbit: 23/3
```

MycGrotzsch, 5000 local-search seeds with the new wrapper:

```text
n: 23
heuristic_best_cut_edges: 55
connected_best_cuts_used: 1
rows: 570
subset_checks: 17670
c5_fails: 0
lift_fails: 0
min C5-LIFT by orbit:
10000: 369953/72450
11000: 127307/22425
10100: 837932/470925
11100: 171348/52325
11010: 1646419/941850
11110: 1091962/470925
11111: 78094/20475
```

This did not reproduce Claude's earlier MycGrotzsch sharp C5-LIFT failure. Comparing against the older `_hardy_gate.maxcut_ls` side explains the mismatch: the older helper returned a connected cut of value 54, while the wrapper found a connected one-flip-stable cut of value 55.

On the older value-54 side:

```text
side: 10101101011001000000001
cut_edges: 54
rows: 556
subset_checks: 17236
c5_fails: 0
lift_fails: 56
first lift failure:
  orbit: 11010
  mask: 11010
  lift_margin: -284895070429/364286352150
  N=23, m=17, eta=104/25, tau=85/23
  f=[1,11], Q=[1,2,12,22,11]
  s=[
    245161302859/47515611150,
    623964665572/109285905645,
    7178076827/2428575681,
    503627524586/60714392025,
    22924088093/7750773450
  ]
```

Interpretation: proper-mask C5-LIFT can fail on a connected non-maximum heuristic cut. In the better value-55 local-search cut I found, all masks pass with large margin. Therefore the MycGrotzsch "sharp 2/3 failure" should not be treated as trusted max-cut evidence unless the cut is independently certified maximum/gamma-minimal.

## Exact MycGrotzsch max-cut audit

I added an exact max-cut/profile audit:

```text
problems/23/writeup/_codex_mycgrotzsch_exact_maxcut_c5lift.py
```

It enumerates all cuts with vertex `0` gauge-fixed, using Gray-code updates, then filters connected max cuts and gamma-min connected max cuts before running the exact C5 subset-profile check.

Command:

```text
python problems/23/writeup/_codex_mycgrotzsch_exact_maxcut_c5lift.py
```

Result:

```text
n: 23
edges: 71
exact_maxcut_value: 55
maxcut_complement_classes: 1
connected_maxcut_classes: 1
min_gamma_connected_maxcuts: 400
gamma_min_connected_classes: 1
first_gamma_min_side: 00000111110111111111100

connected gamma-min max cuts:
  cuts: 1
  rows: 570
  over_rows: 0
  subset_checks: 17670
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_10000: 369953/72450
  min_lift_orbit_11000: 127307/22425
  min_lift_orbit_10100: 837932/470925
  min_lift_orbit_11100: 171348/52325
  min_lift_orbit_11010: 1646419/941850
  min_lift_orbit_11110: 1091962/470925
  min_lift_orbit_11111: 78094/20475
```

This proves the earlier value-54 MycGrotzsch proper-mask failure is not a max-cut/gamma-min witness. The exact unique connected gamma-min maximum cut has no C5-RS or C5-LIFT failures on any mask.

## Exact Petersen[2] max-cut audit

Using the same exact max-cut enumeration functions as the MycGrotzsch audit, Petersen[2] also has a certified proper-mask profile.

Result:

```text
n: 20
edges: 60
exact_maxcut_value: 48
maxcut_complement_classes: 5
connected_maxcut_classes: 5
min_gamma_connected_maxcuts: 300
gamma_min_connected_classes: 5
first_gamma_min_side: 00001100111111000000

connected gamma-min max cuts:
  cuts: 5
  rows: 1920
  over_rows: 0
  subset_checks: 59520
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_10000: 23/3
  min_lift_orbit_11000: 23/3
  min_lift_orbit_10100: 23/3
  min_lift_orbit_11100: 23/3
  min_lift_orbit_11010: 23/3
  min_lift_orbit_11110: 23/3
  min_lift_orbit_11111: 23/3
```

Thus both named non-C5-hom scale guardrails mentioned in Claude's warning now pass exact connected gamma-min max-cut C5-LIFT checks: Petersen[2] and MycGrotzsch.

## Exact Mycielski(Petersen) max-cut audit

I also exact-audited `Mycielski(Petersen)`, another feasible non-C5-hom scale guardrail.

Result:

```text
n: 21
edges: 55
exact_maxcut_value: 42
maxcut_complement_classes: 15
connected_maxcut_classes: 15
min_gamma_connected_maxcuts: 325
gamma_min_connected_classes: 15
first_gamma_min_side: 010111110001011111000

connected gamma-min max cuts:
  cuts: 15
  rows: 3570
  over_rows: 0
  subset_checks: 110670
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_10000: 40483/8925
  min_lift_orbit_11000: 24991/4725
  min_lift_orbit_10100: 31183/8925
  min_lift_orbit_11100: 341147/80325
  min_lift_orbit_11010: 77549/26775
  min_lift_orbit_11110: 293147/80325
  min_lift_orbit_11111: 50821/11475
```

## Tight proper-mask witness pattern, census N<=10

Dumping the exact minimum C5-LIFT proper-mask records over census `N=8..10`, positive eta only, shows the small proper-mask margins come from two simple atoms:

- size 1/2/3 proper masks: N=8, `m=2`, `eta=14/25`, `tau=5/4`, rows with loads
  `s=[1,1,2,1,2]` or `s=[1,3/2,2,1,2]`;
- size 4 proper mask: N=10 sibling atom `I?`FAo]]?`, `m=3`, `eta=1`, `tau=3/2`, row with
  `s=[2,34/15,31/15,12/5,8/5]`.

This suggests the proper-mask branch is not a C5-class-size majorization problem; it is a direct active-set/layer-cake problem where the active set is proper and the reciprocal slack `25 eta/N` is essential.

## Exact Mycielski odd-cycle family audit

I exact-audited `Mycielski(C7)`, `Mycielski(C9)`, and `Mycielski(C11)` using the same gauge-fixed max-cut enumeration and C5 subset-profile checker.

```text
Mycielski(C7):
  n: 15
  edges: 28
  exact_maxcut_value: 23
  maxcut_complement_classes: 7
  connected_maxcut_classes: 7
  min_gamma_connected_maxcuts: 125
  gamma_min_connected_classes: 7
  rows: 196
  over_rows: 0
  subset_checks: 6076
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_11111: 65/12

Mycielski(C9):
  n: 19
  edges: 36
  exact_maxcut_value: 30
  maxcut_complement_classes: 9
  connected_maxcut_classes: 9
  min_gamma_connected_maxcuts: 150
  gamma_min_connected_classes: 9
  rows: 324
  over_rows: 0
  subset_checks: 10044
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_11111: 3413/300

Mycielski(C11):
  n: 23
  edges: 44
  exact_maxcut_value: 37
  maxcut_complement_classes: 11
  connected_maxcut_classes: 11
  min_gamma_connected_maxcuts: 175
  gamma_min_connected_classes: 11
  rows: 484
  over_rows: 0
  subset_checks: 15004
  c5_fails: 0
  lift_fails: 0
  min_lift_orbit_11111: 1819/100
```

These exact non-C5-hom scale graphs have no overloaded rows and no C5-LIFT failures on connected gamma-min maximum cuts. They support the split that non-C5-hom scale examples are guardrails for the non-overloaded/proper-mask layer-cake branch, not counterexamples to the sharp overloaded C5-hom branch.
