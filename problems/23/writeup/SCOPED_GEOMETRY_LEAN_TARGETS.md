# Scoped Geometry Lean Targets

This file freezes the current proof-facing ledger for the delta=0 geometry.
It is deliberately narrower than the exploratory notes: every local lemma
below is stated only in the minimal-counterexample scope where it is intended
to be used.  The broad versions are false.

The final common S2 theorem package is frozen in
`S2_FROZEN_STATEMENT.md`.  This file lists the surrounding application
targets and broad-form guardrails.

## Status Ledger

### Gate-Verified Finite Facts

These are verified on the current exact batteries and may be cited as finite
evidence or as checks of definitions, not as substitutes for the scoped proofs.

```text
H1 terminal-prefix rows:
  terminal_shadow_details / witness_structure reject re-entry.

H2 shortest-row property:
  every row used is selected from cyc[f], the shortest restricted-B geodesics.

H4 strictness:
  _slack_gate.py: s_f(e)=0 iff witness, nonzero slack >= 2.
  cap L>=7 canonical cores have an annulus/corridor excess of exactly 2.
  Lean kernels:
    SlackParityScratch.lean: slack_ge_two_of_even_nonzero.
    MetricSpliceScratch.lean: spliced_dist_le_of_even_nonzero_slack.

REX singleton shape:
  singleton minimum misses are 5/7 terminal annuli in the finite battery.
```

### Evidence Only, Not Proof Inputs

These support the skeleton but are circular if used as assumptions in the row
proof.

```text
component-local row_miss <= 1 in the old finite batteries.
  Superseded/false on the hard H3 all-max side:
  h_blowup(3), side 111111111111111100000000000, v=18.
  The residual component is 9x9 and Hall holds, but three rows each miss two
  exits.  Use residual Hall, not single-miss.
all-min-cost rowmiss/e0miss gates.
mu(F0)-separation gates.
directional RM diagnostic:
  no dangerous c(target)>c(root) comparison occurs in the battery.
```

### Scoped Prose/Lean Obligations

These are the remaining load-bearing geometric facts.  Each has a broad-form
falsifier, so every formal statement must carry its scope hypotheses.

```text
LIVE ROW TARGET:
  Residual-Hall via blue-closed prefix hulls.
  Lean spine:
    problems/23/lean/ResidualHallScratch.lean
  Gate/prose target:
    problems/23/writeup/NO_NAKED_LEAF_RFC_TARGET.md
  Remaining geometry:
    (1) one-door peeling: deficient non-reduced core descends;
    (2) NL descent: reduced deficient fan core descends to a smaller reduced
        deficient fan core.

ARCHIVED ROW TARGET:
  Component-local single-miss / no-two-hole.
  False on hard h_blowup(3) all-max side
  111111111111111100000000000 at v=18.

REUSABLE KERNELS:
  S2. Reduced terminal-theta core.
  Path-splice / slack kernels.

CAP SIDE:
  Cap. Minimal deficient core gives terminal-product normal form.
```

## Broad-Form Falsifiers

The following statements must never be used globally.

```text
H3 broad reducedness:
  false / circular if derived from row_miss<=1, because row_miss<=1 is the
  conclusion of the row proof.

HT broad endpoint contact:
  false on H2-allmax N=18 with a single missed high-tier exit:
  S=(0,1,11,12), f=(0,10), g=(11,16), p=(1,13), q=(0,13).
  This is not a two-hole corridor endpoint.

RM broad persistence:
  false on H2-allmax N=18 for a co-witnessed pair outside the first-interaction
  scope:
  r=(10,16), a=(7,14), b=(6,17), g=(10,17).

Global unmatched-E0 exposure:
  false in inherited stress; a row can miss several unmatched E0 exits
  globally, but they lie in different residual components.
```

## Lean Target 1: Path-Splice Core

Pure graph/path lemmas, independent of the seed/moat machinery.

### P1: Shortest Subpath

If `P` is a shortest blue path between `x` and `y`, every subpath of `P` is a
shortest blue path between its endpoints.

### P2: Two-Row Segment Equality

