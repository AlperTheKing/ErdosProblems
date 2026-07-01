# Door-Cap Normal Form Target

This note records the current row-side fallback target.  The Schur
absorption-Hall route remains primary; this is the clean residual-Hall route
if the Schur proof stalls.

## Objects

Work inside a completed seed+moat terminal-shadow switch `S`.

For a crossing bad edge

```text
f=(t_f,o_f),  t_f in S, o_f notin S,
```

and a boundary blue exit

```text
e=(x_e,y_e),  x_e in S, y_e notin S,
```

define the forced-door length

```text
Lambda_f(e) = d_{B[S]}(t_f,x_e) + 1 + d_{B[V\S]}(y_e,o_f)
```

and the forced-door excess

```text
eps_f(e) = Lambda_f(e) - (ell(f)-1).
```

The exact normal-form primitive is:

```text
f witnesses e  iff  eps_f(e)=0,
f does not witness e  =>  eps_f(e)>=2,
```

with infinite `Lambda_f(e)` allowed for disconnected forced doors.

## Residual Stage

Let

```text
C = delta_M(S),  E = delta_B(S),
L0 = min_{f in C} ell(f),
F0 = {f in C : ell(f)=L0},
F1 = C \ F0,
lambda(e)=min{ell(f): f witnesses e},
E0 = {e in E : lambda(e)=L0}.
```

Stage 0 matches `F0` into `E0` with minimum total rare cost

```text
c(e)=|Wit(e) cap F1|.
```

The residual graph is the bipartite graph on `F1` and
`E \ mu(F0)`.

## Predicates

The current exact gate tests these four local predicates, plus a conservative
TT3 shape diagnostic.

### A. Forced-Door Equivalence

For every crossing `f` and boundary exit `e`:

```text
f~e  iff eps_f(e)=0,
f!~e and eps_f(e)<infty => eps_f(e)>=2.
```

### B. Exit Cap Path Forbidden

For a fixed residual exit `e`, there is no `e`-avoiding co-witness row path

```text
f0,h1,f1,...,hr,fr
```

with

```text
f0!~e, fr!~e,
fi~e for 0<i<r,
t_f0 != t_fr.
```

### C. Row Cap Path Forbidden

For a fixed residual row `f`, there is no co-witness exit path

```text
e0,g1,e1,...,gr,er
```

with

```text
f!~e0, f!~er,
f~ei for 0<i<r.
```

### D. Cyclic Cap Forbidden

There is no directed cyclic cap pattern of length `k>=3`

```text
f_i !~ e_i,   f_i ~ e_{i+1}   (mod k).
```

The `k=2` pattern is intentionally allowed; it is the observed two-terminal
swap atom.

### E. TT3 Defect-Terminal Diagnostic

After A-D, for each residual component and each nonuniversal residual exit
`e`, compute the missing row set

```text
M(e)={f in F_K : f!~e}.
```

If every nonempty `M(e)` lies in one inside-terminal fiber, form the defect
terminal set

```text
{in(e), tau(e) : M(e) nonempty, M(e) subset F_K(tau(e))}.
```

The diagnostic fails if this set has size at least three.  For every such
failure it also reports whether an unused minimum-tier defect exit `e in E0`
has a reachable matched stage-0 exit `u` with strictly larger rare cost

```text
c(u)>c(e),  c(x)=|Wit(x) cap F1|.
```

Thus E does not prove the rare-exchange lemma; it makes the exact TT3
obstruction visible.  On the current battery no such obstruction appears.

## Exact Gate

Implemented in:

```text
python problems/23/writeup/_codex_door_cap_gate.py
```

Canonical rare-stage run for A-E:

```text
python problems/23/writeup/_codex_door_cap_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result:

```text
tested=182, status={'ok': 182}, first=None, VERDICT=PASS
```

Tie-robust all-minimum-stage0 run for A-E:

```text
python problems/23/writeup/_codex_door_cap_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 \
  --max-add 1 --all-stage0 --cap 100000
```

Result:

```text
tested=182,
status={'ok': 139, 'too_many_stage0': 43},
first=None,
VERDICT=PASS.
```

Thus every fully enumerated all-minimum-stage0 case passes A-D; 43 inherited
cases exceed the 100000 matching cap and are explicitly scoped as unenumerated
tie stress, not assumed.

With the E diagnostic installed, the same tie-robust run has the same status:

```text
tested=182,
status={'ok': 139, 'too_many_stage0': 43},
first=None,
VERDICT=PASS.
```

So every fully enumerated minimum-stage0 choice also satisfies the TT3
two-terminal defect shape.

## Proof Burden

The proof should show A-D from:

* terminal-shadow validity,
* shortest blue geodesics,
* triangle-freeness,
* stage-0 minimum rare-cost exchange only for the TT3/three-terminal step.

Then:

```text
A + B => TT1: every nonuniversal residual exit has one missing terminal fiber.
A + C => TT2: every residual row misses at most one exit per component.
TT1 + TT2 + D + rare exchange => TT3: at most two terminal vertices.
```

Consequently each residual component has a two-terminal disjoint-star
complement and satisfies Hall.

## Current Position

This is not the primary proof route while the Schur absorption-Hall proof is
alive.  It is the row-side fallback target, now reduced to forced-door cap
uncrossing rather than raw leakage or arbitrary prefix Hall.
