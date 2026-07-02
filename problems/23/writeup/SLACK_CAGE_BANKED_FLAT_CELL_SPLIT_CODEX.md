# Slack-CAGE Banked Flat-Cell Split

Status: proof-obligation draft, exact-supported but not proved.

This note refines the latest GPT-Pro zero-slack cage-switch route.  The raw
strict-drop conclusion is too strong if applied to positive prebank alone:
the exact N=10 and N=11 microscopes have positive prebank and zero-slack
switches, but every such switch is flat (`DeltaGamma=0`).  They are not
Slack-CAGE violations because the global eta-bank pays them.

The proof target should therefore separate two mechanisms:

```text
flat length-5 cells  -> paid by eta = N^2/25 - m
non-flat cages       -> forbidden by Gamma-minimality
```

## Definitions

For a fixed bad row `Q` and `U subset V`, write

```text
Pi_Q(U) := D_Q(U) - |U| - sigma(U),
sigma(U) := delta_B(U) - delta_M(U),
eta := N^2/25 - |M|.
```

Slack-CAGE is exactly:

```text
Pi_Q(U) <= eta.
```

A counted row is a pair `(g,P)` with `P in cyc[g]`, `V(P) subset U`, and
`V(P) cap V(Q) != empty`.

A cage switch `S subset U` is the GPT-Pro switch already implemented in
`_codex_slack_cage_switch_gate.py`:

1. `B^S` is connected.
2. Every counted row crossing `S` crosses terminally.
3. Every old blue boundary edge in `delta_B(S)` is witnessed by a counted-row
   first exit.
4. `S` is inclusion-minimal for these core properties.

Call a cage switch zero-slack if:

```text
sigma(S)=0.
```

Call a zero-slack cage flat if:

```text
DeltaGamma(S)=0.
```

The exact microscopes show that the relevant flat cages are length-5 cells:
the old deleted bad edge(s) and the created bad edge(s) all retain odd length
5 after the flip.  A proof may use the stronger geometric version:

```text
Flat5(S):
  sigma(S)=0,
  DeltaGamma(S)=0,
  every crossing old bad edge priced by S has ell=5,
  every new bad edge in delta_B(S) has ell_S=5 via the terminal replacement.
```

## Proposed Lemma Tree

### Lemma 1: zero-slack extraction

If `(Q,U)` is a minimal positive-debt pair, meaning

```text
Pi_Q(U) > eta
```

and it is lexicographically minimal by `( |U|, number of counted rows )`,
then some cage switch `S subset U` is zero-slack:

```text
sigma(S)=0.
```

This is the max-cut coarea part.  If every terminal cage had positive slack,
the cage boundary inequalities would sum to `Pi_Q(U) <= eta`.

### Lemma 2: non-flat zero-slack descent

If a zero-slack cage `S` is not `Flat5(S)`, then flipping `S` preserves
connectedness and maximum-cut size and strictly decreases Gamma:

```text
DeltaGamma(S) < 0.
```

Thus a Gamma-minimal connected maximum cut can contain only flat zero-slack
cages.

### Lemma 3: flat-cell eta bank

For every fixed row `Q` and every `U`, the positive part of `Pi_Q(U)` that
can be consumed by flat length-5 cage peelings is at most `eta`.

```text
FlatBank_Q(U) <= eta.
```

The bank demand is not the raw drop

```text
Pi_Q(U) - Pi_Q(U-S).
```

That raw drop can exceed `eta`.  The exact witnesses have `Pi_Q(U)=1`, while
a Flat5 singleton peel can send the remaining prebank to `-2` or `-3`.

The correct consumed bank is the positive-part decrement:

```text
bank(S;U) = max(0, Pi_Q(U)) - max(0, Pi_Q(U-S)).
```

For a peeling sequence

```text
U_0=U,  U_i=U_{i-1}-S_i,
```

define

```text
FlatBank_Q(U;S_1,...,S_k)
  = sum_i ( max(0,Pi_Q(U_{i-1})) - max(0,Pi_Q(U_i)) ).
```

This telescopes to

```text
max(0,Pi_Q(U)) - max(0,Pi_Q(U_k)).
```

The desired bank statement is: if all zero-slack cages in a minimal positive
debt pair are Flat5, then there is a terminal-compatible Flat5 peeling
sequence with

