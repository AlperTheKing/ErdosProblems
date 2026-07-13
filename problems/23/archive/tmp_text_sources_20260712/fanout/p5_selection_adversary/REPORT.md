# P5 selection adversary report

## Verdict

I did not find a graph-realizable counterexample to the proposed
active-scope-first selector.  I also do not find a proof of the selection
principle in the current artifacts.  The strongest proof-ready result is the
exact exchange lemma below.  Its hypotheses are row/graph predicates and do
not assume Hall, a matching, or a FullBank certificate.

The suggested third coordinate, "Pattern-5 quiescent reach", must be made
precise.  Maximizing a scalar such as the number of P5 keys or owner arcs is
not by itself a Hall principle.  The order-compatible object is inclusion of
the physical-source/owner relation after global deduplication and reservation
deduction.

No claim about Erdos #23 is made here.

## Exact setup

For a row choice `omega`, let:

- `V_omega` be the union of selected row vertices;
- `F_omega` be the union of selected blue row edges;
- `H_omega = B[V_omega] minus F_omega`;
- `A_omega` be the union of components of `H_omega` containing both
  endpoints of at least one listed bad edge;
- `r_omega(v)` be the number of selected rows containing `v`;
- `q_omega(v,u)` be the number of selected rows containing both `v,u`;
- `c_omega(v) = 2 sum_u max(0,q_omega(v,u)-1)`;
- `d_omega(v)` be the degree of `v` in `H_omega` when `v in A_omega`;
- `h_omega(v) = max(0,d_omega(v)-max(0,N-5r_omega(v)))`;
- `mu(omega) = sum_(v in A_omega) (c_omega(v)+25h_omega(v))`.

This is the production micro-demand scale used by the N12 artifacts.

## Lemma 1: support-expansion exchange

Let `omega,eta` be two valid row choices for the same graph and bad-edge
list.  Assume:

1. `V_eta subseteq V_omega`;
2. `F_omega subseteq F_eta`;
3. for every `v in A_eta`, `r_eta(v) <= r_omega(v)`;
4. for every `v in A_eta`, `c_eta(v) <= c_omega(v)`.

Hypothesis 4 may be replaced by the stronger, more local condition
`q_eta(v,u) <= q_omega(v,u)` for every `v in A_eta` and every vertex `u`.

Then:

```text
A_eta subseteq A_omega,
d_eta(v) <= d_omega(v)       for v in A_eta,
h_eta(v) <= h_omega(v)       for v in A_eta,
mu(eta) <= mu(omega).
```

Consequently:

- if `A_eta` is a proper subset of `A_omega`, `eta` beats `omega` under
  lexicographic minimization of `(|A|,mu)`;
- if `A_eta=A_omega` and one summed demand inequality is strict, then
  `mu(eta)<mu(omega)` and `eta` again beats `omega`.

### Proof

Every edge of `H_eta` has endpoints in `V_eta subseteq V_omega` and is not
in `F_eta`.  Since `F_omega subseteq F_eta`, it is not in `F_omega` either.
Thus `H_eta` is a subgraph of `H_omega`.

If `v in A_eta`, its `H_eta` component contains the endpoints of a bad edge.
The same path lies in `H_omega`, so the containing `H_omega` component is
active.  Hence `v in A_omega`.  Subgraph inclusion also gives
`d_eta(v)<=d_omega(v)`.

The map

```text
(d,r) |-> max(0,d-max(0,N-5r))
```

is nondecreasing in each argument.  Hypothesis 3 and the degree inequality
therefore give `h_eta(v)<=h_omega(v)`.  Add hypothesis 4 over `A_eta`, then
use `A_eta subseteq A_omega` and nonnegativity of every summand.  This proves
the demand inequality and both lexicographic consequences.

## Lemma 2: exact P5 arc monotonicity at a demand tie

Assume additionally:

1. `A_eta=A_omega=A`;
2. `H_eta` and `H_omega` induce the same component equivalence relation on
   `A`;
