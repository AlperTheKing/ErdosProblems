# P108: upper-slot sweep reduction and the budgeted color-cycle frontier

## Verdict

RM97 is not proved here.  This sidecar gives an independent reduction that
does not use the P106 root-locality mechanism.

There are three proved outputs.

1. RM97 follows from a strictly simpler matching: match only the loose
   intervals to the upper residual slots, while every canonical interval uses
   its own lower slot.
2. The upper-slot Hall inequalities are exactly color-window inequalities in
   the same-color arm graphs.
3. Every directed arm cycle satisfies an exact integer cancellation identity.

The strongest surviving global target exposed by these facts is

\[
 \boxed{
 \sum_u (t_u-n_u)_+
 \le p+V_b+(-\delta)_+ .
 }
 \tag{BC108}
\]

Here `n_u` is the number of folds whose lower high endpoint is `u`, and
`t_u` is the number of loose triangles with shared high endpoint `u`.
In the live positive-defect literal-hole regime, `V_b=0` and `delta>0`, so
BC108 gives

\[
 T_F=\sum_u t_u\le \sum_u n_u+p=C_S+p.               \tag{1}
\]

This already closes the P82 removal step: if `C_S>=epsilon*p^2`, P82.2 gives
`T_F>=eta(epsilon)*p^3`, whereas (1) and
`C_S<=p(p+1)/2` give `T_F=O(p^2)`.

BC108 is exact-tested but unproved.  It is substantially weaker than RM97
and than `T_F<=C_S`; it is the sharp reduced missing inequality from P108.

## 1. Residual coordinates

Put `H=h-b`.  For a canonical fold

\[
 F=(a,c,u,v),\qquad a+c+h=u+v,qquad a\le c<u\le v,
\]

write

\[
 q_F=a+c+b,\qquad L_F=H-v=u-q_F,\qquad U_F=H-u=v-q_F. \tag{2}
\]

Thus its residual interval is `[L_F,U_F]`, and its two distinguishable RM97
slots are at `L_F` and `U_F`.

For a loose triangle with shared shadow coordinates `(a,c,u)`, put

\[
 q=a+c+b,\qquad \tau=u-q,\qquad \lambda=H-u.          \tag{3}
\]

Its residual interval is the hull of `tau` and `lambda`.

### Lemma P108.1 (lower-slot reservation)

If the loose residual intervals can be matched injectively to the multiset
of upper slots `\{U_F:F\in\mathcal F\}`, with every matched upper slot lying
in its interval, then RM97 holds and `T_F<=C_S`.

### Proof

Match every canonical interval to its own distinguishable lower slot `L_F`.
Match the loose intervals by the assumed upper-slot matching.  Lower and
upper slots are distinct copies even when `L_F=U_F`, so the union is an
injective RM97 matching.  The upper-slot matching itself gives
`T_F<=C_S`.  QED.

This is stronger than needed asymptotically, but its Hall form reveals the
correct cycle object.

## 2. Exact color-window form

For a loose triangle define its missing reflected high endpoint

\[
 w_T:=H+q-u=a+c+h-u.                                  \tag{4}
\]

The point `w_T` is not in `B`; otherwise `(a,c,u,w_T)` would be the fold
supporting all three shadow edges, contradicting looseness and the injective
two-coordinate projections.

Let `K` be an integer interval.  Under the affine reversal
`K=H-J`, equations (3)-(4) give

\[
 \lambda\in J\iff u\in K,
 \qquad
 \tau\in J\iff w_T\in K.                             \tag{5}
\]

Also `U_F in J` iff `u_F in K`.  Consequently the upper-slot Hall theorem is
equivalent to

\[
 \boxed{
 \#\{T:u_T\in K,\ w_T\in K\}
 \le
 \#\{F:u_F\in K\}
 \quad\hbox{for every interval }K.}
 \tag{UW108}
\]

This equivalence is exact; no asymptotic or hole hypothesis is used.