```text
Pi_Q(U_k) <= 0
```

and therefore

```text
FlatBank_Q(U) = Pi_Q(U) <= eta.
```

Equivalently, if `Pi_Q(U)>eta`, then the eta-paid Flat5 peelings cannot
consume all positive prebank; a non-Flat5 zero-slack cage remains.  Lemma 2
then gives the Gamma contradiction.

This is the missing bank statement.  The exact data suggest the atomic flat
cell consumes one positive unit in the observed cases:

```text
bank(S;U)=1.
```

Examples:

```text
N=10 microscope:
  eta=2, prebank=1, flat cages S={3},{4}.

N=11 max-prebank microscope:
  eta=71/25, prebank=1, flat cages S={4},{5}.
```

The bank statement should not require a strict Gamma drop for these cells.
They are precisely the cells paid by `N^2/25-m`.

## Why This Proves Slack-CAGE

Assume Slack-CAGE fails and choose a minimal positive-debt pair:

```text
Pi_Q(U) > eta.
```

By Lemma 1 there is a zero-slack cage.  If some zero-slack cage is non-flat,
Lemma 2 contradicts Gamma-minimality.  If all zero-slack cages are flat, Lemma
3 gives `Pi_Q(U) <= eta`, contradicting positive debt.  Hence no positive-debt
pair exists, and Slack-CAGE holds.

At `U=V`, Slack-CAGE gives:

```text
D_Q(V) <= N + eta = N + N^2/25 - m,
```

which is the corrected ROWSUM/GERSH row cap.

## Exact Gates To Run

The current classifier already gates the flat-cell branch on microscopes:

```text
python problems/23/writeup/_codex_slack_cage_prebank_classifier.py --n 10

python problems/23/writeup/_codex_slack_cage_prebank_classifier.py \
  --g6 'J??CAAoR`Y?' --cut-index 0 \
  --Q '4,9,1,7,10' --U '1,4,5,7,9,10'
```

Observed:

```text
N=10:
  positive proper-counted prebank cases = 12
  all have prebank=1
  all have flat zero-slack cages
  none has strict-drop cages

N=11 max-prebank target:
  prebank=1
  eta=71/25
  flat cages S={4},{5}
  strict-drop cages = none
```

Next exact gate for Claude:

For every positive proper-counted prebank case in the full N=11 census, test:

```text
if no strict-drop zero-slack cage exists:
    prebank <= eta
    and a Flat5 cage exists.
```

This is weaker than full Slack-CAGE but directly validates the eta-bank
exception against the whole available census.

## Full N=11 Banked-Flat Gate

I added a graph-sharded parallel gate:

```text
problems/23/writeup/_codex_slack_cage_banked_flat_gate.py
```

It scans all positive proper-counted prebank cases.  For each such case it
enumerates cage-switch core sets and tests:

```text
if no strict-drop zero-slack cage exists:
    prebank <= eta
    and at least one Flat5 zero-slack cage exists.
```

Here `Flat5` is checked directly: every old crossing bad edge deleted by the
switch has old length `5`, and every new bad edge created from an old blue
boundary edge has length `5` in the switched blue graph.

Validation on full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_banked_flat_gate.py \
  --n 10 --workers 60 --chunksize 8
```

Result:

```text
positive_cases = 12
strict_cases = 0
no_strict_cases = 12
no_strict_flat = 12
no_strict_flat5 = 12
no_strict_over_eta = 0
no_strict_no_flat = 0
no_strict_no_flat5 = 0
prebank_values = {1: 12}
VERDICT = PASS_BANKED_FLAT5
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_banked_flat_gate.py \
  --n 11 --workers 60 --chunksize 8
```

Result:

```text
graphs = 90842
cuts = 171182
positive_cases = 40
strict_cases = 0
no_strict_cases = 40
no_strict_flat = 40
no_strict_flat5 = 40
no_strict_over_eta = 0
no_strict_no_flat = 0
no_strict_no_flat5 = 0
prebank_values = {1: 40}
VERDICT = PASS_BANKED_FLAT5

max_nostrict_prebank:
  graph = cenJ??CAAoR`Y?#cut0
  N = 11
  m = 2
  eta = 71/25
  Q = (4,9,1,7,10)
  U = (1,4,5,7,9,10)
  D_Q(U) = 9
  sigma(U) = 2
  prebank = 1
  prebank - eta = -46/25
  Flat5 cages = S={4}, S={5}
  strict cages = none
