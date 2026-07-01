# No-Two-Hole Residual Corridor Atom

Status: exact-gated on the current Codex targeted battery.

Proof status: the finite gates below are evidence/regression checks.  The
noncircular proof obligations are the scoped lemmas in
`SCOPED_ROW_GEOMETRY_LEMMAS.md`; do not use the `row_miss<=1` gate as an
input to prove no-two-hole.

## 2026-07-01 correction: exact Hall replaces single-miss

The component-local one-miss target is too strong.  On the hard H3 side

```text
side=111111111111111100000000000, max_add=2,
S=(3,4,5,6,7,8,9,10,11,12,13,14,15,18,21,22,23,24,25,26),
f=(0,15)
```

the row `f` misses `(1,18)` and `(2,18)` in the same residual component.
The older single-miss/complement-degree sufficient condition fails there.

However this is not a Hall obstruction.  The exact residual Hall gate

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 11 --max-n 10 --h3-hard --max-add 2
```

passes on the hard H3 side, and the selected battery

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

also passes.  The proof-facing target is therefore exact residual Hall, using
replacement/corner geometry for high-tier missed incidences, not
`row_miss<=1`.

Gate:

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result:

```text
tested: 182
status: {'ok': 182}
stats: {('row_miss', 0): 989, ('row_miss', 1): 72}
VERDICT: PASS
```

Additional census-11 sweep:

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 11 --max-n 11 --max-add 1
```

Result:

```text
tested: 11
status: {'ok': 11}
stats: {('row_miss', 0): 11}
VERDICT: PASS
```

Independent H2x mirror using Claude's `witness_structure` machinery:

```text
python problems/23/writeup/_th_corridor_mine.py h2only
```

Result:

```text
switches tested: 196
row_miss histogram: [(0, 580), (1, 172)]
TWO-HOLE rows: 0
VERDICT: NO-TWO-HOLE HOLDS
```

Tie-robust stage-0 row-miss gate:

```text
python problems/23/writeup/_codex_stage0_all_min_rowmiss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

Result:

```text
tested: 119
status: {'ok': 119}
VERDICT: PASS
```

This enumerates every minimum rare-cost matching in the H2 witness battery
and confirms the residual component-local one-miss conclusion is independent
of the deterministic stage-0 tie-break there.

With inherited H3/H4 stress:

```text
python problems/23/writeup/_codex_stage0_all_min_rowmiss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result:

```text
status: {'ok': 139, 'too_many': 43}
row_miss_fail: 0
```

The `too_many` entries are large tied matching families that hit the cap
`100000`; every enumerated minimum matching satisfied row-miss at most one.

Stronger global unmatched-`E0` miss gate:

```text
python problems/23/writeup/_codex_stage0_all_min_e0miss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1
```

Result:

```text
tested: 119
status: {'ok': 119}
VERDICT: PASS
```

But with inherited H3/H4 stress:

```text
python problems/23/writeup/_codex_stage0_all_min_e0miss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

has `e0_miss=3`. Thus one row can miss several unmatched minimum exits
globally; the reason this is harmless is exactly residual component
separation. The component-local theorem is the sharp scope.

Thus every tested residual component row misses at most one residual exit.
The stronger two-hole corridor alternatives were not triggered in this
battery, because no row had two misses.

HT isolation diagnostic:

```text
python problems/23/writeup/_codex_ht_isolation_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 \
  --max-add 1 --all-min --cap 100000
