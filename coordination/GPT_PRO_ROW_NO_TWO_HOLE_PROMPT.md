We are proving the last row-side geometric atom in an Erdős #23 proof.

Do not propose scalar Hall, arbitrary leakage, broad switch certificates, or a
global "one row misses at most one exit" theorem. Those are false or already
exact-disproven.

## Setup

G is triangle-free. Fix a connected-B maximum cut. B is the cut graph; M is
the set of bad monochromatic edges. For a bad edge f, ell(f)=d_B(endpoints)+1
and cyc[f] is the set of shortest B-geodesics between its endpoints.

S is a selected completed seed+moat terminal-shadow switch from a vertex with
R[v]<0. Let:

```text
C = delta_M(S)
E = delta_B(S)
```

For f in C and e in E, f witnesses e if some shortest f-row exits S through e.
Terminal-shadow means every shortest row of every f in C, oriented from the
endpoint tau_f in S, meets S in an initial prefix, exits exactly once through
some e in E, then stays outside S.

Let:

```text
lambda(e)=min{ell(f): f witnesses e}
L0=min_{f in C} ell(f)
F0={f in C: ell(f)=L0}
F1=C\F0
E0={e in E: lambda(e)=L0}
```

Stage0 matches F0 into E0 with minimum total rare cost:

```text
c(e)=deg_F1(e)=|Wit(e) cap F1|.
```

Delete matched exits. In the residual bipartite graph H between F1 and the
remaining exits, f~e iff f witnesses e. Work component-locally.

Exact verified facts:

```text
global row_miss_count     = {0:923, 1:72, 3:18, 8:48}
component row_miss_count  = {0:989, 1:72}
component singleton split = 40 long-lambda, 32 minimum-lambda
```

So global single-miss is false. The target is only:

```text
In every residual connected component (A,B), each f in A misses at most one e in B.
```

## Minimal Corridor Reduction

If f misses two exits in one residual component, define the exit co-witness
graph J on B:

```text
e--e' iff exists g in A witnessing both e and e'.
```

Choose two missed exits e0,ek of f with minimum J-distance. Then there is a
minimal corridor:

```text
e0, g1, e1, g2, ..., gk, ek
```

where each g_i witnesses consecutive exits, f misses e0,ek, and f witnesses
every internal e_i.

For h in C and e=x_e y_e with x_e in S, define terminal slack:

```text
D_h=ell(h)-1
s_h(e)=d_{B[S]}(tau_h,x_e)+1+d_{B[V\S]}(y_e,sigma_h)-D_h.
```

Terminal-shadow gives h witnesses e iff s_h(e)=0. Nonzero slack is at least
2 by parity.

## Request: prove one of the two atoms below

### Atom A: TH-long

If lambda(e0)>L0 or lambda(ek)>L0, prove the row-union disk built from:

```text
f-rows through internal tight exits,
g_i-rows through consecutive exits
```

contains either:

```text
a triangle in G,
```

or:

```text
a B-path for some h in {f,g1,...,gk} of length <= ell(h)-3.
```

The intended proof: the corridor begins with an f-improving strict hinge and
ends with an f-worsening strict hinge. The hinge rows have equal total length.
These make a reduced theta with a strict diagonal. If the diagonal degenerates
at length 2, triangle-freeness kills it.

Make the strict diagonal explicit. Avoid broad lens statements: arbitrary
rows can share corridors without giving a shortcut.

### Atom B: TH-rare

If lambda(e0)=lambda(ek)=L0, prove the stage0 F0-E0 matching has a rare-cost
decreasing alternating exchange.

It is enough to prove:

```text
exists e in {e0,ek}, exists matched u in Alt_mu(e), with c(u)>c(e).
```

or a multi-exchange with lower total c-cost.

Subtlety: a minimum-lambda missed exit need not have an F0 witness remaining
inside its residual component. In exact examples, ell(f)=7 misses a lambda=5
exit whose residual witnesses are four length-7 rows. The F0 row prices the
exit only through the stage0 matching / alternating closure.

The intended proof: one minimum survivor can remain at equal cost, but two
minimum missed exits in the same residual component force their alternating
closures to interact; at the first interaction, one closure reaches a matched
exit of strictly larger c-cost. Otherwise the residual component separates.

## Desired output

Give a rigorous combinatorial proof of Atom A or Atom B, or a smaller
exact-testable lemma that implies it. Do not restate Hall; prove the geometry
or the rare-exchange mechanism.

