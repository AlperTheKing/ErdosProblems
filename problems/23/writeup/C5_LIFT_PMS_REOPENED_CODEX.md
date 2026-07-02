# C5-LIFT-PMS Reopened After Exact Max-Cut Audit

Date: 2026-07-01

This note records a status correction for the equal-length `L=5` branch of
ROWSUM/GERSH.

## Statement

For an all-length-5 K-component row `Q=(q0,...,q4)`, define

```text
s_i = Tw_C(q_i),
tau = 5m/N,
eta = N^2/25 - m,
d(Q) = sum_i max(0, tau - s_i).
```

The stronger C5-LIFT-PMS target is

```text
row_sum(Q) + d(Q) <= N + (2/3) eta.
```

Equivalently, since `5tau = N - 25eta/N`,

```text
sum_i max(0, s_i - tau) <= (25/N + 2/3) eta.
```

Equivalently again, for every nonempty subset `A subset {0,...,4}`,

```text
sum_{i in A} (s_i - tau) <= (25/N + 2/3) eta.
```

This is stronger than the C5-RS budget `(25/N + 1) eta`, and it implies the
equal-length `L=5` rowwise GERSH branch.

## Status Correction

Claude previously warned that sharp C5-LIFT could fail at non-C5-hom scale,
based on a MycGrotzsch local-search cut. I exact-audited that case.

The alleged failing MycGrotzsch side has cut value `54`. Exact Gray-code
enumeration shows the true maximum cut value is `55`, with a unique connected
gamma-min maximum cut. On that exact cut:

```text
rows=570,
over_rows=0,
subset_checks=17670,
c5_fails=0,
lift_fails=0.
```

All C5-LIFT subset margins are positive, including the full mask.

The same exact connected gamma-min max-cut audit gives full C5-LIFT pass on:

```text
Petersen[2]:
  n=20, exact_maxcut=48, gamma_min_cuts=5,
  rows=1920, lift_fails=0, min every orbit=23/3.

Mycielski(Petersen):
  n=21, exact_maxcut=42, gamma_min_cuts=15,
  rows=3570, lift_fails=0.

Mycielski(C7):
  n=15, exact_maxcut=23, gamma_min_cuts=7,
  rows=196, lift_fails=0.

Mycielski(C9):
  n=19, exact_maxcut=30, gamma_min_cuts=9,
  rows=324, lift_fails=0.

Mycielski(C11):
  n=23, exact_maxcut=37, gamma_min_cuts=11,
  rows=484, lift_fails=0.
```

Therefore the current trusted state is:

```text
No exact connected gamma-min maximum-cut counterexample to C5-LIFT-PMS is known.
```

The previous MycGrotzsch warning should be treated as a non-maximum-cut artifact,
not as evidence against the theorem.

## Consequence

The proper-mask-only target remains useful, but the stronger full C5-LIFT-PMS
should now be treated as live again. If exact-gated on Claude's full battery, it
would replace the proper-mask/full-mask split by one inequality:

```text
sum_i max(s_i, tau) <= N + (2/3) eta.
```

This would close the equal-length `L=5` branch at a stronger-than-needed margin.

## Guardrails

Still do not use the three false reductions:

```text
sum_i (s_i - N/5)_+ <= eta                       # false HL
row-majorization by C5 class sizes               # false RM
all length-5 components are C5-hom               # false, Grotzsch
```

The live proof must control the actual `tau=5m/N` layer-cake or prove the
weighted pentagonal stability directly.


## Proper-Active Coefficient Probe

I added a coefficient gate:

```text
problems/23/writeup/_codex_c5lift_active_proper_gate.py
```

For proper-active rows, i.e. active set

```text
A={i:s_i>tau} != {0,1,2,3,4},
```

it tests

```text
row_sum(Q) + d(Q) - N <= c eta.
```

The tempting stronger coefficient `c=1/3` is false on the weighted sibling
quotient with weights in `{1,2}`:

