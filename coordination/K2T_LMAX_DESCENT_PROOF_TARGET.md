# K2T Lmax Descent Proof Target

## RETRACTED 2026-07-01

This selector theorem is no longer a live route to Erdős #23.  The underlying
K2T target

```text
K2*T <= N*T
```

is false on the two-lane `L=12` unique gamma-min maximum cut, where
`rho(K2)>N` and `R[v]<0` occurs without a neutral connected gamma descent.  The
local Lmax data below may still be useful for understanding special
near-extremal gadgets, but it must not be used as a global proof target.

The live route is first-moment `Gamma<=N^2`, especially UNIF-LOAD /
LOAD-PSC-type inequalities that survive two-lane.

Status: current Codex proof-facing target after the 2026-07-01 K2T /
Collatz-Wielandt reduction.

## Global Reduction

For a connected-`B` maximum cut, let

```text
K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q],
T = K2 * 1,
R[v] = N*T[v] - (K2*T)[v].
```

The remaining theorem is:

```text
gamma-minimal connected-B maximum cut => R[v] >= 0 for every v.
```

Indeed, `R>=0` is `K2*T <= N*T`; by Collatz-Wielandt on the positive
`T`-support this gives `rho(K2)<=N`.  Jensen gives `K<=K2`, and hence
`Gamma<=N^2`.

Thus it is enough to prove the contrapositive:

```text
R[v] < 0
=> there is a cut-neutral, B-connected, Gamma-decreasing switch S containing v.
```

## Lmax Selector

For `R[v]<0`, define

```text
Lset(v) = { ell(f) : exists Q in cyc[f] with v in Q },
Lmin(v) = min Lset(v),
Lmax(v) = max Lset(v).
```

For all rows `Q` of length `Lmax(v)` that contain `v`, take the closed
prefix/suffix unions through `v`, in the two global orientations.  The exact
candidate family has at most four sets:

```text
S = Pref_0(v,Lmax), Suff_0(v,Lmax), Pref_1(v,Lmax), Suff_1(v,Lmax).
```

Exact gates:

```text
_mech_selector_char.py:
  R[v]<0 sites total = 56
  Lmax>Lmin = 56/56
  witness-at-Lmax = 56/56
  best max-drop witness at Lmax = 56/56

_lmax_psi_mechanism.py:
  Lmax winner = 56/56
  terminal_shadow_psi defined = 56/56
  Gamma drop == Psi = 56/56
  Psi > 0 = 56/56
```

## Theorem To Prove

```text
L_MAX DESCENT.
If R[v]<0, then one of the four Lmax half-switches S through v satisfies:

1. 0 < |S| < N and v in S;
2. delta_B(S) = delta_M(S);
3. B^S is connected;
4. S is terminal-shadow safe;
5. Psi(S) > 0.
```

Then flipping `S` preserves maximum-cut size, keeps `B` connected, and lowers
`Gamma`, contradicting gamma-minimality.

## Lemma Tree

### L1. Mixed-Length Forcing

```text
R[v]<0 => Lmax(v)>Lmin(v).
```

Interpretation: a negative `K2T` residual cannot be created by a one-length
geodesic bundle.  There must be a shorter row carrying positive overload and a
longer row enclosing it through `v`.

### L2. Lmax Half-Switch Neutrality

Among the four `Lmax(v)` prefix/suffix unions through `v`, at least one has

```text
delta_B(S)-delta_M(S)=0.
```

Every switch has nonnegative cut-loss by maximality, so the proof should show
that the total coarea balance of the four Lmax terminal shadows is zero or that
positive cut-loss would contradict `R[v]<0`.

### L3. Terminal-Shadow Safety

The neutral `Lmax` half-switch satisfies the terminal-shadow gates:

* every crossing bad row meets `S` as a terminal prefix/suffix;
* every new bad boundary edge is witnessed by some old crossing bad row;
* every noncrossing old bad edge keeps a shortest geodesic avoiding the new
  bad boundary.

This is a shortest-geodesic no-reentry statement scoped to the Lmax selector,
not to arbitrary prefix hulls.

### L4. Positive Square Surplus

For the neutral terminal-shadow `Lmax` switch,

```text
Psi(S) =
  sum_{f in delta_M(S)} ell(f)^2
  - sum_{e in delta_B(S)} lambda_S(e)^2
> 0.
```

In all exact gates, the surplus is paid by a nested short/long terminal theta.
The base atom is `(ell_short, ell_long)=(5,7)` and contributes

```text
7^2 - 5^2 = 24.
```

The proof should show that `R[v]<0` forces at least one strict boundary pricing
event `lambda_S(e)<ell(f)` in the Lmax switch, and that no positive cut tax
remains after L2.

## Guardrails

* Do not use universal ROWSUM/SPEC; the two-lane unique gamma-min family
  refutes that stronger statement.
* Do not use arbitrary terminal-shadow Hall/no-reentry.  Multi-door fan
  counterexamples exist outside the selected `R[v]<0` domain.
* Do not use per-edge strict-lens positivity without the `R[v]<0` hypothesis;
  Mycielski stress cuts refute the broad per-edge implication.

## Next Proof Attack

The most local sublemma is L4 after L2/L3 are assumed: prove that a neutral
terminal-shadow Lmax switch selected from `R[v]<0` must contain a strict
nested terminal theta, hence `Psi>0`.  This is exactly the square-surplus
identity already verified by `_lmax_psi_mechanism.py`.

## 2026-07-01 Signature Compression

Codex mined the chosen Lmax winners on the same mixed battery as
`_lmax_psi_mechanism.py`.  Every selected switch had crossing and boundary
price lengths drawn only from `{5,7}`.  The signature counts were:

```text
21  cross=(5,7), lambda=(5,5), Psi=24
10  cross=(5^4,7^4), lambda=(5^8), Psi=96
15  cross=(5^9,7^9), lambda=(5^18), Psi=216
 4  variants with Psi=48
 3  variants with Psi=72
 3  variants with Psi=144
```

More invariantly:

```text
Psi = 24 * (# of strict 7-to-5 boundary pricing events).
```

Some larger switches also contain zero-surplus baggage where `7`-priced
boundaries pair with `7` crossing lengths, but no selected switch used any
length outside `{5,7}` in the surplus component.

Thus L4 can be sharpened:

```text
L4'.  A neutral terminal-shadow Lmax switch selected from R[v]<0 contains at
least one nested 5/7 terminal theta: a length-7 crossing bad row whose new
boundary exit is witnessed/priced by a length-5 crossing bad row.  All other
components are zero-surplus baggage or additional copies of the same 5/7 atom.
```

This matches the deficient-cap and residual-singleton-miss diagnostics: the
same terminal theta is the only positive square-surplus atom seen anywhere in
the K2T descent machinery.