The mandatory exact gate has zero UW108 failures on P75, P94, and P98.  It
fails by `13` on the negative-defect P105 witness and by `34` on each phase
of the positive-defect non-hole P88 witness.  Thus both the literal phase and
the endpoint budget are load-bearing.

## 3. The arm graphs and cycle cancellation

Fix `u`.  List the folds of color `u` as

\[
 F_i=(a_i,c_i,u,v_i),\qquad
 v_i=a_i+c_i+h-u.                                     \tag{6}
\]

Make a directed graph `G_u` on these folds.  A loose triangle gives the arc
`i -> j` when its `AU` arm is `F_i`, its `CU` arm is `F_j`, and its base
fold has low pair `(a_i,c_j)`.  Put

\[
 w_{ij}=a_i+c_j+h-u.                                  \tag{7}
\]

This is exactly the missing endpoint (4) of that loose triangle.

### Lemma P108.2 (directed cycle cancellation)

For every directed cycle

\[
 i_1\to i_2\to\cdots\to i_k\to i_1
\]

in `G_u`, with indices read cyclically,

\[
 \boxed{\sum_{r=1}^k w_{i_r i_{r+1}}
       =\sum_{r=1}^k v_{i_r}.}                        \tag{8}
\]

### Proof

Using (6)-(7),

\[
 \sum_r w_{i_ri_{r+1}}
 =\sum_r(a_{i_r}+c_{i_{r+1}}+h-u)
 =\sum_r(a_{i_r}+c_{i_r}+h-u)
 =\sum_rv_{i_r}.
\]

The middle equality is the cyclic permutation of the `c`-indices.  QED.

The cancellation retains the literal order.  If all arc endpoints selected
by a color window lie in `K`, then every cycle has all `u,w_{ij}` in `K`.
For example, choosing a vertex with minimum `c_i` shows that the outgoing
cycle endpoint satisfies `v_i<=w_{ij}`; since `v_i>=u`, at least one
diagonal partner `v_i` also lies in `K`.  What remains unproved is a global
bounded-multiplicity charge of independent cycle excess to these marks, to
phase-collided fold labels, or to negative endpoint defect.  BC108 states
exactly the required aggregate charge.

## 4. Why BC108 is sufficient

Let

\[
 n_u=|V(G_u)|,\qquad t_u=|E(G_u)|.
\]

Every fold has one color and every loose triangle has one shared color, so

\[
 C_S=\sum_un_u,\qquad T_F=\sum_ut_u.                  \tag{9}
\]

Since `t_u<=n_u+(t_u-n_u)_+`, BC108 and (9) give

\[
 T_F\le C_S+p+V_b+(-\delta)_+.                       \tag{10}
\]

Under the literal hole, `V_b=0`.  Under positive defect, `(-delta)_+=0`.
Equation (10) then gives (1), and P82.2 yields `C_S=o(p^2)` as explained in
the verdict.  Thus BC108 is not another theorem-strength restatement of
RM97: it permits linear slack, drops every interval window, and asks only
for the total positive cycle excess.

## 5. Exact falsifiers to stronger shortcuts

### 5.1 Min-side saturation is false

The claim that the RM97 interval graph always matches its smaller side is
false.  Take

```text
B={0,22,24,137,146,172,173,201,258,273,306,365,369},
h=370, b=1.
```

This is endpoint-normalized and integer Sidon, with

```text
p=13, delta=-122, C_S=7, T_F=8, V_b=3,
intervals=15, slots=17, maximum matching=14.
```

The deficient window `[28,168]` contains ten intervals but nine slots.  The
row is not a literal hole.  Its parity lift `B -> 2B+1, h -> 2h, b=1` is a
literal hole with `delta=-492`; it has 15 intervals, 14 slots, matching 14.
This shows that the endpoint budget cannot be omitted.

### 5.2 Literal-hole planarity alone is false