```

Result:

```text
tested: 182
status: {'ok': 139, 'too_many': 43}
stats: {
  'matchings': 136938,
  'missed_exit': 1632,
  'missed_high_tier': 480,
  'ht_hinge': 2688,
  'ht_no_contact': 2688,
  ('no_contact_miss_count', 1): 2688,
  'missed_min_tier': 1152
}
VERDICT: PASS
```

This is evidence for the sharpened high-tier proof target: a high-tier
no-contact first hinge is a one-miss branch. Therefore, in a genuine two-hole
corridor, the high-tier endpoint must either produce the Door/Long certificate
or the no-contact branch contradicts the existence of the second missed exit in
the same residual component. The diagnostic is not a proof input.

## Setup

Let `S` be a completed seed+moat terminal-shadow switch. Let

```text
C = delta_M(S)
E = delta_B(S)
```

and let `Wit(f)` be the set of terminal exits witnessed by the crossing bad
edge `f`. Let

```text
L0 = min_{f in C} ell(f)
F0 = {f in C : ell(f)=L0}
F1 = C \ F0
```

For exits, write

```text
lambda(e)=min{ell(f): f witnesses e}
E0={e in E: lambda(e)=L0}.
```

Stage 0 matches `F0` into `E0` with minimum rare cost

```text
c(e)=|Wit(e) cap F1|.
```

After deleting the matched exits, form residual components of the bipartite
graph between `F1` and remaining exits.

## Slack Form

For a crossing bad edge `f=tau_f sigma_f` with `tau_f in S`, define

```text
D_f = ell(f)-1
s_f(e) = d_{B[S]}(tau_f,x_e) + 1
       + d_{B[V\S]}(y_e,sigma_f) - D_f
```

where `e=x_e y_e`, `x_e in S`, `y_e notin S`.

Terminal-shadow validity says:

```text
f witnesses e iff s_f(e)=0.
```

By parity, nonzero slack is at least `2`.

## Atom

In any residual connected component `(A,B)`, no tuple

```text
f; e0,g1,e1,g2,...,gk,ek
```

exists with:

```text
f,g_i in A
e_i in B
g_i witnesses e_{i-1} and e_i
s_f(e0)>0, s_f(ek)>0
s_f(e_i)=0 for 1<=i<=k-1
```

where `e0,...,ek` is shortest in the exit co-witness graph. This implies the
component-local single-miss theorem:

```text
for every f in A, |B \ Wit(f)| <= 1.
```

Equivalently, define the residual exit co-witness graph `J(A,B)` on exits in
`B` by

```text
e -- e' in J(A,B) iff exists g in A with g witnesses both e and e'.
```

Because the residual bipartite component is connected, `J(A,B)` is connected
on every nontrivial exit set.  If some row `f` missed two exits, choose two
missed exits with minimum `J`-distance.  The shortest `J` path between them
has exactly the tuple above: the endpoints have positive terminal slack, and
all internal exits have slack zero.  Thus the no-two-hole theorem is exactly
the exclusion of these shortest residual corridors.  This reduction is
purely component-local; global multi-misses in different residual components
are intentionally outside the statement.

## Frozen TH-Corridor Acceptance Target

For every residual component `(A,B)`, every `f in A`, and every shortest
two-hole residual corridor

```text
e0, g1, e1, g2, ..., gk, ek
```

with

```text
g_i witnesses e_{i-1} and e_i,
s_f(e0)>0,
s_f(ek)>0,
s_f(e_i)=0 for 1<=i<=k-1,
```

one of the following certificates must exist.

### TH-long / endpoint-lens certificate

If at least one endpoint has `lambda(e)>L0`, then the row-union disk built
from:

```text
f-rows through the internal tight exits,
g_i-rows through consecutive exits,
```

contains either:

```text
1. a triangle in G, or
2. a B-path between the endpoints of some h in {f,g1,...,gk}
   of length <= ell(h)-3.
```

This is the long-door two-hinge lens.  In Lean-facing terms, the endpoint
slack gives the even nonzero strict source; the remaining application
geometry must supply the split/rejoin vertices and replacement walk required
by `MetricSpliceScratch.lean:spliced_dist_le_of_even_nonzero_slack` and the
S2 wrapper.

### TH-rare / minimum-door exchange certificate

If both endpoints satisfy

```text
lambda(e0)=lambda(ek)=L0,
```

then the stage-0 matching admits a rare-cost-decreasing alternating exchange.
The singleton sufficient form is:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e) cap mu(F0)
with c(u)>c(e).
```

The multi-exchange form is:

```text
replace unmatched minimum exits Z by matched exits U,
|Z|=|U|,
sum_{z in Z} c(z) < sum_{u in U} c(u).
```

In Lean-facing terms, the stage-0 algebra after the witness-set inclusion or
strict cost comparison is already covered by
`Stage0MatchingScratch.lean:witness_inclusion_contradicts_no_improving_exchange`.
The remaining geometric obligation is scoped RM: at the first interaction of
the two cost-flat minimum side blocks, either S2 fires or the near-side
`F1` witness set is included in the far-side witness set after deleting the
genuinely new witness.

