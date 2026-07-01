We are working on Erdős Problem #23, but the request below is only about one
finite/graphon reduction target. Please do not suggest scalar Hall, fixed-depth
Neumann, terminal degree equalities, or no-two-hole/single-miss corridor lemmas;
all of those have exact counterexamples in our gates.

## Context

Let `G` be triangle-free, and choose a connected maximum cut `B` with bad
edges `M`, tie-broken to minimize

```text
Gamma = sum_{f in M} ell(f)^2,
```

where `ell(f)` is the odd-cycle length obtained from a shortest blue
(`B`-edge) path between the endpoints of the bad edge `f`.

For each bad edge `f`, let `cyc[f]` be the set of all shortest blue geodesics
between the endpoints of `f`. Define the vertex load

```text
T(v) = sum_f ell(f) * Pr_{Q in cyc[f]}[v in Q].
```

The remaining goal can be proved by showing a Hardy matrix is PSD. The matrix is

```text
H = diag(N - T) + Lstar,
```

where `N=|V(G)|` and

```text
Lstar = sum_f beta'_ell(f)/|cyc[f]| * sum_{Q in cyc[f]} L_Q.
```

Here `L_Q` is the usual cycle Laplacian on the shortest odd cycle `Q plus f`,
and `beta'_ell <= ell/(2+2 cos(pi/ell))` is a certified rational lower
coefficient. The local circulant identity gives

```text
N I - K2 >= H,
```

so `H >= 0` closes the reduction.

Let

```text
O = {v : T(v) > N},      U = V \ O.
```

Assume `H_UU` is a nonsingular Stieltjes M-matrix and form the exact Schur
complement on overloaded vertices:

```text
S = H_OO - H_OU H_UU^{-1} H_UO.
```

In all exact gates, `S` is a symmetric Z-matrix. Write

```text
c_ij = -S_ij >= 0  (i != j),
rho_i = sum_j S_ij,
S = L_c + diag(rho).
```

If all `rho_i >= 0`, then `S` is PSD by diagonal dominance. If exactly one
row shunt is negative, say at `a`, then `S >= 0` follows from the direct star
rescue inequality

```text
rho_a + sum_{p != a} c_ap * rho_p / (c_ap + rho_p) >= 0,
```

with zero denominator terms omitted.

## Exact empirical target

The gates support the following graph-specific lemma:

```text
For every connected-B, Gamma-minimal maximum cut in a triangle-free graph:

1. S is a symmetric Z-matrix.
2. At most one rho_i is negative.
3. If rho_a < 0, then a is the strict-majority overload apex:

   T(a)-N > sum_{p in O, p != a} (T(p)-N).

4. If rho_a < 0, the direct star-rescue inequality above holds.
```

The only non-diagonally-dominant guardrail currently seen is MycGrotzsch_N23:
`O=[1,2,3,10,22]`, only vertex `22` has `rho<0`, it is the strict-majority
overload apex, and the star margin is about `0.026221 > 0`.

Important guardrail: the statement is false for arbitrary connected maximum
cuts. A hard `h_blowup(3)` side has six negative Schur row sums and `S` not PSD,
but exact quotient enumeration shows it is not `Gamma`-minimal (`Gamma=666`
while `Gamma_min=450`). Thus Gamma-minimality is essential.

## Request

Give one concrete proof route for the graph-specific Schur row-shunt lemma.
Prefer a lemma stated in terms of:

```text
rho_o = (N - T(o)) + (Lstar h)_o,
```

where `h_O=1` and `H_UU h_U = -H_UO 1`, so `rho=S 1`.

In words, `rho_o<0` means the Hardy current leaving overloaded vertex `o`
under harmonic boundary value `1` is smaller than its overload `T(o)-N`.

I need either:

1. A proof of the strict-majority implication

```text
rho_o < 0 ==> T(o)-N > sum_{p in O,p!=o}(T(p)-N),
```

using triangle-freeness, shortest-geodesic structure, max-cut, and
Gamma-minimality; or

2. A stronger or different exact-testable inequality that implies
`|{rho<0}|<=1` and the singleton star rescue.

Please make the proposed lemma exact-testable from the objects above (`M`,
`ell`, `cyc`, `T`, `H`, `S`, `rho`, `c_ij`). Avoid generic M-matrix facts
unless they use the specific graph/geodesic/Gamma-minimal structure.
