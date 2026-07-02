# Slack-CAGE Proof Target

Status: new exact-supported candidate, not proved.  This replaces the false
uniform DEFICIT-CAGE Hall transport suggested by GPT-Pro on 2026-07-01.

## Definitions

Fix a connected-B gamma-minimum maximum cut.  Let `M` be the bad edges,
`m=|M|`, and `cyc[g]` the shortest B-geodesic rows for `g`.

For a fixed bad row `Q in cyc[f]` and vertex set `U`, define the row-cage
demand

```text
D_Q(U)
  = sum_{g in M} (1/|cyc[g]|)
      * sum_{P in cyc[g], V(P) subset U} |V(P) cap V(Q)|.
```

Let

```text
eta = N^2/25 - m,
sigma(U) = delta_B(U) - delta_M(U).
```

The proposed **slack-CAGE** inequality is:

```text
D_Q(U) <= |U| + sigma(U) + eta
```

for every fixed row `Q` and every `U subset V`.

At `U=V`, this gives rowwise GERSH:

```text
sum_{v in Q} Tw(v) = D_Q(V) <= N + eta.
```

Thus slack-CAGE implies the corrected ROWSUM/GERSH target recorded in
`CV_PERCOMP_SPECTRAL.md`.

## Dead Uniform Hall Variant

GPT-Pro first suggested a uniform-capacity Hall condition:

```text
D_Q(U) <= ((N + eta)/N) * |U|.
```

Exact gate:

```text
python problems/23/writeup/_codex_deficit_cage_gate.py \
  --stop-first --min-n 7 --max-n 9 --two-lane-max 20 \
  --blowup-t 3 --blowup-nmax 20 --max-cuts 4
```

Result:

```text
FAIL at two-lane-L8
N=27, m=4, A=1304/25
Q=(0,1,2,3,4,5,6)
U=(0,1,2,3,4,5,6,7,8)
D_Q(U)=24
((N+eta)/N)|U|=1304/75
excess=496/75
```

The failure shows the deficit budget cannot be spread uniformly over all
vertices.  It must localize through cut slack or a more structured corridor
capacity.

For the same witness,

```text
|U|=9,
sigma(U)=18,
eta=629/25,
```

so slack-CAGE gives `24 <= 9+18+629/25`.

## Surgical Exact Probe

A scratch exact probe tested slack-CAGE on:

- all subsets of pure `C7` and `C9`;
- all subsets of the N=10 PMS equality atom `I?BD@g]Qo` with side
  `0001111000`;
- row/corridor interval subsets for two-lane `L=8,12,20`.

Result:

```text
C7: PASS, min margin 24/25 at U=empty
C9: PASS, min margin 56/25 at U=empty
I?BD@g]Qo: PASS, min margin 1/3 at U=V for row (7,5,8,6,9)
two-lane-L8 rowsets: PASS, min margin 604/25 at U=V for row (0..8)
two-lane-L12 rowsets: PASS, min margin 1296/25 at U=V for row (0..12)
two-lane-L20 rowsets: PASS, min margin 3544/25 at U=V for row (0..20)
```

This is not a full gate; it is a small sanity check before asking Claude to
run a full exact battery.

## Split Gate Results

After optimizing `_codex_slack_cage_gate.py` to precompute the subset-local
load vector

```text
Tw_U(v) = sum_g (1/|cyc[g]|) * #{P in cyc[g] : P subset U, v in P},
```

the checker ran the following exact split gates.

Two-lane rowset cages:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode rowsets --stop-first --skip-census --skip-blowups \
  --skip-named --two-lane-max 100
```

Result:

```text
checks = 359080
violations = 0
min_margin = 604/25 at two-lane-L8, U=V
```

Direct odd-cycle blowups, rowset cages, through `t=2`:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode rowsets --stop-first --skip-census --skip-two-lane \
  --skip-named --blowup-t 2 --blowup-nmax 26
```

Result:

```text
checks = 1105627
violations = 0
min_margin = 0 at direct-C5[1], U=empty
```

All-subset census through `N=9`:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode all --stop-first --skip-two-lane --skip-blowups \
  --skip-named --min-n 7 --max-n 9 --max-cuts 4
