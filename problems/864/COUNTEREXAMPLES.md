# Counterexamples and Guardrails

No candidate lemma is accepted without an exact gate.

Mandatory fixtures:

1. Genuine Sidon sets.
2. Erdos-Freud reflected sets B union (s-B).
3. Unbalanced reflected sets.
4. Exact extremizers through N=69.
5. Sets with no exceptional sum.
6. Sets whose exception has many representations.
7. Even/odd exceptions and endpoint exceptions.

Record each killed statement with:
- exact statement;
- smallest falsifier;
- verifier command;
- arithmetic model;
- reason the repair is materially different.

## P45 signed carry twins

At `h=6,b=2`, the sets `B-={2,4,5}` and `B+={2,3,5}` are integer Sidon and
satisfy `-b notin 3B-B`, with repetitions allowed. They have identical
unsigned profile

    (a,c,delta,R,u,R12,M1+M2)=(1,1,7,5,0,2,7),

but `(M1,M2)=(3,4)` and `(4,3)`. Hence neither carry level universally
dominates, and `M1-M2<=u` is false. Verified by
`compute/p45/audit_signed_carry_identity.py`.

## P49 interval-to-cycle transfer

The odd valid set `E={1,7,11}` has distinct diagonal-inclusive pair sums and
`E intersect 3E=empty`, but modulo 12 it has the collision
`1+1=7+7`. Thus reduction modulo `max(E)+1` does not preserve strong
4-independence.

## P46 collision-only defect

At `p=4,h=14,b=1`, the Sidon set `B={1,3,9,13}` satisfies
`-1 notin 3B-B`. Its modular sum and shifted-difference supports are
disjoint, so all carry overlaps and moments vanish, yet

    delta=9, C_S=3, C_D=6, H_0=0.

This falsifies every proposed defect bound whose right side contains only
carry overlap/count/moment terms and vanishes when the overlap is empty.

## P57 linear fold-repair falsifier

Let

    Z={0,7,37,48,52,68,76,101,110,111,123,161,167,188,190,193,207},
    p=17, gamma=80, b=2, h=288, B=gamma+Z.

Then `B` is integer Sidon, `-2 notin 3B-B`, `delta=138`, and both modular
fold counts vanish: `C_S=C_D=0`. Hence
`delta<=5(C_S+C_D)+4p` fails by 70. The scale-repaired inequality was later
killed by P58. Exact reconstruction:
`compute/p57/scan_fold_repair_translations.py`.

## P58 constant-2 square fold-repair falsifier

At `p=14,h=183,b=1`, let

    B={33,60,72,75,79,81,95,119,124,132,149,150,160,182}.

This is integer Sidon, `-1 notin 3B-B`, and `C_S=C_D=0`. Its defect is
`delta=105`, so

    max(delta-5(C_S+C_D),0)^2=11025>10976=4p^3.

The exact verifier checks all `14^4=38416` ordered quadruples. Run
`python -B problems/864/compute/p58/verify_counterexample.py`.

## P53 unconditioned folded-sum bound falsifier

At `p=25,h=494`, the ruler

    {1,2,34,84,105,111,125,164,186,201,204,250,252,259,315,
     344,357,387,431,441,457,465,476,488,493}

is integer Sidon and has positive defect 432, but `C_S=49>47=2p-3`.
It does not falsify the hole-restricted lemma because
`1+1+201-204=-1` and `1+2+488-493=-2`.

## P50 all-scale coefficient 13/6 falsifier

For `A={1,2,4,8,10,11}` and `N=H=11`, the sole repeated sum is 12 and

    (k,M_H,G_H,D_H,Q_H,Z_H)=(6,21,0,38,6,32).

The coefficient-`13/6` margin is `3X_H-26U_H=341>0`. This does not touch
LG33 (`9U_H-X_H=88>0`) or the prescribed scale `H=5`.

## P55 cross-disjointness without internal Sidonicity

For `X={0,1}` and `Y={0,2,...,2(q-1)}`, the positive difference value sets
are disjoint, but `span(X)+span(Y)=2q-1=o((|X|+|Y|)^2)`. Thus P48's span
claim requires internal difference injectivity of both components, not only
cross-disjointness.

## P51 all-distinct equal-three-sum collision

The valid pair `Z={0,1,5,11,13,20,44}`, `G=16` has

    25=0+5+20=1+11+13.

Both representations are all-distinct with disjoint supports. This is the
smallest falsifier in `(p,W)` to the claim that every low triple collision
contains a repeated summand.

## P59 barycenter block-count coupling

For `Z={0,7,9,12,20,26,30,58}` and `G=15`, maximum feasible barycentric
sets at 37 and 39 are

    {0,7,9,12,20,26}, {0,7,9,12,20,30}.

They intersect in five marks, while their block-count parameters sum to
four. Actual balanced supports at sums 39 and 42 also fail by one.

