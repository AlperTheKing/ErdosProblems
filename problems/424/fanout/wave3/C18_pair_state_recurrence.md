# C18: pair-state recurrence for the fixed affine orbit

## Verdict

This lane does **not** prove

\[
\Delta(X)\le \tau_\alpha(X)F(X)
\]

eventually for any \(\alpha\le 1/2\). It does give an exact inverse-parent
recurrence for arbitrary affine pair and tuple states, and it identifies two
rigorous obstructions to the proposed finite closure.

1. The three pair roots \(P_{23},P_{25},P_{35}\) have respectively 3, 4,
   and 4 arithmetically live first-parent types. All 11 types have actual
   witnesses in the fixed orbit.
2. The triple root \(P_{235}\) has one first-parent type, exactly:
   \(t=30u+29\) and parent forms
   \((36u+35,100u+97,225u+218)\).
3. Literal primitive relation states do not close finitely. Repeating the
   parent choice \((5,3)\) from \(P_{35}\) gives an infinite sequence of
   distinct feasible states with coefficients \((5^{n+1},3^{n+1})\).
4. The live branches are not disjoint. At \(t=547\), one \(P_{23}\) pair
   belongs to both the \((3,2)\) and \((5,2)\) parent branches. Thus adding
   pair-state branch counts is not an exact recurrence; its first correction
   already requires a triple-parent state.

Consequently, no finite recurrence whose types are the literal primitive
affine pair relations and whose edges retain every feasible inverse-map pair
can be transition-closed. This does not rule out a finite quotient carrying
additional arithmetic data, or an infinite-state weighted argument. Neither
is supplied here.

Code is in
[C18_pair_state](../../compute/wave3/C18_pair_state/).

## 1. Exact affine-tuple recurrence

Let \(K=\{2,3,5\}\), and let \(B\) be the least set containing
\(2,3,5\) and closed under

\[
T_k(x)=kx-1,\qquad k\in K,\qquad x\ne k.
\]

For an integer \(n\), put

\[
\Pi(n)=\left\{k\in K:
 k\mid n+1,\ {n+1\over k}\in B,\ {n+1\over k}\ne k\right\}.
\]

For \(n>5\), the least-set definition gives the exact equivalence

\[
n\in B\quad\Longleftrightarrow\quad \Pi(n)\ne\varnothing.       \tag{1}
\]

Let \({\bf L}=(L_1,\ldots,L_d)\), where

\[
L_i(t)=a_it+b_i,\qquad a_i>0,
\]

and define the affine-tuple state

\[
{\cal S}_{\bf L}(T)=
\{t\in\mathbb Z:0\le t\le T,\ L_i(t)\in B\ (1\le i\le d)\}.    \tag{2}
\]

With \(N_{\bf L}(T)=|{\cal S}_{\bf L}(T)|\), the four C09 collision
functions are exactly

\[
\begin{aligned}
P_{23}(X)&=N_{(2t,3t)}\!\left(\left\lfloor{X+1\over6}\right\rfloor\right),\\
P_{25}(X)&=N_{(2t,5t)}\!\left(\left\lfloor{X+1\over10}\right\rfloor\right),\\
P_{35}(X)&=N_{(3t,5t)}\!\left(\left\lfloor{X+1\over15}\right\rfloor\right),\\
P_{235}(X)&=N_{(6t,10t,15t)}\!\left(\left\lfloor{X+1\over30}\right\rfloor\right),
\end{aligned}
\]

and \(\Delta=P_{23}+P_{25}+P_{35}-P_{235}\).

Fix a map assignment \({\bf k}=(k_1,\ldots,k_d)\in K^d\). A parameter can
use this assignment only if

\[
a_it+b_i+1\equiv0\pmod {k_i}\qquad(1\le i\le d).          \tag{3}
\]

Write

\[
g_i=(a_i,k_i),\qquad m_i={k_i\over g_i}.
\]

The \(i\)-th congruence is impossible unless
\(g_i\mid b_i+1\). If all congruences are compatible, the generalized
Chinese remainder theorem gives one class

\[
t\equiv r_{\bf k}\pmod {M_{\bf k}},\qquad
M_{\bf k}=\mathop{\rm lcm}_i m_i,\quad 0\le r_{\bf k}<M_{\bf k}. \tag{4}
\]

