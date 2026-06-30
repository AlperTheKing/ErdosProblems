# K2T Strict-Lens Proof Split

Status: active decomposition of the K2T/CSM route.

## Main Certificate

Let

```text
K2[v,w] = sum_f Pr_{Q in cyc[f]}[v,w in Q]
T = K2*1
R[v] = N*T[v] - (K2*T)[v].
```

The target is

```text
R[v] >= 0  for every v.
```

This implies `rho(K2) <= N` by Collatz-Wielandt, then `rho(K)<=N`
by Jensen, and finally `Gamma<=N^2`.

## Strict Lens

A strict bad-geodesic lens is an ordered pair of bad edges `(f,g)` such that

```text
ell[f] > ell[g]
```

and some `Pg in cyc[g]` is a contiguous subpath of some `Pf in cyc[f]`,
allowing reversal.

The intended proof is:

```text
gamma-minimality forbids strict lenses
strict-lens-free => K2*T <= N*T
```

## Lemma 1: Positive Per-Edge Contribution Forces A Strict Lens

For each bad edge `g` and vertex `v`, define

```text
C_g(v)
  = (1/|cyc[g]|) * sum_{Q in cyc[g], v in Q}
      (sum_{u in Q} T[u] - N*ell[g]).
```

Candidate lemma:

```text
C_g(v) > 0
=> g is the short member of a strict lens (f,g),
   and v lies on a participating short geodesic Pg of g.
```

Then strict-lens-free cuts satisfy `C_g(v)<=0` for every `g,v`,
which gives `K2*T <= N*T` after summing over `g`.

Local gate:

```text
census all connected-B max cuts N<=10
Grotzsch all max cuts
H?AFBo][2], H?AFBo][3] inherited cuts
random80 N=11/12

cuts = 18554
positive C_g(v) entries = 222
covered = 222
fail = 0
```

## Lemma 2: Gamma-Minimality Forbids Strict Lenses

If a strict lens exists, use an equal-length geodesic-bundle prefix/suffix
switch.  The switch must be:

```text
cut-neutral: dB(S)=dM(S)
B-connected after flipping
terminal-shadow safe
Psi(S)>0
```

where

```text
Psi(S) = sum_{f in crossing old bad edges} ell[f]^2
       - sum_{e in old B-boundary} lambda_S(e)^2.
```

Here `lambda_S(e)` is the smallest length of a crossing old bad edge whose
old shortest geodesic exits through `e`.  The terminal-shadow gates imply

```text
Gamma(after) <= Gamma(before) - Psi(S).
```

Thus a gamma-minimal cut cannot contain the strict lens.

Local gate:

```text
_codex_k2t_lenbundle_terminal_shadow_gate.py
census N<=10 + H?AFBo][2],[3] + random80:
negative vertices = 56
covered by Psi-positive length-bundle switches = 56
fail = 0
```

## Remaining Mathematical Work

Prove the two statements above without finite enumeration:

1. `C_g(v)>0` forces a shorter bad geodesic to sit as a subpath of a
   longer bad geodesic.
2. Every strict lens produces a terminal-shadow `Psi>0` length-bundle switch.

The second statement is purely switch/geodesic geometry.  The first is the
load-cancellation statement in antichain form.