```text
graph=sib, N=15, m=7, eta=2, tau=7/3,
side=0001111001,
weights=[2,1,2,1,2,1,2,1,1,2],
Q=[3,8,6,1,9],
s=[37/17, 1293/323, 7153/2261, 443/133, 3],
row_sum=35439/2261,
d=8/51,
debt=5636/6783,
debt - eta/3 = 1114/6783.
```

The next clean coefficient `c=1/2` passes the local exact gates I ran:

```text
N=8..10 + named:
  proper_rows=74436, fails=0, worst_margin=1/10.

N=11 census:
  proper_rows=779785, fails=0, worst_margin=331/550.

weighted quotient equality seed, weights in {1,2}, qmax cuts:
  proper_rows=41040, fails=0, worst_margin=19/66.

weighted quotient sibling seed, weights in {1,2}, qmax cuts:
  proper_rows=39950, fails=0, worst_margin=1147/6783.
```

This suggests a cleaner proof split:

```text
proper-active branch:
  row_sum(Q)+d(Q) <= N + eta/2;

active-all-five branch:
  row_sum(Q) <= N + (2/3) eta.
```

Together these imply full C5-LIFT-PMS. The proper-active branch is strictly
easier than the full active-all-five row-sum branch, but `eta/3` is too sharp.

### Exhaustive quotient weights in {1,2,3}

The same `PROPER-ACTIVE HALF` gate also passes exhaustive qmax quotient scans with weights in `{1,2,3}`:

```text
Equality seed I?BD@g]Qo:
  weights=59049,
  qmax cuts=145957,
  proper_rows=1456465,
  fails=0,
  worst_margin=109/380,
  worst weights=[1,1,1,1,1,3,3,3,3,3].

Sibling seed I?`FAo]]?:
  weights=59049,
  qmax cuts=125821,
  proper_rows=1527168,
  fails=0,
  worst_margin=1147/6783,
  same witness as the weights-{1,2} run.
```

The `eta/3` coefficient is still false; `eta/2` has now survived exact census through `N=11` and both weighted quotient seeds through max weight `3`.

## Proof Split After Proper-Active Half Gate

Current live decomposition for full C5-LIFT-PMS:

```text
sum_i max(s_i,tau) <= N + (2/3)eta
```

is now:

```text
(A) Proper-active half:
    if some row coordinate is inactive (s_j <= tau), then
    sum_i max(s_i,tau) <= N + eta/2.

(B) Active-all-five stability:
    if all five coordinates are active, then
    row_sum(Q) <= N + (2/3)eta.
```

The split is exact because `eta/2 <= 2eta/3`. The coefficient `eta/3` in (A) is false; the weighted sibling quotient witness shows the proper-active branch has genuine debt between `eta/3` and `eta/2`.

This suggests different proof mechanisms:

```text
proper-active branch:
  layer-set / side-door proof using at least one inactive coordinate as a real drain;
  likely not C5-class majorization, because RM is false.

active-all-five branch:
  row-sum stability / weighted pentagonal PMS proof;
  this is where the sparse equality atom lives.
```

A useful next exact-testable refinement for (A): split proper-active rows by active-set arcs on the 5-cycle. Since any proper active set has a nonempty inactive boundary, a proof can charge active arcs to inactive drains. The current worst exact records are active-4 with one inactive endpoint; smaller active sets have substantially larger margin.

### Random quotient weights up to 100

I also ran an in-memory random stress using the existing weighted quotient functions directly, with `5000` random weight vectors in `[1,100]` and qmax cuts only.

```text
Equality seed:
  samples=5000,
  qmax cuts=5115,
  proper_rows=51998,
  fails=0,
  worst_margin=2721639315064890/5175554630119.

Sibling seed:
  samples=5000,
  qmax cuts=5105,
  proper_rows=63025,
  fails=0,
  worst_margin=20384878291/29929950.
