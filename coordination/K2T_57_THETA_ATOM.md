# K2T 5/7 Terminal-Theta Atom

## RETRACTED 2026-07-01

This local atom remains a correct square-surplus calculation for selected
terminal-shadow switches, but the global K2T/Lmax descent route it was meant
to support is false on the two-lane unique gamma-min family.  Keep this note
only as a local diagnostic; do not treat it as a proof path for the conjecture.

Status: local square-surplus lemma for the K2T Lmax descent route.

This note proves only the local `Psi>0` step once the Lmax switch is already
known to be neutral and terminal-shadow safe.  It does not by itself prove that
the Lmax switch exists.

## Setup

Let `S` be a terminal-shadow switch.  Write

```text
C = delta_M(S)     old bad edges crossing S,
E = delta_B(S)     old cut edges crossing S.
```

For each `e in E`, define

```text
lambda(e) = min { ell(f) : f in C and some shortest row of f exits S through e }.
```

The square surplus is

```text
Psi(S) = sum_{f in C} ell(f)^2 - sum_{e in E} lambda(e)^2.
```

If `S` is neutral, terminal-shadow safe, and `B^S` is connected, then the
standard terminal-shadow replacement argument gives

```text
Gamma(after flipping S) <= Gamma(before) - Psi(S).
```

Thus `Psi(S)>0` is enough for a strict `Gamma` descent.

## Atomic 5/7 Configuration

Assume a component of the switch boundary contains exactly two old crossing bad
edges

```text
g, h in C,
ell(g)=5, ell(h)=7,
```

and two old boundary cut exits

```text
e_1, e_2 in E.
```

Assume both exits are witnessed by the short edge `g`:

```text
g witnesses e_1 and e_2.
```

The longer edge `h` may also witness either exit; that does not affect the
minimum boundary price.  Then

```text
lambda(e_1)=lambda(e_2)=5.
```

The contribution of this component to `Psi` is therefore

```text
ell(g)^2 + ell(h)^2 - lambda(e_1)^2 - lambda(e_2)^2
  = 5^2 + 7^2 - 5^2 - 5^2
  = 24.
```

So any neutral terminal-shadow switch containing this atom has positive square
surplus unless another component has negative surplus.

## No Negative Component Under Boundary Pricing

For any terminal-shadow component, every boundary exit is witnessed by at least
one crossing bad edge.  Therefore

```text
lambda(e) <= max_{f in C_component} ell(f).
```

The exact Lmax winner signatures show that non-5/7 components appearing with
the selected switches are zero-surplus pure baggage: crossing lengths and
boundary prices match componentwise, for example a pure odd-cycle atom with

```text
cross=(L), lambda=(L), Psi=0.
```

Thus a disjoint sum of pure baggage plus at least one 5/7 atom has

```text
Psi(S) >= 24.
```

## Conditional Lemma

```text
5/7 THETA SURPLUS.
Let S be a neutral, B-connected, terminal-shadow-safe switch.  Suppose its
crossing/boundary witness graph decomposes into components each of which is
either:

  A. pure baggage with equal crossing and lambda multisets, or
  B. a 5/7 terminal-theta atom as above.

If at least one component is type B, then Psi(S)>0 and flipping S strictly
lowers Gamma.
```

Proof: add the component contributions.  Type A contributes `0`; each type B
contributes `24`; all contributions are independent because `Psi` is a sum over
crossing bad edges and boundary exits.

## Remaining Geometric Burden

The hard part of the full K2T proof is to show that the Lmax switch selected by
`R[v]<0` actually has this decomposition, and contains at least one type-B
component.  Exact gates currently verify this on the mixed battery:

```text
Psi = 24 * (# strict 7-to-5 boundary pricing events).
```

So the proof reduces to a terminal-theta rigidity statement:

```text
R[v]<0
=> the Lmax terminal-shadow switch contains a nested 5/7 component;
   all other support components are pure baggage or additional 5/7 copies.
```
