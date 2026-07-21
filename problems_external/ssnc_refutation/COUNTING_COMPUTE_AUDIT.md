# Independent audit of the order-18 counting obstruction

Date: 2026-07-21.

Verdict: **ACCEPT** the local packing lemma and the resulting contradiction in
`CONSTRUCTION_N18.md`.  This establishes only the exact `n=18`,
minimum-outdegree-at-least-8 obstruction.  It is not a proof of SSNC and it is
not a counterexample.

## Claim audited

For an oriented graph on 18 vertices with minimum out-degree at least 8, let

- `A={v:d+(v)=8}`;
- `R_u={v in A : u` is neither in `{v} union N+(v)` nor in `N2+(v)}`;
- `r_u=|R_u|`;
- `e_u=d+(u)-8`;
- `mu_u` be the number of nonneighbors of `u`;
- `t_u=e_u+mu_u`.

The local claim is

```
t_u=0  =>  r_u=0,
r_u>0  =>  r_u <= 2t_u-1.                  (L)
```

The local claim does not need the global counterexample hypothesis.  The
global hypothesis is used only to obtain at least two unreachable targets for
each degree-8 root.

## Independent proof check

Fix `u` and put

```
U_u = V \ ({u} union N-(u)),
C_v = {v} union N+(v).
```

For `v in R_u`, direct evaluation of the definition gives `C_v subset U_u`.
Furthermore,

```
|U_u|=d+(u)+mu_u=8+t_u,  |C_v|=9.
```

Thus `t_u=0` makes `R_u` empty.  For `t_u>=1`, define
`B_v=U_u\C_v`, so `|B_v|=t_u-1`.

For distinct `v,w in R_u`, both roots lie in `U_u`.  If neither
`w in B_v` nor `v in B_w`, then `w in C_v` and `v in C_w`.  Since the roots
are distinct, this says both `v->w` and `w->v`, a forbidden digon.  Hence the
ordered exclusions in the `B_v` sets cover every unordered root pair:

```
binom(r_u,2)
  <= sum_{v in R_u} |B_v intersect R_u|
  <= r_u(t_u-1).
```

Division is used only when `r_u>0`, and gives (L).  No missing implication,
unstated adjacency assumption, or second-neighborhood convention was found.

## Direct bitset computation

The audit implementation is
`engine/audit_counting_obstruction.py`.  It independently computes first,
raw two-step, new second, and unreachable sets using integer bitsets.  For
every positive incidence count it checks all of the following separately:

1. `C_v subset U_u`;
2. `|B_v|=t_u-1`;
3. every unordered pair of roots is covered by an ordered exclusion;
4. the exclusion sum is at most `r_u(t_u-1)`;
5. `r_u<=2t_u-1`.

### Exhaustive structured family

Start with the cyclic 8-out-regular orientation on `Z/18Z`, leaving the nine
antipodal pairs missing.  Each antipodal pair independently has three states:
missing or either orientation.  All `3^9=19,683` graphs in this family have
minimum out-degree at least 8 and were checked.

Result:

```
graphs                         19683
maximum r_u-(2t_u-1)               0
saturated (u,graph) incidences 157464
local violations                   0
```

The zero maximum shows the proposed bound is sharp in this family, rather
than passing only with unused slack.

The exact missing-edge histogram for `h=0,...,9` was

```
[512,2304,4608,5376,4032,2016,672,144,18,1].
```

### Sampled general orientations

A deterministic Markov walk changed arbitrary unordered-pair states while
rejecting every mutation that would reduce an out-degree below 8.  It checked
20,000 distinct graphs, seed `20260721`, with eight mutation attempts between
recorded states.

Result:

```
distinct graphs                 20000
attempted mutations            307720
accepted mutations              29296
maximum r_u-(2t_u-1)                0
saturated incidences               121
local violations                    0
```

These samples are an audit, not an exhaustive enumeration of all order-18
oriented graphs.

## CP-SAT adversarial model

A separate CP-SAT model used 306 arc variables, exact degree-8 indicators,
exact two-step reachability to a fixed target, exact unreachable indicators,
and exact incidence indicators.  It asked only for an integer violation
`r_u>=2t_u` with `r_u>=1`; it did not impose the claimed packing bound.

After 30.10 seconds and 1,322,302 branches, the solver returned `UNKNOWN`
with no model.  This is **inconclusive** and is not counted as verification or
as an infeasibility proof.  The accepted verdict rests on the checked finite
set argument above, supported by the direct computations.

## Pure integer/global contradiction

Let `q` be the number of missing pairs.  Edge accounting gives

```
sum_u t_u = 9+q =: S,
|A| >= 9+q = S.
```

If `s` vertices have positive `t_u`, then `s>=1`.  Summing the local bound
over those vertices gives the exact relaxed maximum

```
sum_u r_u <= 2 sum_u t_u - s <= 2S-1.
```

The global counterexample condition requires

```
sum_u r_u >= 2|A| >= 2S.
```

Thus the pure integer/incidence relaxation is infeasible for every
`q=0,...,9`, with a gap of at least one before any graphical constraints are
added.  This closed-form comparison exhausts all integer distributions of the
`t_u` and is stronger than a sampled test.

A generic CP-SAT encoding of the same summed constraints returned `UNKNOWN`
at its time limits; those status codes carry no mathematical weight because
the displayed summation already gives the exact infeasibility certificate.

## Final scope

The audit found no flaw or counterexample to the local bound.  The global
double count is valid.  The result excludes the registered order-18 layer
only; it does not license a claim about larger orders or the full conjecture.
