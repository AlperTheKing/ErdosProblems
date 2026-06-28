# Phantom-Hall Repair For ROWSUM

Status: **retired / false surrogate**.  The small-census gate passed, but
Claude's large quotient blow-up and local verification by
`_gptpro_c7_check.py` found a non-uniform `C7` blow-up with `N=1212` where
ROWSUM, STAR-K-multi, and therefore full-set Phantom-Hall fail.  The full
inverse cond3 certificate still holds on that instance.

Counterexample:

```text
C7 parts = (3,423,173,7,176,7,423)
ROWSUM margin = -3540476630161/3271659686685
full-inverse cond3 O-row margin = +633.9663
```

This note is kept only as a record of the false diagonal-bound route and the
small-case diagnostics that failed to expose the large blow-up obstruction.

Script:

```text
problems/23/writeup/_codex_phantom_hall.py
```

## Definitions

Fix a gamma-min connected-B maximum cut and an overloaded row `o in O`.
Let

```text
X_f := sum_{o' in O} p_f(o')
s_q := sum_{o' in O} K[o',q]     for q in Q
psi_o(q) := K[o,q] / (N - T(q) + s_q)
```

For each bad edge `f`, define the row demand atom

```text
c_f(o) := X_f * ( p_f(o) + sum_{q in Q} psi_o(q) p_f(q) ).
```

This is the atom used in the row-Hall attempt.  The false support-Hall
claim was:

```text
sum_{f in H} c_f(o) <= |union_{f in H} supp(p_f)|.
```

It fails at `N=9` because ROWSUM uses all `N` vertices, while support-Hall
throws away vertices idle for the whole row.

Define the active row support:

```text
A_o := { f : c_f(o) > 0 }
U_o := union_{f in A_o} supp(p_f)
idle_o := N - |U_o|.
```

## Candidate

For every subset `H subset A_o`:

```text
sum_{f in H} c_f(o) <= |union_{f in H} supp(p_f)| + idle_o.
```

The stronger truncated-mass version is:

```text
A_H(v) := sum_{f in H} X_f p_f(v)

sum_{f in H} c_f(o)
  <= sum_v min(1, A_H(v)) + idle_o.
```

The case `H=A_o` implies the desired row bound because the right side is at
most `|U_o| + idle_o = N`.

## Exact Verification

Command:

```text
python problems/23/writeup/_codex_phantom_hall.py -n 11 --workers 61 --max-m 14
```

Result:

```text
cuts=8494
skip=0
row_fail=0
ph_fail=0
tm_ph_fail=0
```

Worst slack:

```text
g6=J???E?pNu\?
side=00111111000
N=11
o=9
H={(0,10),(1,10),(8,10)}
demand=791867/77025
union=11
idle=0
support+idle cap=11
truncated+idle cap=95/9
slack=demand - truncated_cap = -63524/231075
```

## Interpretation

This is a strict repair of the false support-Hall route:

```text
support-Hall capacity         = |union supp(H)|                 false
phantom-Hall capacity         = |union supp(H)| + idle_o        live
truncated phantom capacity    = sum min(1,A_H) + idle_o         live
```

The new capacity bank `idle_o` is fixed for the row and represents vertices
that carry no active geodesic support for that row.  It precisely repairs the
N=9 failure where support-Hall had capacity `7` but ROWSUM had budget `N=9`.

This remains a nontrivial subset-Hall statement; it is not merely the full
ROWSUM inequality repeated for `H=A_o`.

Enhanced diagnostics on the same `N<=11` census:

```text
subset_gt_full=12012
tm_subset_gt_full=38628
```

So many proper subsets have larger support/truncated deficit than the full
active set.  Phantom-Hall is not explained by "the full active set is always
worst."

Trimmed adversarial battery:

```text
python problems/23/writeup/_codex_phantom_hall.py --mode adversarial --workers 61 --max-m 14
```

Result:

```text
cuts=310
skip=0
row_fail=0
ph_fail=0
tm_ph_fail=0
```

This includes smaller Mycielskians, selected non-uniform `C5` blow-ups, and
glued island/gadget examples.  The `N=23` iterated Mycielskian is intentionally
left to Claude's specialized gate because exhaustive max-cut generation in
this local script is too slow.

## Failed Modular Split

The tempting split

```text
Q contribution <= Q truncated capacity       (Q-CAP)
O-direct contribution <= O truncated capacity + idle_o
```

does not work.  The second inequality is false already through `N<=9`:

```text
oside_fail=598
worst: G?`F`w, side=11110000, N=8, o=6,
       H={(4,7),(5,7)}, O-direct=4, O-cap+idle=2.
```

Thus a proof of truncated phantom-Hall must use coupled transport: unused
capacity on `Q` can pay part of the overloaded-anchor term.  The surviving
object is a genuine global Hall statement with a row-idle bank, not a direct
sum of independent `Q` and `O` inequalities.

## Useful Reformulation

For a fixed row `o`, define

```text
h_o(v) =
  1              if v=o,
  psi_o(v)       if v in Q,
  0              otherwise.
```

Then for every `H subset A_o`,

```text
sum_{f in H} c_f(o) = sum_v A_H(v) h_o(v).
```

