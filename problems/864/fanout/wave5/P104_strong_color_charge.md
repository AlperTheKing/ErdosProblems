# P104: global strong-color charge is false without positive defect

## Verdict

The requested unrestricted inequality is false.  Affinely lift the P88
60-point order counterexample by

\[
 B'=2B+1,\qquad h'=2h=6572,qquad b=1.                 \tag{A}
\]

The lift is endpoint-normalized and integer Sidon.  It preserves every fold
and every loose triangle, while every positive difference of `B'` is even
and every low sum plus `b` is odd.  Exact enumeration gives

\[
 C_S=182,\qquad T_F=200,\qquad V_1=0,
\]

and hence

\[
 T_F-C_S-V_1=18.                                      \tag{B}
\]

The lift also satisfies the full literal hole.  Therefore neither a global
discharging nor a graph decomposition can prove the inequality under only
endpoint normalization and integer Sidonicity.

The row has

\[
 \delta=(3p^2-p+2)/2-h'=-1201.
\]

Thus it does not falsify the positive-defect implication needed by P82.  If
positive defect was intended as an unstated hypothesis, that corrected
version remains open; it is not proved in this note.

## Exact formulation

Let `G=G_AC` be the bipartite graph on labelled copies `B_A,B_C`.  A
canonical fold

\[
 a+c+h=u+v,\qquad a\le c<u\le v,
\]

gives the edge `a_Ac_C`, colored by `u`.  Integer Sidonicity makes the
`(a,c)`, `(a,u)`, and `(c,u)` projections injective, so this is a proper
edge-coloring.  For a color `u`, let `M_u` be its matching and let `A_u,C_u`
be the endpoint sets of `M_u`.  Then

\[
 T_F=\sum_u\bigl(e_G(A_u,C_u)-|M_u|\bigr).             \tag{1}
\]

Give a fold edge `ac` the phase label

\[
 \ell(ac)=a+c+b,
\]

and call it collided when `\ell(ac)` is a represented positive difference
of `B`.  The number of collided fold edges is `V_b`.  The target is the
global strong-coloring defect bound

\[
 \boxed{T_F\le |E(G)|+V_b.}                            \tag{2}
\]

Under the literal hole, `V_b=0`; however, (A)--(B) show that this conclusion
requires the additional positive-defect hypothesis before it can be used
with P82.

## Dead per-color decomposition

The tempting colorwise strengthening

\[
 e_G(A_u,C_u)\le 2|M_u|+
 |\{e\in M_u:\ell(e)\in\Delta^+(B)\}|                \tag{3}
\]

is false.  So is the proposed explanation that deleting the collided edges
of `M_u` leaves `G[A_u,C_u]` a pseudoforest.

The exact P88 translation at `gamma=41`, `b=2`, has a color `u=2421` with

\[
 |M_u|=9,\qquad e_G(A_u,C_u)=38,\qquad
 |M_u\cap V_b|=3.
\]

Thus both proposed bounds have residual

\[
 38-2\cdot9-3=17.
\]

Across all 4,170 positive-defect P88 translations, (3) fails on 2,196 rows
and the pseudoforest form fails on 2,302 rows.  The witness is reproduced by
`compute/p104/audit_strong_color_decomposition.py`.  The full row still
satisfies (2), so any proof must transfer charge between distinct colors.

Pooling all collision capacity across colors is still insufficient if color
deficits are discarded.  On the same `gamma=41`, `b=2` row,

\[
 \sum_u\max(0,e_G(A_u,C_u)-2|M_u|)=87>63=V_b.          \tag{4}
\]

Thus the pooled positive-part residual is 24.  In contrast, the signed sum is

\[
 \sum_u(e_G(A_u,C_u)-2|M_u|)=T_F-C_S=51,
\]

and the global target has slack `63-51=12`.  A valid decomposition must use
both collision capacity and negative excess from other colors; neither a
colorwise bound nor pooled payment of positive color excess can prove (2).

## Verification

Run

```powershell
python -m py_compile problems/864/compute/p104/audit_strong_color_decomposition.py problems/864/compute/p104/verify_affine_lift_counterexample.py
python -B problems/864/compute/p104/verify_affine_lift_counterexample.py
python -B problems/864/compute/p104/audit_strong_color_decomposition.py --max-width 0
```

The first verifier uses exact Python integers and independently reconstructs
all sums, differences, folds, loose triangles, collisions, the literal hole,
and the defect.  The second reproduces the 4,170-row P88 decomposition audit.
