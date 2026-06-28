# Selected Fractional-SPLIT Tie-Break Target

Status: proof target, not a proof.

## Verified Facts

The all-cut fractional SPLIT certificate is false.  The first exact witness is

```text
g6 = J?AAFAwe_}?
side = 11111010000
f = (1,6)
A = (1, 2, 19/7, 71/35, 47/35)
ROWSUM = 318/35 < 11
```

But the selected-cut version survives the full census gate currently available:

```text
python problems/23/writeup/_frac_selected_gate.py

N=7:  graphs-with-gamma-min-cuts=15     NO-GOOD-CUT=0
N=8:  graphs-with-gamma-min-cuts=85     NO-GOOD-CUT=0
N=9:  graphs-with-gamma-min-cuts=650    NO-GOOD-CUT=0
N=10: graphs-with-gamma-min-cuts=5800   NO-GOOD-CUT=0
N=11: graphs-with-gamma-min-cuts=65244  NO-GOOD-CUT=0
```

Thus the current certificate target is:

> Every connected-B gamma-min maximum-cut class contains at least one cut for
> which fractional SPLIT holds for every bad edge.

This is enough for ROWSUM-O, because the reduction may choose a gamma-min cut.

## Fractional SPLIT Condition

For bad edge `f` of length `L`, let

```text
A_i(f) = sum_{v in layer i of f} p_f(v) S(v)
R(f)   = sum_i A_i(f) - N
B_t(f) = OUT_t(f) - 2tN/L
```

The fractional shell certificate for `f` is

```text
R(f) <= 0,
min_t B_t(f) <= 0,
max_t B_t(f) >= R(f).
```

Adding the averaged outer and central inequalities gives ROWSUM-O for `f`.

## N<=11 Bad-Cut Classification

The probe

```text
python problems/23/writeup/_codex_frac_switch_repair.py -n 11 --workers 61
```

checks `189447` gamma-min cuts.  Only eight are fractional-SPLIT-bad.  All
eight bad rows have `L=5`.

Seven bad cuts have a SPLIT-good gamma-min cut at Hamming distance `1`.  The
single exception has a SPLIT-good gamma-min cut at Hamming distance `2`.

The exact bad rows are:

```text
J?AAFAwe_}?  11111010000  f=(1,6)
  A=(1,2,19/7,71/35,47/35), defect=1/7, repair flip {1}

J?AAFAwe_}?  11111110000  f=(1,6)
  A=(1,2,19/7,71/35,47/35), defect=1/7, repair flip {1}

J?AAF@cm?}?  11111110000  f=(1,6)
  A=(41/30,29/15,7/3,12/5,1), defect=1/15, repair flip {6}

J?ABCfG]@h?  11111100000  f=(0,5)
  A=(17/12,13/6,9/4,9/4,1), defect=1/20, repair flip {5}

J?ABCdW{?{?  00001111110  f=(4,8)
  A=(1,13/6,13/5,19/10,41/30), defect=1/15, repair flip {4}

J?AFCpc{?t?  00001011110  f=(4,7)
  A=(1,11/5,34/15,7/3,7/6), defect=1/15, repair flip {4}

J?AFCpc{?t?  00001111110  f=(4,7)
  A=(1,11/5,34/15,7/3,7/6), defect=1/15, repair flip {4}

J?b@b_wBuD?  10000111100  f=(0,5)
  A=(7/6,7/3,7/3,7/3,7/6), defect=2/15,
  repair flips {0,4} or {1,5}
```

## Length-5 Interpretation

For `L=5`, fractional SPLIT fails only if both central overload inequalities
hold:

```text
A_2 > N/5,
A_1 + A_2 + A_3 > 3N/5.
```

Equivalently,

```text
B_2 < R,
B_1 < R.
```

The bad N<=11 cases are exactly small central-shell overloads of a length-5
bad edge.  The observed repairs rotate or replace the bad edge while preserving
the max-cut value, connectedness of `B`, and Gamma.

## Endpoint-Rotation Algebra For `L=5`

Write

```text
A = (a0,a1,a2,a3,a4),       R = a0+a1+a2+a3+a4 - N.
```

If the left endpoint of the bad edge is flipped and the bad edge rotates to
the first B-edge on a unique shortest path, the new row has the cyclic order

```text
A^L = (a0,a4,a3,a2,a1).
```

If the right endpoint is flipped, the new order is

```text
A^R = (a4,a0,a1,a2,a3).
```

For the left rotation,

```text
B_2(A^L) - R = N/5 - a3,
B_1(A^L)     = a0+a1 - 2N/5.
```

So the left rotation is certified by the two scalar inequalities

```text
a3 <= N/5,
a0+a1 <= 2N/5.
```

For the right rotation,

```text
B_2(A^R) - R = N/5 - a1,
B_1(A^R)     = a3+a4 - 2N/5.
```

So the right rotation is certified by

```text
a1 <= N/5,
a3+a4 <= 2N/5.
```

The observed one-flip repairs satisfy one of these two endpoint certificates.
The single two-flip exception is exactly the case where both adjacent central
layers are above the uniform level:

```text
a1 > N/5,  a3 > N/5.
```