## P52 spectral-slope reversal

For `Z={0,3,4}`, `G=2`, every structured polynomial hypothesis holds, but
twice the autocorrelation slope is

    (3,5,4,6,8,6,4,4,3,1).

The decrease `5,4` followed by the increase to `6` falsifies the proposed
single-peak slope theorem.

## P68 literal-hole smoothing

For `Z={0,24,26,29,30}` and `G=7`, the set
`E=G+2Z={7,55,59,65,67}` is Sidon and disjoint from `3E`. In the shifted
support `Z-3Z`, every integer from 7 through 23 is missing; 6 and 24 are
represented. Thus a literal hole need not be isolated or locally smooth.

## P56 blocked reflected completion

`A={0,2,3,6}` is admissible with exceptional sum 6. Reflecting its residual
point 2 adds 4 and produces repeated sums 4, 6, and 8. The virtual label 2
collides with the existing difference `2-0`. Hence naive same-span reflected
completion is false even when the reflection shift is zero.

## P61 local completion charges

For `A={0,1,2,5}` with exceptional sum 2,
`(p,eps,u,L,tau,beta,h_S)=(1,1,1,5,3,0,2)`, so the tempting bound
`2beta+tau<=h_S` reads `3<=2`.

For `A={0,4,6,7,12}` with exceptional sum 12, the residual is `{4,7}` and
all three virtual labels collide. Thus `beta=3`, `|D_R|=7`, and
`2beta+u<=|D_R|` reads `8<=7`.

## P64 one-label LG33 bridge

For the stored reflected row `ruzsa-9ab2ac138632`,
`(N,H,p,W,c,gamma)=(4925,290,46,2127,4924,670)`. The proposal replacing
the full adjacent duplicate mass by one copy of each touched label fails by
exactly 64,625, while LG33 itself has positive slack 53,731,150.

## P65 fold-graph shortcuts

The valid set
`B={23,24,56,127,133,186,272,281,337,341,366,379,409,453,479,487,498,510,515}`
has `(p,h,b,C_S)=(19,516,2,20)` and `-2 notin 3B-B`, so `C_S<=p-1` is
false. A separate valid Singer row has a literal `K_3,3` in its outer fold
graph and degeneracy six, falsifying planarity and 2-degeneracy mechanisms.

## P67 pairwise fiber coupling

For every q>=3 there is a valid Sidon/gap instance with two type-111 fibers
of q blocks each whose supports meet in `3q-1` marks. Since their total block
count is `2q`, any P59-style pairwise intersection estimate with `o(q)`
additive loss is false.

## P71 unrestricted hole-restricted fold bound

The exact set
`B={3,5,69,169,211,223,251,329,373,403,409,501,505,519,631,689,715,775,863,883,915,931,953,977,987}`
has `(p,h,b)=(25,988,1)`, 325 distinct unordered sums including diagonals,
300 distinct positive differences, and a literal `-1 notin 3B-B` hole, but
`C_S=49>47=2p-3`. The affine rule `B_q=qA+(q-1)` gives infinitely many
counterexamples because folds are preserved and the hole follows modulo q.
Their compensated defects are `delta_q=926-494q<0`; in particular the
displayed member has `delta=-62`. This does not falsify the hard-regime
candidate `delta>0 => C_S<=2p-3`.

## P75 positive-defect hole-restricted fold bound

Adjoin `639` to the displayed P71 set. The resulting 26-point ruler has
`(h,b,delta,C_S)=(988,1,14,51)`, all 351 unordered sums and 325 positive
differences are unique, and parity proves the literal hole. Since
`51>49=2p-3`, the positive-defect form is false. Exact verification:
`compute/p75/verify_hard_fold_counterexample.py`.

## P79 fold-graph biclique exclusions

The P75 outer graph already contains K4,4. The stored Singer row
`singer-e82f2d6a63ca` contains K5,5 and has pair codegree 11; the full P20
translation corpus reaches codegree 12. Thus K2,4 and K4,4 exclusions are
false even with positive defect and the literal hole.

## P80 universal endpoint sumset-translate bound

The 29-point ruler recorded in `fanout/wave5/P80_Sidon_sumset_translate.md`
has endpoint shift `h=640` and `C_S=58>57=2p-1`, while all 435 unordered
sums and 406 positive differences are unique. It is not a hole witness:
`D` meets `S+1` in 89 labels and `S+2` in 97. Exact verification:
`compute/p80/verify_sumset_translate_counterexample.py`.

## P83 fourth phase nonedge

The positive-defect literal-hole ruler
`B={5,7,18,24,25,28,33}`, `(h,b)=(34,2)`, has a loose fold triangle with
phase parameters `(d,R)=(14,-6)`, but `d-R=20=25-5` is a represented
positive difference. Thus the three forced phase nonedges cannot be enlarged
by the symmetric-looking fourth label `d-R`.