3. the positive co-occurrence witnesses on active boundary vertices persist:
   `q_omega(o,a)>0` implies `q_eta(o,a)>0` for every demanded owner `o` and
   every `a in A`;
4. every old P5-free ordered pair stays free:
   `q_omega(x,y)=0` implies `q_eta(x,y)=0` for every ordered pair occurring
   in a P5 source of `omega`;
5. the demanded-owner set is unchanged;
6. every physical half used by an old P5 arc remains outside the union of
   reservations introduced by all other terminal kinds at `eta`.

Then the globally keyed P5 source-owner arc relation satisfies

```text
R5(omega) subseteq R5(eta).
```

If one inclusion is strict, raw P5 owner-arc reach strictly increases.
If the P1--P4 relation is also inclusion-monotone across the exchange, then
the full P1--P5 relation is inclusion-monotone after deduplication.

### Proof

Because `A` is unchanged, the quiescent graph `B[V minus A]`, all of its
components, and all component boundaries in `A` are identical for the two
choices.  Hypotheses 2 and 3 preserve each old owner/attachment witness.
Hypothesis 4 preserves the `FreeHalf` predicate.  Switch loss depends only on
the fixed graph and the fixed union of quiescent components, so its
nonnegativity is unchanged.  Hypothesis 6 is exactly the missing global
reservation deduction.  Therefore every old physical source-owner arc is
still legal at `eta`.

This proof uses no common-blue idempotence assumption.  P5 itself introduces
no reservation, but that fact alone does not imply hypothesis 6.

## Why a scalar P5 tie-break is insufficient

Even after fixing `|A|` and `mu`, equal key counts or equal owner-arc counts
do not control Hall shores.  With owners `a,b`, each of demand two, compare:

```text
R_good: s1,s2 -> a;  s3,s4 -> b
R_bad:  s1,s2,s3,s4 -> a
```

Both relations have four physical keys and four owner arcs.  `R_good` has a
matching; `R_bad` fails on shore `{b}`.  This is an abstract relation
counterexample, not a graph-realizable P5 counterexample.  It proves that a
selection theorem cannot use only either scalar without an additional
graph-realizable exchange argument.

## Exact targeted probe

`lex_probe.py` enumerates only two pinned fixtures and uses the integer
`p5_core` reconstruction.  Command:

```powershell
python tmp/fanout/p5_selection_adversary/lex_probe.py
```

Results:

```text
J?BEFboL`{? : 4096 tuples; min (|A|,mu)=(0,0); 3296 ties; 0 P1-P5 failures.
K??E@cyjFgWk: 2400 tuples; min (|A|,mu)=(0,0); 2335 ties; 0 P1-P5 failures.
```

Maximizing any of `P5 key count`, `P5 owner-arc count`, or `new P5 owner
arcs` does not change these verdicts because P5 reach is zero when `A` is
empty.  These are targeted checks only.  They do not model the honest
FullBank typed capacities or cross-terminal reservation ledger.

For the 2943 cage, the supplied artifacts show only that the all-anchor tuple
has `|A|=19` and passes the static P5 shore, while the baseline has
`|A|=2775` and is P5-starved.  They do not prove that all-anchor globally
minimizes `|A|`, and they do not instantiate an honest FullBank ledger.

## Remaining frontier stated noncircularly

The missing theorem can now be isolated as follows: from a FullBank-deficient
owner shore at a lex-minimal row choice, construct a second valid row choice
satisfying Lemma 1 with a strict first or second coordinate, or satisfying
the equal-coordinate hypotheses of Lemma 2 with strict relation improvement
on that shore.  The conclusion must be a simultaneous shortest-row exchange;
the R29 evidence rules out requiring a one-row exchange.

This frontier mentions the deficient shore only as input.  Its required
output consists entirely of explicit row support, multiplicity,
co-occurrence, component, and reservation predicates, so it is not a
restatement of matching existence.
