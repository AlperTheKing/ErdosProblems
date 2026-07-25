# Actual hive wall crossing: exact Ehrhart jump and obstruction

Date: 2026-07-22

Status: **DEAD for coefficientwise-positive actual-volume propagation across a
support-number flip.**  This is not a counterexample to KTT and not a
counterexample to GHTE.

## 1. Exact local question and answer

The proposed local lemma was the following: after reducing an actual hive
support-number wall to its primitive circuit in the saturated intrinsic
lattice, express the Ehrhart-coefficient change as a nonnegative contribution
of the flipped cell and its link.  Such a formula would propagate ordinary
monomial-coefficient positivity across adjacent hive chambers without needing
full GHTE.

This lemma is false, already for an actual full-dimensional side-four hive
with trivial link and a primitive unimodular `2<->2` circuit.  On the side
where `r=-Omega>0`, the exact chamber-polynomial jump is

```text
binomial(r*n+1,3) = (r^3/6)*n^3 - (r/6)*n.            (1)
```

It is nonnegative as a function on nonnegative integers `n`, but its ordinary
linear coefficient is negative.  Thus even the cleanest possible flipped
cell is not coefficientwise effective.

## 2. The actual hive wall and its intrinsic lattices

The two integral side-four triples found by the exact cddlib wall gate are

```text
L = ((11,3,1,0), (13,6,2,0), (16,12,7,1)),
R = ((14,3,2,0), (12,5,3,0), (22,8,7,2)).
```

Both hive polytopes have intrinsic dimension three.  In the standard three
interior hive coordinates their saturated tangent and dual lattices are

```text
M = Z^3,                 N = Hom(M,Z) = Z^3.          (2)
```

The wall occurs at the midpoint.  To keep all boundary data integral, put

```text
W = L+R
  = ((25,6,3,0), (25,11,5,0), (38,20,14,3)),

D = R-L
  = ((3,0,1,0), (-1,-1,1,0), (6,-4,0,1)),

H(z) = W+zD.                                             (3)
```

Thus `H(-1)=2L`, `H(0)=W`, and `H(1)=2R`.  For rational
`z=sign/m`, the integral triple `mH(z)=mW+sign*D` gives an exact
denominator-cleared sample of the same support line.

The four changing primitive outer normals, in their exact sorted order, are

```text
a=(-1,1,0),  b=(0,0,-1),  c=(0,1,0),  d=(1,0,-1),
a-b-c+d=0.                                                (4)
```

Deleting `a,b,c,d` in turn gives determinants

```text
(1,1,-1,-1).                                             (5)
```

Consequently the circuit is primitive and every circuit basis is unimodular;
there is no quotient-lattice multiplicity hidden in (1).  The link is a
point, with lattice enumerator one.

For the four normals `(a,b,c,d)`, the support vectors at `L` and `R` are

```text
h_L=(3,-33,28,-7),       h_R=(3,-34,31,-7).
```

The translation-invariant circuit parameter is

```text
Omega(h)=h_a-h_b-h_c+h_d.
```

It has values `Omega(L)=1`, `Omega(R)=-1`, and along (3)

```text
Omega(H(z))=-2z.                                         (6)
```

At the wall the unique nonsimple vertex is tight on `a,b,c,d`.  The changed
maximal normal cones are exactly

```text
Omega>0:  abc, bcd;
Omega<0:  abd, acd.                                     (7)
```

This is an actual support-number bistellar `2<->2` wall, not an abstract fan
model.

## 3. All Ehrhart coefficients on the support line

For a fixed chamber, write

```text
E_z(n)=e_0(z)+e_1(z)n+e_2(z)n^2+e_3(z)n^3.
```

For rational `z`, `e_j(z)` means the homogeneous local
Euler--Maclaurin coefficient, equivalently

```text
e_j(z)=m^(-j) [n^j] L_(mH(z))(n)
```

after integral denominator clearing.  Exact interpolation gives

```text
z<0 (the L chamber):
e_0^-(z) = 1,
e_1^-(z) = 13/2 + z/6,
e_2^-(z) = 27/2 - (3/2)z^2,
e_3^-(z) = 9 - 3z^2 - (2/3)z^3;

z>0 (the R chamber):
e_0^+(z) = 1,
e_1^+(z) = 13/2 - z/6,
e_2^+(z) = 27/2 - (3/2)z^2,
e_3^+(z) = 9 - 3z^2 + (2/3)z^3.                       (8)
```

The wall itself has