## P86 reflection-sensitive loose-triangle count

The P75 ruler and its reflection about 495 have identical
`(p,h,b,delta,C_S)=(26,988,1,14,51)` and both satisfy the literal hole, but
their exact loose-triangle counts are 25 and 37. Hence `T_F` is not
determined by the scalar fold data and is not reflection invariant.

## P95 support-fold Hall injection

The P94 row `(p,h,b,C_S,T_F)=(104,14484,1,142,116)` has no matching from
all loose triangles to their three supporting folds. Its maximum matching
has size 105, and 72 triangles have only 61 neighboring supporting folds.

## P92 one-step hexagon-label injection

A 138-point exact row at `(h,b,delta,C_S,T_F)=(28410,1,88,48,11)` has
eight loose triangles whose complete one-step neighborhoods under all three
P83 labels and every signed represented-hexagon step contain only seven
fold labels. Exact verifier: `compute/p92/verify_hexagon_hall_counterexample.py`.

## P88 pure-order C84

The endpoint Sidon ruler in `fanout/wave5/P88_phase_redteam.md` has
`(p,h,delta,C_S,T_F)=(60,3286,2085,182,200)`. Its component excess is 35,
so total, componentwise, and ordered-threshold forms of pure C84 are false.
It fails both literal holes; the hole-restricted candidate is not falsified.

## P98: componentwise fold charge fails under every frontier gate

Deleting `4740` from the P94 tight row gives an endpoint-normalized Sidon
set with `p=103`, `h=14484`, `b=1`, `delta=1379`, and the literal hole.
Globally `(C_S,T_F,V_b)=(132,110,0)`, but one loose-triangle component has
110 triangles on 109 folds. Reproduce with
`compute/p98/verify_single_deletion_falsifier.py`.

## P105: unrestricted corrected C84 and RM97 are false

The 57-mark row in `fanout/wave5/P105_corrected_c84_falsifier.md` has
`(h,b,delta,C_S,T_F,V_b)=(6572,1,-1726,159,160,0)` and satisfies the literal
hole. Hence both unrestricted `T_F<=C_S+V_b` and unrestricted RM97 fail.
The positive-defect restriction required by the actual application remains
unfalsified. Reproduce with `compute/p105/verify_witness.py`.

## P109: canonical residual intervals do not form closed components

For `B={8,10,15,23,24,27}`, `h=28`, `b=2`, the system has positive defect
24 and the literal hole. Its unique loose triangle uses three folds whose
canonical residual intervals are `[3,3]`, `[-1,2]`, and `[2,2]`; hence its
support crosses two interval-overlap components. There are 304 such rows in
the complete positive-defect literal-hole width-30 audit. Reproduce with
`compute/p109/audit_residual_components.py`.

## P111: abstract ordered linearity does not prove weighted independence

A 20-vertex, 51-edge ordered linear rooted 3-graph has rank 50 for the
fold-only rows `(S,E,dE)`. It is not asserted to be arithmetically realizable.
The exact edge list is checked by
`compute/p111/verify_abstract_rank_counterexample.py`.

## P114: outer endpoints plus span length do not satisfy abstract Hall

The 13-vertex linear proper-middle system in
`compute/p114/verify_abstract_span_hall_counterexample.py` has 20 triples
but maximum matching 19 to outer endpoints and span lengths. It does not
falsify P113's full support-plus-difference Hall statement.

## P106: positive defect alone does not imply RM97

The exact 67-mark row in `fanout/wave5/P106_rm97_positive_defect.md` has
`(h,b,delta,C_S,T_F,V_b)=(6572,1,129,199,221,20)`, so
`T_F>C_S+V_b`. Its minimal Hall window has 411 intervals and 410 slots.
It is not a literal hole. Reproduce with
`compute/p106/verify_positive_falsifier.py`.

## P110/P115: dense arithmetic rows kill the global matrix and color budgets

The 104-mark endpoint ruler in `compute/p110/dimension_falsifiers.json` has
`(h,delta,C_S,T_F)=(9821,6352,579,1104)`, so every proposed relation matrix
with at most `C_S+4p=995` columns is dimensionally impossible. The same row
has `V_1=314` and positive color excess `E_+=598`, falsifying BC108 because
`598>104+314`. It is not a literal hole; its parity lift is a hole with
negative defect. See `fanout/wave6/P115_bc108_cycle_budget.md`.

## GPT raw-overlap estimate is false at the sharp endpoint scale

The archived Singer-lift construction in
`gpt_pro/2026-07-13_raw_overlap_singer_falsifier_response.md` has
`max(E)=(3+o(1))p^2` but carry overlap `|I|=Omega(p^2)`. The exact 44-mark
member has `|I|=614`; its overlap is cancelled by uncovered residues in the
signed defect `a+c+|I|-H`. Therefore no `O(p^(3/2))` raw-overlap lemma can
close the reflected route.