For \(t=M_{\bf k}u+r_{\bf k}\), define the integral parent forms

\[
L_i^{\bf k}(u)=
{a_iM_{\bf k}\over k_i}u+
{a_ir_{\bf k}+b_i+1\over k_i}.                            \tag{5}
\]

### Lemma 1 (exact Boolean tuple transition)

Let \({\cal E}_{\bf L}(T)\) be the subset of (2) on which at least one
\(L_i(t)\) is a seed in \(\{2,3,5\}\). Then

\[
{\cal S}_{\bf L}(T)
= {\cal E}_{\bf L}(T)\ \cup
\bigcup_{\substack{{\bf k}\in K^d\\\text{(3) compatible}}}
\left\{M_{\bf k}u+r_{\bf k}:
\begin{array}{l}
0\le M_{\bf k}u+r_{\bf k}\le T,\\
L_i^{\bf k}(u)\in B,\\
L_i^{\bf k}(u)\ne k_i\quad(1\le i\le d)
\end{array}\right\}.                                    \tag{6}
\]

In particular,

\[
N_{\bf L}(T)\le 3d+
\sum_{\substack{{\bf k}\in K^d\\\text{(3) compatible}}}
N_{{\bf L}^{\bf k}}
\left(\left\lfloor{T-r_{\bf k}\over M_{\bf k}}\right\rfloor\right).
                                                               \tag{7}
\]

Here a term with a negative cutoff is zero. The estimate (7) deliberately
drops the licensing exclusions and counts overlaps more than once.

#### Proof

For a parameter outside \({\cal E}_{\bf L}(T)\), every coordinate is greater
than 5. If it belongs to \(B\), (1) supplies at least one licensed immediate
parent \(k_i\) for that coordinate. The resulting assignment satisfies (3),
and substitution gives (5). This proves containment in the right side of
(6). Conversely, every licensed parent in the right side maps under
\(T_{k_i}\) to \(L_i(t)\), so closure of \(B\) proves the reverse
containment. Finally, each equation \(L_i(t)\in\{2,3,5\}\) has at most three
integer solutions in total, and the union bound in (6) gives (7). \(\square\)

Equation (6) is a rigorous multitype recurrence, but its type set is not
finite and its union is not disjoint.

## 2. The complete first transition table

The forms in the last column are listed in the coordinate order of the root.
All map assignments omitted from the table make (3) inconsistent. Licensing
exclusions from (6) remain understood.

| root forms | parent maps | parameter class | parent forms |
|---|---:|---:|---|
| \((2t,3t)\) | \((3,2)\) | \(t=6u+1\) | \((4u+1,9u+2)\) |
| \((2t,3t)\) | \((3,5)\) | \(t=15u+13\) | \((10u+9,9u+8)\) |
| \((2t,3t)\) | \((5,2)\) | \(t=10u+7\) | \((4u+3,15u+11)\) |
| \((2t,5t)\) | \((3,2)\) | \(t=6u+1\) | \((4u+1,15u+3)\) |
| \((2t,5t)\) | \((3,3)\) | \(t=3u+1\) | \((2u+1,5u+2)\) |
| \((2t,5t)\) | \((5,2)\) | \(t=10u+7\) | \((4u+3,25u+18)\) |
| \((2t,5t)\) | \((5,3)\) | \(t=15u+7\) | \((6u+3,25u+12)\) |
| \((3t,5t)\) | \((2,2)\) | \(t=2u+1\) | \((3u+2,5u+3)\) |
| \((3t,5t)\) | \((2,3)\) | \(t=6u+1\) | \((9u+2,10u+2)\) |
| \((3t,5t)\) | \((5,2)\) | \(t=10u+3\) | \((6u+2,25u+8)\) |
| \((3t,5t)\) | \((5,3)\) | \(t=15u+13\) | \((9u+8,25u+22)\) |
| \((6t,10t,15t)\) | \((5,3,2)\) | \(t=30u+29\) | \((36u+35,100u+97,225u+218)\) |

For example, the last row follows without search. The numbers \(6t+1\),
\(10t+1\), and \(15t+1\) can use only maps \(5,3,2\), respectively.
Their congruences are

\[
t\equiv4\pmod5,\qquad t\equiv2\pmod3,\qquad t\equiv1\pmod2,
\]