```

Thus every positive proper-counted prebank case in the full `N<=11` census is
eta-paid and Flat5.  No case requires a strict Gamma-drop cage at census scale,
which reinforces that the proof must first extract zero-slack cages, then
separate:

```text
Flat5 cells  -> eta bank
Non-flat     -> Gamma descent
```

## Positive-Part Peel Gate

The corrected Flat5 bank demand is the positive-part decrement, not the raw
drop.  I added:

```text
problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py
```

The gate asks a stronger finite question than the previous Flat5-existence
gate:

```text
For every positive proper-counted prebank case,
either a strict zero-slack Gamma-drop cage exists,
or a true Flat5 zero-slack cage S has pre_Q(U-S) <= 0.
```

In the second branch the bank consumed is

```text
max(0,pre_Q(U)) - max(0,pre_Q(U-S)) = pre_Q(U),
```

so the only remaining eta check is `pre_Q(U)<=eta`.

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py \
  --n 10 --workers 60 --chunksize 8
```

Result:

```text
positive = 12
needs_bank = 12
flat5_consumes_positive = 12
max_prebank = 1
max_bank = 1
VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py \
  --n 11 --workers 60 --chunksize 8
```

Result:

```text
positive = 40
needs_bank = 40
flat5_consumes_positive = 40
max_prebank = 1
max_bank = 1
VERDICT = PASS_FLAT5_POSITIVE_PART_PEEL

max case:
  graph = cenJ??CAAoR`Y?#cut0
  N = 11
  m = 2
  eta = 71/25
  Q = (4,9,1,7,10)
  U = (1,4,5,7,9,10)
  S = (4)
  prebank = 1
  pre_after = -3
  bank = 1
  margin = 46/25
```

This directly supports the corrected bank statement: the observed Flat5
rotations may have raw drops `3` or `4`, but the positive-part bank consumed
is exactly `1`, safely within `eta`.

## Unit Flat5 Overlap-Pair Atom

I also extracted structural signatures for every positive proper-counted
prebank case through the full `N=10` and `N=11` censuses:

```text
problems/23/writeup/_codex_slack_cage_positive_signatures.py
```

Full `N=10`:

```text
cases = 12
unique_signatures = 2
```

Full `N=11`:

```text
cases = 40
unique_signatures = 3
```

The signatures differ only in the available zero-slack Flat5 switch shape
(`singleton` versus `shared 4-path`).  The counted-row core is identical in
all cases:

```text
local counted bad rows = 2
prebank = 1
|U| = 6
number of counted rows = 2
row lengths = (5,5)
row geodesic denominators = (1,1)
intersections with Q = (5,4)
pairwise row intersection = 4
U = union of the two counted rows
strict zero-slack cages = none
flat zero-slack cages = Flat5
```

Scope correction: the `2` above is local to the counted Flat5 overlap core.
It is not a global hypothesis `m=2`.  Extra disjoint or bridged odd-cycle
components can raise the global bad-edge count while leaving this local
`(Q,U)` atom unchanged.  The global count `m=|M|` only re-enters in the
packing bank `eta=N^2/25-m`.

Thus the observed bank atom is:

```text
Two length-5 bad rows P0,P1 share a terminal 4-vertex blue path.
Both bad edges have unique shortest blue geodesics in the counted family.
The selected row Q is one of them.
U = V(P0) union V(P1), so |U|=6.
D_Q(U)=5+4=9.
sigma(U)=2.
Pi_Q(U)=9-6-2=1.
```

The Flat5 peel can remove either the private endpoint of one row or the shared
terminal 4-path, depending on the embedding.  In all signatures it consumes
the single positive unit:

```text
max(0,Pi_Q(U))-max(0,Pi_Q(U-S)) = 1.
```

Candidate local lemma:

```text
UNIT-FLAT5-OVERLAP:
In a minimal positive-prebank pair, if every zero-slack cage is Flat5 and no
strict Gamma-drop cage exists, then the positive-prebank component contains a
unit overlap-pair atom as above.  Peeling one of its Flat5 terminal sides
consumes all positive prebank contributed by that component.
```

This would reduce the Flat5 eta-bank branch to packing these unit atoms
against `eta=N^2/25-m`.

## Unit-Atom Packing Target

If `UNIT-FLAT5-OVERLAP` is the correct local structure, then the global
Flat5 bank statement should be expressed as a packing inequality.

Let `A_Q(U)` be a terminal-compatible selected family of unit Flat5
overlap-pair atoms produced by the canonical cage peeling of a fixed `(Q,U)`.
Each atom has positive-part bank demand `1`.  The desired global packing
statement is:

```text
|A_Q(U)| <= eta = N^2/25 - m.
```

Equivalently,

```text
m + |A_Q(U)| <= N^2/25.                            (UNIT-PACK)
```

This avoids charging raw prebank drops and avoids using Gamma descent for
Flat5 rotations.  It says that a selected unit overlap atom behaves like one
additional missing bad edge in the sharp `C5` extremal count.

The likely graph-theoretic mechanism is an augmented `C5` packing:

```text
original bad edges M
plus one pseudo-bad edge for each selected unit atom
```

should still be controlled by the same max-cut/triangle-free `C5` product
bound.  In the finite `N<=11` witnesses the global graph happens to have
`m=2`:

```text
N=10: m=2, |A|=1, m+|A|=3 <= 4 = N^2/25.
N=11: m=2, |A|=1, m+|A|=3 <= 121/25.
```

This example-only `m=2` does not belong in `UNIT-FLAT5-OVERLAP`: a bridged
extra `C5` component gives `N=15`, global `m=3`, and the same local two-row
Flat5 atom with bank demand `1`.

Executable guardrail:

```text
python problems/23/writeup/_codex_slack_cage_unit_atom_guardrail.py

