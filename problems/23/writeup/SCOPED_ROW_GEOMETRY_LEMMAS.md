# Scoped Row Geometry Lemmas

This file is the row-side proof ledger after the 2026-06-30 audit.  The
purpose is to prevent false global lemmas from re-entering the proof.

The verified finite consequences are strong evidence, but the row proof must
use only the scoped minimal-counterexample statements below.

## Common Objects

Fix a completed terminal-shadow switch `S`.

```text
C = delta_M(S)          crossing bad edges
E = delta_B(S)          boundary blue exits
Wit(e) subset C         rows witnessed by exit e
lambda(e) = min ell(h) over h in Wit(e)
L0 = min lambda(e)
F0 = {h in C : ell(h)=L0}
F1 = C \ F0
E0 = {e in E : lambda(e)=L0}
c(e) = |Wit(e) cap F1|
```

Stage 0 chooses an injective matching

```text
mu : F0 -> E0
```

minimizing

```text
sum_{h in F0} c(mu(h)).
```

After deleting the matched exits `mu(F0)`, the residual graph has left side
`F1` and right side `E \ mu(F0)`.

## False Broad Lemmas

The following statements are false and must not be used.

### Component-Local Single-Miss

False statement:

```text
After the stage-0 matching, every row in every residual F1/E component misses
at most one residual exit.
```

Counterexample:

```text
H3-hard side 111111111111111100000000000, max_add=2,
S=(3,4,5,6,7,8,9,10,11,12,13,14,15,18,21,22,23,24,25,26),
f=(0,15) misses (1,18),(2,18) in the same residual component.
```

This is not a Hall obstruction.  The exact residual Hall gate passes on this
hard side, including components with maximum row-miss 2 and 4:

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 11 --max-n 10 --h3-hard --max-add 2
```

The selected battery also passes exact residual Hall:

```text
python problems/23/writeup/_codex_residual_exact_hall_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Therefore the row-side target is exact residual Hall, not `row_miss<=1`.

### Broad HT Contact

False statement:

```text
If f misses p, f witnesses q, g witnesses p and q, and lambda(p)>L0,
then terminal rows R_f(q), R_g(p) have both inside and outside contact.
```

Counterexample:

```text
H2-allmax, n=18, side=111111111110000000,
S=(0,1,11,12),
f=(0,10), g=(11,16), p=(1,13), q=(0,13),
lambda(p)=7, L0=5.
```

Here `f` has only one missed high-tier exit.  It is not a two-hole endpoint.

### Broad RM Persistence

False statement:

```text
For every F1 row r and co-witnessed exits a,b, if r witnesses a but not b,
then the local disk for r/a and g/a,g/b already gives S2.
```

Counterexample:

```text
H2-allmax, n=18, side=111111111100000000,
S=(0,1,2,3,4,5,6,10,11,12,13,14,15),
r=(10,16), a=(7,14), b=(6,17), g=(10,17).
```

The disk has no `ell(h)-3` shortcut for `h in {r,g}`.

## Lemma 1: Minimal Corridor Reducedness

Assume, for contradiction, that some row `f in F1` misses two residual exits
in one residual component.  Choose missed exits `e0,ek` at minimum distance in
the exit co-witness graph `J`, and choose a shortest corridor

```text
e0, g1, e1, g2, ..., gk, ek.
```

Hypotheses:

```text
g_i witnesses e_{i-1} and e_i,
f misses e0 and ek,
f witnesses every internal e_i.
```

Reducedness conclusions:

1. No internal exit is missed by `f`; otherwise a closer missed pair exists.
2. No hinge row `g_i` witnesses two nonconsecutive corridor exits; otherwise
   the `J` path shortcuts.
3. Any first split / last rejoin chosen inside the row-union disk is reduced
   by construction; a smaller one would have been selected first.

This lemma supplies H3 for row TH-long/EHR without using the desired
`row_miss<=1` conclusion.

Lean target:

```text
shortest_path_in_J ->
  no_hinge_witnesses_nonconsecutive_exits
```

plus the minimality statement for first split / last rejoin.

## Lemma 2: Scoped Two-Ended High-Tier Rigidity

Assume the setup of Lemma 1 and suppose one endpoint is high tier, say

```text
lambda(e0) > L0.
```

Then the full shortest two-hole corridor, including the opposite missed
endpoint, supplies the S2 reduced-theta hypotheses.  It is not enough to look
at the first endpoint hinge alone:

```text
e0, g1, e1
```

together with `f`; that endpoint-local statement is false.  In the genuine
two-hole scope the corridor supplies:

```text
terminal-prefix rows,
shortest rows,
endpoint slack s_f(e0) >= 2,
reducedness from Lemma 1,
no intermediate terminal door unless the branch is already closed.
```

Conclusion:

```text
triangle, or intermediate terminal door, or high-tier no-contact isolation,
or a blue path for an involved bad edge h with length <= ell(h)-3.
```

In a triangle-free shortest-row configuration with no intermediate terminal
door, this is impossible.  Therefore the high-tier endpoint branch of a
minimal two-hole corridor is impossible.

This is the scoped replacement for broad HT contact.  It is not a statement
about singleton high-tier misses or arbitrary high-tier first hinges.  The new
isolation branch is precisely what the broad counterexample exhibits: if the
endpoint-local contact fails, the high-tier miss is a one-miss branch.

Lean target:

```text
MinimalTwoHoleEndpointHighTier ->
  StrictReducedThetaShortcut
```

where `StrictReducedThetaShortcut` is the shared S2 theorem.

## Lemma 3: Scoped Rare-Monotonicity Persistence

Assume both endpoints of the minimal two-hole corridor have minimum tier:

```text
lambda(e0)=lambda(ek)=L0.
```

Let `A(e)` be the alternating closure of an unmatched minimum exit `e` in the
`F0-E0` witness graph:

```text
e -> h        if h in F0 witnesses e,
h -> mu(h)   if h is matched.
```

Stage-0 optimality gives:

```text
if u in A(e) cap mu(F0), then c(u) <= c(e).
```

Now take two cost-flat shadows and choose their first interaction.  At that
first interaction, orient the comparison from a nearer exit `a` to a farther
exit `b`.

Scoped persistence statement:

```text
Every F1 row counted in c(a) is also counted in c(b),
unless the first-interaction disk already gives S2.
```

If some new row `r` witnesses `b` but not `a`, then, after persistence,

```text
c(b) >= c(a) + 1.
```

This produces a matched exit reachable from the unmatched endpoint with
larger rare cost, contradicting stage-0 optimality.

This is the scoped replacement for broad RM persistence.  It is only asserted
at the first interaction of cost-flat shadows in a minimal two-hole
counterexample.

Lean target:

```text
FirstShadowInteraction ->
  (S2Shortcut) or (F1WitnessSetInclusionNearFar)
```

followed by the finite matching-dual lemma:

```text
reachable matched u with c(u)>c(e) -> contradicts min-cost(mu).
```

## Lemma 4: Shadow Separation

If two cost-flat shadows for the two minimum endpoints do not interact, then
the matched exits `mu(F0)` separate their terminal side blocks.  After deleting
`mu(F0)`, the two endpoints cannot lie in one residual component.

This is the disjoint case complementary to Lemma 3.

Lean target:

```text
CostFlatShadowClosed + DisjointShadows ->
  no_residual_cowitness_path_between_endpoints
```

## Splice/Matching Package For Single-Miss

The row proof should be packaged around one metric splice lemma and one
stage-0 matching-dual lemma.  Both are scoped to a genuine minimal two-hole
corridor; neither is a broad statement about arbitrary co-witnessed exits.

### Atom S: two-contact splice

Let `f,g in C`, let `q in Wit(f)`, let `p in Wit(g)`, and suppose
`p notin Wit(f)`.  Choose terminal rows `R_f(q)` and `R_g(p)`, decomposed as

```text
inside prefix + exit + outside suffix.
```

If the inside prefixes meet at some vertex `z` and the outside suffixes meet
at some vertex `w`, then replacing the `g` middle segment by the `f` middle
segment gives a blue path for `g` shorter by at least the slack `s_f(p)`.
Since `p notin Wit(f)`, the slack gate gives `s_f(p)>=2`; hence the new path
has length at most `ell(g)-3`.  The length-two degeneration is exactly
S2-Core 2 and gives a triangle.

This is the metric content already isolated in Lean as:

```text
MetricSpliceScratch.lean:
  spliced_dist_contradicts_shortest
  spliced_even_slack_contradicts_shortest

S2CoreScratch.lean:
  triangle_of_blue_and_bad
  s2_core_wrapper
```

Thus, after the scoped geometry supplies the two-contact walks and the
nonzero even slack, the HT branch has a Lean-complete finite contradiction
with shortestness.

### Atom HT: two-ended high-tier discharge

In a shortest residual two-hole corridor

```text
e0,g1,e1,...,gk,ek
```

for row `f`, if an endpoint `p=e0` has `lambda(p)>L0`, then the whole
two-ended corridor must supply either an intermediate terminal door, a
no-contact isolation contradiction, or the S2 splice data.  The first hinge
`p,g1,e1` may be one-sided separated in broad examples; the opposite missed
endpoint is part of the load-bearing scope.

Exact-test target for future synthetic gates:

```text
MinimalTwoHoleCorridor(f; e0,g1,e1,...,gk,ek)
lambda(p)>L0
------------------------------------------------
Door OR exists two-contact splice data with even nonzero endpoint slack
OR no-contact high-tier miss is the only f-miss in the residual component
```