### Lean consolidation

For formalization, state the row-side target once.  The S2 core must not
assume "no intermediate terminal door"; if the geometry exposes such a door,
the row application closes it immediately using H3 minimal-corridor kernels.
After this upstream Door discharge, the Lean-facing wrapper consumes only the
two remaining certificate branches:

```text
shortest two-hole corridor
+ terminal-prefix / no-reentry rows
+ shortest J-corridor minimality
+ endpoint slack parity
+ stage-0 minimum-cost matching
=> TH-long splice/triangle certificate
   OR TH-rare stage-0 exchange certificate.
```

Then prove the consequences separately:

```text
intermediate terminal door
=> contradiction to the chosen minimal corridor / terminal block
   by the H3 reducedness kernels:
   no_internal_marked_of_minimal_marked_corridor
   and/or no_nonconsecutive_common_witness_of_shortest_corridor.

TH-long certificate
=> shorter B-path or triangle
=> contradiction to ell(h)-minimality / triangle-free.

TH-rare certificate
=> stage-0 rare-cost contradiction
=> contradiction to minimum-cost matching.

No shortest two-hole corridor
=> component-local |B \ Wit(f)| <= 1.
```

This avoids duplicating the theorem across the Atom, Frozen Target, and Proof
Split sections.  The finite gates remain regression evidence only; the Lean
target uses the scoped corridor hypotheses above.

#### Single theorem to formalize

The intended row-side discharge theorem is the following abstract contract.

```text
ROW_SIDE_TWO_HOLE_DISCHARGE

Inputs:
  S is a completed seed+moat terminal-shadow switch.
  (A,B) is one residual component after deleting the stage-0 matched exits.
  mu is a minimum rare-cost matching of F0 into E0.
  f in A.
  e0,g1,e1,...,gk,ek is a shortest J(A,B)-corridor between two exits missed by f.

Corridor hypotheses:
  g_i witnesses e_{i-1} and e_i.
  s_f(e0) != 0 and s_f(ek) != 0.
  s_f(e_i) = 0 for 1 <= i <= k-1.
  Nonzero slacks are even.
  The corridor is shortest among missed-endpoint pairs.
  Terminal rows satisfy prefix/no-reentry for S.

Geometry output after upstream Door discharge:
  either
    Long: for some h in {f,g1,...,gk}, the long-endpoint geometry supplies
      the walk data required by MetricSpliceScratch.spliced_even_slack_contradicts_shortest,
      or a triangle degeneration;
  or
    Rare: the minimum-endpoint geometry supplies p,q,newWitness with
      p notin mu(F0), q in mu(F0),
      Wit_F1(p) subset (Wit_F1(q)).erase newWitness,
      newWitness in Wit_F1(q),
      and the corresponding one-exit replacement preserves cardinality.

Consequences already Lean-kernelized:
  Door is excluded upstream by S2CoreScratch H3 reducedness kernels:
    no_internal_marked_of_minimal_marked_corridor, or
    no_nonconsecutive_common_witness_of_shortest_corridor.
  Long => contradiction by MetricSpliceScratch.spliced_even_slack_contradicts_shortest
          or S2CoreScratch.triangle_of_blue_and_bad.
  Rare => contradiction by
          Stage0MatchingScratch.witness_inclusion_contradicts_no_improving_exchange.

Conclusion:
  the shortest two-hole corridor cannot exist.
```

Thus the only non-kernel obligations left for this theorem are the two scoped
application-geometry outputs:

```text
HT geometry:
  a shortest two-hole corridor with at least one high-tier endpoint forces
  Door or Long.  Door is discharged by H3 before applying the Lean wrapper.
  Equivalently, endpoint-local no-contact must isolate that high-tier miss
  from all other missed exits in the residual component.  The endpoint-local
  contact version is false; the opposite missed endpoint is part of the
  strict/reducedness input.

RC/RM geometry:
  two minimum-tier endpoints force Door, Long, or Rare.  Door is discharged by
  H3 before applying the Lean wrapper.
```

The exact gates in this file are evidence that these scoped geometry outputs
hold on the tested census. They are not assumptions in the proof.

