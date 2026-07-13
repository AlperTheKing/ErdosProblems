# P97: global phase charge and the residual-interval frontier

## Verdict

The componentwise inequality is not proved here.  In fact, its natural
collision-corrected extension is false componentwise, so the surviving proof
target is necessarily global.

This note gives an exact reduction of the corrected target

\[
 T_F\le C_S+V_b,\qquad
 V_b=\#\{(a,c,u,v)\in\mathcal F:a+c+b\in\Delta^+(B)\},              \tag{1}
\]

to a one-dimensional residual-interval matching statement.  The matching is
strictly stronger than (1).  It has zero failures on all 1,583,738
unrestricted width-30 rows and all 4,170 positive-defect translations of the
P88 counterexample.  It also has zero failures on the 779,086 literal-hole
rows underlying P84/P94/P96.

No proof of the required Hall window inequality is obtained.  Thus (1), C84,
and the requested componentwise hole theorem remain candidates, not lemmas.

## 1. Complementary intervals and the load-bearing phase

Every canonical fold

\[
 F=(a,c,u,v),\qquad a\le c<u\le v,\qquad a+c+h=u+v,                 \tag{2}
\]

is a nested complementary pair

\[
 [c,u]\subset[a,v],\qquad (u-c)+(v-a)=h.                           \tag{3}
\]

The pure ordered version is false.  P88 gives an endpoint Sidon set with

\[
 (p,h,C_S,T_F)=(60,3286,182,200),                                  \tag{4}
\]

and one component containing 165 folds and 200 loose triangles.  It fails
both literal holes.  Therefore neither nesting, order, nor the three
injective Sidon arm maps alone can prove C84.

For a fold define its low phase label and residual endpoints by

\[
 q_F=a+c+b,\qquad L_F=h-b-v,\qquad U_F=h-b-u.                       \tag{5}
\]

Then

\[
 q_F+L_F=u,\qquad q_F+U_F=v.                                       \tag{6}
\]

Hence `q_F` is a represented positive difference exactly when translating
some mark of `B` by `q_F` reaches another mark.  The literal hole
`Delta+(B) cap (B+B+b)=empty` gives `V_b=0`.

P101's exact audits show no failure of (1), but its componentwise form fails
twice.  Thus collision capacity can be exported between loose-triangle
components; a component-local proof cannot establish the corrected theorem.

## 2. Residual interval attached to every shadow triangle

The canonical and loose shadow triangles are the triples `(a,c,u)` counted
by

\[
 C_S+T_F=\sum_{a,c,u}M_{AC}(a,c)M_{AU}(a,u)M_{CU}(c,u).             \tag{7}
\]

Attach to every such triple

\[
 \tau=u-a-c-b,\qquad \lambda=h-b-u,
 \qquad I(a,c,u)=[\min(\tau,\lambda),\max(\tau,\lambda)].         \tag{8}
\]

For a canonical triple belonging to `F`, (8) is exactly

\[
 I(F)=[\min(L_F,U_F),\max(L_F,U_F)].                               \tag{9}
\]

For a loose triangle in the P83 normal form

\[
\begin{array}{lll}
F_0=(a,c,u+R,s),&F_Z=(a,c+Z,u,s+R+Z),
&F_X=(a+X,c,u,s+R+X),
\end{array}                                                        \tag{10}
\]

the six supporting residual endpoints are exactly

\[
\begin{array}{c|cc}
 &L&U\\ \hline
F_0&\tau+R&\lambda-R\\
F_Z&\tau-Z&\lambda\\
F_X&\tau-X&\lambda.
\end{array}                                                        \tag{11}
\]

In particular, the two arm folds have the common endpoint `lambda`.  The
base residual interval is concentric with the loose interval:

\[
 (\tau+R)+(\lambda-R)=\tau+\lambda.                               \tag{12}
\]