If two shortest blue rows meet in two vertices `r,s`, then the corresponding
segments between `r,s` have equal length unless one of the original rows can be
shortened by splicing the shorter segment into the longer row.

### P3: Strict Splice

If a valid splice replaces a row segment by a blue segment shorter by at least
`2`, then the corresponding bad edge has a blue path of length at most
`ell(h)-3`.

### P4: Triangle Degeneration

If the strict splice is obstructed only by the length-2 degeneration around a
bad edge, the original graph contains a triangle.

## Lean Target 2: S2 Reduced Terminal-Theta

### Hypotheses

A reduced terminal theta consists of:

```text
1. two split/rejoin vertices r,s;
2. two internally disjoint blue arms A,B from r to s;
3. terminal row continuations attached to A and B;
4. every involved row is a shortest row and has terminal-prefix form:
   inside prefix + one boundary exit + outside suffix;
5. no involved row re-enters S after leaving it;
6. reducedness supplied by the application-specific minimality condition;
7. a strict source: an application-supplied terminal slack, annulus excess, or
   first-interaction rare-cost jump gives a valid replacement saving at least
   two blue edges.
```

### Conclusion

At least one of the following holds:

```text
1. there is an intermediate terminal door;
2. some involved bad edge h has a blue path of length <= ell(h)-3;
3. the original graph contains a triangle.
```

Thus in a triangle-free graph with shortest rows and no intermediate terminal
door, a strict reduced terminal theta is impossible.

The absence of an intermediate terminal door is not a core hypothesis. Each
application first case-splits: an existing door closes by minimality; in the
no-door branch S2 supplies the triangle or shorter-row contradiction.

## Application A: Row H3 Reducedness

**Archived row application.** This application targeted component-local
single-miss / no-two-hole.  That target is false on the hard `h_blowup(3)`
all-max side.  The pure graph kernels below may still be reused, but this is
not a live proof obligation.

### Scope

Assume a minimal two-hole residual corridor:

```text
f; e0,g1,e1,...,gk,ek
```

where `f` misses exactly the endpoints among the chosen shortest `J` path and
witnesses every internal exit.

### Required Reducedness Facts

```text
1. Internal exits are f-tight:
   otherwise a closer pair of missed exits exists.

2. No hinge row g_i witnesses nonconsecutive corridor exits:
   if g_i witnessed e_a and e_b with b>a+1, the exit co-witness graph J has
   the shortcut e_a--e_b, contradicting shortestness of the chosen J path.

3. Any smaller split/rejoin inside the disk is chosen instead:
   use the innermost/outermost split-rejoin pair as the S2 theta.
```

Important wording: the reducedness condition is on the hinge rows `g_i`, not
on the reference row `f`.  The reference row `f` is allowed to witness all
internal exits.

Lean status: the pure graph kernel for item 2 is proved in
`problems/23/lean/S2CoreScratch.lean` as `no_adj_getVert_of_shortest`.  It
says that a shortest walk has no edge joining two nonconsecutive positions,
which is exactly the exit-co-witness shortcut contradiction after applying it
to the `J`-corridor.

The definitional bridge from a hinge witness to a `J` shortcut is also proved
there as `coWitnessGraph_adj_of_common_witness` and
`no_nonconsecutive_common_witness_of_shortest_corridor`. Thus the formal H3
kernel covers the exact phrase "a hinge row witnessing two nonconsecutive
exits contradicts shortestness of the residual co-witness corridor."

Lean status: the pure minimal-pair kernel for item 1 is proved in the same
file as `no_internal_marked_of_minimal_marked_corridor`.  It says that if the
two endpoint exits are chosen with minimum corridor length among all distinct
missed pairs, then every internal vertex of that corridor is unmarked. Applied
with `Marked = missed by f`, this is the formal core of "internal exits are
f-tight."

## Application B: HT/EHR Two-Ended High-Tier Discharge

**Archived row application.** This was part of the false no-two-hole route.
Do not use it as a live obligation.  The metric-splice kernels named below
remain reusable local facts.

### Scope

Only inside a genuine shortest residual two-hole corridor endpoint:

```text
f misses e0 and ek,
g1 witnesses e0,e1,
internal exits are f-tight,
the corridor is shortest in J.
```