## Proof Split

Every hypothetical two-hole corridor must satisfy exactly one of the following.

### Long-Lambda Endpoint

If either endpoint has `lambda(e)>L0`, the row-union disk built from:

```text
f-rows through the internal tight exits
g_i-rows through consecutive exits
```

must contain either a triangle or a `B`-path between the endpoints of some
bad edge `h in {f,g_1,...,g_k}` of length at most `ell(h)-3`. Equivalently,
the new path is at least two `B`-edges shorter than the defining shortest
geodesic length `ell(h)-1`.

This is checked in `_codex_th_corridor_gate.py` by
`disk_shorter_certificate`.

Status: classified by Claude/GPT-Pro on 2026-06-30T21:59:45Z as proven by
the same S2 endpoint-hinge rigidity used on the cap side.  A reduced first
hinge with `lambda(e)>L0` forces a first-split/last-rejoin theta; the
degenerate case is a triangle, otherwise one involved bad edge has a shorter
blue geodesic.  Thus the long-lambda branch is no longer the live obstacle.

### Minimum-Lambda Endpoints

If both endpoint exits lie in `E0`, the stage-0 minimum-cost matching must
admit a rare-cost-improving alternating exchange. In the current gate the
tested sufficient certificate is:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e)
with c(u)>c(e).
```

This is checked by `alt_reach_cost_drop`.

The tempting stronger invariant:

```text
every unmatched E0 exit is universal to F1
```

is false. The gate

```text
python problems/23/writeup/_codex_rare_stage0_universal_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

has `rem_e0_not_universal` failures. Therefore TH-rare cannot be proved by
global unmatched-universality.

The correct target is side-block separation:

```text
Flat minimum-lambda survivors may remain, but each residual co-witness
component meets at most one such survivor side block. If two minimum missed
exits in the same residual component are connected by a co-witness corridor,
then either one endpoint has a strict cost-dropping alternating path, or the
two flat alternating closures meet/cross and create an intermediate terminal
door. The latter contradicts the same shortest-row theta exclusion used in
S2/TH-long.
```

### Dangerous-Direction RM Persistence Sanity Check

The first broad near-witness-persistence gate was intentionally too broad: it
asked every co-witnessed non-persistence pair to fire S2, including comparisons
between already matched exits and comparisons in the cost-increasing direction.

The corrected diagnostic scopes to the only direction that can close TH-rare:

```text
root e in E0 \ mu(F0),
matched u in Alt_mu(e) cap mu(F0),
c(u)>c(e),
r in F1 witnesses e but not u.
```

Only that direction would need the scoped first-interaction/S2 argument.  If
`c(u)<=c(e)`, the comparison is consistent with the stage-0 min-cost condition
and is recorded as harmless.

Gate:

```text
python problems/23/writeup/_codex_rm_directional_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result after dangerous-direction scoping:

```text
tested: 182
status: {'ok': 182}
stats: {'skip_nondangerous_cost': 7484}
VERDICT: PASS
```

This is a sanity check, not a proof of RM: no dangerous alternating-shadow
comparison occurs in the current finite battery, while 7484 comparisons are
precisely the min-cost-compatible direction `c(u)<=c(e)`.  The true scoped RM
lemma lives inside a hypothetical minimal two-hole corridor / first shadow
interaction; that object does not occur in the battery and remains a prose/Lean
obligation.

## Current Audit Obligation

The finite data supports the stronger statement that no two-hole corridor
exists at all in the selected seed+moat switches. The long-lambda alternative
has been reduced to S2. The minimum-lambda alternative is classified as S2 plus
stage-0 min-cost, but the scoped RM step is a proof obligation rather than a
real-data gate:

```text
minimum endpoints -> rare monotonicity (S2) + shadow separation
                 -> stage-0 rare-cost exchange.
```

The remaining work is not another finite gate.  It is to write the common
S2 reduced-theta lemma with hypotheses strong enough for both row applications:

```text
TH-long / endpoint hinge rigidity,
TH-rare / rare monotonicity.
```

Every application must explicitly check terminal-prefix rows, shortest
co-witness minimality, no re-entry, and the absence of an already-existing
intermediate terminal door.