After taking endpoint hulls, the base and loose residual intervals are nested
because they have the same midpoint.  Their relative radii are
`|lambda-tau-2R|/2` and `|lambda-tau|/2`.  Equations (11)-(12) retain order,
phase, and all three arm maps.

## 3. Stronger residual-interval matching candidate

Create two distinguishable slots at every fold, located at `L_F` and `U_F`.
If `q_F in Delta+(B)`, create one additional slot at `L_F`.  Duplicating
`U_F` instead also passes the individually tested hard rows, but the complete
audit below uses `L_F`.

### Residual matching statement (RM97)

The `C_S+T_F` intervals in (8) can be matched injectively to these
`2C_S+V_b` slots, with every interval matched to a slot it contains.

RM97 immediately implies

\[
 C_S+T_F\le2C_S+V_b,
\]

which is exactly (1).  Under the literal hole it gives `T_F<=C_S`, and P82.2
then forces `C_S=o(p^2)`.

Because intervals and slots lie on a line, the standard earliest-deadline
greedy algorithm is exact.  Equivalently, Hall's condition reduces to the
single family of window inequalities

\[
 \#\{(a,c,u):I(a,c,u)\subseteq J\}
 \le
 \#\{F:L_F\in J\}+\#\{F:U_F\in J\}
 +\#\{F:q_F\in\Delta^+(B),\ L_F\in J\}                            \tag{13}
\]

for every real interval `J`.  Equation (13) is the exact remaining proof
obligation.  It is global: canonical intervals crossing the boundary of `J`
contribute endpoint slots even when their folds lie in different
loose-triangle components or color thresholds.

## 4. Exact tests

The integer-only audits in `compute/p97/` give:

* RM97: zero failures on 1,583,738 unrestricted width-30 rows; 6,132 rows
  contain at least one loose triangle.
* RM97: zero failures on all 4,170 positive-defect P88 translations.
* The zero-collision phase-hull precursor: zero failures on 464,981
  width-30 literal holes, 313,863 archived translation holes, and 242
  insertion holes.
* The P94 tight row matches all 258 canonical-plus-loose intervals into 284
  residual endpoint slots; P75 matches all 76 into 102 slots.
* At P88 `(gamma,b)=(41,2)`, phase-hull matching fails by five, while RM97
  matches all `C_S+T_F=413` intervals into `2C_S+V_b=425` slots.

Run

```powershell
python -B problems/864/compute/p97/audit_residual_interval_matching.py `
  --output problems/864/compute/p97/residual_interval_matching.json
python -B problems/864/compute/p97/audit_phase_interval_matching_w30.py `
  --max-width 30
python -B problems/864/compute/p97/audit_phase_interval_matching_archived.py `
  --workers 16 `
  --output problems/864/compute/p97/phase_interval_matching_archived.json
```

These are finite verifications, not a proof of (13).

## 5. Falsified shortcuts and remaining frontier

The following stronger routes are false on exact rows:

* pure ordered complementary-interval sparsity: P88 has component excess 35;
* matching each triangle to a supporting fold: P95 has a `72` versus `61`
  Hall witness;
* one signed hexagon step: P92 has an `8` versus `7` Hall witness;
* degree-one peeling: the P94 tight component has a 75-edge, 64-vertex
  two-core;
* inner-length or phase-label pair selection: all 729 order-equivariant
  support-pair rules fail on the hard archived rows;
* corrected phase-hull matching: P88 at `(gamma,b)=(41,2)` leaves five
  unmatched triangles despite positive total corrected slack;
* matching only to residual endpoints, or reserving one fixed residual side
  for canonical folds: P75 and the P94 tight row are exact counterexamples.

The highest-leverage open lemma is therefore (13).  A proof must use the
concentric base relation (12) to transfer Hall deficit across interval
boundaries, and must show that a globally closed transfer consumes one of the
extra slots indexed by `q_F in Delta+(B)`.  When the literal hole holds no
such closure slot exists, so the transfer must terminate at an ordinary fold
endpoint.  No valid closure invariant establishing this statement is proved
here.