```

These random cases are not near-tight; the exact small-weight sibling witness remains the current closest proper-active half case.

### Proper-active debt by active-mask orbit, quotient weights {1,2,3}

I computed exact maxima of `debt/eta` by dihedral orbit of the active mask for the two quotient seeds, weights in `{1,2,3}`, qmax cuts only.

Equality seed:

```text
10000: -7/8
11000: -1175/2114
10100: -7675/27482
11100: -3175/13741
11010: -175/1963
11110: 81/380
```

Sibling seed:

```text
00000: -25/26
10000: -7775/13741
11000: -11225/27482
10100: -557/2380
11100: 557/6783
11010: 710875/32540768
11110: 2818/6783
```

Thus, in these exact quotient scans, all serious positive proper-active debt is active-size `4` (one inactive coordinate). Active-size `<=3` is either negative or very small; the only positive size-3 orbit above is `557/6783 < 1/10`.

A finer live split is therefore:

```text
active size <= 3:
  row_sum+d-N <= eta/10      (candidate; needs broader gate)

active size = 4:
  row_sum+d-N <= eta/2       (current proper-active half)
```

This would make the proper-active proof a one-inactive-coordinate problem plus a much easier low-active branch.

### Active-low tenth gate

I extended `_codex_c5lift_active_proper_gate.py` with active-size filters:

```text
--active-min k
--active-max k
```

This makes the finer proper-active split directly testable.

Candidate:

```text
ACTIVE-LOW TENTH:
  if |{i:s_i>tau}| <= 3, then row_sum(Q)+d(Q)-N <= eta/10.
```

Exact local gates:

```text
N=8..10 census + named:
  cuts=18259,
  proper_rows(active<=3)=54855,
  fails=0,
  worst_margin=7/125.

N=11 census:
  cuts=171182,
  proper_rows(active<=3)=354675,
  fails=0,
  worst_margin=509/4125.

weighted quotient equality seed, weights in {1,2}:
  cuts=4156,
  proper_rows(active<=3)=20570,
  fails=0,
  worst_margin=59/165.

weighted quotient sibling seed, weights in {1,2}:
  cuts=3330,
  proper_rows(active<=3)=24454,
  fails=0,
  worst_margin=1213/33915.
```

The closest active-low case is the sibling quotient witness with active set
`[0,1,2]`:

```text
N=15, m=7, eta=2, tau=7/3,
weights=[2,1,2,1,2,1,2,1,1,2], side=0001111001,
Q=(1,6,8,3,7),
s=[443/133, 7153/2261, 1293/323, 37/17, 1],
row_sum=30917/2261,
d=76/51,
debt=1114/6783,
eta/10 - debt = 1213/33915.
```

This supports the sharper decomposition:

```text
active size <= 3: debt <= eta/10;
active size = 4:  debt <= eta/2;
active all five: row_sum <= N + (2/3)eta.
```

The max-weight `{1,2,3}` quotient orbit table already had active-size `<=3`
worst ratio `557/6783 < 1/10`; direct max-weight-3 filtered scans were too slow
with the current unoptimized script and should be delegated or optimized before
claiming a full exact max-weight-3 gate.

### Active4 half isolated gate

After adding active-size filters, I also isolated the active-size `4` branch under
`ACTIVE4 HALF`:

```text
if |{i:s_i>tau}| = 4, then row_sum(Q)+d(Q)-N <= eta/2.
```

Exact local gates:

```text
N=8..10 census + named:
  cuts=18259,
  active4_rows=19581,
  fails=0,
  worst_margin=4/15.

N=11 census:
  cuts=171182,
  active4_rows=425110,
  fails=0,
  worst_margin=331/550.

weighted quotient equality seed, weights in {1,2}:
  cuts=4156,
  active4_rows=20470,
  fails=0,
  worst_margin=19/66.

weighted quotient sibling seed, weights in {1,2}:
  cuts=3330,
  active4_rows=15496,
  fails=0,
  worst_margin=1147/6783.