### Obligation

The full two-hole corridor, not a single hinge alone, supplies the two-sided
contact or reduced terminal theta needed for the contradiction.  The broad
assertion

```text
f in F1, p missed, q witnessed, g witnesses p,q => two-sided contact
```

is false and must not be used.

### Expected Proof Shape

Use the high-tier endpoint dichotomy:

```text
first hinge has two-sided contact
  -> metric splice with endpoint slack >=2;

first hinge has no two-sided contact
  -> the high-tier missed exit is isolated as the only miss of f in that
     residual component.
```

The second branch contradicts the two-hole hypothesis.  Thus the full
two-ended corridor, not a single local hinge, forces one of:

```text
1. a closer two-hole corridor,
2. an intermediate terminal door, or
3. the S2 reduced theta directly.
```

Lean status: the arithmetic/metric strictness part of this splice is isolated
in `MetricSpliceScratch.lean`.

```text
spliced_dist_le_of_even_nonzero_slack
spliced_dist_contradicts_shortest
spliced_even_slack_contradicts_shortest
```

Once the scoped endpoint-contact geometry supplies the two common split/rejoin
vertices, the slack candidate inequality, nonzero even slack, and shortestness
identity for the hinge row, these lemmas give the branch contradiction.

Remaining HT burden:

```text
minimal two-hole corridor with at least one high-tier endpoint
  -> intermediate door OR
     scoped no-contact isolation contradiction OR
     two-contact walks + nonzero even slack + shortestness identity
```

The no-contact isolation line remains a scoped proof obligation.  The current
finite gates are evidence only until the Grotzsch/Mycielskian/glued-island
stress battery is fully reconciled.

Lean status: the row-side wrapper from the frozen TH-Corridor target to the
component-local one-miss conclusion is isolated in `THCorridorScratch.lean`.
It proves the abstract plumbing:

```text
two missed exits -> exists TwoHoleCorridor
Door is excluded upstream by H3 reducedness kernels
every TwoHoleCorridor -> TH-long certificate OR TH-rare certificate
TH-long certificates impossible
TH-rare certificates impossible
---------------------------------------------------------------
AtMostOneMiss
```

This does not prove the HT/EHR or RM geometric discharges.  Those remain the
open application obligations supplying the Long/Rare output after any Door
alternative has already been closed by H3 minimal-corridor kernels.

Lean status: the first arrow is kernelized in two pieces in
`THCorridorScratch.lean`.

```text
WitnessChain / WitnessChain.toWalk:
  an alternating residual row-exit witness chain projects to a walk in J.

LooseWitnessChain / LooseWitnessChain.toWalk:
  an incidence-component chain that may repeat an exit projects to a J-walk
  after deleting stationary exit steps.

WitnessChain.ofWalk / exists_witnessChain_of_walk:
  a J-walk can be expanded to an alternating witness chain by choosing the row
  witness for each co-witness adjacency.

twoHoleCorridor_of_minimal_missed_walk:
  a J-walk chosen with minimum length among distinct missed-exit pairs has no
  internal missed exits; if not-missed implies witnessed, it is a
  TwoHoleCorridor.

twoHoleCorridor_of_minimal_witnessChain:
  composed form starting from an explicit alternating witness chain.

twoHoleCorridor_of_minimal_connected_walk:
  walk-facing alias for the same minimal-pair kernel.

atMostOneMiss_of_minimal_missed_walk_target:
  one-shot wrapper consuming minimal missed-pair J-walks directly.

atMostOneMiss_of_connected_missed_pairs_target:
  if any distinct missed pair has a J-walk, choose a globally shortest
  missed-pair J-walk by well-ordering of Nat; the TH-Corridor target then
  gives the component-local one-miss conclusion.

dichotomy_of_endpoint_split:
  formal splitter for `hdich`: a long-tier endpoint gives `LongCert`; two
  minimum-tier endpoints give `RareCert`.

atMostOneMiss_of_endpoint_split_connected_target:
  connected-pair wrapper that exposes the two scoped geometry obligations
  directly instead of taking an opaque `hdich`.

atMostOneMiss_of_witnessChain_connected_missed_pairs_target:
  same conclusion when residual connectivity supplies a `WitnessChain` for
  every distinct missed pair.

atMostOneMiss_of_looseWitnessChain_connected_missed_pairs_target:
  same conclusion when residual connectivity supplies a `LooseWitnessChain`
  for every distinct missed pair.
```