whose unique joint solution is \(t\equiv29\pmod {30}\). Therefore, with

\[
T=\left\lfloor{X+1\over30}\right\rfloor,
\]

the triple correction has the exact one-step recurrence

\[
P_{235}(X)=
\#\left\{0\le u\le\left\lfloor{T-29\over30}\right\rfloor:
36u+35,100u+97,225u+218\in B\right\}.                    \tag{8}
\]

The right side is zero when \(T<29\). Its licensing conditions are automatic.

Every one of the 11 pair rows is populated. The least parameters found by
exact enumeration are:

| root | maps and least \(t\) |
|---|---|
| \(P_{23}\) | \((3,2):115\), \((3,5):223\), \((5,2):67\) |
| \(P_{25}\) | \((3,2):13\), \((3,3):196\), \((5,2):327\), \((5,3):82\) |
| \(P_{35}\) | \((2,2):109\), \((2,3):91\), \((5,2):133\), \((5,3):73\) |

Thus none of the live rows can be deleted merely because its congruence class
misses the orbit.

## 3. Infinite primitive relation graph

A pair relation state \((A,D,c)\) denotes

\[
Ax-Dy=c,\qquad x,y\in B.                                 \tag{9}
\]

If \(x=T_i(u)\) and \(y=T_j(v)\), substitution gives

\[
(Ai)u-(Dj)v=c+A-D.                                       \tag{10}
\]

Let \(g=(Ai,Dj)\). This branch has no integer points if
\(g\nmid c+A-D\); otherwise division by \(g\) gives its primitive successor.
This is an exact arithmetic dead-branch test.

The root \(P_{35}\) has relation \((5,3,0)\). Define

\[
q_n=\left(5^{n+1},3^{n+1},c_n\right),\qquad
c_n=\sum_{r=1}^n(5^r-3^r)
={5(5^n-1)\over4}-{3(3^n-1)\over2}.                     \tag{11}
\]

### Proposition 2 (no finite literal pair closure)

For every \(n\ge0\), the parent choice \((5,3)\) sends \(q_n\) to
\(q_{n+1}\). Hence every transition-closed collection of primitive relation
states containing the \(P_{35}\) root and every arithmetically feasible
parent branch is infinite.

#### Proof

The two new coefficients in (10) are \(5^{n+2}\) and \(3^{n+2}\), whose
gcd is one. The new offset is

\[
c_n+5^{n+1}-3^{n+1}=c_{n+1}.
\]

Thus the branch is feasible and has state \(q_{n+1}\). The first coefficient
strictly increases, so all states are distinct. \(\square\)

This obstruction is not only visible in empty symbolic branches. Write
\(T_{k_1\cdots k_m}=T_{k_m}\circ\cdots\circ T_{k_1}\), so words are in
application order, and set

\[
u=T_{3252222}(5)=2129,\qquad
v=T_{232533252}(5)=45627.
\]

Every displayed step is licensed. Direct evaluation gives

\[
T_5^5(u)=6{,}652{,}344=3\cdot2{,}217{,}448,
\]

\[
T_3^5(v)=11{,}087{,}240=5\cdot2{,}217{,}448.             \tag{12}
\]

Thus \(q_0,\ldots,q_5\) are all populated along this ancestry chain. At
depth five the primitive equation is

\[
15625u-729v=3542,
\]

which the displayed integers satisfy. Equation (12) is a finite witness, not
a claim that every state in (11) is populated.

## 4. Exact non-disjointness falsifier

The first-level union in Lemma 1 cannot be replaced by a sum of pair-state
counts. In application order,

\[
219=T_{255}(5),\qquad
365=T_{3333}(5),\qquad
821=T_{35322}(5).
\]

Consequently,

\[
T_5(219)=1094=T_3(365),\qquad T_2(821)=1641.              \tag{13}
\]

Taking \(t=547\), (13) says

\[
(2t,3t)=(1094,1641)\in B^2.
\]

The same parameter belongs to both the \((5,2)\) and \((3,2)\) rows of the
\(P_{23}\) table. Their intersection has the exact reparameterization

\[
t=30q+7,\qquad
12q+3,\ 20q+5,\ 45q+11\in B.                            \tag{14}
\]