```text
L_W(n)=1+(13/2)n+(27/2)n^2+9n^3.                      (9)
```

In particular, the actual coefficient functions on the two sides are

```text
e_1(z)=13/2-|z|/6,
e_2(z)=27/2-(3/2)z^2,
e_3(z)=9-3z^2+(2/3)|z|^3.                             (10)
```

Moving away from the wall therefore decreases the linear and quadratic
coefficients.  Positivity at the wall is not propagated by adding a
coefficientwise-nonnegative local piece.

For clarity, the two integral endpoints themselves are still positive and
even Ehrhart-equivalent:

```text
L_(2L)(n)=L_(2R)(n)
          =1+(19/3)n+12n^2+(20/3)n^3.                 (11)
```

There is no KTT counterexample here.

## 4. The exact branch jump and the all-q sign table

Extend each polynomial in (8) across the wall algebraically and compare them
at the same support `H(z)`.  The right extension minus the left extension is

```text
E_z^+(n)-E_z^-(n)
  = (4/3)z^3 n^3 - (1/3)z n
  = (-Omega^3 n^3 + Omega n)/6.                       (12)
```

On the right side, `r=-Omega=2z>0`, and (12) is exactly (1).  In the GHTE
indexing, where `q` pairs with `n^(3-q)`, every degree is therefore:

| `q` | Ehrhart degree | right-minus-left branch jump |
|---:|---:|---:|
| 0 | `n^3` | `r^3/6 > 0` |
| 1 | `n^2` | `0` |
| 2 | `n^1` | `-r/6 < 0` |
| 3 | `n^0` | `0` |

The signs are mixed in the saturated intrinsic lattice even though all four
circuit bases have determinant one.

## 5. Why the formulas are exact

1. `ghte_find_r4_wall_pair.py` reconstructs both complete fans with cddlib
   over GMP rationals.  It verifies the unique four-tight wall vertex, the
   wall scale two, the primitive circuit (4), the two fan signatures (7), and
   `Omega(L)=1`, `Omega(R)=-1`.
2. On a fixed normal fan, local Euler--Maclaurin makes `e_j` a homogeneous
   polynomial of degree `j` in the support numbers.  Hence its restriction to
   (3) has degree at most `j`.
3. Two independent exact Ehrhart paths agree on every sample: direct lattice
   enumeration and interpolation in `r4_reeve/hive4.py`, and saturated
   cone triangulation with half-open fundamental boxes in `engineC/ehr.py`.
   Every sampled polytope has vertex denominator one in `M=Z^3`, and both
   paths also check held-out dilations of every stretching polynomial.
4. The samples `m=1,...,j+1` uniquely determine the degree-`j` polynomial in
   (8).  Samples `m=5,6`, unused by every degree-at-most-three interpolation,
   match (8) exactly.  Every sample also has the exact endpoint fan signature.
5. Subtracting the two uniquely determined branch polynomials gives (12),
   and the binomial identity (1) is immediate.

Replay:

```text
python problems_external/ktt_lr_negativity/actual_hive_wall_ehrhart_obstruction.py
```

The expected terminal line is `PASS`.

The general partition-function wall-crossing framework, including the fact
that discrete wall jumps are obtained from a local residue rather than the
Ehrhart polynomial of a closed lattice polytope, is consistent with
Boysal--Vergne, *Paradan's wall crossing formula for partition functions and
Khovanskii--Pukhlikov differential operator*, arXiv:0803.2810.

## 6. Direct-route decision

The requested rank-uniform bridge cannot be:

```text
wall-positive coefficient vector
  + coefficientwise-nonnegative flipped-cell/link vector
  = adjacent-chamber-positive coefficient vector.
```

Equation (1) has negative linear coefficient with a point link.  Moreover, if
a proposed higher-dimensional factorization merely multiplies (1) by a link
Ehrhart polynomial `L_K(n)`, then `L_K(0)=1` leaves the coefficient of `n`
equal to `-r/6`; a nonnegative link does not repair it.  Any viable
wall-crossing proof must supply an additional global inequality or
cancellation that dominates this negative local linear term.  The vanishing
circuit parameter, flipped cell, intrinsic indices, and link alone do not do
so.

The exact exit record is

```text
DEAD: actual-volume coefficientwise wall propagation -- the primitive
unimodular hive flip has jump binomial((-Omega)n+1,3), with negative linear
coefficient Omega/6 on the Omega<0 side.
```

This kills only the proposed actual-face-volume propagation lemma.  It does
not kill GHTE, a more global hive-specific wall transport, or KTT itself.
