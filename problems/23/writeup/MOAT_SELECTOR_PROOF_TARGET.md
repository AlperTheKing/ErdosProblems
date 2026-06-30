# One-Vertex Moat Selector Proof Target

This note replaces the false plain length-bundle selector.  The descent identity
is already exact-gated elsewhere: for any neutral terminal-shadow-gated switch
`S`, `DeltaGamma(S) = -Psi(S)`.  Thus `Psi(S)>0` contradicts gamma-minimality.

## Target Lemma

Let `(G,side)` be a connected-`B` maximum cut in the K2 residual setting, and
let `R[v] = N*T[v] - (K2*T)[v]`.  If `R[v] < 0`, then there exists a
length-bundle half-switch seed `A` through `v` and a set `S` with either

```text
S = A
```

or

```text
S = A union {z}
```

such that:

```text
boundary_delta(S) = 0,
B is connected after flipping S,
terminal_shadow_psi(S) > 0.
```

Equivalently, every negative residual vertex has a neutral B-connected
Gamma-decreasing terminal-shadow switch obtained from a length-bundle seed by
adding at most one moat vertex.

## One-Vertex Neutralizer Sublemma

In all currently gated cases where `S=A union {z}` is needed, the added vertex
is not arbitrary.  It satisfies:

```text
boundary_delta({z}) = 0,
e_M(z,A) = 0,
boundary_delta(A) = 2 * e_B(z,A),
boundary_delta(A union {z}) = 0.
```

The only observed profiles are:

```text
(boundary_delta(A), boundary_delta({z}), boundary_delta(S), e_B(z,A), e_M(z,A))
= (4,0,0,2,0)  or  (2,0,0,1,0).
```

So the moat vertex is a cut-neutral vertex that internalizes exactly the old
cut-boundary excess of the seed, with no old bad adjacency to the seed.

## Exact Gate Evidence

Selector gate:

```text
python problems/23/writeup/_codex_bundle_moat_gate.py --max-n 11 --h2-allmax --h-blowups 4 --random 200 --max-add 1 --examples 8
```

Result:

```text
bad cuts: 14
negative: 193
covered: 193
fail: 0
added histogram: {0: 165, 1: 28}
Psi histogram: {24:32, 48:32, 96:80, 144:6, 216:15, 288:8, 384:20}
VERDICT: PASS
```

Neutralizer-rule gate:

```text
python problems/23/writeup/_codex_moat_rule_gate.py --max-n 11 --h2-allmax --h-blowups 4 --random 200
```

Result:

```text
selected: 193
added0: 165
added1: 28
bad_added0: 0
bad_rule: 0
rule_hist: {(4,0,0,2,0):24, (2,0,0,1,0):4}
VERDICT: PASS
```

## Proof Decomposition To Attack

1. Length-bundle seed production: prove `R[v]<0` gives a length-bundle seed `A`
   through `v` with positive terminal-shadow surplus after neutralization.
2. Neutralizer existence: if the seed is not neutral, prove there is a single
   vertex `z` satisfying the neutralizer identities above.
3. Terminal-shadow stability under neutralization: prove adding such `z` repairs
   terminal-shadow validity and preserves positive `Psi`.
4. Connectivity: prove the same `z` repairs or preserves B-connectivity after
   flip.

The H2 all-max rescue orbits suggest `z` is constant for an entire cut orbit,
so it may be identifiable as a side-defect/twin gate rather than a seed-specific
choice.

## 2026-06-30 Correction: Do Not Require Lmax Seed

A separate existence gate shows that the completed switch cannot always be
chosen from an `Lmax` seed with one moat vertex.

```text
_codex_lmax_existence_gate.py:
negative 193, selected 193, no_switch 0, no_lmax 24.
```

The failures are precisely hard H2 all-max one-moat cases.  A representative:

```text
side = 011111111111000000, v=2, R[v]=-4.
seed A = {2,12,13} has boundary_delta(A)=4, B-after disconnected, no terminal shadow.
moat z = 1.
S = {1,2,12,13} is neutral, B-connected after flip, Gamma 296 -> 200.
```

For this completed switch:

```text
crossing bad lengths = (5,5,5,5,7,7,7,7)
boundary lambda prices = (5,5,5,5,5,5,5,5)
Psi = 96.
```

So the moat is not merely a neutralizer.  It can introduce the strict long-edge
surplus.  The final selector must allow an arbitrary length-bundle seed, not
only `Lmax`; the completed switch itself carries the long witnesses.