VERDICT = PASS_UNIT_ATOM_LOCAL_NOT_GLOBAL_M2
```

## Row-Union Eta-Or-Unit Stress Gate

I added a local row-union stress gate:

```text
problems/23/writeup/_codex_slack_cage_rowunion_unit_gate.py
```

It avoids all-subset enumeration.  For each tested row `Q`, it checks candidate
sets `U` that are unions of one or two shortest rows touching `Q`.  Positive
row-union cases are allowed in two branches:

```text
1. directly eta-paid: pre_Q(U) <= eta;
2. tight Flat5 branch: the local counted core is UNIT-FLAT5-OVERLAP.
```

This corrected the overbroad claim that every positive row-union must be a
unit Flat5 atom.  Two-lane long-row unions can have positive prebank but are
far from tight and are directly eta-paid.

Run:

```text
python problems/23/writeup/_codex_slack_cage_rowunion_unit_gate.py \
  --two-lane-max 24 --max-cuts 2 --include-gmins-blowups
```

Result:

```text
candidates = 446933
positive = 30
eta_paid = 30
unit_eta_paid = 2
nonunit_eta_paid = 28
fails = 0
VERDICT = PASS_ROWUNION_ETA_OR_UNIT
```

The first nonunit eta-paid case is the expected long-row two-lane atom:

```text
two-lane-L8:
  N = 27
  m = 4
  eta = 629/25
  pre = 1
  margin = 604/25
  row_lengths = [5,7,7,9]
```

Thus the Flat5 unit atom should be used only for the tight/near-tight Flat5
bank branch.  Long-row row-union prebank belongs to the eta-paid / Banked-UPO
branch, not to UNIT-FLAT5.

Bounded triple-row stress:

```text
python problems/23/writeup/_codex_slack_cage_rowunion_unit_gate.py \
  --two-lane-max 18 --max-cuts 1 --max-union-rows 3 --max-candidates 20000

candidates = 39789
positive = 18
eta_paid = 18
unit_eta_paid = 2
nonunit_eta_paid = 16
fails = 0
VERDICT = PASS_ROWUNION_ETA_OR_UNIT
```

This is not exhaustive for all triple row-unions; it is only a bounded stress
check that the eta-or-unit split persists beyond pair unions on the generated
battery.

Full census pair-row-union gate:

```text
python problems/23/writeup/_codex_slack_cage_rowunion_census_gate.py \
  --n 11 --workers 60 --chunksize 8 --max-cuts 8 --max-union-rows 2

