# P92: the global one-step hexagon-label charge is false

## Verdict

The natural global injection suggested by P83 does not prove the P84
candidate `T_F<=C_S`.  For a loose triangle `tau` with P83 parameters
`(d,X,Z,R)`, let

\[
 P(\tau)=\{d,d+X,d+Z\}
\]

be its three missing fold labels, and put

\[
 Q(\tau)=\{0,\ \mathord\pm X,\ \mathord\pm Z,\ \mathord\pm R,
 \ \mathord\pm(R+X),\ \mathord\pm(R+Z),\
 \ \mathord\pm(Z-X)\}.
\]

Writing

\[
 \mathcal F_b=\{a+c+b:a+c+h=u+v\text{ is a canonical fold}\},
\]

define the full one-step global neighborhood

\[
 N(\tau)=\mathcal F_b\cap(P(\tau)+Q(\tau)).             \tag{1}
\]

Every member of `N(tau)` is a canonical fold label and hence a missing
positive-difference label.  Nevertheless, the family `(N(tau))` need not
have a system of distinct representatives.  There is an exact
positive-defect literal-hole row containing eight loose triangles whose
neighborhood union in (1) has only seven labels.

## Exact counterexample

Take the 138-element set `B` embedded in
`compute/p92/verify_hexagon_hall_counterexample.py`, with

\[
 h=28410,\qquad b=1,\qquad \max B=h-1.
\]

The SHA-256 of its comma-separated mark list, with no spaces, is

```text
60adf8b413d5ff178059e8b173b75b1b5123f8d4101fe9ee5cda33b8006f1152
```

Exact enumeration gives

\[
 |B+B|=9591={138\cdot139\over2},\qquad
 |\Delta^+(B)|=9453={138\cdot137\over2},               \tag{2}
\]

with every unordered sum and every positive difference represented once.
Moreover,

\[
 \Delta^+(B)\cap(B+B+1)=\varnothing,
 \qquad
 \delta={3\cdot138^2-138+2\over2}-28410=88>0.          \tag{3}
\]

The row has

\[
 C_S=48,\qquad T_F=11.                                 \tag{4}
\]

Among its loose triangles, select the following eight.  Each row lists the
shared triple `(a,c,u)`, then `(X,Z,R)`, then `P(tau)`:

```text
(11504,12669,25686)  ( 136, 1051,-1097)  (24174,24310,25225)
(11504,12736,24589)  ( 136,  -67, 1187)  (24241,24377,24174)
(11504,12736,25686)  ( 898,  984,   90)  (24241,25139,25225)
(11504,13720,25776)  ( 136, -984,  -90)  (25225,25361,24241)
(11640,12669,24589)  (-136,   67, 1097)  (24310,24174,24377)
(11640,12736,25686)  ( 762,  -67,-1097)  (24377,25139,24310)
(11640,12736,25776)  (-136,  984,-1187)  (24377,24241,25361)
(11640,13720,25686)  (-136,-1051,   90)  (25361,25225,24310)
```

Computing (1) against all 48 canonical fold labels gives exactly

\[
 \bigcup_{\tau\text{ in the table}}N(\tau)
 =\{24174,24241,24310,24377,25139,25225,25361\}.        \tag{5}
\]

Thus these eight triangles have only seven available targets.  Hall's
condition fails, so no injection can assign every loose triangle to a
distinct canonical fold label using any of the three P83 phase labels and
one arbitrary signed step from the entire represented hexagon.

## Verification and claim boundary

Run

```powershell
python -B problems/864/compute/p92/verify_hexagon_hall_counterexample.py
```

The standalone integer verifier reconstructs (2)--(5), all 48 folds and all
11 loose triangles.  It prints

```text
{'p': 138, 'h': 28410, 'b': 1, 'delta': 88,
 'C_S': 48, 'T_F': 11, 'Hall_left': 8, 'Hall_neighbors': 7}
```

The broader exact scan in `compute/p92/c84_translation_scan.json` checked
all 313,863 admissible positive-defect translations from P86.  It found two
failures of the charge (1), but no row with `T_F>C_S`.  Therefore this note
falsifies the global one-step hexagon-label injection, not C84 itself.
