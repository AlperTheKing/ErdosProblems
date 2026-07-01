# LOAD-PSC Component Frontier

Status: proof-facing assembly note. This is not a completed proof.

The current live target is `LOAD-PSC-5`:

```text
5 * sum_v a_tau(v) * (L - a_tau(v))
>=
N * (TV_B(a_tau) - TV_M(a_tau)),

a_tau(v)=min(T(v),tau),
L=N+N^2/25-|M|.
```

Equivalently, for load superlevels

```text
H_s={v:T(v)>s},
sigma_s=delta_B(H_s)-delta_M(H_s),
D=N^2-25|M|,
```

the running coarea balance is

```text
Phi(tau)=int_0^tau ((D+25N-50s)|H_s|-5N sigma_s) ds >= 0.
```

The ROWSUM/SPEC/K2T route is retired: the two-lane `L=12` gamma-min
connected-B maximum cut has `rho(O)>N` and `K2*T <= N*T` fails, while
`Gamma<=N^2` remains true.

## GPT-Pro C5 Collapse Suggestion

The latest GPT-Pro consult proposed:

```text
FIRST-NEGATIVE C5 QUOTIENT COLLAPSE.

If F(tau)>0 at the first critical level, where
F(tau)=N*(TV_B(a_tau)-TV_M(a_tau))
       -5*sum_v a_tau(v)*(L-a_tau(v)),
then the whole graph is a balanced C5 blow-up quotient.
```

This would imply `F(tau)=0`, hence contradiction. The idea is useful as an
equality-forcing slogan, but it is too global as a gate: the standing exact
battery has no first bad `tau`, so the implication is currently vacuous.

## Exact-Gated Smaller Frontier

The exact-validated LOAD-PSC route has split into low-side deposit and
high-side withdrawal pieces.

### 1. Low-Side Deposit

For each consecutive load band `[t_j,t_{j+1}]` with

```text
2*t_{j+1} <= N,
H_j={v:T(v)>t_j},
sigma_j=delta_B(H_j)-delta_M(H_j),
```

the full-battery verified deposit caps are

```text
LOW-XSLACK:    |H_j|*(N^2-25|M|) >= N*sigma_j,
LOW-GAMMA-CAP: |H_j|*(N^2-Gamma) >= N*sigma_j.
```

`LOW-GAMMA-CAP` is stronger. These statements are false outside the low-side
condition, so the threshold is real, not cosmetic.

Codex local scan found a useful split for `LOW-GAMMA-CAP`.

If

```text
Gamma <= N*|H_j|,
```

then `LOW-GAMMA-CAP` follows from the trivial pair bound

```text
sigma_j <= |H_j|*(N-|H_j|).
```

The remaining hard case is therefore `Gamma > N*|H_j|`. In this hard case,
the following simpler five-bound survived the local exact scan through census
`N<=11` plus two-lane/k-lane diagnostics:

```text
LOW-HARD-P5:
Gamma > N*|H_j|  and  2*t_{j+1}<=N
==>
sigma_j <= 5*|H_j|.
```

Local result:

```text
low bands checked = 507834,
hard rows Gamma>N|H| = 22113,
LOW-HARD-P5 violations = 0.
```

This does not by itself prove `LOW-GAMMA-CAP`, because some hard rows have
`Gamma > N*(N-5)`, where the five-bound has to be sharpened by its surplus.
But it isolates the low-side geometry: outside the trivial pair-count case,
the signed boundary has C5-scale size.

The remaining hard-excess rewrite is:

```text
LOW-HARD-EXCESS:
Gamma > N*|H_j|, Gamma > N*(N-5), and 2*t_{j+1}<=N
==>
N*(5*|H_j|-sigma_j) >= |H_j|*(Gamma-N*(N-5)).
```

This is exactly `LOW-GAMMA-CAP` rewritten in the near-extremal hard case,
but it isolates the mechanism: the spare five-bound slack must pay the
square-deficit excess above `N*(N-5)`. Codex exact gate:

```text
python problems/23/writeup/_low_hard_excess_gate.py \
  --min-n 7 --max-n 11 --two-lane-max 100 --blowup-t 5 --blowup-nmax 26

low bands = 507885,
trivial Gamma<=N|H| rows = 485763,
hard rows = 22122,
hard rows where P5 alone suffices = 21919,
hard-excess rows = 203,
LOW-HARD-P5 violations = 0,
LOW-HARD-EXCESS violations = 0,
max excess/payment ratio = 35/58.
```

### 2. High-Side Sign / Support

Use the BRIDGE-A band notation from
`problems/23/writeup/COMPONENT_BRIDGE_A_TARGET.md`:

```text
w_j=t_{j+1}-t_j,
A_j=w_j*(N+eta-t_j-t_{j+1})*|H_j|,
eta=N^2/25-|M|,
B_j=25*A_j-N*w_j*sigma_j.
```

The exact gates suggest the sharp support statement:

```text
POS-SUPPORT-CONTAINMENT.

If some high BRIDGE-A band has B_j<0, then the entire positive-load support
{v:T(v)>0} lies in a single K-component.
```

Equivalently, if the positive-load support has at least two K-components, then
every high band has nonnegative BRIDGE-A balance. Claude's full-battery gate
reported:

```text
high-negative configurations = 78225,
violations = 0.
```

A weaker sign lemma also passed: in disconnected positive-support cases, every
high band has `B_j>=0`; the only high bands found were nonnegative.

### 3. Single-Component BRIDGE-A

Once high negative withdrawal is confined to one K-component, the remaining
proof target is the component-local bridge bank.

For a K-component `C`, define

```text
A_pre(C)=sum_{2*t_j<N} w_j*(N+eta-t_j-t_{j+1})*|H_j cap C|.
```

Split high negative withdrawal proportionally:

```text
D_C += (-B_j) * |H_j cap C| / |H_j|.
```

The full-battery exact target is

```text
D_C <= 15*A_pre(C)
```

for every K-component. The exact maximum observed ratio is

```text
D_C/A_pre(C)=8305/559 < 15.
```

This is currently the smallest high-side bank statement in the load route.

## Dead Shortcuts

The following reductions have exact counterevidence and should not be used:

```text
1. Pointwise sigma_s <= 5|H_s|.
   False; k-lane examples reach sigma/|H|=6.

2. Endpoint-only/unimodality of Phi.
   False; _psc5_unimodal_gate.py finds upward sign recrossings by N=9.

3. Global ROWSUM/SPEC/K2T.
   False on two-lane L=12.

4. Single straddle band bank.
   False; full pre-half bank is needed.

5. Net_H<=3 as a standalone route.
   It remains only a scoped reduction depending on local atoms; it is not the
   current global LOAD-PSC proof path.

6. Low-side outside-vertex deficit payment.
   The tempting vertex-local strengthening
   `N*max(0,net_H(w)) <= |H|*(N-T(w))` for every `w notin H`
   is false. Diagnostic `_low_vertex_deficit_gate.py --stop-first` finds an
   `N=8` census witness with margin `-1` at `[a,b]=[3,4]`, `|H|=3`,
   `T(w)=3`, and positive boundary net `2`. Any low-side proof must pool at
   least beyond individual outside vertices.

7. Low-side outside K-component deficit payment.
   The natural pooled strengthening
   `N*max(0,net_H(C)) <= |H|*sum_{w in C\H}(N-T(w))`, assigning each boundary
   edge to the K-component of its outside endpoint, also fails. Diagnostic
   `_low_component_deficit_gate.py` finds exactly one violation through the
   current local battery: an `N=11` census row with margin `-1` at
   `[a,b]=[10/3,5]`, `|H|=5`, component net `21`, and outside-component
   deficit `46`. Thus the low-side proof still needs a small cross-component
   or structural correction even after K-component pooling.
```

## Current Proof Tasks

The proof work should focus on:

```text
(A) Prove LOW-GAMMA-CAP for low bands.

(B) Prove POS-SUPPORT-CONTAINMENT, or equivalently the multi-component
    high-band sign lemma B_j>=0.

(C) Prove SINGLE-COMPONENT BRIDGE-A:
    D_C <= 15*A_pre(C).
```

Together these are the most concrete exact-gated sublemmas currently supporting
`PREFIX-LOAD-PSC-5`.