```

The closest active4 case remains the sibling quotient witness:

```text
N=15, m=7, eta=2, tau=7/3,
weights=[2,1,2,1,2,1,2,1,1,2], side=0001111001,
Q=(3,8,6,1,9),
s=[37/17, 1293/323, 7153/2261, 443/133, 3],
row_sum=35439/2261,
d=8/51,
debt=5636/6783,
eta/2 - debt = 1147/6783.
```

In exact census `N<=11`, active4 is not near the `eta/2` boundary; the closest
pressure comes from weighted quotient scaling of the sibling atom.

### Max-weight `{1,2,3}` quotient orbit gates

I added deterministic sharding and JSON summaries to
`_codex_c5lift_active_size_quotient_fast.py`, plus a 64-worker runner:

```text
python problems/23/writeup/_codex_parallel_active_gate.py ...
```

This closes the earlier "too slow" note.  Exact weighted quotient scans with
weight orbits and weights in `{1,2,3}` give:

```text
ACTIVE-LOW TENTH, equality seed:
  rows_checked=87508,
  fails=0,
  worst_margin=5/19.

ACTIVE-LOW TENTH, sibling seed:
  rows_checked=498534,
  fails=0,
  worst_margin=1213/33915.

ACTIVE4 HALF, equality seed:
  rows_checked=75077,
  fails=0,
  worst_margin=109/380.

ACTIVE4 HALF, sibling seed:
  rows_checked=285516,
  fails=0,
  worst_margin=1147/6783.
```

The sibling extremizers at weights `{1,2}` remain the closest cases after
extending to `{1,2,3}`.

### Active-all-five `{1,2,3}` quotient orbit gates

I removed the diagnostic skip for `active_count=5` in
`_codex_c5lift_active_size_quotient_fast.py`, so the same 64-worker runner can
test the active-all-five row-sum stability branch:

```text
row_sum(Q) <= N + (2/3) eta.
```

Exact weighted quotient scans with weight orbits and weights in `{1,2,3}` give:

```text
ACTIVE5 2/3, equality seed:
  rows_checked=16608,
  fails=0,
  worst_margin=0.

ACTIVE5 2/3, sibling seed:
  rows_checked=55885,
  fails=0,
  worst_margin=1/3.
```

The equality seed worst case is the expected sparse PMS atom:

```text
N=10, m=3, eta=1, tau=3/2,
weights=[1,1,1,1,1,1,1,1,1,1], side=0001111000,
Q=(7,5,8,6,9),
s=[2,34/15,32/15,34/15,2],
row_sum=32/3,
row_sum - N = 2/3 = (2/3)eta.
```

Thus the current active-size decomposition has survived the equality and
sibling quotient seeds through max weight `3` in all three branches:
active `<=3`, active `=4`, and active `=5`.

### Active-all-five `{1,2,3,4}` quotient orbit gates

After the OHDX refinement, the only full-row C5 quotient burden is the
active-all-five overfull branch.  I reran the active-5 gate with weight orbits
and weights in `{1,2,3,4}`:

```text
python problems/23/writeup/_codex_parallel_active_gate.py --graph eq --max-weight 4 --coeff 2/3 --active-min 5 --active-max 5 --workers 56 --shards 56 --weight-orbits

weights=1048576
orbit_skips=941664
qmax_cuts=213213
rows_checked=207739
fails=0
worst_margin=0
worst all-ones equality atom:
  N=10, m=3, eta=1,
  Q=(7,5,8,6,9),
  row_sum=32/3,
  debt=2/3.

python problems/23/writeup/_codex_parallel_active_gate.py --graph sib --max-weight 4 --coeff 2/3 --active-min 5 --active-max 5 --workers 56 --shards 56 --weight-orbits

weights=1048576
orbit_skips=522240
qmax_cuts=926894
rows_checked=754765
fails=0
worst_margin=1/3
worst all-ones sibling atom:
  N=10, m=3, eta=1,
  Q=(1,6,8,4,9),
  row_sum=31/3,
  debt=1/3.
