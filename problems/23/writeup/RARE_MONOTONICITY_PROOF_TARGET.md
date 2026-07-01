# Rare Monotonicity Proof Target

This is the precise row-side statement needed for Atom B / TH-rare.

## Setup

Let `S` be a completed terminal-shadow switch.  Let

```text
C = delta_M(S),   E = delta_B(S),
F0 = {f in C : ell(f)=L0},
F1 = C \ F0,
E0 = {e in E : lambda(e)=L0}.
```

Stage 0 chooses a matching

```text
mu : F0 -> E0
```

minimizing

```text
sum_{h in F0} c(mu(h)),      c(e)=|Wit(e) cap F1|.
```

For an unmatched minimum exit `e`, define its alternating closure `A(e)` in
the `F0-E0` witness graph:

```text
e -> h       if h in F0 witnesses e,
h -> mu(h)  if h is matched.
```

Stage-0 optimality gives:

```text
if u in A(e) cap mu(F0), then c(u) <= c(e).
```

Otherwise toggling the alternating path from `e` to `u` lowers the stage cost.

## RM Statement

Let `a,b in E0` be exits in the same local side-shadow comparison, with `b`
farther inward along a reduced row-side corridor than `a`.

Suppose an `F1` row `r` witnesses `b` but does not witness `a`.

Then one of the following holds.

1. S2 shortcut:

```text
the first-split/last-rejoin disk for r and the relevant F0 shadow contains
an intermediate terminal door, a triangle, or a blue path for an involved bad
edge h of length <= ell(h)-3.
```

2. Strict witness contribution:

```text
r in Wit_F1(b) \ Wit_F1(a).
```

In case 2, if every other `F1` witness of `a` remains a witness of `b` along
the cost-flat shadow closure, then

```text
c(b) > c(a).
```

This is the rare monotonicity inequality.

## How RM Closes TH-Rare

Assume two unmatched minimum exits `e0,ek` missed by the same residual row `f`
lie in one residual component and have no negative rare-cost exchange.

Let `A(e0)` and `A(ek)` be their cost-flat alternating closures.  There are
two possibilities.

### Disjoint shadows

If the closures do not interact, their terminal side blocks are separated by
the matched exits `mu(F0)`.  After deleting `mu(F0)` they cannot be in one
residual component.  Contradiction.

### First interaction

At the first interaction, orient the comparison from the outer shadow toward
the inner/farther exit.  Apply RM.

If RM gives S2 shortcut, the graph violates triangle-freeness, shortestness,
or terminal minimality.  Otherwise RM gives `c(b)>c(a)` for a matched exit
`b` reachable from the unmatched `a`.  Toggling the alternating path lowers
the stage-0 rare cost, contradicting minimality.

Thus no two cost-flat minimum misses lie in one residual component.

## Proof Obligations Inside RM

RM must prove the following local facts.

1. First interaction is reduced.

```text
No smaller split/rejoin pair occurs before the selected interaction; otherwise
the shadows interacted earlier.
```

2. Near witnesses persist.

```text
Every F1 row counted in c(a) is also counted in c(b), unless S2 already gives
an intermediate terminal door or a shorter blue geodesic.
```

3. The row `r` is genuinely new at `b`.

```text
r witnesses b and not a by hypothesis, so after near-witness persistence it
strictly increases c(b).
```

The delicate part is (2).  It is another first-split/last-rejoin S2
application: if a near witness fails to persist to the farther exit, its
terminal row crosses the same side-shadow corridor and creates either a
smaller interaction or an S2 shortcut.

## Exact Gate Status

No actual two-minimum-endpoint corridor appears in the current exact battery,
so the full RM contradiction is not directly observed.  The correct scoped RM
statement is therefore not a real-data finite gate; it is a proof obligation
inside a minimal two-hole counterexample.

The broad predicate is false:

```text
python problems/23/writeup/_codex_rm_persistence_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Current result:

```text
tested: 26
status: {'ok': 25, 'rm_no_s2': 1}
VERDICT: FAIL
```

First broad-form falsifier:

```text
H2-allmax, n=18, side=111111111100000000,
S=(0,1,2,3,4,5,6,10,11,12,13,14,15),
r=(10,16), a=(7,14), b=(6,17), g=(10,17).
```

A narrowed diagnostic that checks only the rare-cost-danger direction has no
finite support:

```text
root e unmatched in E0,
matched u in Alt_mu(e) cap mu(F0),
c(u)>c(e),
r in F1 witnesses e but not u.
```

Run:

```text
python problems/23/writeup/_codex_rm_directional_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result:

```text
tested: 182
status: {'ok': 182}
stats: {
  'unmatched_roots': 992,
  'reachable_matched': 7484,
  'skip_nondangerous_cost': 7484
}
VERDICT: PASS
```

This is only a sanity check: it shows the finite battery contains no dangerous
`c(u)>c(e)` comparison to test.  It does not prove the scoped RM persistence
lemma.

Thus RM must be stated only at the first cost-flat shadow interaction in a
minimal two-hole counterexample.  In that scoped setting the battery has empty
support, because no two-hole residual corridor occurs.  The empirical handle
is synthetic: construct a minimal two-hole / first-interaction object avoiding
S2 and test whether it is realizable.

RM is also supported indirectly by:

```text
_codex_mu_separation_gate.py:
  no two unmatched E0 exits missed by one f lie in comp(f).

_codex_stage0_all_min_rowmiss_gate.py:
  component-local row_miss<=1 for every enumerated minimum matching.

_codex_rex_theta_gate.py:
  every singleton minimum miss is a 5/7 terminal theta.
```

A synthetic falsifier must produce:

```text
two cost-flat minimum exits for one f,
a residual co-witness path avoiding mu(F0),
no S2 shortcut/intermediate terminal door,
and no strict F1 witness-set inclusion.
```

No such object is currently known.
