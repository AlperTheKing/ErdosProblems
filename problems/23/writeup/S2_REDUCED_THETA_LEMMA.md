# S2 Reduced-Theta Lemma

This note is the proof-grade target behind the cap L=5 forcing, row
TH-long/EHR, and row TH-rare/RM applications.

Canonical scoped/formalization ledger:

```text
problems/23/writeup/SCOPED_GEOMETRY_LEAN_TARGETS.md
```

That ledger is authoritative on what is gate-verified, what is only evidence,
and which scoped statements remain prose/Lean obligations.

## Path-Splice Lemma

Let `P` be a shortest blue row for a bad edge `h`, so `P` is a shortest
`B`-path between the endpoints of `h`.

Then every subpath of `P` is a shortest blue path between its endpoints.

Proof: if a subpath `P[a,b]` could be replaced by a shorter blue path between
the same endpoints, splicing that replacement into `P` gives a shorter blue
row for `h`.

Consequently, if two shortest rows `P in cyc[h]` and `Q in cyc[g]` meet in
two vertices `a,b`, and the corresponding `P[a,b]` and `Q[a,b]` segments are
internally disjoint, then either their blue lengths are equal or one of
`g,h` already has a shorter blue row.

This is the only automatic shortest-path fact used below.

## Reduced Theta Setup

A reduced terminal theta consists of:

```text
two split/rejoin vertices r,s,
two internally disjoint blue arms A and B from r to s,
terminal row continuations attached to the arms,
and no intermediate terminal door in the theta interior.
```

It is produced by terminal-prefix rows, so every row involved has the form

```text
inside prefix + one boundary exit + outside suffix
```

and never re-enters the switch after leaving it.

Reduced means:

1. no smaller split/rejoin pair gives the same obstruction;
2. no hinge row witnesses two nonconsecutive exits in the selected corridor;
3. no internal exit in the selected corridor is slack for the reference row.

## Strict Diagonal Lemma

Assume a reduced terminal theta has a positive even slack/excess source.
Concretely, one of the two arms can be used to replace the other in an
involved terminal row, and the length difference is at least `2`.

Then the theta gives one of:

```text
1. an intermediate terminal door;
2. a blue path for an involved bad edge h of length <= ell(h)-3;
3. a triangle in G.
```

Proof outline:

If an intermediate terminal door lies in the theta interior, we are in case
1.  Otherwise the terminal-prefix property lets us splice one blue arm in
place of the other inside one involved bad-edge row.  The positive even
slack/excess says the replacement saves at least two blue edges.  Since a row
for `h` has `ell(h)-1` blue edges, the replacement has length at most
`ell(h)-3`, giving case 2.

The only way the splice is not a valid simple blue path is the minimal
degeneration where the replacement plus the bad edge has length three in the
original graph.  That is exactly a triangle, case 3.

Thus in a triangle-free graph with shortest rows and no intermediate terminal
door, the strict reduced theta is impossible.

## Sources Of Strictness

The applications must explicitly identify one of these sources:

### Endpoint Slack

For a terminal-shadow switch and crossing edge `f`, define

```text
D_f = ell(f)-1,
s_f(e)=d_{B[S]}(tau_f,x_e)+1+d_{B[V\S]}(y_e,sigma_f)-D_f.
```

The slack gate verifies:

```text
s_f(e)=0  <=>  f witnesses e,
nonzero s_f(e) >= 2.
```

Thus a long-door two-hole corridor with endpoint slack has the required
strict even saving.

### Annulus Excess

In a nested `L/(L+2)` cap core or a singleton row REX `5/7` annulus, the
outer row has two more blue edges than the inner row.  Crossing two annuli or
putting an interior split into the middle corridor exposes an arm replacement
that saves exactly this positive even excess.

### Rare Monotonicity

In the minimum-lambda row case, strictness is not a scalar overload.  It is
the first point where a cost-flat shadow interacts with another shadow.  If
an `F1` row witnesses the farther exit but not the nearer exit, then it is a
new member of the farther `F1` witness set.  If S2 did not give a shortcut or
intermediate door, the row would have to witness both exits, contradicting
the assumed near/far separation.  Therefore

```text
c(farther)>c(nearer).
```

This supplies the strict rare-cost increase used by the alternating-exchange
argument.

## Application Audit

### Cap L=5 Forcing

S2 inputs:

```text
terminal-prefix rows from the cap classification,
no intermediate terminal door by minimal deficient block,
interior split in an L>=7 nested core,
annulus excess >=2.
```

S2 output:

```text
terminal-product normal form; hence an L>=7 core has a universal shared
middle blue edge.
```

Then the core recut turns that universal blue edge into the unique core bad
edge and lowers the gamma contribution from `L^2+(L+2)^2` to `L^2`,
contradicting gamma-minimality.  Therefore `L=5`.

### Row TH-long / Endpoint Hinge Rigidity

S2 inputs:

```text
shortest exit co-witness corridor,
internal exits f-tight,
one endpoint f-slack,
hinge rows terminal-prefix through consecutive exits.
```

The first strict hinge and last opposite strict hinge form a reduced theta.
Endpoint slack is nonzero, hence at least two by parity.

S2 output:

```text
triangle or blue path <= ell(h)-3 for some involved h.
```

This is impossible, closing the long-lambda branch.

### Row TH-rare / Rare Monotonicity

S2 inputs:

```text
minimum-lambda endpoint corridor,
cost-flat alternating closure,
first interaction of two residual shadows,
terminal-prefix singleton 5/7 annuli from the REX theta gate.
```

S2 output:

```text
either an intermediate terminal door / shorter row,
or the interaction is monotone: c(farther)>c(nearer).
```

At first shadow interaction, monotonicity gives a matched exit reachable from
an unmatched minimum exit with larger rare cost.  Toggling the alternating
path lowers the stage-0 matching cost, contradiction.  If the shadows do not
interact, the matched `mu(F0)` exits separate them, so they cannot lie in one
residual component.

## Current Verification Anchors

```text
_slack_gate.py:
  switches=119, f-e pairs=5404, mismatch=0, nonzero slack<2=0.

_codex_rex_theta_gate.py:
  singleton misses have ell(f)=7 and contain an ell=5 F0 row.

_codex_th_corridor_gate.py:
  tested=182, ok=182, no row with two residual misses.

_codex_l5_forcing_gate.py / _l5forcing_gate.py:
  L>=7 canonical stretched cores recut to one shared-corridor bad edge.
```

This file is still prose.  The next formalization task is to turn the
Path-Splice Lemma and Strict Diagonal Lemma into Lean-ready graph statements.