max_ratio_by_active_mask worst ratio:
  1028/2261 at weights [2,1,2,1,2,1,2,1,1,2],
  margin 2876/6783.
```

This is evidence only for the active-all-five full-row stability branch
`row_sum <= N + (2/3)eta`.  It does not revive the later fixed-mask or
active-size split with small proper-mask coefficients; that split is killed by
the exact Myc(Grotzsch) guardrail below.

### Fixed-mask-size strengthening

The active-size split can be strengthened to fixed row masks.  For every
nonempty mask `A subset {0,...,4}`, define

```text
L(A) = sum_{i in A} (s_i - tau).
```

The exact-testable strengthening is:

```text
|A| <= 3:  L(A) <= (25/N + 1/10) eta,
|A| = 4:  L(A) <= (25/N + 1/2) eta,
|A| = 5:  L(A) <= (25/N + 2/3) eta.
```

This implies the active-size split by taking `A={i:s_i>tau}`, but is cleaner
as a layer-cake proof target because `A` is fixed in advance.

I added the exact gates:

```text
problems/23/writeup/_codex_c5_masksize_split_gate.py
problems/23/writeup/_codex_parallel_c5_masksize_gate.py
```

Results:

```text
N=8..10 census + named:
  cuts=18259,
  rows=80320,
  mask_checks=2489920,
  fails=0.

N=11 census, positive eta:
  cuts=171182,
  rows=1045374,
  mask_checks=32406594,
  fails=0.
```

The `N=11` closest margins by mask size are:

```text
size 1: 1528/1375
size 2: 1731/2750
size 3: 509/4125
size 4: 331/550
size 5: 14/25
```

The size-3 and size-4 minima match the earlier active-low and active4
branch pressures, so the fixed-mask strengthening did not expose a worse
census obstruction.

I also added the weighted quotient runner:

```text
problems/23/writeup/_codex_parallel_c5_masksize_quotient.py
```

Exact weighted quotient scans with weight orbits and weights in `{1,2,3}`:

```text
fixed-mask split, equality seed:
  rows=179193,
  mask_checks=5554983,
  fails=0,
  worst size 1: 177/190
  worst size 2: 39/76
  worst size 3: 13/95
  worst size 4: 109/380
  worst size 5: 0.

fixed-mask split, sibling seed:
  rows=839935,
  mask_checks=26037985,
  fails=0,
  worst size 1: 169/190
  worst size 2: 179/380
  worst size 3: 1213/33915
  worst size 4: 1147/6783
  worst size 5: 1/3.
```

Again the closest quotient cases are the same size-3 and size-4 sibling
atoms found by the active-set gate; no fixed non-active mask is worse through
weight `3`.

### Active-mask orbit profile, `{1,2,3}` weights

I also added active-mask orbit aggregation to the same scanner.  Here the
active mask is

```text
{i : s_i > tau}
```

canonicalized under the dihedral group of the row cycle.

Running the full C5-LIFT margin

```text
row_sum(Q)+d(Q) <= N+(2/3)eta
```

over all active masks, with weight orbits and weights in `{1,2,3}`, gives:

```text
Equality seed:
  rows_checked=179193,
  fails=0,
  active mask counts:
    10000: 258
    10100: 7407
    11000: 4213
    11010: 64905
    11100: 10725
    11110: 75077
    11111: 16608
  worst_margin=0 at mask 11111, the sparse PMS atom.

Sibling seed:
  rows_checked=839935,
  fails=0,
  active mask counts:
    00000: 38
    10000: 6091
    10100: 89936
    11000: 34611
    11010: 245821
    11100: 122037
    11110: 285516
    11111: 55885
  worst_margin=1/3 at mask 11111.