It has

```text
A = (7/6,7/3,7/3,7/3,7/6),  N=11.
```

Thus the remaining local proof can be split into:

1. an endpoint-rotation case, where one endpoint certificate holds and the
   corresponding endpoint is max-cut balanced; and
2. a central-three-heavy case, where a paired switch must rotate two bad
   5-cycles simultaneously.

## Candidate Lemma

Let `C` be a connected-B maximum cut with minimum Gamma.  Among all such cuts,
choose one minimizing

```text
V(C) = sum_f max(0, R(f) - max_t B_t(f)).
```

Then `V(C)=0`.

More local target:

> If `V(C)>0`, then there is a gamma-preserving switch of one vertex, except
> for one symmetric length-5 pattern where a two-vertex switch is needed, that
> strictly decreases `V`.

This would prove the selected fractional-SPLIT certificate and hence ROWSUM-O.

The proof needs a graph-theoretic reason why every length-5 central overload
admits such a zero-cost rotation.  The switch should be phrased without
reference to the census labels: likely as a prefix/endpoint rotation on a
shortest bad cycle, with a paired switch in the balanced symmetric case.

## Switch Form Seen in the Census

For the seven one-vertex repairs, the switched vertex is an endpoint of the
SPLIT-bad length-5 edge and is max-cut balanced:

```text
d_M(v) = d_B(v) = 1.
```

Switching it preserves the max-cut value and replaces the bad edge `ab` by the
first or last B-edge on the shortest 4-edge B-geodesic from `a` to `b`.  The
new bad edge still has length `5`, so Gamma is unchanged.

The single radius-2 exception has failing bad edge `ab=(0,5)` and path

```text
0 - 10 - 6 - 9 - 5.
```

Here each endpoint has one unit of max-cut slack:

```text
d_B(0)-d_M(0)=1,
d_B(5)-d_M(5)=1.
```

No one-endpoint flip is a max cut.  But there are two tight paired switches:

```text
{0,4} and {1,5}.
```

In each pair, both vertices have one unit of slack and the pair contains a
cut-edge between them.  Switching the pair preserves the cut value.  It rotates
two length-5 bad edges at once and keeps Gamma unchanged.

Thus a more precise local target is:

> If a gamma-min cut has a length-5 SPLIT-bad row, then either one endpoint of
> that bad edge is balanced and its endpoint rotation decreases `V`, or the
> row lies in a symmetric two-edge configuration where a tight cut-edge pair
> switch decreases `V`.

## N=12 Refutation Of Selected-Cut SPLIT

The selected-cut SPLIT theorem is false as stated.  A full `N=12` stress scan
with `_codex_frac_switch_repair_stress.py` found one graph for which every
gamma-min connected-B max cut has at least one fractional-SPLIT-bad row:

```text
graph6 = K??CE@A{?]Fc
gamma-min cuts = 11
SPLIT-good cuts = 0
```

The same scan produced:

```text
bad_cuts=256
bad_rows=325
ell_gt5=38
endpoint_pattern_fail=130
radius_gt2=55
max_min_ham=6
min_ham_hist={1:141, 2:60, 3:25, 4:12, 5:6, 6:1, none:11}
```

So the local `N<=11` repair picture does not generalize:

1. SPLIT-bad rows can have `ell > 5`.
2. Repair distance can exceed `2`.
3. Some rows break the endpoint `d_same=1` pattern.
4. One graph has no SPLIT-good gamma-min cut at all.

This refutes selected-cut SPLIT as a universal certificate.  It does not refute
ROWSUM-O: the listed bad rows on the no-good witness still have `R <= 0`, so the
row-sum inequality survives while this decomposition fails.

## Tight-Cap Descent Refutation

GPT-Pro suggested rescuing selected-SPLIT by proving a tight-cap descent lemma:
for a unique `L=5` central-overload row, one of

```text
W0={v0}, W4={v4}, W01={v0,v1}, W34={v3,v4}
```

that lowers the local row defect should be max-cut tight and support-preserving,
so a lexicographic defect potential descends.

The no-good witness refutes this descent.  In graph

```text
K??CE@A{?]Fc
```

cut `3`

```text
000011111100
```

has two SPLIT-bad rows, both with defect `1/5`:

```text
(2,11): path (2,9,1,8,11), A=(1,11/5,13/5,3,12/5)
(3,11): path (3,9,1,8,11), A=(1,11/5,13/5,3,12/5)
```

For both rows the cap

```text
W34={8,11}
```

is tight:

```text
delta_B(W34)=3, delta_M(W34)=3
```

and lowers the local row defect to `0` in the five-point rotation algebra.
But the actual switched cut

```text
000011110101
```

still has defect vector `(1/5,1/5)`, now on rows

```text
(4,11): path (4,10,6,8,11), A=(1,11/5,13/5,3,12/5)
(5,11): path (5,10,6,8,11), A=(1,11/5,13/5,3,12/5)
```

with the same `Gamma=75`.  Thus the cap is locally defect-lowering for the
distinguished rows but not support-preserving globally; it transports the
defects to new rows.  Lexicographic defect descent fails.
