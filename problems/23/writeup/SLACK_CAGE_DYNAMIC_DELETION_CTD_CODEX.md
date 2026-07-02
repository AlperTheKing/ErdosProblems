# Slack-CAGE Dynamic Deletion CTD

This note replaces the false fixed-mass CTD formulation.

## Prebank

For a row `Q` and a set `U`, write

```text
pre_Q(U) = D_Q(U) - |U| - sigma(U),
sigma(U) = delta_B(U) - delta_M(U).
```

Slack-CAGE is

```text
pre_Q(U) <= eta,
eta = N^2/25 - |M|.
```

For a peel `S subset U`, define the dynamic deletion mass

```text
del_Q(S;U) = D_Q(U) - D_Q(U-S).
```

Then

```text
drop_Q(S;U)
  = pre_Q(U) - pre_Q(U-S)
  = del_Q(S;U) - |S| - (sigma(U)-sigma(U-S)).
```

The eta-bank charge is not the raw drop.  It is the consumed positive part:

```text
bank_Q(S;U)
  = max(0, pre_Q(U)) - max(0, pre_Q(U-S)).
```

This is the quantity that telescopes along a peel sequence.

## Why Fixed-Mass CTD Is Wrong

GPT-Pro's intermediate fixed atomic measure used the row family already counted
inside `U`:

```text
R_Q(U) = {(g,P): P in cyc[g], V(P) subset U, V(P) cap V(Q) nonempty}
```

and

```text
mu_R(S) =
  sum_{(g,P) in R_Q(U)} |V(P) cap V(Q) cap S| / |cyc[g]|.
```

The tempting residual

```text
mu_R(S)-|S|-sigma(S)
```

does not describe the Flat5 bank branch.  Exact census gates show that a Flat5
peel may consume all positive `pre_Q(U)` dynamically while this fixed residual
is zero or negative.

Full CTD structure scan:

```text
script:
  problems/23/writeup/_codex_slack_cage_ctd_structure_gate.py

N=10:
  positive = 12
  Flat5 fixed-pre nonpositive = 8
  Flat5 fixed-pre positive = 4
  max fixed subset pre = 4

N=11:
  positive = 40
  Flat5 fixed-pre nonpositive = 28
  Flat5 fixed-pre positive = 12
  max fixed subset pre = 4
  min Flat5 fixed pre_S = -1
```

Witness:

```text
graph = J??CAAoR`Y?
Q = (4,9,1,7,10)
U = (1,4,5,7,9,10)
pre_Q(U) = 1
S = (4,)  # Flat5 zero-slack peel

fixed:
  mu_R(S)-|S|-sigma(S) = 0
  fixed residual after S = 1
  fixed consume = 0

dynamic:
  pre_Q(U-S) = -3
  bank_Q(S;U) = 1
```

Thus the bank branch lives in the disappearing rows

```text
{(g,P): V(P) subset U, V(P) not subset U-S, V(P) cap V(Q) nonempty},
```

not in the vertex mass of `S` alone.

## Correct Lemma Tree

### Lemma D-CTD: dynamic terminal deletion

Let `(Q,U)` be a lexicographically minimal positive prebank pair:

```text
pre_Q(U) > 0.
```

Then at least one of the following holds.

1. **Flat5 bank peel.** There is a connected terminal-shadow Flat5 zero-slack
   peel `S subset U` such that

   ```text
   pre_Q(U-S) < pre_Q(U)
   ```

   and therefore `bank_Q(S;U)>0`.

2. **Strict residual cage.** There is a connected terminal-shadow zero-slack
   cage `S subset U`, not a Flat5 bank atom, such that

   ```text
   Xi2(S) > 0.
   ```

The finite gates support the stronger census fact that, whenever the strict
branch does not occur through `N<=11`, a single Flat5 peel has

```text
pre_Q(U-S) <= 0.
```

### Lemma D-BANK: Flat5 dynamic bank is globally bounded

For every terminal-closure-compatible sequence of Flat5 bank peels

```text
U_0 = U,
U_i = U_{i-1} - S_i,
```

the positive-part bank consumption satisfies

```text
sum_i bank_Q(S_i;U_{i-1}) <= eta.
```

Equivalently, augment the bad-edge count by the Flat5 bank units selected by
the dynamic deletion process and prove the extremal `C5` product bound

```text
|M| + sum_i bank_Q(S_i;U_{i-1}) <= N^2/25.
```

This is the real eta-bank theorem.

### Lemma D-STRICT: non-Flat5 residual drops Gamma

If `S` is a connected terminal-shadow zero-slack cage, is not a Flat5 bank atom,
and has

```text
Xi2(S)>0,
```

then flipping `S` preserves maximum-cut size and connectedness while strictly
decreasing `Gamma`.

This follows from the witness-bijection square comparison already encoded in
the Xi2 gate.

## Final Dynamic Proof Skeleton

Assume a minimal Slack-CAGE violation:

```text
pre_Q(U) > eta.
```

Apply D-CTD repeatedly.

If a non-Flat5 strict residual cage occurs, D-STRICT contradicts
`Gamma`-minimality.

Otherwise the process consists only of Flat5 bank peels.  The positive parts
of `pre_Q(U_i)` telescope:

```text
pre_Q(U)_+ - pre_Q(U_k)_+
  = sum_i bank_Q(S_i;U_{i-1}).