```

Among proper active masks, the closest C5-LIFT margins in these quotient
profiles are active-4 masks.  This matches the coefficient split: proper masks
need the inactive-drain argument, while the only tight C5-LIFT equality remains
the full-mask sparse PMS atom.

### Active-mask `debt/eta` ratios

For coefficient discovery, I also record the maximum exact ratio

```text
debt(Q) / eta = (row_sum(Q)+d(Q)-N) / eta
```

by active-mask orbit in the same `{1,2,3}` quotient stress.

Equality seed:

```text
10000: -7/8
10100: -7675/27482
11000: -1175/2114
11010: -175/1963
11100: -3175/13741
11110: 81/380
11111: 2/3
```

Sibling seed:

```text
00000: -25/26
10000: -7775/13741
10100: -557/2380
11000: -11225/27482
11010: 710875/32540768
11100: 557/6783
11110: 2818/6783
11111: 1028/2261
```

In these quotient stresses, active masks with at most three active vertices stay
below `1/10`; active-4 stays below `1/2`; active-all-five is governed by the
separate row-sum stability coefficient, tight at `2/3` only in the equality
seed.

### Fixed-mask-size layer-set strengthening

I added a stronger exact gate:

```text
problems/23/writeup/_codex_c5_masksize_split_gate.py
```

For every nonempty mask `A subset {0,...,4}` it tests

```text
sum_{i in A}(s_i - tau) <= (25/N + c_|A|) eta,
```

with

```text
c_1=c_2=c_3=1/10,
c_4=1/2,
c_5=2/3.
```

This is stronger than bounding only the actual active set, and it is a cleaner
layer-cake target: any positive part is controlled by applying the relevant
mask inequality to `A={i:s_i>tau}`.

Exact gates:

```text
N=8..10 census + named:
  checks=2489920,
  fails=0.

N=11 census, positive eta only, 60-worker graph-sharded run:
  cuts=171182,
  rows=1045374,
  checks=32406594,
  fails=0.
```

The N=11 minimum margins by mask size are:

```text
size 1: 1528/1375
size 2: 1731/2750
size 3: 509/4125
size 4: 331/550
size 5: 14/25
```

The tightest proper-mask pressure in N=11 is orbit `11010`, size `3`, at
margin `509/4125`; the full mask margin is `14/25` in this census slice.

### Exact Myc(Grotzsch) guardrail falsifies fixed-mask and active-size splits

I added:

```text
problems/23/writeup/_codex_exact_named_c5_masksize_gate.py
```

This enumerates true maximum cuts, filters to connected-B gamma-min cuts, and
then applies the fixed-mask gate.  The small smoke cases passed:

```text
Petersen + Grotzsch:
  cuts=10, rows=215, checks=6665, fails=0.

Petersen[2]:
  cuts=5, rows=1920, checks=59520, fails=0.

Myc(Petersen):
  cuts=15, rows=3570, checks=110670, fails=0.
```

But the exact `Myc(Grotzsch)` gamma-min max cut falsifies the proposed
fixed-mask-size strengthening:

```text
N=23, m=16, eta=129/25, tau=80/23
side=00000111110111111111100
f=(5,12)
Q=(5,10,16,22,12)
s=(737/210, 11147/1638, 232/117, 935/126, 23813/8190)

mask=01010, size=2
lhs=136933/18837
budget=(25/N+1/10)eta=35217/5750
margin=-5390527/4709250.
```

The same row also falsifies the weaker active-size split with the proposed
`1/10` coefficient for active sets of size at most three:

```text
active={0,1,3}
active_lhs=1375219/188370
budget=(25/N+1/10)eta=35217/5750
active_margin=-2768876/2354625.
```

However the actual C5-RS/ROWSUM reciprocal-slack target survives this row:

```text
(25/N+1)eta - sum_i max(0,s_i-tau) = 3266401/941850 > 0.
```

Conclusion: the fixed-mask and active-size coefficient split is dead.  The
live target must keep the full `+ eta` reciprocal slack, or use a different
decomposition that can transfer slack across the active layers.
