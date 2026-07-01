# K2T Terminal-Shadow Proof Target

## RETRACTED 2026-07-01

This route is not valid as a proof of Erdős #23.  Claude independently
confirmed the two-lane `L=12` unique gamma-min maximum cut has

```text
rho(K)=rho(K2)=rho(O)=40.2094 > N=39,
R[v]=N*T[v]-(K2*T)[v] < 0 on nine vertices,
```

and no neutral connected `Gamma` descent of size `<=3`.  Thus

```text
gamma-min => K2*T <= N*T
```

is false, and the Collatz-Wielandt/spectral route is another form of the
pruned ROWSUM/SPEC strengthening.  The live target is first-moment:

```text
Gamma <= N^2
```

via UNIF-LOAD / COUPLE / LOAD-PSC, with two-lane as a mandatory negative
control for any spectral or second-moment claim.

The notes below are retained only as dead-end diagnostics.

Current live theorem:

```text
K2*T <= N*T
```

where `K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q]` and
`T = K2*1`.

By Collatz-Wielandt, `K2*T <= N*T` implies `rho(K2)<=N`.
Together with Jensen `K <= K2`, this gives `Gamma<=N^2`.

## 2026-07-01 CW Zero-Support Audit

There is no reducibility hole in the Collatz-Wielandt step.  Since

```text
T = K2 * 1
```

and `K2` is entrywise nonnegative, any vertex with `T[v]=0` has zero row sum in
`K2`, hence the entire `v`-row is zero.  By symmetry its column is also zero.
Thus the zero-load vertices split off as zero spectral blocks.

On the active support

```text
S = { v : T[v] > 0 },
```

the vector `T_S` is strictly positive and the componentwise inequality

```text
K2[S,S] * T_S <= N * T_S
```

implies `rho(K2[S,S])<=N` by the standard Collatz-Wielandt theorem.  Therefore
the full matrix also satisfies `rho(K2)<=N`.

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

## 2026-07-01 Lmax Selector Target

The current sharp selector is the longest length bundle through the negative
residual vertex.

For a vertex `v` with `R[v]<0`, define

```text
Lset(v) = { ell(f) : exists Q in cyc[f] with v in Q },
Lmax(v) = max Lset(v).
```

For every row of length `Lmax(v)` containing `v`, take the closed prefix union
or suffix union through `v`, in either orientation.  This gives four candidate
`Lmax` half-switches.

Exact gate:

```text
python problems/23/writeup/_mech_selector_char.py
R[v]<0 sites total: 56
Q1 strictly MIXED (Lmax>Lmin): 56; not mixed: 0
Q2 witness-at-Lmax: 56; witness-NOT-at-Lmax: 0
Q3 BEST(max-drop) witness length histogram: {'=Lmax': 56}
Q4 rule [L=Lmax, both orientations] covers: 56 / 56
```

Square-surplus gate:

```text
python problems/23/writeup/_lmax_psi_mechanism.py
R[v]<0 sites: 56; no L_max winner: 0
Psi computable: 56; Psi=None: 0
descent identity drop==Psi: 56
Psi > 0: 56
Psi range: 24 .. 216
```

So the proof target can be sharpened to:

```text
L_MAX DESCENT THEOREM.
If R[v]<0, then some Lmax(v) prefix/suffix half-switch S through v is neutral,
B-connected after flipping, terminal-shadow safe, and has Psi(S)>0.
```

The terminal-shadow identity then gives a neutral connected
`Gamma`-decreasing switch, contradicting gamma-minimality.  This theorem is
weaker and more concrete than broad ROWSUM/SPEC descent and avoids the
two-lane guardrail.
