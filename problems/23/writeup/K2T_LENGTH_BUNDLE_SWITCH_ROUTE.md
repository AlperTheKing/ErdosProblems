# K2T Length-Bundle Switch Route

Status: active proof route for the CSM/K2T certificate.

## Target

For a connected-B maximum cut, define

```text
R[v] = N*T[v] - (K2*T)[v].
```

The exact-gated Collatz certificate is

```text
R[v] >= 0  for every vertex v.
```

This implies `rho(K2) <= N` by Collatz-Wielandt, hence `rho(K) <= N` by
Jensen, hence `Gamma <= N^2`.

It is enough to prove the contrapositive switch statement:

```text
R[v] < 0
=> there exists a cut-neutral B-connected switch S containing v
   with Gamma(after S) < Gamma(before).
```

Then gamma-minimality forbids `R[v] < 0`.

## False Narrow Candidate

The first narrowed switch family used one bad edge at a time:
for a bad edge `f`, union all prefixes or suffixes of shortest rows in
`cyc[f]` that contain `v`.

This is false.

Counterexample:

```text
H?AFBo][2], inherited side from 111110000
N = 18
cut = maxcut = 40
Gamma = 296
bad-edge lengths = {5, 7}
negative residual vertices = 14
per-bad-edge half-switch coverage = 2 / 14
arbitrary neutral Gamma-descent switch coverage = 14 / 14
```

Reason: in a blow-up, the descent switch is not attached to one bad edge.
It flips an entire equal-length row bundle.

## Repaired Candidate

For each length `L` and vertex `v`, collect all shortest rows `Q` of all
bad edges `f` with `ell[f] = L` and `v in Q`.

For each orientation define two candidate switches:

```text
Pref_L(v) = union_Q Q[:index_Q(v)+1]
Suff_L(v) = union_Q Q[index_Q(v):]
```

where the union is over all oriented rows of length `L` containing `v`.

Candidate theorem:

```text
If R[v] < 0, then for some length L and orientation,
Pref_L(v) or Suff_L(v) is cut-neutral, leaves B connected with finite Gamma,
and strictly decreases Gamma.
```

Gate script:

```text
problems/23/writeup/_codex_k2t_lenbundle_switch_gate.py
```

## Local Exact Evidence

Run:

```text
python _codex_k2t_lenbundle_switch_gate.py --max-n 10 --h-blowups 3 --random 80 --examples 16
```

Result:

```text
census N<=10: fail=0
H?AFBo][2]: inherited cut, 14/14 negative vertices covered
H?AFBo][3]: inherited cut stress, 21/21 covered
random 80 connected triangle-free N=11/12: no new negative-residual vertices
```

`H?AFBo][2]` was separately brute-confirmed to have inherited cut maximum:

```text
N=18, cut=40, maxcut=40.
```

## Structural Reading From H?AFBo] And Blow-Ups

For the base obstruction `H?AFBo]`, side `111110000`:

```text
bad edges: (5,8) with ell=7, (6,8) with ell=5
T = [7,6,6,6,6,7,12,12,12]
R = [1,-1,-1,-1,-1,1,-2,-2,-2]
Gamma = 74
```

Rows of length 7 have overload `-1`.
Rows of length 5 have overload `+3`.
The negative residual is caused by the positive length-5 contribution
overwhelming the negative length-7 contribution, but the descent switch is
the length-7 bundle switch.  It replaces the length-7 packet by length-5
bad edges and lowers Gamma to `50`.

In `H?AFBo][2]`, a typical switch at a clone of vertex 1 is

```text
S = {both clones of 5, both clones of 0, both clones of 6, chosen clone of 1}
```

This is exactly `Pref_7(v)` over the whole length-7 bundle, not a single
bad-edge prefix.

## Proof Obligation

The desired proof should show:

```text
R[v] < 0
=> some equal-length geodesic bundle through v has a principal prefix/suffix
   whose switch is neutral and shortens at least one old bad row.
```