Broad HT is false; the minimal-two-hole-corridor hypothesis is load-bearing.

### Atom M: stage-0 matching duality

Let `D_mu` be the directed exchange graph on `E0`, with an arc

```text
p -> q
```

when some `h in F0` satisfies `p in Wit(h)` and `mu(h)=q`.  If `p` is an
unmatched `E0` exit and `q` is a matched exit reachable from `p`, then
stage-0 minimum cost gives

```text
c(q) <= c(p).
```

Indeed toggling the alternating path replaces the used exit `q` by `p`, so
the cost change is exactly `c(p)-c(q)`.

Lean target:

```text
MinCostMatching(mu) + ReachableInExchangeDigraph(p,q) ->
  c(q) <= c(p)
```

This is finite matching duality; it contains no row geometry.

Lean status:

```text
Stage0MatchingScratch.lean:
  cost_le_of_no_improving_exchange
  strict_cost_contradicts_no_improving_exchange
```

### Atom RC: rare-cost endpoint exchange

If both endpoints of a minimal two-hole corridor are `L0` exits, then at least
one endpoint `p in {e0,ek}` has a reachable matched exit `q in R_mu(p)` such
that

```text
Wit_F1(p) subset Wit_F1(q) \ {f}.
```

Thus `c(q)>=c(p)+1`, contradicting Atom M.  This is the scoped directional RM
target: the dangerous direction is unmatched endpoint -> reachable matched
exit with larger rare cost.  The broad symmetric persistence statement is
false and must not be used.

Lean status:

```text
Stage0MatchingScratch.lean:
  rare_cost_strict_of_subset_erase
  witness_inclusion_contradicts_no_improving_exchange
```

Thus, after the scoped geometry supplies the alternating replacement set and
the witness-set inclusion, the minimum-tier branch has a Lean-complete finite
contradiction with stage-0 min-cost.

### Residual Hall proof from the package

Assume a residual component after the chosen stage-0 matching.

If a longer row misses a residual exit, the high-tier/replacement geometry
must supply a witnessed replacement exit of one of the following forms:

```text
same outside,
same row-terminal,
or oriented corner (inside(e), outside(f)).
```

The hard H3 counterexample to single-miss is exactly a corner-replacement
case: `_codex_replacement_exit_gate.py` reports `missing=6, corner=6`.
This local replacement rule is not by itself a Hall theorem.  There is a
three-by-three abstract countermodel: two rows both witness only one exit,
the third row witnesses all three exits, and all three exits have the same
outside door.  Every missed incidence has a same-outside replacement, the
component is connected and balanced, but the first two rows violate Hall.

Thus the proof target must keep the prefix-hull geometry.  The replacements
are only the visible local shadows of the stronger statement: every
right-closed deficient Hall set has a blue-closed prefix hull whose extra
blue boundary can be injected into residual bad side-door edges.

If both endpoints are minimum-tier, Atom RC gives a reachable matched exit
with larger rare cost, contradicting Atom M.

Therefore every residual component satisfies Hall.  The stronger statement
that every row misses at most one exit is false.  The remaining geometric proof
obligations are exactly:

```text
HT geometry:
  residual high-tier missing incidence -> blue-closed side-door Hall,
  or a local S2 splice contradiction.

RC geometry:
  minimal minimum-tier endpoints -> alternating replacement set +
  Wit_F1(p) subset Wit_F1(q) \ {f}, with f in Wit_F1(q).

Hall geometry:
  no reduced deficient multidoor fan core in the blue-closed prefix hull.
```

All finite contradiction steps after these scoped geometric outputs are now
covered by sorry-free Lean scratch kernels.

## Verified Evidence, Not Proof Inputs

The following exact gates are evidence and regression checks, but the proof
must not cite them as assumptions:

```text
_slack_gate.py:
  s_f(e)=0 iff witness, and every nonzero slack is >=2.

_codex_th_corridor_gate.py:
  row_miss<=1 in residual components on the finite battery.

_codex_stage0_all_min_rowmiss_gate.py:
  row_miss<=1 for every enumerated minimum stage-0 matching is false on the
  hard H3 side; do not use it.

_codex_residual_exact_hall_gate.py:
  exact residual Hall passes on the hard H3 side and selected battery.

_codex_ht_endpoint_contact_gate.py:
  broad HT is false, so the scoped hypothesis is essential.

_codex_rm_persistence_gate.py:
  broad RM is false, so first-interaction scope is essential.

_codex_rm_directional_gate.py:
  dangerous reachable matched exits have empty support:
  tested=182, ok=182, reachable_matched=7484, all c(target)<=c(root).
```

## Current Proof Status

The row-side finite consequences are verified.  The remaining rigorous work is
to prove Lemmas 1-4 from terminal-prefix shortest-row geometry, triangle
freeness, and stage-0 min-cost optimality.

These are prose/Lean targets, not broad census gates.