graphs = 90842
cuts = 164978
candidates = 43646364
positive = 40
eta_paid = 40
unit_eta_paid = 40
nonunit_eta_paid = 0
fails = 0
min_margin = 46/25
VERDICT = PASS_CENSUS_ROWUNION_ETA_OR_UNIT
```

Together with the earlier `N=8,9,10` row-union census runs, this says that
through the full `N<=11` census every positive pair-row-union case is exactly
the tight UNIT-FLAT5 overlap atom; the generated long-row/two-lane nonunit
positives remain directly eta-paid and do not appear in the small exact
census.

Full pair-row-union census:

```text
python problems/23/writeup/_codex_slack_cage_rowunion_census_gate.py \
  --n 10 --workers 60 --chunksize 8 --max-cuts 8 --max-union-rows 2

graphs = 9832
cuts = 15497
candidates = 1839450
positive = 12
eta_paid = 12
unit_eta_paid = 12
nonunit_eta_paid = 0
fails = 0
VERDICT = PASS_CENSUS_ROWUNION_ETA_OR_UNIT
```

```text
python problems/23/writeup/_codex_slack_cage_rowunion_census_gate.py \
  --n 11 --workers 60 --chunksize 8 --max-cuts 8 --max-union-rows 2

graphs = 90842
cuts = 164978
candidates = 43646364
positive = 40
eta_paid = 40
unit_eta_paid = 40
nonunit_eta_paid = 0
fails = 0
VERDICT = PASS_CENSUS_ROWUNION_ETA_OR_UNIT
```

Thus on the exact `N<=11` census, every positive pair-row-union case is not
merely eta-paid but actually the local unit Flat5 atom.  The nonunit eta-paid
branch appears in generated long-row families, not in the `N<=11` census.

## Unit-Pack Proxy Diagnostic

I added:

```text
problems/23/writeup/_codex_slack_cage_unit_pack_census.py
```

This enumerates the positive pair-row-union UNIT-FLAT5 atoms in the census and
computes simple packing proxies:

```text
max_per_q
max_disjoint_all
max_disjoint_by_q
```

These are not the final canonical selected family, but they test whether the
observed atom multiplicities already threaten `UNIT-PACK`.

Full `N=10`:

```text
python problems/23/writeup/_codex_slack_cage_unit_pack_census.py \
  --n 10 --workers 32 --chunksize 8 --max-cuts 8 --max-union-rows 2

groups = 6
total_atoms = 12
worst_atoms:
  atoms = 2
  eta = 2
  q_count = 2
  max_per_q = 1
  max_disjoint_all = 1
  max_disjoint_by_q = 1
violations = 0
VERDICT = PASS_UNIT_PACK_PROXY
```

Full `N=11`:

```text
python problems/23/writeup/_codex_slack_cage_unit_pack_census.py \
  --n 11 --workers 60 --chunksize 8 --max-cuts 8 --max-union-rows 2

groups = 20
total_atoms = 40
worst_atoms:
  atoms = 2
  eta = 71/25
  q_count = 2
  max_per_q = 1
  max_disjoint_all = 1
  max_disjoint_by_q = 1
violations = 0
VERDICT = PASS_UNIT_PACK_PROXY
```

Thus the census multiplicity is only a symmetric duplication: each group has
two unit atoms, but they correspond to two rows and no row sees more than one
atom.  Any disjoint-`U` selected family has size `1`, below the eta bank.

The proof still needs to define the canonical selected family `A_Q(U)` so that
overlapping unit atoms are not double-counted.  A natural target is a laminar
terminal-peeling family:

```text
U_0=U,
choose a unit Flat5 atom S_i in U_{i-1},
U_i=U_{i-1}-S_i,
stop when pre_Q(U_i)<=0 or a non-Flat5 zero-slack cage appears.
```

Then

```text
sum_i bank(S_i;U_{i-1}) = number of selected unit atoms
```

because every observed selected atom consumes exactly one positive unit.

So the Flat5 branch is now reduced to two proof obligations:

```text
LOCAL: UNIT-FLAT5-OVERLAP extracts a unit atom whenever the positive bank
       branch is active.

GLOBAL: UNIT-PACK bounds the number of selected unit atoms by eta.
```

If `UNIT-PACK` fails in a larger stress case, the failure should exhibit a
family of overlapping Flat5 atoms whose positive-part demands cannot be
represented as one pseudo-bad edge each.
