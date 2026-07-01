# RIGID-5/7 Terminal-Theta Proof Atom

This note isolates the common geometric atom now appearing in all exact gates:

```text
cap deficient positive core,
row residual singleton miss,
restricted positive-overload lens at R[v]<0.
```

The finite gates no longer point to a scalar Hall inequality.  They point to a
single shortest-geodesic fact: the only relevant terminal obstruction is a
5/7 theta, and any attempt to create a larger or doubled obstruction gives a
triangle, a shorter B-geodesic, or a stage-0 rare-cost exchange.

## Verified finite shadows

### Row REX full containment

Gate:

```text
python problems/23/writeup/_codex_rex_theta_gate.py \
  --min-n 5 --max-n 10 --h2-allmax --h-inherited 4 --max-add 1
```

Result:

```text
tested=182
misses=72
ell_hist={7:72}
strong_f0_theta=72
fail=0
window_pos_hist={1:32,2:40}
```

Claude independently mirrored this in `witness_structure`:

```text
switches=119
singleton misses=86
ell(f)=7 for all misses
nested_ok=86
nested_fail=0
```

Normal form:

```text
short edge g in F0, ell(g)=5, Q=(q0,q1,q2,q3,q4) in cyc[g],
long edge  f in F1, ell(f)=7, and Q is a contiguous length-5 window in
P in cyc[f].
```

Thus the row singleton miss is a full length-5 row plus two extra B-edges
distributed at the terminals of the long row.  In the selected orientation the
observed window positions are `1` and `2`; up to reversing the long row, this
means either:

```text
centered type:    P=(a,q0,q1,q2,q3,q4,b),
terminal type:    P=(a,b,q0,q1,q2,q3,q4).
```

The proof should use only the invariant statement "full length-5 row is a
contiguous window of the length-7 row", not the stronger centered-only form.

### Cap deficient one-ended containment

Gate:

```text
python problems/23/writeup/_codex_defcap_theta_gate.py \
  --min-n 5 --max-n 10 --glued-c5
```

Result:

```text
defcap=736
positive=736
baggage=640
theta=736
theta_sig={(5,7,'trim_left',5,7):736}
fail=0
```

Normal form:

```text
short edge g, ell(g)=5, Q=(q0,q1,q2,q3,q4) in cyc[g],
long edge  h, ell(h)=7, P=(a,q1,q2,q3,q4,b,c) in cyc[h],
```

up to reversal.  The long row contains the short row after one terminal
endpoint is removed.  In the canonical atom:

```text
Q=(0,6,9,3,8)
P=(1,6,9,3,8,2,7)
```

The cap proof must therefore not use the false stronger statement that `P`
contains all of `Q`.

### Restricted positive-overload lens

Gate:

```text
python problems/23/writeup/_codex_restricted_lens_mine.py \
  --min-n 5 --max-n 10 --h-blowups 3
```

Result:

```text
positive entries at R<0 vertices=222
all have ell(g)=5 and longer enclosing lengths=(7,)
```

The broad statement `C_g(v)>0 => lens` is false on the `MycGrotzsch_N23`
stress cut.  Every use of this lens must keep the `R[v]<0` or selected
terminal-shadow hypothesis.

## Common terminology

Let `B` be the cut graph and `M` the bad-edge set.  A row of a bad edge `f=xy`
is a shortest `B`-path between `x` and `y`; it has `ell(f)` vertices and
`ell(f)-1` B-edges.

A `5/7 terminal theta` is a pair of bad edges `(g,h)` with rows `Q in cyc[g]`
and `P in cyc[h]` such that:

```text
ell(g)=5, ell(h)=7,
```

and either:

```text
full type:      Q is a contiguous subpath of P;
one-ended type: Q without one endpoint is a contiguous subpath of P.
```

The row-side REX atom uses the full type.  The cap-side deficient core uses the
one-ended type.

## Candidate rigidity lemma

```text
RIGID-5/7.
Let S be a neutral terminal-shadow switch selected at a vertex v with R[v]<0,
after the stage-0 minimum-rare-cost matching.

Every relevant terminal obstruction is a disjoint sum of:
  A. pure odd-cycle baggage components, each with one bad edge and Psi=0;
  B. 5/7 terminal theta components of the full or one-ended type above.

Moreover, two distinct 5/7 terminal annuli cannot occur for the same residual
row in one co-witness component.  If they do, then either:
  1. the annuli cross, producing a triangle or a B-geodesic shorter by at
     least two edges for one involved bad edge; or
  2. the annuli are separated, producing a negative stage-0 rare-cost
     alternating exchange.
```

This single lemma implies:

```text
cap side:
  deficient cap => type A/B component decomposition
  => R_full = R_local + (N-|V_component|)T >= 0
  => no deficient cap in an R[v]<0 selected switch
  => strict side-cap expansion.

row side:
  two residual misses => two terminal 5/7 annuli
  => crossing shortcut or rare exchange
  => component-local single-miss theorem.
```

## Proof subclaims to formalize

### S1. Shortest-row splice principle

The safe form is local to a fixed bad edge.  Let

```text
P=(p0,...,p_{L-1}) in cyc[h]
```

be a shortest B-row for the bad edge `h=p0 p_{L-1}`.  If `0<=i<j<=L-1`,
then the segment

```text
P[i,j]=(p_i,...,p_j)
```

is a shortest B-path between `p_i` and `p_j`.  Otherwise replacing that segment
by a shorter B-path gives a shorter B-row for `h`.

This is the only automatic splice fact.  It does **not** say that arbitrary
ears from two different bad edges are globally shortest after endpoints are
changed.  That broader reading is exactly where the false unrestricted lens
claims enter.

The useful two-row corollary is:

```text
Let P in cyc[h] and Q in cyc[g].  Suppose they meet in two vertices a,b and
the P-segment P[a,b] and Q-segment Q[a,b] are internally vertex-disjoint.
Then |P[a,b]| = |Q[a,b]| unless one of g,h has a shorter B-row.
```

Here `|.|` means number of B-edges in the segment.  If `|Q[a,b]|<|P[a,b]|`,
splice the Q-segment into P to shorten `h`; if `|P[a,b]|<|Q[a,b]|`, splice the
P-segment into Q to shorten `g`.

Consequences:

```text
1. two rows cannot enter, leave, and re-enter the same corridor with unequal
   intervening segment lengths;
2. non-laminar terminal annuli create a reduced equal-length theta unless a
   shorter row already exists;
3. every strict diagonal in that reduced theta gives the TH-long shortcut
   certificate.
```

Triangle-freeness is used to rule out the degenerate two-edge replacement that
would close a triangle with a bad edge.

The remaining work in S3 is to show that two crossing REX annuli always
produce a strict diagonal, not merely an equal-length alternate row.  This
strictness is where terminal-shadow orientation and the two slack endpoints
enter.

### S2. Excess annulus descent

In a neutral terminal-shadow switch, suppose a long row contains a short row
or one-ended short core with excess more than two B-edges.

Then the terminal prefix/suffix switch around the excess annulus is neutral or
can be made neutral by the same stage-0 exit exchange, and the new bad edge is
priced by the shorter row.  The deleted square length exceeds the created
square length, giving a Gamma descent.

This is the step that should specialize `L/(L+2)` shadows to actual `5/7`
under the selected `R[v]<0` hypotheses.  The exact gates have found no
realized `7/9`, `9/11`, ... core.

### S3. Crossing-annulus shortcut

For row REX, assume one residual row `f` has two singleton misses.  By the
`REX-Theta` gate, each miss gives:

```text
P_f = a_i + Q_i + b_i
```

where `Q_i` is a length-5 row of an `F0` edge.

If the two annuli overlap non-laminarily along `P_f`, then the endpoints of
the two short rows and the long row form a reduced theta.  Splicing the two
short corridors across the overlap gives either:

```text
a triangle in G, or
a B-path for f or one of the F0 edges shorter by at least two B-edges.
```

This is the `TH-long` certificate checked by `_codex_th_corridor_gate.py` when
a long-lambda endpoint exists.

### S4. Separated-annulus rare exchange

If the two singleton-miss annuli of one residual row are laminar/separated,
then their missed exits lie in two minimum-lambda side blocks of the same
residual co-witness component.

Let `c(e)=deg_F1(e)` for `E0` exits.  Stage 0 chose a matching
`mu:F0 -> E0` minimizing

```text
sum_{h in F0} c(mu(h)).
```

The separated annuli force an alternating path from one missed `E0` exit to a
matched `E0` exit of strictly larger `c`.  Replacing along this path lowers the
stage-0 cost, contradiction.

This is the `TH-rare` certificate.

## Exact acceptance gate for any proposed proof

A proof of `RIGID-5/7` should be accepted only if Claude can mirror all of:

```text
1. Row REX full-theta:
   every singleton miss has ell(f)=7 and contains a full ell=5 F0 row.

2. Cap deficient one-ended theta:
   every positive deficient component has ell=(5,7) and contains a
   one-ended ell=5 core in an ell=7 row.

3. TH-long:
   every hypothetical long-endpoint two-hole corridor has the disk shortcut
   certificate.

4. TH-rare:
   every hypothetical minimum-endpoint two-hole corridor has the rare-cost
   alternating exchange certificate.
```

The first two are already exact-verified.  The last two are the remaining
mathematical subclaims; in the current finite battery no two-hole corridor
exists, so they are proof obligations rather than observed certificates.
