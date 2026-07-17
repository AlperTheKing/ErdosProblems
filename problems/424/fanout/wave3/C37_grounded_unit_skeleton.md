# C37: grounded unit skeleton - clean finite lemma and rank obstruction

## Verdict

Outcome (ii) is obtained, together with a precise obstruction of type (iii).

There is no cutoff-uniform construction proved here.  There is, however, a
strictly smaller combinatorial certificate lemma in which all witness
variables and all continuous stationarity equations have been eliminated.
Its data are only seed-2 chain edges, lower parent-pair choices, and upper
parent transversals.  The lemma is proved below by summing elementary gate
inequalities, not by appealing to LP duality.

The complete-gate extraction passes exactly at every one of the 147 hard
cutoffs through 2000.  At every cutoff it has the same integer objective as
the full grounded LP dual.  Thus incomplete AND/OR fragments in the HiGHS
bases are not needed for the inequality; they are zero-objective
stationarity shims.

The hoped-for local rank recurrence is false.  Canonically replacing lower
pairs by maximum death-rank pairs and upper choices by earliest-death parents
fails first at the hard cutoff 1644: its exact score is 118, while 119 is
required.  It fails at 13 of the 147 hard cutoffs through 2000.

## 1. Elementary unit inequalities

Fix a cutoff (X).  Let (A_X) be the allowed values in ([2,X]), let
({\cal P}(n)) be the admissible parent pairs (a<b), (ab=n+1), let
(D_X) be the hard values, and let (G_X) be the literal grounded core.
Write (T(x)=2x-1).

The grounded LP has source variables (s_x), image variables (f_n), and
boundary variables (q_{T(x)}).  Its facets directly imply the following
three inequalities.

For one pair (p=(a,b)\in{\cal P}(n)), one lower AND row and one lower OR
row give

\[
 f_n\ge s_a+s_b-1.                                      \tag{L}
\]

For a transversal (\tau_n) choosing one parent from every pair in
({\cal P}(n)), one upper OR row and one upper AND row for each pair give

\[
 f_n\le \sum_{p\in{\cal P}(n)}s_{\tau_n(p)}.             \tag{U}
\]

For a seed-2 edge (x\to T(x)), the lower boundary row gives

\[
 q_{T(x)}\ge f_{T(x)}-f_x.                              \tag{B}
\]

Every row used in (L), (U), and (B) has multiplier one.

## 2. Clean-skeleton lemma

Choose the following finite data.

* (C\subseteq\{T(x):x\in A_X,\ T(x)\le X\}), the selected boundary
  children.
* (L\subseteq\{(n,p):p\in{\cal P}(n)\}), the selected lower gates.
  No pair is selected more than once.
* (U\subseteq\{n:{\cal P}(n)\ne\varnothing\}), the selected upper gates.
* For every (n\in U), a transversal (\tau_n) of ({\cal P}(n)).

Put

\[
 \ell_n=|\{p:(n,p)\in L\}|,
 \qquad u_n=1_{n\in U},
\]

and count source-parent occurrences by

\[
 \lambda_x=|\{(n,p)\in L:x\in p\}|,
 \qquad
 \mu_x=|\{(n,p):n\in U,\ \tau_n(p)=x\}|.
\]

The remaining source-bound coefficient is

\[
 \sigma_x=\lambda_x-\mu_x.                              \tag{1}
\]

The image coefficient after chain telescoping and complete gates is

\[
 \rho_n=
 1_{n\in D_X}+1_{n\in C}-1_{T(n)\in C}-\ell_n+u_n,       \tag{2}
\]

where (1_{T(n)\in C}=0) when (T(n)>X).

Define the exact bound contributions

\[
 B_s(x,r)=
 \begin{cases}
 r,&x\in G_X,\\
 \min(r,0),&x\notin G_X,
 \end{cases}                                             \tag{3}
\]

and

\[
 B_f(n,r)=
 \begin{cases}
 r,&n\in\{2,3\},\\
 0,&n\notin\{2,3\},\ {\cal P}(n)=\varnothing,\\
 \min(r,0),&\text{otherwise}.
 \end{cases}                                             \tag{4}
\]

Finally set

\[
 \Phi(C,L,U,\tau)=
 -|L|+\sum_{x\in A_X}B_s(x,\sigma_x)
      +\sum_{n\in A_X}B_f(n,\rho_n).                    \tag{5}
\]

**Clean-skeleton lemma.** If

\[
 \Phi(C,L,U,\tau)\ge |D_X|,                             \tag{CS}
\]

then the grounded LP proves