```

Result:

```text
checks = 2903168
violations = 0
min_margin = 14/25 at cenG?`F`w, U=empty
```

The all-subset census was then extended to `N=10` with the parallel exact
checker `_codex_slack_cage_parallel_census.py`, distributing by graph and
adding each row atom to all supermasks of its vertex set.

```text
python problems/23/writeup/_codex_slack_cage_parallel_census.py \
  --n 10 --workers 60 --chunksize 8 --stop-first
```

Result:

```text
graphs = 9832
cuts = 16016
checks = 74895360
violations = 0
min_margin = 0 at cenI?rFf_{N?, U=empty
```

The same run with category minima gave:

```text
min_empty = 0 at cenI?rFf_{N?, U=empty
min_full = 0 at cenI?rFf_{N?, U=V
min_proper_nonempty = 1
  at cenI?AAD@wF_, Q=(3,8,1,6,9), U=(1,3,4,6,8,9)
```

Thus, in the full `N=10` all-subset census, every interior cage
`empty != U != V` has at least one unit of Slack-CAGE margin.  Equality only
appears at the two global extremes in the balanced `C5` extremal.

Rowset census through `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode rowsets --stop-first --skip-two-lane --skip-blowups \
  --skip-named --min-n 7 --max-n 10 --max-cuts 4
```

Result:

```text
checks = 3642782
violations = 0
min_margin = 0 at cenI?rFf_{N?, U=empty
```

Named rowset cases (`Grotzsch`, `M(C7)`, and `C7|Grotzsch`), capped at two
maximum cuts:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode rowsets --stop-first --skip-census --skip-two-lane \
  --skip-blowups --max-cuts 2
```

Result:

```text
checks = 26754
violations = 0
min_margin = 21/25 at Grotzsch, U=empty
```

Named all-subset cases (`Grotzsch`, `M(C7)`, and `C7|Grotzsch`), capped at two
maximum cuts:

```text
python problems/23/writeup/_codex_slack_cage_gate.py \
  --subset-mode all --stop-first --skip-census --skip-two-lane \
  --skip-blowups --max-cuts 2
```

Result:

```text
checks = 18739200
violations = 0
min_margin = 21/25 at Grotzsch, U=empty
```

Balanced odd-cycle blowups were then checked with the quotient script
`_codex_slack_cage_blowup_quotient.py`.  It uses the part symmetry of
`C_c[t]`: relative to a fixed row `Q`, a rowset subset is represented by the
part counts and by the flags saying which parts contain the `Q`-vertex.

```text
python problems/23/writeup/_codex_slack_cage_blowup_quotient.py \
  --cycles 5,7,9 --t 1,2,3
```

Result:

```text
quotient_checks = 5374
expanded_checks_represented = 883400236
violations = 0
min_margin = 0 at C5[1], U=empty
```

The same quotient gate was stretched to `t=1..20`:

```text
python problems/23/writeup/_codex_slack_cage_blowup_quotient.py \
  --cycles 5,7,9 --t 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Result:

```text
quotient_checks = 50254
expanded_checks_represented = 474210084013627378261468
violations = 0
min_margin = 0 at C5[1], U=empty
```

For nonempty proper rowset subsets in the same balanced quotient scan, the
best margin is:

```text
best_proper_rowset_margin = 1
  at C5[1], singleton rowset
```

The generic rowset category scanner
`_codex_slack_cage_rowset_categories.py` was also run on the sparse/named
rowset battery:

```text
python problems/23/writeup/_codex_slack_cage_rowset_categories.py \
  --two-lane-max 100 --skip-blowups
```

Result:

```text
cases = 51
min_empty = 21/25 at Grotzsch, U=empty
min_full = 2498/1575 at Grotzsch, U=V
min_proper_nonempty = 71/25 at Grotzsch, singleton U
INTERIOR_UNIT_GAP = True
```

## Proof Interpretation

The candidate says every row-overlap cage either has enough vertices, enough
max-cut slack on its boundary, or enough global bad-edge deficit.  The full
set `U=V` has zero cut slack and recovers exactly the corrected row cap.

The likely proof shape is a max-cut coarea/Hall argument over cages `U`,
where `sigma(U)` pays local concentration and `eta` pays global sparsity.  It
is strictly weaker than the false uniform-Hall transport but stronger than the
desired rowwise GERSH.

## Balanced Odd-Cycle Blowup Quotient Gate

The dense balanced odd-cycle blowup cases admit a quotient check.  For
`C_L[t]` with the alternating cut leaving only `A_{L-1}A_0` bad, fix a row
`Q` with one distinguished vertex in each class.  A subset `U` is summarized by
class counts `c_i=|U cap A_i|`; the slack-CAGE left side is maximized by
including the distinguished `Q` vertex in every nonempty class.  Thus all clone
subsets reduce to count vectors `c_i in {0,...,t}`.

The quotient checker is:

```text
python problems/23/writeup/_codex_slack_cage_codd_quot.py
```

It uses the exact formula

```text
D_Q(U) = sum_i 1_{c_i>0} prod_{j != i} c_j / t^(L-2),
```

and exact boundary slack between complete bipartite class pairs.

Results:

```text
C5[t], t=1..8: 0 violations, min_margin=0 at U=empty.
C7[t], t=1..7: 0 violations, min_margin=(24/25)t^2 at U=empty.
C9[t], t=1..3: 0 violations, min_margin=(56/25)t^2 at U=empty.
```

This resolves the earlier generic-checker scaling gap for dense balanced
blowups at `t=3`; the quotient check is over all clone-count subsets, not just
rowsets.

## Fresh Direct Census Rerun

On 2026-07-01 I reran the direct all-subset census at `N=10` using:

```text
python problems/23/writeup/_codex_slack_cage_parallel_census.py \
  --n 10 --workers 60 --chunksize 8
```

Windows `multiprocessing` hit the handle limit at 64 workers, so 60 workers is
the clean setting on this machine.

Result:

```text
graphs = 9832
cuts = 16016
checks = 74895360
VERDICT = HOLDS

min_margin = 0
  at eta=0, U=empty / U=V C5 extremal cases.

min_proper_nonempty = 1
  at n=10, m=2, eta=2,
  f=(3,9), Q=(3,8,1,6,9),
  U=(1,3,4,6,8,9),
  lhs=9, rhs=10.
```

## Fixed-Row Zeta Guardrail: Myc(Grotzsch)

I added:

```text
problems/23/writeup/_codex_slack_cage_fixed_row_zeta.py
```

For one fixed row `Q`, it computes `D_Q(U)` for every subset `U` by subset
zeta transform and tracks `sigma(U)` in Gray-code order.  All arithmetic is
exact: row weights are scaled by the common denominator of the shortest-row
bundle sizes.

This was run on the exact `Myc(Grotzsch)` true connected-B gamma-min max cut:

```text
N=23, m=16, eta=129/25
side=00000111110111111111100
```

The row that falsifies the fixed-mask and active-size split,

```text
f=(5,12), Q=(5,10,16,22,12),
```

has:

```text
all-subset min_margin = 129/25 at U=empty,
min_proper_nonempty_margin = 179/25 at U=(11),
min_counted_margin = 113311/20475 at U=V,
VERDICT = PASS.
```

Fresh rerun on 2026-07-01:

```text
python problems/23/writeup/_codex_slack_cage_fixed_row_zeta.py \
  --graph MycGrotzsch
```

Result:

```text
scale = 81900
atoms_used = 496
supermask_additions = 130023424
full_lhs = 92653/4095
full_rhs = 704/25
full_margin = 113311/20475
min_all = 129/25 at U=empty
min_full = 113311/20475 at U=V
min_proper = 179/25 at U=(11)
VERDICT = HOLDS
```

A second full-mask-pressure row,

```text
f=(0,1), Q=(0,6,10,5,1),
```

has the same minima:

```text
all-subset min_margin = 129/25 at U=empty,
min_proper_nonempty_margin = 179/25 at U=(11),
min_counted_margin = 244687/40950 at U=V,
VERDICT = PASS.
```

Thus the exact N=23 guardrail that kills the proposed active/fixed-mask split
does not pressure SLACK-CAGE.  More strongly, in both tested rows the best
subset with any counted row mass (`D_Q(U)>0`) is the full set `U=V`; all proper
subsets that minimize the margin have `D_Q(U)=0` and are irrelevant to the
row-overlap cage.  This keeps SLACK-CAGE as the stronger live proof target
rather than the dead layer-size coefficient split.

## Small Proper Counted Cage Microscope

After adding `min_proper_counted` to:

```text
problems/23/writeup/_codex_slack_cage_parallel_census.py
```

the exact `N=10` all-subset census gives the smallest proper counted margin:

```text
g6 = I?AAD@wF_
side = 0000011110
m = 2
eta = 2
f = (3,9)
Q = (3,8,1,6,9)
U = (1,3,4,6,8,9)
D_Q(U) = 9
|U| = 6
sigma(U) = 2
rhs = |U| + sigma(U) + eta = 10
margin = 1
```

The local structure is two length-5 bad rows inside `U`:

```text
(3,9): 3-8-1-6-9, contribution 5
(4,9): 4-8-1-6-9, contribution 4
```

The blue boundary is:

```text
delta_B(U) = {(2,8), (5,9)}
delta_M(U) = empty
sigma(U) = 2.
```

Enumerating the GPT-Pro cage-switch core conditions inside this `U` finds
exactly two inclusion-minimal zero-slack cages:

```text
S = {3}, sigma(S)=0, DeltaGamma=0
S = {4}, sigma(S)=0, DeltaGamma=0
```

So this near-tight proper counted case is a balanced length-5 cell: zero-slack
switches exist but do not strictly decrease `Gamma`.  This matches the proposed
proof mechanism, where positive SLACK debt must exclude the balanced C5-cell
case before forcing `DeltaGamma<0`.

Equivalently, for the pre-bank quantity

```text
prebank_Q(U) := D_Q(U) - |U| - sigma(U),
```

the full `N=10` census gives:

```text
max prebank_Q(U) = 1,
```

attained at exactly the same microscope witness above.  Since `eta=2` there,
the global deficit bank more than pays for the only positive proper counted
prebank case in the `N=10` census.  This suggests the proof should decompose
positive prebank into balanced length-5 cells paid by `eta`, plus non-balanced
terminal cages forbidden by Gamma-minimality.

With positive-prebank counters enabled, the same `N=10` census reports:

```text
positive_prebank_checks = 48
positive_proper_counted_prebank_checks = 12

positive_prebank_values:
  1:    12
  2/3:  20
  1/3:  6
  1/6:  8
  2/15: 2

positive_proper_counted_prebank_values:
  1: 12
```

So every positive proper counted prebank case in the `N=10` census has the
same unit bank demand as the displayed balanced-cell microscope.  The smaller
fractional prebank values occur only outside the proper-counted bucket.

I then added a classifier:

```text
problems/23/writeup/_codex_slack_cage_prebank_classifier.py
```

It enumerates every positive proper-counted prebank case and then enumerates
the GPT-Pro cage-switch core sets inside `U`.  On the full `N=10` census:

```text
cases = 12
no_zero = 0
no_flat = 0
strict_drop_cases = 0
prebank_values = {1: 12}
VERDICT = PASS_BALANCED
```

Thus every positive proper-counted prebank case in the exact `N=10` census has
at least one zero-slack flat cage (`DeltaGamma=0`), and none has a strict
Gamma-drop cage.  The first case has exactly:

```text
zero/flat cages:
  S={3}, sigma=0, DeltaGamma=0
  S={4}, sigma=0, DeltaGamma=0
```

This supports the refined proof split:

```text
positive proper counted prebank
  = balanced length-5 flat cells paid by eta
    + non-balanced terminal cages forbidden by Gamma-minimality.
```

## Zero-Switch Lemma Audit

The latest GPT-Pro formulation of the zero-slack cage-switch lemma was compared
against `_codex_slack_cage_switch_gate.py`.  The script matches the stated
exact gate conventions:

- minimal positive-debt pair by `(len(U), len(counted_rows))`;
- counted rows are those fully contained in `U` and meeting the fixed row `Q`;
- cage switches require `S subset U`, connected `B^S`, terminal crossing of
  counted rows, blue boundary witnessed by counted-row first exits, and the
  same single-vertex deletion minimality used in the GPT-Pro pseudocode;
- success requires `sigma(S)=0` and `DeltaGamma(S)<0`.

The scripts compile:

```text
python -m py_compile \
  problems/23/writeup/_codex_slack_cage_switch_gate.py \
  problems/23/writeup/_codex_slack_cage_gate.py \
  problems/23/writeup/_codex_slack_cage_parallel_census.py
```

Census-only zero-switch smoke:

```text
python problems/23/writeup/_codex_slack_cage_switch_gate.py \
  --min-n 7 --max-n 9 --max-cuts 16 --skip-named --skip-two-lane
```

Result:

```text
cuts = 2243
no_debt = 2243
positive = 0
switch = 0
fails = 0
VERDICT = VACUOUS_NO_POSITIVE_DEBT
```

Thus the zero-switch lemma remains a contradiction scaffold in the current
finite tests: the stronger Slack-CAGE inequality itself has no positive-debt
pair on this slice.

Random/substructured exact Fraction stress:

```text
python problems/23/writeup/_codex_slack_cage_random_gate.py \
  --samples 120 --seed 230701 --max-cuts 2 --two-lane-max 60 --include-mycg
```

Result:

```text
sides = 44
checks = 1854203
violations = 0
min_margin = 14/25
VERDICT = HOLDS
```

Current proof burden:

```text
minimal positive debt
=> terminal cage decomposition
=> some cage has zero cut slack
=> outside balanced C5 cells, the zero-slack cage strictly decreases Gamma.
```

## All-Row N=23 Zeta Guardrail

The fixed-row profiler was then upgraded to a compiled all-row scanner:

```text
problems/23/writeup/_codex_slack_cage_allrow_zeta.cpp
problems/23/writeup/_codex_slack_cage_allrow_zeta.py
```

For each subset `U`, it computes the subset-local load vector `Tw_U(v)` once
by integer subset-zeta transform and then minimizes the Slack-CAGE margin over
all target rows `Q`. This checks every row against every subset for the
selected graph/cut.

Smoke test on `Grotzsch`:

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph Grotzsch --threads 8
```

Result:

```text
rows = 31
scale = 12600
min_all = 21/25 at U=empty
min_full = 2498/1575 at U=V
min_proper = 71/25 at singleton U=(5)
VERDICT = HOLDS
```

Full exact `Myc(Grotzsch)` guardrail:

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph MycGrotzsch --threads 60 --force-compile
```

Result:

```text
N = 23
m = 16
eta = 129/25
rows = 570
subsets = 2^23
scale = 81900
atoms = 570
target_rows = 570

min_all = 129/25
  row = (0,6,10,5,1)
  U = empty

min_full = 113311/20475
  row = (5,10,16,22,12)
  U = V
  lhs = 92653/4095
  rhs = 704/25

min_proper = 179/25
  row = (0,6,10,5,1)
  U = (11)

VERDICT = HOLDS
```

Thus the full exact all-row/all-subset Slack-CAGE check passes on the N=23
guardrail graph whose C5 active/fixed-mask split fails.

Two additional exact named guardrails were checked with the same all-row
scanner.

`Petersen[2]`:

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph Petersen2 --threads 60
```

Result:

```text
N = 20
m = 12
rows = 384
subsets = 2^20
scale = 800
min_all = 4 at U=empty
min_full = 9 at U=V
min_proper = 7 at U=(0)
VERDICT = HOLDS
```

`Myc(Petersen)`:

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph MycPetersen --threads 60
```

Result:

```text
N = 21
m = 13
rows = 240
subsets = 2^21
scale = 900
min_all = 116/25 at U=empty
min_full = 523/75 at U=V
min_proper = 191/25 at U=(1)
VERDICT = HOLDS
```

The same all-row scanner was also run on the remaining exact Mycielski/bridge
named guardrails:

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph MycC7 --threads 60
```

```text
N = 15
m = 5
rows = 28
subsets = 2^15
min_all = 4 at U=empty
min_full = 27/4 at U=V
min_proper = 6 at U=(7)
VERDICT = HOLDS
```

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph MycC9 --threads 60
```

```text
N = 19
m = 6
rows = 36
subsets = 2^19
min_all = 211/25 at U=empty
min_full = 1419/100 at U=V
min_proper = 261/25 at U=(9)
VERDICT = HOLDS
```

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph MycC11 --threads 60
```

```text
N = 23
m = 7
rows = 44
subsets = 2^23
min_all = 354/25 at U=empty
min_full = 2291/100 at U=V
min_proper = 404/25 at U=(11)
VERDICT = HOLDS
```

```text
python problems/23/writeup/_codex_slack_cage_allrow_zeta.py \
  --graph C7Grotzsch --threads 60
```

```text
N = 18
m = 5
rows = 32
subsets = 2^18
min_all = 199/25 at U=empty
min_full = 24737/1575 at U=V
min_proper = 224/25 at U=(6)
VERDICT = HOLDS
```

## Full N=11 all-subset census

Command:

```text
python problems/23/writeup/_codex_slack_cage_parallel_census.py \
  --n 11 --workers 60 --chunksize 8
```

Result:

```text
graphs = 90842
connected gamma-min maximum cuts = 171182
checks = 2167949312
violations = 0
VERDICT = HOLDS

min_margin = 21/25
  graph = cenJ?BEFo}}@{?#cut0
  m = 4
  row Q = (5,0,9,2,10)
  U = empty

min_full = 21/25
  graph = cenJ?BEF_m}@{?#cut6
  m = 4
  row Q = (0,9,2,10,5)
  D_Q(V) = 11
  |V| + eta = 296/25

min_proper_nonempty = 251/150
  graph = cenJ?`Db_{N?]?#cut4
  m = 4
  row Q = (2,8,4,10,6)
  U = (0,2,3,4,5,6,7,8,9,10)
  D_Q(U) = 55/6
  |U| + sigma(U) + eta = 271/25

min_proper_counted = 251/150
  same witness as min_proper_nonempty

max_prebank = 1
  graph = cenJ??CAAoR`Y?#cut0
  m = 2
  row Q = (4,9,1,7,10)
  U = (1,4,5,7,9,10)
  D_Q(U) = 9
  |U| = 6
  sigma(U) = 2
  eta = 71/25
  margin = 46/25
```

This extends the exact all-subset Slack-CAGE gate from N <= 10 to the full
N = 11 connected gamma-min maximum-cut census. The minimum proper nonempty
margin remains strictly positive; the global minimum is attained by the
empty/full eta-bank boundary cases.

## N=11 max-prebank cage classification

The full N=11 census identified the largest proper-counted prebank witness:

```text
graph = J??CAAoR`Y?
m = 2
eta = 71/25
U = (1,4,5,7,9,10)
prebank = D_Q(U) - |U| - sigma(U) = 1
margin = eta - prebank = 46/25
```

Direct exact classification:

```text
python - <<PY
import sys
sys.path.insert(0, 'problems/23/writeup')
import _codex_slack_cage_prebank_classifier as c
cases = c.run_graph('J??CAAoR`Y?', None)
...
PY
```

PowerShell was used with a here-string pipe for this local run.

Result:

```text
positive proper-counted prebank cases = 8
prebank values = {1: 8}
no_zero = 0
no_flat = 0
strict_drop_cases = 0

Every case has the same balanced-cell structure:
  zero-slack flat cages S={4} and S={5}
  sigma(S)=0
  DeltaGamma(S)=0
```

Thus the N=11 max-prebank witness matches the N=10 microscope: positive
proper-counted prebank is a banked balanced length-5 cell, not a non-balanced
Gamma-drop cage. This supports the refined proof split:

```text
positive prebank =
  balanced length-5 cell bank charged to eta
  + non-balanced terminal cage surplus forbidden by Gamma-minimality.
```

## Targeted N=11 Prebank Microscope

I added targeted input mode to:

```text
problems/23/writeup/_codex_slack_cage_prebank_classifier.py
```

so a specific graph/cut/row/subset can be classified without rerunning the
full census.  The full `N=11` census max-prebank witness was checked by:

```text
python problems/23/writeup/_codex_slack_cage_prebank_classifier.py \
  --g6 'J??CAAoR`Y?' --cut-index 0 \
  --Q '4,9,1,7,10' --U '1,4,5,7,9,10'
```

Result:

```text
N = 11
m = 2
eta = 71/25
side = 10110001010
f = (4,10)
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
D_Q(U) = 9
sigma(U) = 2
prebank = D_Q(U)-|U|-sigma(U) = 1
margin = eta-prebank = 46/25

counted rows:
  (4,10): 4-9-1-7-10
  (5,10): 5-9-1-7-10

zero/flat cages:
  S = {4}, sigma(S)=0, DeltaGamma=0
  S = {5}, sigma(S)=0, DeltaGamma=0

strict drop cages: none
VERDICT = PASS_BALANCED_TARGET
```

Thus the exact `N=11` max-prebank witness has the same structure as the `N=10`
microscope: two length-5 rows sharing the same internal blue path, unit
positive prebank, and only zero-slack flat C5-cell switches.  This supports
the banked proof split:

```text
minimal positive debt
=> terminal cage decomposition
=> non-flat zero-slack cage gives Gamma drop
   OR balanced length-5 flat cell consumes one unit of eta-bank.
```
