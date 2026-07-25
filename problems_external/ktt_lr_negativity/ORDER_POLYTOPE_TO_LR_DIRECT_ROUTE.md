# Negative Order Polytope to LR: Direct Route

Status: DEAD; bounded structural audit completed.  See
`NEGATIVE_ORDER_POLYTOPE_LR_TRANSFER_OBSTRUCTION.md`.

## 1. Exact final deliverable

Either an explicit partition triple whose stretched LR polynomial is exactly
the Ehrhart polynomial of the Liu--Tsuchiya order polytope `O(P_{7,7})`, or a
theorem-level dilation-compatible embedding into the homogeneous skew-Kostka
bridge which preserves every lattice point for every dilation.

## 2. Current frontier lemma

Decide whether `O(P_{7,7})` is integrally affinely equivalent to (i) an LR hive
polytope, (ii) a fixed-content skew Gelfand--Tsetlin polytope, or (iii) a face
or direct product of either, with no projection, non-singleton fibre, or
dimension-changing auxiliary variables.

## 3. Explicit logical bridge

The verified value `a_1(O(P_{7,7}))=-3041/1430` is negative.  An integral
affine dilation-compatible bijection, or a direct-product identity with a
factor whose Ehrhart polynomial is identically one, would transfer the entire
Ehrhart polynomial to a stretched skew-Kostka family.  The homogeneous bridge
would then give an explicit LR stretching polynomial with the same negative
coefficient, hence a literal counterexample to full KTT.

## 4. Next falsifiable action

Write the exact inequalities and lattice of `O(P_{7,7})`; compare them with
the order/weight equations of skew tableaux and with the hive/flow structural
invariants.  Test the only natural tableau realization: order-preserving maps
of the two-level poset versus fixed-content SSYT.  Accept only an explicit
integer-affine bijection with singleton fibres and equality for every
dilation.

## 5. Exit condition

Produce the explicit LR triple and two-engine exact polynomial certificate if
the bijection exists.  Otherwise declare

```text
DEAD: negative order-polytope transfer fails -- <exact structural obstruction>.
```

Stop after the first theorem-level invariant excluding all three authorized
realizations; do not replace a failed bijection by an extended formulation or
a bounded rank census.