The remaining concrete input is only to extract a J-walk, `WitnessChain`, or
`LooseWitnessChain` from the residual component data.  The minimum-length
missed-pair selection is now pure Lean plumbing.

## Application C: RM Directional Near-Witness Persistence

### Scope

Only at the first interaction of two cost-flat alternating shadows in a
hypothetical minimum-lambda two-hole corridor.

Let:

```text
e = unmatched root in E0,
u = matched exit in Alt_mu(e) cap mu(F0),
c(u)>c(e) be the dangerous rare-cost direction,
r in F1 witnesses e but not u,
g in F0 witnesses both e and u.
```

The finite battery contains no such dangerous instance, so this is not
real-data gateable.

### Obligation

At the first interaction, either:

```text
1. S2 fires: intermediate terminal door, triangle, or shorter blue row; or
2. every near F1 witness persists from the near/root side to the farther side,
   and r is a genuinely new F1 witness there, giving c(farther)>c(nearer).
```

Then the alternating path from the unmatched root to the higher-cost matched
exit lowers the stage-0 rare cost, contradicting the min-cost choice.

Lean status: the stage-0 contradiction after directional persistence is
machine-checked in `Stage0MatchingScratch.lean`:

```text
rare_cost_strict_of_subset_erase
strict_cost_contradicts_no_improving_exchange
witness_inclusion_contradicts_no_improving_exchange
```

Thus the remaining RM proof obligation is only geometric: at the first
interaction, either S2 fires or the near-side F1 witness set is contained in
the far-side witness set after deleting the genuinely new witness. Once that
inclusion is supplied, the stage-0 contradiction is Lean-covered.

Remaining RC burden:

```text
minimal minimum-tier two-hole endpoints
  -> alternating replacement set +
     Wit_F1(near) subset Wit_F1(far) \ {new witness},
     with new witness in Wit_F1(far)
```

### Noncircular Reducedness

Use first interaction:

```text
Any earlier near-witness failure would itself be an earlier interaction or an
S2 theta.
```

Do not use row_miss<=1 or mu-separation as assumptions.

## Application D: Cap Terminal-Product Normal Form

### Scope

A minimal deficient cap core after the Ferrers/laminar classification.

### Obligation

Minimality plus no intermediate terminal door implies:

```text
terminal cap -- rigid middle corridor -- terminal cap
```

For `L>=7`, the rigid middle corridor contains a blue edge common to all
shortest rows of both core bad edges.  Recutting that edge lowers the core
gamma contribution from `L^2+(L+2)^2` to `L^2`, unless an attachment creates
an S2 shorter-row/intermediate-door contradiction.  Hence `L=5`.

## Immediate Next Formalization Order

```text
1. P1-P4 path-splice lemmas.
2. S2 reduced terminal-theta theorem.
3. Row H3 reducedness from shortest J-corridor.
4. HT/EHR scoped endpoint contact.
5. RM directional first-interaction persistence.
6. Cap terminal-product / L=5 forcing.
```

This ordering keeps every circular finite consequence out of the proof inputs.

## Focused Residual Hall Target

The old proof-facing row-side `hdich` atom in
`HDICH_NO_TWO_HOLE_CORRIDOR_ATOM.md` is now archived because its
`AtMostOneMiss` conclusion is false on the hard H3 all-max side.

The active replacement is
`RESIDUAL_HALL_CORNER_ATOM.md`.

That file is the handoff target for the remaining residual matching theorem:

```text
after the stage-0 rare-cost matching,
every residual F1/E component satisfies Hall.
```

The hard H3 side shows why this is the right strength:

```text
single-miss false,
residual Hall true,
misses repaired by corner/fiber exits.
```

Current exact gate:

```text
_codex_residual_exact_hall_gate.py:
  PASS, tested=175, components=178, no failures.
```