Equivalently, prove the contrapositive:

```text
If every length-bundle half-switch through v is either cut-positive or
nondecreasing in Gamma when neutral, then R[v] >= 0.
```

This has the shape of a discrete coarea/uncrossing theorem over the
geodesic row posets of fixed length.  The failed per-bad-edge theorem shows
that the coarea unit must be the equal-length bundle, not an individual
bad edge.

## Strict-Lens Simplification Check

It is tempting to replace the negative-residual hypothesis by the simpler
condition that `v` lies on the short side of a strict bad-geodesic lens.  This
is false.

Gate:

```text
python _codex_k2t_strict_lens_switch_gate.py --max-n 10 --h-blowups 3 --random 80
```

Result:

```text
strict-lens short vertices covered: 386
strict-lens short vertices FAIL: 128
negative vertices covered: 56
negative vertices FAIL: 0
first strict-lens-only failure:
  ('I??CF@wFo', 10, '1111110000', 9, R[9]=10, strict_lens_pairs=1)
```

So strict lenses are not forbidden by gamma-minimality in isolation.  The
current proof target must keep the weighted hypothesis:

```text
R[v] < 0
=> some length-bundle half-switch through v is cut-neutral, B-connected,
   terminal-geodesic/safe, and has Psi(S)>0.
```

The terminal-shadow gates then give the Gamma descent using only old-cut data.

## Psi-Only Refinement

The explicit neutrality filter may not be the structural core.  Local scan:

```text
terminal-shadow length-bundle switches with Psi>0:
  total: 903
  neutral: 903
  nonneutral: 0
```

And the simplified target also passes:

```text
R[v] < 0
=> some length-bundle switch through v has terminal_shadow_psi(S)>0
```

Gate on the same local battery:

```text
negative vertices: 56
covered by terminal_shadow_psi(S)>0: 56
fail: 0
chosen nonneutral or non-B-connected: 0
```

So the proof may split into:

```text
1. R[v]<0 produces a length-bundle terminal-shadow switch with Psi(S)>0.
2. For this switch family, terminal-shadow Psi(S)>0 plus max-cut implies
   boundary_delta(S)=0 and B^S connected, or these are forced by the same
   closure argument.
3. Psi(S)>0 gives Gamma descent by the terminal-shadow replacement lemma.
```

Local auxiliary gate for step 2:

```text
terminal-shadow length-bundle switches with Psi>0:
  total: 903
  boundary_delta=0: 903
  B^S connected: 903
  fail: 0
```

Positive `Psi` is not equivalent to `R[v]<0`; there are positive-residual
vertices with positive-`Psi` switches.  This is harmless and clarifies the
logic:

```text
gamma-minimality forbids every positive-Psi terminal-shadow switch,
while R[v]<0 only has to force existence of one.
```

## Dead Selector: Peak Terminal Overload

The deterministic selector

```text
maximize Omega_{L,sign}(v)/(L*m_L(v))
```

does not choose the descent bundle in general, although its coarea identity is
exact.

Gate:

```text
python _codex_peak_terminal_overload_gate.py --max-n 10 --h-blowups 3 --random 80
```

Result:

```text
Omega identity failures: 0
negative vertices: 56
some peak good: 47
some peak FAIL: 9
```

First failure is the base `H?AFBo]` cut `111110000` at vertex `6`:

```text
R[6] = -2.

Peak bundles:
  L=5 pref:  Omega=3/2, score=3/10, S={6}, delta=2, not B-connected.
  L=5 suff:  Omega=3/2, score=3/10, S={1,2,3,4,6,7,8}, delta=0, Psi=0.

Working descent:
  L=7 pref:  Omega=-5/2, score=-5/14, S={0,5,6}, delta=0, Psi=24.
```

So the correct selector cannot be “positive terminal overload.”  The descent
packet may be a longer enclosing bundle with negative terminal overload whose
crossing square surplus pays for the short overloaded packet.
