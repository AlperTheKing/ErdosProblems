# Row No-Two-Hole Proof Draft

Goal:

```text
In every residual connected component (A,B) after stage-0 rare matching,
each row f in A misses at most one exit in B.
```

This is the row-side component-local single-miss theorem. It is exact-gated
in `NO_TWO_HOLE_RESIDUAL_CORRIDOR.md`; no two-hole row appears in the current
batteries.

Current H2 diagnostic:

```text
global row_miss_count     = {0:923, 1:72, 3:18, 8:48}
component row_miss_count  = {0:989, 1:72}
component singleton split = 40 long-lambda, 32 minimum-lambda
```

Thus the global one-miss statement is false; multi-misses are harmless when
they lie in different residual components. The theorem must use residual
component separation.

Additional stage-0 tie diagnostics:

```text
rare unmatched-universal gate:
  tested=182, ok=163, rem_e0_not_universal=19

all-min row-miss gate, H2-only:
  tested=119, ok=119, worst row_miss <= 1

all-min row-miss gate, H2 plus inherited H3/H4:
  ok=139, too_many=43, row_miss_fail=0

all-min unmatched-E0 miss gate:
  H2-only: tested=119, ok=119
  H2 plus inherited H3/H4: e0_miss=3
```

So a proof cannot use the false shortcut "every unmatched minimum exit is
universal to F1".  But the row-miss conclusion is robust across every
enumerated minimum-cost stage-0 tie; the deterministic tie-break is not the
source of the theorem.  A second tempting shortcut is also false in inherited
blow-ups: one F1 row may miss several unmatched `E0` exits globally.  Those
exits are harmless because they lie in different residual components.  This
confirms that component separation is the exact scope of TH-rare.

## 1. Reduction to a Minimal Corridor

Let `H=(A,B)` be a residual connected component, with edges `f~e` iff `f`
witnesses exit `e`. Fix `f in A` and suppose that it misses two exits.

Define the exit co-witness graph `J` on `B`:

```text
e--e' in J iff exists g in A with g witnesses both e and e'.
```

Because `H` is connected, `J` is connected on every nontrivial component.
Choose two missed exits `e0,ek` of `f` with minimum `J`-distance. Then there is
a shortest co-witness corridor

```text
e0, g1, e1, g2, ..., gk, ek
```

with:

```text
g_i witnesses e_{i-1} and e_i,
f misses e0 and ek,
f witnesses every internal e_i.
```

Thus the theorem follows once such a minimal two-hole corridor is impossible.

Lean status: the pure minimum-pair step is formalized in
`problems/23/lean/S2CoreScratch.lean` as
`no_internal_marked_of_minimal_marked_corridor`. It proves that if the endpoints
are chosen with minimum corridor length among all distinct marked pairs, then
no internal corridor vertex is marked. With `Marked(e) = "f misses e"`, all
internal exits of the minimal corridor are therefore `f`-witnessed.

## 2. Terminal Slack

For a crossing bad edge `h=tau_h sigma_h`, with `tau_h in S`, and an exit
`e=x_e y_e`, with `x_e in S`, define:

```text
D_h = ell(h)-1
s_h(e) = d_{B[S]}(tau_h,x_e) + 1
       + d_{B[V\S]}(y_e,sigma_h) - D_h.
```

Terminal-shadow validity gives:

```text
h witnesses e iff s_h(e)=0.
```

Every nonzero slack is at least `2`, because all terminal rows have the same
parity.

Lean status: the arithmetic form is in `SlackParityScratch.lean` as
`slack_ge_two_of_even_nonzero`. The metric splice consequence is in
`MetricSpliceScratch.lean` as `spliced_dist_le_of_even_nonzero_slack`, which
turns an even nonzero slack plus the two-contact splice hypotheses into a
blue-distance saving of at least two.

In the minimal corridor:

```text
s_f(e0) >= 2,
s_f(ek) >= 2,
s_f(e_i) = 0 for 1<=i<=k-1.
```

## 3. Long-Endpoint Lemma

Lemma TH-long:

```text
If lambda(e0)>L0 or lambda(ek)>L0, then the row-union disk of the minimal
corridor contains either a triangle or a B-path for one involved bad edge
h in {f,g1,...,gk} of length <= ell(h)-3.
```

Here `ell(h)-1` is the shortest B-distance between the endpoints of `h`, so a
path of length `<=ell(h)-3` is at least two B-edges shorter and is impossible.

### Proof Mechanism

For each hinge `g_i`, choose terminal rows:

```text
P_i^- exits through e_{i-1},
P_i^+ exits through e_i.
```

Write these rows as:

```text
inside prefix + exit + outside suffix.
```

Because both rows are shortest rows of the same bad edge `g_i`, shifting the
exit from `e_{i-1}` to `e_i` preserves total length:

```text
|I_i^-| + 1 + |O_i^-| = |I_i^+| + 1 + |O_i^+|.
```

For `f`, the internal exits are tight but the endpoints are slack. Therefore
the corridor starts with a strict `f`-improving hinge and ends with a strict
`f`-worsening hinge. Summing the hinge equalities along a shortest `J`-path
forces a reduced theta in which one diagonal saves the positive endpoint
slack.

The reduced theta is made from:

```text
f-rows through the internal exits,
g_i-rows through consecutive exits.
```

Minimality of the co-witness corridor gives:

```text
no g_i witnesses two nonconsecutive exits,
no internal exit is f-slack,
no row re-enters S after leaving.
```

Lean status: the pure shortest-corridor part is formalized in
`problems/23/lean/S2CoreScratch.lean` as `no_adj_getVert_of_shortest`. Applied
to the exit co-witness graph `J`, it proves that no shortest `J`-corridor has
an edge between nonconsecutive exits. The remaining row-specific work is to
connect a hinge row witnessing two nonconsecutive exits to precisely such a
`J` shortcut edge.

That bridge is now also formalized in the same scratch file:
`coWitnessGraph_adj_of_common_witness` and
`no_nonconsecutive_common_witness_of_shortest_corridor`. It packages the
definition of the co-witness graph and proves that a common hinge witness for
two distinct nonconsecutive corridor exits contradicts shortestness.

If the diagonal is not a valid shorter B-path, the only obstruction is a
length-2 degeneration, which together with the relevant bad edge forms a
triangle. Triangle-freeness excludes it.

This is the prose version of `disk_shorter_certificate` in
`_codex_th_corridor_gate.py`.

Claude's 2026-06-30 classification, updated at 21:59:45Z: TH-long is the
row-side mirror of the already-proven cap S2 theta exclusion and is accepted
at S2-level rigor. GPT-Pro's returned proof introduces endpoint hinge rigidity:
a reduced first hinge with `lambda(e0)>L0` is impossible, because the
first-split/last-rejoin theta forces either an elementary minimum-lambda hinge
or a blue shortcut/triangle. Thus

```text
lambda(e0)>L0 or lambda(ek)>L0
=> row-union disk has a triangle or a shorter B-geodesic.
```

TH-long is no longer the live row-side obstruction.

## 4. Minimum-Endpoint Lemma

Lemma TH-rare:

```text
If lambda(e0)=lambda(ek)=L0, then the stage-0 F0-E0 matching has a
rare-cost-decreasing alternating exchange.
```

The gate currently uses the sufficient certificate:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e)
with c(u)>c(e),
```

where:

```text
c(e)=deg_F1(e)=|Wit(e) cap F1|.
```

The H2 stage0 diagnostic shows the singleton minimum-lambda survivors occur
in equal-cost side blocks. For example:

```text
F0 = two length-5 rows,
E0 = four exits, all with c(e)=4 or all with c(e)=3,
stage0 uses two exits,
two unused E0 exits remain,
each residual component sees at most one harmless survivor.
```

This is exactly the shape TH-rare must rule out in pairs: one minimum survivor
can remain at equal cost, but two in the same residual component would force
their alternating closures to interact.

Important subtlety: a minimum-lambda missed exit need not have an `F0` witness
remaining in its residual component. In the H2 examples, a typical row is:

```text
ell(f)=7,
missed exit has lambda=5,
residual witnesses of that exit are four length-7 rows.
```

The length-5 row that prices the exit is used only through the stage-0
`F0-E0` matching and its alternating closure. The residual component itself
is an `F1` object after the matched `E0` exits have been deleted.

### Proof Mechanism

At a minimum-lambda missed exit `e`, every `F0` row witnessing `e` lies in the
terminal side block avoided by `f`; otherwise that `F0` row would also provide
a shortest witness for `f` at `e` or create an intermediate terminal door.

Let `p` be the first internal exit of the residual corridor that `f` witnesses.
The terminal-prefix geometry gives an alternating reachability relation:

```text
e -> F0 rows witnessing e -> their matched exits.
```

Any matched exit reached from `e` but not cheaper than `e` is protected by the
stage-0 optimality condition. Therefore a missed minimum exit can persist only
as an unmatched rare survivor at the boundary of its side block.

If there are two missed minimum exits `e0,ek` in the same residual component,
their terminal side blocks are connected by the residual co-witness corridor.
The two alternating closures cannot remain disjoint without separating the
component. At the first meeting or crossing of the closures, one closure
reaches a matched exit `u` with:

```text
c(u)>c(e)
```

for one of `e=e0,ek`. Replacing along the alternating path lowers

```text
sum_{h in F0} c(mu(h)),
```

contradicting the stage-0 minimum-cost matching.

This is the prose version of `alt_reach_cost_drop` in
`_codex_th_corridor_gate.py`.

The stricter statement "unmatched E0 exits are universal to F1" is false.
Exact failures occur in the H2/H3 inherited stress families. The replacement
is:

### Side-block separation lemma

For a minimum-cost stage-0 matching `mu`, let `e` be an unmatched minimum
exit. If every matched exit in `Alt_mu(e)` has rare cost at most `c(e)`, then
the closure of `e` is a terminal side block: all residual F1 rows missing
that block have the same terminal on the opposite side, and the block is
separated from the rest of the residual co-witness graph by the matched
stage-0 exits of the same cost.

Two such flat closures cannot lie in one residual co-witness component. If
they are disjoint, their separating matched exits disconnect the component.
If they meet or cross, the first-split/last-rejoin argument creates an
intermediate terminal door or a shorter B-geodesic, i.e. the same S2 theta
contradiction as TH-long.

Consequently a residual co-witness corridor between two minimum missed exits
must produce a strict alternating exchange:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e)
with c(u)>c(e).
```