So the truncated phantom-Hall candidate is exactly

```text
sum_v A_H(v) h_o(v) <= sum_v min(1,A_H(v)) + idle_o.
```

Equivalently, with

```text
excess_o(H) := A_H(o) - min(1,A_H(o)),
Q_surplus(H) := sum_{q in Q} ( min(1,A_H(q)) - psi_o(q) A_H(q) ),
O_other_cap(H) := sum_{o' in O, o' != o} min(1,A_H(o')),
```

the exact residual form is

```text
excess_o(H)
  <= idle_o + Q_surplus(H) + O_other_cap(H).
```

This residual makes the failed modular split transparent: `idle_o +
O_other_cap(H)` alone does not pay `excess_o(H)`.  The live mechanism must
show that geodesics which overload the fixed row `o` necessarily create
enough `Q_surplus` or row-idle capacity.

## Minimal-Counterexample Shape

For fixed `o`, let

```text
C(H) := |union_{f in H} supp(p_f)| + idle_o
D(H) := sum_{f in H} c_f(o).
```

Assume a phantom-Hall counterexample exists and choose an inclusion-minimal
one `H`.  Then:

```text
D(H) > C(H),
D(H \ {f}) <= C(H \ {f})  for every f in H.
```

Subtracting gives the necessary irreducibility condition

```text
c_f(o) > priv_H(f) := |supp(p_f) \ union_{g in H\{f}} supp(p_g)|
```

for every `f in H`.  The idle bank does not appear in the marginal
subtraction because it is a global dummy capacity adjacent to every active
edge.  It appears only in the total obstruction:

```text
sum_{f in H} c_f(o) - |union supp(H)| > idle_o.
```

Thus a minimal counterexample must be a no-peel corridor bundle whose total
private-support deficit exceeds the row-idle bank.  This is the corrected
version of the old support-Hall proof skeleton:

```text
old false target:     total private deficit <= 0
phantom-Hall target:  total private deficit <= idle_o
```

The N=9 row-Hall failure lives exactly in the gap: it has support deficit
`54/7 - 7 = 5/7`, while `idle_o=2`, so phantom-Hall passes.

## Near-Tight Diagnostics

Script:

```text
problems/23/writeup/_codex_phantom_neartight.py
```

Command:

```text
python problems/23/writeup/_codex_phantom_neartight.py -n 11 --workers 61 --keep 60
```

The tightest `N<=11` phantom-Hall subsets are highly structured:

```text
top slack = 154/237
graph = J???E?pNu\?
H_size = 2
active_size = 3
idle_o = 0
no_peel = true
each c_f(o) = 871/237
each private support size = 1
union size = 8
```

The first 16 entries are symmetric copies of this two-edge no-peel bundle.
The full active triple in the same graph has slightly larger slack
`55408/77025` and is peelable (`no_peel=false`).

However, a pure pairwise reduction is not valid as a proof strategy:
near-tight `H_size=3` no-peel examples appear by the top-60 list, e.g.

```text
g6=I?`FAo]]?
N=10
H_size=3
idle_o=0
no_peel=true
slack=42112023350903/45971715879720
```

So the likely proof route is:

1. Peeling removes edges with `c_f(o) <= private_H(f)`.
2. The irreducible residual is a no-peel corridor bundle.
3. Show every no-peel bundle satisfies the phantom-Hall bound, with the
   uniform odd-cycle blow-up as the zero-idle extremal and idle vertices as
   extra capacity in non-uniform cases.

## No-Peel Pattern Summary

Script:

```text
problems/23/writeup/_codex_nopeel_patterns.py
```

Command:

```text
python problems/23/writeup/_codex_nopeel_patterns.py -n 11 --workers 61 --keep 20
```

The run found `140` coarse no-peel pattern classes.  The key is

```text
(|H|, idle_o, shared_core_size, multiplicity_histogram, private_sizes)
```

where the shared core is the union support minus vertices private to a
single edge of `H`.

Smallest-slack patterns:

```text
#1 slack=154/237
key=(2, 0, 6, ((1, 2), (2, 6)), (1, 1))
g6=J???E?pNu\?  H=[(0,10),(1,10)]

#2 slack=42112023350903/45971715879720
key=(3, 0, 4, ((1, 1), (2, 5), (3, 4)), (0, 0, 1))
g6=I?`FAo]]?  H=[(3,8),(4,9),(4,7)]

#3 slack=3726703333599538/4009586841135995
key=(3, 0, 7, ((1, 4), (3, 7)), (1, 1, 2))
g6=J??CABoBz{?  H=[(1,10),(2,10),(3,10)]
```

This rules out a proof that only treats parallel two-edge bundles.  The
live irreducible class includes genuine three-edge no-peel bundles, some
with zero-private edges.  A viable proof needs a shared-core/corridor
capacity statement for arbitrary no-peel support hypergraphs:

```text
sum_{f in H} c_f(o) - sum_f private_H(f)
  <= shared_core_size(H) + idle_o.
```

This is exactly phantom-Hall rewritten after peeling, but the diagnostic
suggests the shared core, not pairwise corridors, is the correct object to
charge.