At \(q=18\), the three forms in (14) are precisely \(219,365,821\).
Thus an exact inclusion-exclusion recurrence already leaves the pair-state
category after one step. Exhaustive use of (1) verifies that \(547\) is the
least \(P_{23}\) parameter with more than one live first-parent branch.

This is independent of the triple root in (8): it is a triple of distinct
parents created by the intersection of two pair branches. Tracking only
\(P_{23},P_{25},P_{35},P_{235}\) therefore cannot make (6) count-exact.

## 5. Exact finite census

All computations use Python integers. Primitive relation states were divided
only after the exact gcd divisibility test following (10). Affine tuple states
were identified up to coordinate permutation and an integral shift of their
parameter.

The breadth-first primitive-relation census from all three pair roots is:

| depth | new states | cumulative |
|---:|---:|---:|
| 0 | 3 | 3 |
| 1 | 11 | 14 |
| 2 | 50 | 64 |
| 3 | 154 | 218 |
| 4 | 616 | 834 |
| 5 | 1,838 | 2,672 |
| 6 | 6,374 | 9,046 |

The affine-tuple censuses are:

| root | new states by depth | cumulative |
|---|---|---:|
| \(P_{23}\) | \(1,3,20,55,227,662,2447\) through depth 6 | 3,415 |
| \(P_{25}\) | \(1,4,18,68,262,842,2877\) through depth 6 | 4,072 |
| \(P_{35}\) | \(1,4,17,59,267,861,2927\) through depth 6 | 4,136 |
| \(P_{235}\) | \(1,1,12,24,219\) through depth 4 | 257 |

An independent orbit enumeration through \(10^8\) gives

\[
|B\cap[1,10^8]|=19{,}072{,}023.
\]

With every coordinate constrained to be at most \(10^8\), it finds

\[
\begin{array}{c|rrrr}
\text{state}&P_{23}&P_{25}&P_{35}&P_{235}\\ \hline
\text{count}&630{,}863&574{,}801&511{,}281&952.
\end{array}
\]

The first \(P_{235}\) parameter is \(t=12{,}839=30\cdot427+29\). Its
three parents in (8) are

\[
15407=T_{2222232252}(5),\quad
42797=T_{323233352}(5),\quad
96293=T_{232225222322}(5),
\]

which map under \((5,3,2)\) to
\((77034,128390,192585)=(6t,10t,15t)\).

Reproduction:

```powershell
python relation_states.py --depth 6 --largest 20
python tuple_states.py --root P23 --depth 6
python tuple_states.py --root P25 --depth 6
python tuple_states.py --root P35 --depth 6
python tuple_states.py --root P235 --depth 4
python orbit_witnesses.py --limit 100000000
python -m unittest -v test_pair_states.py
```

The nine unit tests pass. They verify the complete root transition tables,
the infinite symbolic branch formula through depth 20, the overlap witness,
the depth-five actual witness, and the first \(P_{235}\) witness.

## 6. Consequence for the threshold

Lemma 1 supplies a valid infinite-state Boolean recurrence and the upper
recurrence (7). It does not supply the coefficient estimate needed in C09.
There are two separate losses:

1. Summing the branch terms in (7) overcounts actual tuple parameters, as
   (13) proves. Restoring equality introduces higher-arity intersection
   states such as (14).
2. Even before those intersections are added, Proposition 2 proves that the
   literal affine relation types are infinite. The finite depth counts do not
   provide a transition-closed truncation or a summable tail estimate.

Accordingly, no implication

\[
\Delta(X)\le\tau_\alpha(X)F(X),\qquad \alpha\le {1\over2},
\]

follows from this recurrence alone. A continuation must prove one genuinely
new ingredient: either a finite quotient that preserves the Boolean unions
and their intersections, or nonnegative weights on the infinite tuple graph
whose transition inequality yields the floor-exact coefficient
\(\tau_{1/2}(X)\). The computations here establish neither condition.

## Prior-art check

The [official problem page](https://www.erdosproblems.com/424) lists problem
424 as open and lists no partial solution. Shamazov and Talambutsa's
[affine-orbit paper](https://arxiv.org/abs/2507.06875) proves results under
free-semigroup or exact-cover hypotheses; as audited in C09, neither applies
to this nonfree Boolean parent recurrence. The cited sources do not state a
finite collision-state recurrence of the form above.