Claude's 2026-06-30T22:33Z classification gives the missing proof skeleton:

1. Define the alternating closure `A(e)` of an unmatched minimum exit `e` in
   the `F0-E0` witness graph.  Stage-0 min-cost says no matched exit
   `u in A(e)` has `c(u)>c(e)`, because toggling the alternating path would
   lower the rare cost.

2. Prove rare monotonicity (RM) for reduced row-side corridors: if an `F1`
   row sees a farther exit but not a nearer exit, then that row contributes
   to `Wit_F1(farther)\setminus Wit_F1(nearer)`, hence rare cost strictly
   increases inward.  The proof is the same first-split/last-rejoin S2 theta
   used for TH-long and the cap endpoint-hinge rigidity.

3. Cost-flat shadows are closed under residual reachability.  If two flat
   shadows for minimum missed exits lie in one residual component, either
   they interact, in which case RM gives a reachable matched exit of larger
   rare cost, or they are disjoint, in which case `mu(F0)` separates them and
   they are not in one residual component.

Thus the genuinely new row-side atom has been reduced to S2 plus the
stage-0 min-cost exchange. The all-min row-miss gate supports it without
relying on the deterministic stage-0 tie-break:

```text
python problems/23/writeup/_codex_stage0_all_min_rowmiss_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --max-add 1

tested=119, status={'ok':119}
```

The stronger global statement

```text
for every f in F1, f misses at most one unmatched E0 exit
```

is true on H2 but false on inherited H3 stress.  The first failing pattern has
one row missing three unmatched minimum exits, all in different residual
components.  Therefore the proof must show:

```text
two flat minimum side blocks missed by the same f cannot be connected by a
residual co-witness corridor.
```

That is the precise "interact or separate" formulation.

Lean status: the min-cost exchange contradiction is formalized in
`Stage0MatchingScratch.lean` as
`witness_inclusion_contradicts_no_improving_exchange`. It says that if the
near/root witness set is contained in the far/matched witness set after erasing
one genuinely new F1 witness, then the far/matched rare cost is strictly larger
than the near/root rare cost, contradicting the stage-0 no-improving-exchange
inequality.

## 5. Consequence

Any two-hole row produces a minimal corridor.

If one endpoint is long-lambda, TH-long contradicts triangle-freeness or
shortestness.

If both endpoints are minimum-lambda, TH-rare contradicts the stage-0
minimum-cost matching.

Therefore no two-hole row exists, and the component-local single-miss theorem
holds.

## 6. Remaining Audit Point

The row-side skeleton is now closed modulo one proof-grade audit:

1. Verify every use of rare monotonicity and endpoint hinge rigidity satisfies
   the S2 reduced-theta hypotheses: terminal-prefix rows, no re-entry after
   leaving `S`, shortest co-witness corridor, and no already-existing
   intermediate terminal door.

Atom A/TH-long and Atom B/TH-rare are both classified as S2 consequences.
The next task is to state S2 once with exact hypotheses and check the row and
cap applications against that statement.