```

Once no positive prebank remains, `pre_Q(U_k)_+=0`, so

```text
pre_Q(U) = sum_i bank_Q(S_i;U_{i-1}) <= eta
```

by D-BANK, contradicting `pre_Q(U)>eta`.

Therefore no Slack-CAGE violation exists.

## Exact Gates Already Run

Positive-part Flat5 peel gate:

```text
script:
  problems/23/writeup/_codex_slack_cage_flat5_peel_gate.py

N=10:
  positive = 12
  needs_bank = 12
  flat5_consumes_positive = 12
  fail = 0
  max_bank = 1

N=11:
  positive = 40
  needs_bank = 40
  flat5_consumes_positive = 40
  fail = 0
  max_bank = 1
```

Xi2 split gate:

```text
script:
  problems/23/writeup/_codex_slack_cage_xi2_parallel_gate.py

N=10:
  positive_cases = 12
  zero cages = 20
  flat5 = 20
  xi2_zero = 20
  no non-Flat5 bad Xi2 cases

N=11:
  positive_cases = 40
  zero cages = 64
  flat5 = 64
  xi2_zero = 64
  no non-Flat5 bad Xi2 cases
```

Interpretation:

```text
Observed positive prebank cases through N<=11 are entirely Flat5 dynamic-bank
cases.  The fixed-mass CTD route is false/insufficient for this branch.
```

Deletion profile gate:

```text
script:
  problems/23/writeup/_codex_slack_cage_flat5_deletion_profile.py

N=10:
  cases = 12
  deleted row profiles:
    ((5,1,4),)       : 4
    ((5,1,5),)       : 4
    ((5,1,4),(5,1,5)): 4
  delD:
    4 : 4
    5 : 4
    9 : 4
  raw drops:
    3 : 4
    4 : 4
    5 : 4
  sigma_diff:
    0 : 12

N=11:
  cases = 40
  deleted row profiles:
    ((5,1,4),)       : 14
    ((5,1,5),)       : 14
    ((5,1,4),(5,1,5)): 12
  delD:
    4 : 14
    5 : 14
    9 : 12
  raw drops:
    3 : 14
    4 : 14
    5 : 12
  sigma_diff:
    0 : 40
```

Here `(5,1,k)` means a deleted length-5 row with unit row mass and
`|P cap Q|=k`.  Thus every observed Flat5 bank peel deletes only length-5
row mass, changes no local cut slack, and consumes only the clipped
positive-part bank:

```text
bank_Q(S;U) = pre_Q(U)_+ - pre_Q(U-S)_+ = 1
```

even when the raw row-deletion drop is `3`, `4`, or `5`.  The next proof
target is therefore not a fixed-residual cage inequality, but the global
bound that these clipped length-5 Flat5 row-deletion bank units satisfy

```text
|M| + sum bank_Q(S_i;U_{i-1}) <= N^2/25.
```