\[
 H_{F(S)}(X)\le Q_{F(S)}(X)
\]

for every source vector with (s_g=1) for (g\in G_X), hence for every
set (S\supseteq G_X).

### Proof

Use (B) for children in (C), and use (q_c\ge0) otherwise.  Then

\[
 \sum_{n\in D_X}f_n+\sum_c q_c
 \ge \sum_n b_n f_n,
 \qquad
 b_n=1_{n\in D_X}+1_{n\in C}-1_{T(n)\in C}.             \tag{6}
\]

Sum (L) over (L), and sum the negatives of (U) over (U).  Their image
coefficient at (n) is (ell_n-u_n), their source coefficient at (x)
is (mu_x-lambda_x=-\sigma_x), and their total constant is (-|L|).

Add the source bound with coefficient (sigma_x).  If (sigma_x>0),
use the lower bound; if (sigma_x<0), use the upper bound.  Its exact
constant is (3), because (s_x=1) on (G_X) and (0\le s_x\le1)
otherwise.  This cancels every source coefficient.

Add the image bound with coefficient (ho_n) in the same way.  Its exact
constant is (4), since (f_2=f_3=1), a pairless nonseed has (f_n=0),
and every other (f_n) lies in ([0,1]).  By (2), the resulting image
coefficient is

\[
 \ell_n-u_n+\rho_n=b_n.
\]

The summed inequalities therefore give

\[
 \sum_n b_n f_n\ge\Phi(C,L,U,\tau).
\]

Combine this with (6) and (CS).  This proves the lemma.  \(\square\)

This is smaller than the grounded LP: it contains no (w)-variables, no
primal (s,f,q) search, and no real multipliers.  Once (C,L,U,\tau) are
given, (1)-(5) are an integer check.

## 3. Seed-2 chain form

Group the children in (C) by their unique seed-2 chain.  Every group has a
unique decomposition into maximal consecutive depth intervals.  On one
interval (T^{r+1}(v),\ldots,T^s(v)), (B) telescopes to

\[
 \sum_{j=r+1}^{s}q_{T^j(v)}
 \ge f_{T^s(v)}-f_{T^r(v)}.                              \tag{7}
\]

Thus (C) is exactly a family of unit chain intervals; (L) and (U) route
their endpoint coefficients through common source-parent labels.  The
quantities (lambda_x-mu_x), not the rank of an individual pair, are the
global conservation law.

The first two sparse atoms illustrate both mechanisms.

* At (X=54), the full interval
  (6\to11\to21\to41) has (f_6=0) and grounded (f_{41}=1), so its
  three boundary rows already contribute one unit.
* At (X=186), the conditional atom uses
  (f_{186}\ge s_{11}), (f_{32}\le s_{11}), and the interval
  (32\to63\to125), where (f_{125}=1).  Hence
  (f_{186}+q_{63}+q_{125}\ge1).

These are direct inequalities, not interpretations of a floating-point
solution.

## 4. All nine endpoint supports

The normalization rule is deterministic once a C34 support is given:

1. retain every selected boundary-lower row;
2. retain a lower gate only when both its AND-lower and OR-lower rows occur;
3. retain an upper gate only when its OR-upper row and exactly one AND-upper
   row for every parent pair occur;
4. delete all other gate fragments and recompute bound coefficients by
   (1)-(4).

The exact integer audit gives:

| (X) | (|D_X|) | (Phi) | (|C|) | (|L|) | (|U|) | chain intervals |
|---:|---:|---:|---:|---:|---:|---:|
| 54 | 1 | 1 | 7 | 4 | 1 | 7 |
| 74 | 2 | 2 | 10 | 6 | 1 | 9 |
| 186 | 8 | 8 | 24 | 16 | 3 | 20 |
| 362 | 19 | 19 | 43 | 30 | 5 | 37 |
| 500 | 27 | 33 | 68 | 51 | 10 | 54 |
| 1000 | 66 | 70 | 125 | 97 | 11 | 102 |
| 2000 | 147 | 151 | 245 | 215 | 30 | 194 |
| 5000 | 410 | 442 | 627 | 592 | 69 | 489 |
| 10000 | 878 | 943 | 1227 | 1235 | 134 | 956 |

At all nine endpoints, (Phi) is exactly the full grounded dual objective.
No upper OR row is lost: every selected upper OR has a complete parent
transversal.  The deleted rows are incomplete fragments balanced by variable
bounds; they contribute zero to (5).

The original observation that only grounded bounds have large multipliers is
not invariant under this normalization.  After zero fragments are removed,
some non-ground residual bounds have multiplicity greater than one.  The
fragments therefore serve partly to split residual multiplicity into unit
bound rows; they do not carry objective value.

