# K2T Terminal-Shadow Proof Target

Current live theorem:

```text
K2*T <= N*T
```

where `K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q]` and
`T = K2*1`.

By Collatz-Wielandt, `K2*T <= N*T` implies `rho(K2)<=N`.
Together with Jensen `K <= K2`, this gives `Gamma<=N^2`.

## Residual

For a connected-B maximum cut define

```text
R[v] = N*T[v] - (K2*T)[v].
```

Exact identity:

```text
(K2*T - N*T)[v]
  = sum_f (1/|cyc[f]|) sum_{Q in cyc[f], v in Q}
      (sum_{u in Q} T[u] - N*ell[f]).
```

Thus K2T is equivalent to `R[v]>=0` for all vertices.

## Gamma-Minimality Bridge

Target contrapositive:

```text
R[v] < 0
=> exists a cut-neutral connected switch S containing v
   with Gamma(after) < Gamma(before).
```

Gamma-minimal cuts forbid such switches, so the bridge proves K2T.

## Closed Half-Switch Family

For each bad edge `f` and each orientation of all paths in `cyc[f]`,
for a vertex `v` occurring in at least one path, define:

```text
Pref(f,v) = union of prefixes through v over all oriented paths containing v.
Suff(f,v) = union of suffixes from v over all oriented paths containing v.
```

The candidate switch family consists of all such sets.

Local gate:

```text
census N<=10 all connected-B max cuts:
negative vertices = 21
covered by closed half-switch = 21
failures = 0
```

All examples are the `H?AFBo]` symmetry class.

## Strict Lens Split

A strict bad-geodesic lens is an ordered pair `(f,g)` with `ell(f)>ell(g)`
such that some `Pg in cyc[g]` is a contiguous subpath of some
`Pf in cyc[f]`, up to reversal.

Exact gates:

```text
census N<=10:
strict-lens-free connected-B max cuts = 18373
K2T violations among strict-lens-free cuts = 0

strict lenses = 66 pair-level cases
covered by closed half-switch Gamma descent = 66
```

Proof split:

1. Gamma-minimality forbids strict lenses.
2. Strict-lens-free shortest-geodesic systems satisfy K2T.

## Terminal-Shadow Psi Certificate

For a switch `S`, let:

```text
crossM = d_M(S)
bdyB = d_B(S)
```

Terminal-geodesic gate:

1. For every `f in crossM`, every `Q in cyc[f]`, oriented from the endpoint
   of `f` inside `S`, has membership pattern `1...10...0`.
2. Every `e in bdyB` is the exit edge of at least one such crossing path.
3. Every noncrossing old bad edge has a shortest old geodesic avoiding `bdyB`.

For `e in bdyB`, define

```text
lambda_S(e) = min ell[f]
```

over crossing bad edges `f` whose terminal path exits through `e`.

Define

```text
Psi(S) = sum_{f in crossM} ell[f]^2
       - sum_{e in bdyB} lambda_S(e)^2.
```

If the terminal-geodesic gates hold, `d_B(S)=d_M(S)`, flipped `B` is connected,
and `Psi(S)>0`, then

```text
Gamma(after) <= Gamma(before) - Psi(S) < Gamma(before).
```

Local gate:

```text
census N<=10 negative vertices = 21
covered by terminal-shadow Psi-positive switch = 21
Psi histogram = {24: 21}
```

Remaining proof target:

```text
R[v] < 0
=> exists a closed half-switch S containing v
   satisfying the terminal-geodesic gates and Psi(S)>0.
```
