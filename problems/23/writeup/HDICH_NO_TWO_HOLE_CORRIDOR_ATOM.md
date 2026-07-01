# hdich No-Two-Hole Corridor Atom

## Superseded Warning, 2026-07-01

This note is now an archived route, not the active proof target.

The component-local `AtMostOneMiss` conclusion is false on the hard
`h_blowup(3)` all-max side

```text
111111111111111100000000000
```

For the negative-residual switch at `v=18`, after the stage-0 matching the
residual component has size `9 x 9` and Hall holds, but rows

```text
(0,15), (1,15), (2,15)
```

each miss two residual exits.  For example `(0,15)` misses `(1,18)` and
`(2,18)`.  Therefore the proof cannot target no-two-hole or single-miss.

The replacement target is `RESIDUAL_HALL_CORNER_ATOM.md`: prove the exact
residual Hall theorem after stage 0, with corner/fiber replacements explaining
the hard H3 survivor.  The Lean plumbing in `THCorridorScratch.lean` remains a
useful archived scaffold, but it must not be used as a load-bearing theorem
unless its conclusion is changed from `AtMostOneMiss` to the residual Hall
condition.

This note freezes the current proof target for the row-side `hdich`
obligation consumed by `THCorridorScratch.lean`.

It is not a new global lemma.  It is the component-local statement for a
completed terminal-shadow switch after the stage-0 rare-cost matching.

## Existing Machine-Checked Spine

`problems/23/lean/THCorridorScratch.lean` already proves the logical wrapper:

```text
residual connectivity + not-missed-implies-witnessed
  -> choose a shortest missed-pair J-walk
  -> build a TwoHoleCorridor
  -> LongCert OR RareCert
  -> LongCert impossible and RareCert impossible
  -> AtMostOneMiss
```

The remaining hard content is therefore only the endpoint split:

```text
TwoHoleCorridor with a high-tier endpoint
  -> LongCert

TwoHoleCorridor with two minimum-tier endpoints
  -> RareCert
```

## Corridor Object

Let `(A,B)` be one residual connected component.  The residual exits are
vertices of `B`, and residual rows are vertices of `A`.

For an exit `e = x_e y_e`, with `x_e in S` and `y_e notin S`, and a crossing
bad edge `f = tau_f sigma_f`, with `tau_f in S`, set

```text
D_f = ell(f) - 1
s_f(e) =
  d_{B[S]}(tau_f, x_e) + 1 + d_{B[V\S]}(y_e, sigma_f) - D_f.
```

Terminal-shadow validity gives:

```text
f witnesses e  <=>  s_f(e)=0.
```

The parity gate gives:

```text
s_f(e)>0  =>  s_f(e)>=2.
```

Build the exit co-witness graph `J(A,B)`:

```text
e ~_J e'  <=>  exists g in A witnessing both e and e'.
```

If a row `f in A` misses two exits, choose a shortest `J` path between two
missed exits:

```text
e0, g1, e1, g2, ..., gk, ek
```

where each `g_i` witnesses `e_{i-1}` and `e_i`.  Shortest missed-pair
minimality and the partition `not Miss => Wit` give:

```text
s_f(e0)>0,
s_f(ek)>0,
s_f(e_i)=0 for 1<=i<=k-1.
```

This is the minimal two-hole residual corridor.

## Branch A: Long-Lambda Endpoint

If at least one endpoint has

```text
lambda(e)>L0,
```

then the corridor must produce a `LongCert`.

Proof target:

```text
The row-union disk of
  f and the hinge rows g_i
contains either
  a triangle,
  an intermediate terminal door,
  or a blue path for some h in {f,g1,...,gk}
     of length <= ell(h)-3.
```

Why this is the right local shape:

* each hinge `g_i` can shift from `e_{i-1}` to `e_i` without changing its
  shortest length;
* row `f` is strict at both endpoints and tight at every internal exit;
* the first and last strict hinges form a reduced two-hinge theta;
* the positive even slack supplies a saving of at least two blue edges.

The contradiction after the geometric output is already covered by the
existing Lean kernels:

```text
SlackParityScratch.lean:
  slack_ge_two_of_even_nonzero

MetricSpliceScratch.lean:
  spliced_dist_le_of_even_nonzero_slack
  spliced_even_slack_contradicts_shortest

S2CoreScratch.lean:
  no_internal_marked_of_minimal_marked_corridor
  no_nonconsecutive_common_witness_of_shortest_corridor
```

The open burden is not the arithmetic.  It is the two-ended geometry that
turns a high-tier endpoint of a genuine two-hole corridor into the reduced
terminal theta or door.

## Branch B: Minimum-Lambda Endpoints

If both endpoints satisfy

```text
lambda(e0)=lambda(ek)=L0,
```

then the corridor must produce a `RareCert`.

Stage 0 chooses an injective matching

```text
mu : F0 -> E0
```

minimizing

```text
sum_{h in F0} c(mu(h)),      c(e)=|Wit(e) cap F1|.
```

For an unmatched minimum exit `e`, let `Alt_mu(e)` be the directed alternating
closure:

```text
e -> h       if h in F0 witnesses e,
h -> mu(h)  for matched h.
```

Stage-0 minimality gives the matching-dual obstruction:

```text
u in Alt_mu(e) cap mu(F0)  =>  c(u)<=c(e).
```

Proof target:

```text
If a minimum-lambda two-hole corridor exists, then either
  one endpoint reaches a matched exit u with c(u)>c(e), or
  a multi-exchange replaces unmatched exits Z by matched exits U with
    |Z|=|U|
    sum_{z in Z} c(z) < sum_{u in U} c(u).
```

The contradiction after the geometric output is already covered by
`Stage0MatchingScratch.lean`:

```text
strict_cost_contradicts_no_improving_exchange
witness_inclusion_contradicts_no_improving_exchange
```

The open burden is the scoped rare geometry:

```text
two cost-flat minimum side blocks missed by the same row
cannot remain in one residual component after deleting mu(F0).
```

Equivalently, at the first interaction of the two cost-flat shadows, either
S2 fires or the F1 witness set is monotone in the needed direction:

```text
Wit_F1(near) subset Wit_F1(far) \ {new witness},
new witness in Wit_F1(far).
```

## Exact Gates Re-Run

These are regression checks, not proof inputs.

```text
python problems/23/writeup/_codex_th_corridor_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119
status={'ok': 119}
row_miss={0:325, 1:72}
VERDICT: PASS
```

```text
python problems/23/writeup/_codex_mu_separation_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119
status={'ok': 119}
VERDICT: PASS
```

```text
python problems/23/writeup/_codex_stage0_all_min_rowmiss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119
status={'ok': 119}
VERDICT: PASS
```

## Current Gap

The current gap is exactly:

```text
hdich:
  TwoHoleCorridor -> LongCert OR RareCert.
```

In concrete terms:

```text
Long branch:
  minimal two-hole corridor + lambda(endpoint)>L0
  -> reduced terminal theta / door / shorter-row certificate.

Rare branch:
  minimal two-hole corridor + both endpoints in E0
  -> stage-0 rare-cost exchange.
```

No proof may use component-local `row_miss<=1`, all-min row-miss gates, broad
HT contact, or broad RM persistence as assumptions.  Those are either the
desired conclusion or known false globally.