## 5. What is stable, and what is not

The rank heuristics have high agreement but are not selection rules.

* A lower pair maximizes
  (min(d(a),d(b))) in respectively
  (4/4,6/6,16/16,30/30,51/51,96/97,211/215,586/592,1209/1235)
  complete lower gates at the nine endpoints.
* An upper transversal chooses the earlier-death parent in respectively
  (1/1,1/1,3/3,5/5,11/11,14/14,39/40,89/93,189/197)
  parent-pair choices.
* Through (X=2000), every selected all-ground lower pair is also a
  minimum-generation-rank grounded pair.  This first ceases to be universal
  at the larger endpoints.

There are four exact obstructions to promoting these frequencies to a local
recurrence.

1. **The chain support is not prefix-nested.**  From (X=500) to (1000),
   the support below 500 removes boundary children
   (63,185,189,225,245,347) and adds
   (117,227,287,309,351,371,425,429,453).

2. **The same lower gate changes pair.**  Node 185 uses ((3,62)) at
   (X=500), but ((2,93)) at (X=2000).

3. **The same upper gate changes transversal.**  At node 567, the pair
   ((8,71)) selects 8 at (X=2000) and 71 at (X=5000).

4. **Canonical local rank normalization is false.**  At (X=1644), replace
   every lower pair by a maximum-(min(d(a),d(b))) pair and every upper
   choice by an earliest-death parent, while leaving all selected chain edges
   and gate nodes fixed.  The exact score drops from 122 to 118, below the
   required 119.

The last failure is structural.  In the pairs

\[
 (8,71),\qquad(8,83),\qquad(8,89),
\]

the local rule selects 8, of death rank 1, at upper nodes 567, 663, and 711.
This creates three unmatched upper occurrences of (s_8), recorded exactly
as (sigma_8=-3).  The original support selects (71,83,89), with death
ranks (2,2,4), because those labels are supplied by lower gates elsewhere.
The same cutoff also changes lower node 1067 from ((3,356)) to the locally
higher-ranked ((2,534)).  Thus pair choice is controlled by the global
source balance (1), not by chain depth, pair rank, or parent rank separately.

The combined local rank rule was exact-tested at every hard cutoff through
2000.  It fails at 13 cutoffs, first at 1644; at (X=2000) it gives 145
against the required 147.

## 6. Exact finite gate

`scan_complete_gate_rule.py` regenerated the grounded LP support at every
hard cutoff through 2000, required every nonzero gate/boundary multiplier to
be exactly unit within the discovery tolerance, applied the complete-gate
normalization, and then rebuilt stationarity and the objective using integer
coefficients only.

The result is:

```text
tested hard cutoffs:              147
complete-gate exact passes:       147
objective differs from full dual: 0
cutoffs with deleted fragments:   145
largest deleted-fragment count:   18
minimum certificate margin:       0
maximum certificate margin:       10
```

The floating LP is used only to discover a support.  Acceptance of the
normalized certificate is an exact integer check of every coefficient and
its objective.

The rank-normalization falsifier was also run at all 147 hard cutoffs, not
only at the first failing endpoint.

Reproduction:

```text
python problems/424/compute/wave3/C37_grounded_unit_skeleton/analyze_supports.py --output problems/424/compute/wave3/C37_grounded_unit_skeleton/support_report.json

python problems/424/compute/wave3/C37_grounded_unit_skeleton/scan_complete_gate_rule.py --stop 2000 --output problems/424/compute/wave3/C37_grounded_unit_skeleton/complete_gate_scan_2000.json

python problems/424/compute/wave3/C37_grounded_unit_skeleton/scan_rank_normalization_all.py --stop 2000 --output problems/424/compute/wave3/C37_grounded_unit_skeleton/rank_normalization_all_2000.json
```

Supporting exact audits are in `clean_subset_audit.json` and
`rank_pattern_audit.json`.

## 7. Remaining frontier

The infinite problem is now the following discrete statement:

> For every hard cutoff (X), construct chain intervals (C), lower pairs
> (L), upper gate nodes (U), and globally balanced transversals (	au)
> satisfying (CS).

This is strictly smaller than the grounded LP, but it is not proved for all
cutoffs.  The finite gate through 2000 cannot be extrapolated.  Any successful
recurrence must carry the source-balance vector
((\sigma_x)_{x\in A_X}) as state; a recurrence based only on independent
chain endpoints or local parent ranks is killed by the exact (X=1644)
counterexample.