The undirected arm graph of the P88 row at color `u=2173` has eight vertices,
sixteen simple edges, and a Kuratowski subdivision; it is nonplanar.  P88 has
positive defect but fails the literal hole.

The parity lift

\[
 B\mapsto2B+1,\qquad h\mapsto2h,qquad b=1
\]

preserves all folds, triangles, and arm graphs and makes the literal hole
automatic.  It has `delta=-1201`, and the corresponding graph at color
`4347` remains nonplanar.  Hence neither positive defect nor the literal
hole separately forces planar arm graphs.  The conjunction remains
exact-clean, but planarity is stronger than BC108 and is not claimed.

### 5.3 The two correction banks are both necessary in the current data

For original P88,

```text
positive color excess=69, p=60, V_1=77, delta=2085.
```

Thus the mark budget alone fails by nine, while the collision bank pays.
For its parity lift,

```text
positive color excess=69, p=60, V_1=0, delta=-1201.
```

Now the literal hole removes the collision bank, while the negative-defect
bank pays.  In the live conjunction both banks vanish and BC108 gives the
linear error required by (1).

## 6. Exact gates

All combinatorial acceptance arithmetic is integer-exact.

* `audit_sweep_saturation.py` checks P75, P94, P98, P105, both P88 phases,
  and the P88 parity lift.  It also checks 1,857,024 unrestricted
  width-30/translation phases.  BC108 has zero failures there.
* `audit_upper_matching_positive_holes.py` exhausts all 919,484
  positive-defect width-30 candidates.  Among the 464,981 literal holes,
  1,037 have a loose triangle; UW108 has zero failures.
* `audit_defect_budget_domains.py` checks 523,672 phases from every normalized
  orientation of every subset of the P98 17-mark parent, including 234,890
  literal holes.  It also checks all 261,836 parity lifts.  The quantitative
  RM, upper-slot, and BC108 defect budgets have zero failures.
* `verify_sweep_identities.py` checks every endpoint window on all mandatory
  rows.  It verifies the exact full-window identity

  \[
  D(J)=T_F-C_S-V_b+C_{\rm avoid}(J)+V_{\rm out}(J)
       -T_{\rm escape}(J),                             \tag{11}
  \]

  and the color-window equivalence (5), with zero identity failures.
* `audit_arm_planarity.py` constructs every mandatory arm graph and records
  the exact P88 Kuratowski certificates.  NetworkX is used only as a finite
  planarity discovery/checking tool; no planarity theorem is inferred from
  the census.

Reproduce with

```powershell
python -B problems/864/compute/p108/audit_sweep_saturation.py `
  --max-width 30 --max-translation 30 `
  --output problems/864/compute/p108/sweep_saturation_w30_g30.json
python -B problems/864/compute/p108/audit_upper_matching_positive_holes.py `
  --max-width 30 `
  --output problems/864/compute/p108/upper_matching_positive_holes_w30.json
python -B problems/864/compute/p108/audit_defect_budget_domains.py `
  --output problems/864/compute/p108/defect_budget_parent_subsets.json
python -B problems/864/compute/p108/verify_sweep_identities.py `
  --output problems/864/compute/p108/sweep_identities_mandatory.json
python -B problems/864/compute/p108/audit_arm_planarity.py `
  --output problems/864/compute/p108/arm_planarity_mandatory.json
```

## Claim boundary

P108 proves the lower-slot reservation, the exact upper color-window
equivalence, the cycle cancellation (8), and the sweep identity (11).  It
does not prove RM97, UW108, BC108, arm-graph planarity under the live
conjunction, or the full Erdős 864 theorem.

The recommended next proof target is BC108.  A valid proof may choose a
cycle basis in every `G_u` and must charge every positive cycle-excess unit
with bounded multiplicity to exactly one of three global banks:

\[
 \text{a mark of }B,qquad
 \text{a collided fold label counted by }V_b,qquad
 \text{a unit of }(-\delta)_+.
\]

P88 and its parity lift show that deleting either of the last two banks is
false.
