# C58: acyclic Horn dual obstruction

## Verdict

Acyclicity of the binary Horn hypergraph does **not** yield the C56
inequality, and it does not make the C56 relaxation integral.  Both failures
already occur in finite topologically ordered systems with two seeds, the
splitless boundary condition, and one complete distinguished unary chain.

The smallest raw counterexample has five vertices.  Even after imposing the
arithmetic-local condition that every hard parent is a positive vertex of
the distinguished chain, the smallest counterexample has six vertices.  Its
LP relaxation has an exact fractional vertex supported by an active minor of
determinant `-2`.

The strongest arithmetic-specific replacement proved here is the
hard-parent/two-step lemma in Section 4.  It forces every hard parent onto a
seed-2 chain and keeps two seed-2 successors below the hard output.  It does
not force that chain to re-enter the closed set.  The actual least arithmetic
closure at cutoff `74` is an exact falsifier to that stronger local claim.
Consequently, the integral C56 duals through `100000` use genuinely global
arithmetic incidence; they cannot follow from Horn acyclicity or endpoint
chain transport alone.

## 1. Generic analogue

Let `V` be topologically ordered.  Fix two seeds `s0,s1`.  A binary Horn
clause is

\[
        a\wedge b\longrightarrow c,
        \qquad a,b<c,\quad a\ne b.                    \tag{1}
\]

A nonseed with no incoming clause is **splitless** and is fixed outside the
set.  A node is **hard** when it has an incoming clause but none of its
incoming clauses uses either seed.  A distinguished unary edge

\[
        p\longrightarrow c                             \tag{2}
\]

means that `(s0,p)->c` is one of the Horn clauses.  For a Horn-closed set `T`
containing the seeds and excluding the splitless nodes, put

\[
 H_T=\#\{h:h\text{ is hard},\ h\notin T\},
 \qquad
 Q_T=\#\{p\to c:p\notin T,\ c\in T\}.                \tag{3}
\]

This is the literal abstract version of the splitless-closed C56 model.

## 2. Smallest raw counterexample

Take the five nodes

\[
        s_0,s_1,r,c,h
\]

with clauses

\[
        s_0\wedge s_1\to c,
        \qquad
        r\wedge c\to h,                                \tag{4}
\]

and distinguish the unary edge `s1 -> c`.  The node `r` is splitless and
`h` is hard.  The set

\[
        T=\{s_0,s_1,c\}                                \tag{5}
\]

is closed, contains both seeds, and excludes every splitless nonseed.  But

\[
        H_T=1,
        \qquad Q_T=0.                                  \tag{6}
\]

Five vertices are minimal in this raw schema.  Besides the two seeds, a
nonempty chain needs a nonhard child.  A hard binary clause then needs two
distinct nonseed parents and its own output.  With only four vertices there
is only one available nonseed parent below the hard output.

The exact checker exhausted all topological systems of this form through
order four: `5` models and `7` closed sets, with no failure.  At order five
its first failure is isomorphic to (4).  The preceding vertex count proves
that stopping at that first order-five witness preserves minimality.

## 3. Arithmetic-strengthened counterexample and nonintegrality

One can exclude the cheap mechanism in (4) by requiring both parents of a
hard clause to be positive vertices of a complete distinguished chain whose
root is splitless.  Acyclicity still does not suffice.

Take six nodes

\[
        s_0,s_1,r,x,y,h
\]

and clauses

\[
 s_0\wedge r\to x,
 \qquad
 s_0\wedge x\to y,
 \qquad
 x\wedge y\to h.                                      \tag{7}
\]

The distinguished chain is

\[
        r\longrightarrow x\longrightarrow y.          \tag{8}
\]

Both hard parents are non-splitless chain children.  Nevertheless
`T={s0,s1}` is closed and has

\[
        H_T=1>0=Q_T.                                   \tag{9}
\]

This six-node model is minimal under the strengthened conditions: two
seeds, one splitless chain root, two distinct positive chain vertices for a
hard clause, and the hard output are all necessary.  Independently, the
exact enumeration checked `54` models and `152` closed sets at order five
without a failure, then found (7) at order six after `4103` models and
`16829` closed sets.

The same model disproves a total-unimodularity explanation of the C56
integral optima.  In the continuous relaxation set

\[
 t_r=0,\qquad t_x=t_y=\frac12,\qquad t_h=0,
 \qquad q_{rx}=\frac12,qquad q_{xy}=0.                \tag{10}
\]

All Horn and boundary convex-hull inequalities hold.  In the variable order
`(t_x,t_y,t_h,q_rx,q_xy)`, five independent active rows are

\[
 \begin{pmatrix}
  1&-1& 0& 0&0\\
  1& 1&-1& 0&0\\
  0& 0& 1& 0&0\\
  1& 0& 0&-1&0\\
  0& 0& 0& 0&1
 \end{pmatrix}.                                       \tag{11}
\]

Its determinant is `-2`.  Thus (10) is a fractional vertex and the generic
acyclic Horn-plus-chain matrix is not totally unimodular.  This is logically
separate from (9): the integral point in (9) already defeats the desired
objective lower bound, while (10) rules out generic LP integrality.

## 4. Arithmetic hard-parent/two-step lemma

Let

\[
        {\cal A}=\{n\ge2:n\not\equiv1\pmod3\},
        \qquad U(u)=2u-1.                              \tag{12}
\]

Call `h` hard-shaped as in C56, and suppose

\[
        h+1=uv,\qquad 2\le u<v,\qquad u,v\in{\cal A}. \tag{13}
\]

### Lemma

For each `w in {u,v}`:

1. `w` is odd and `w>=5`;
2. `p=(w+1)/2` belongs to `A`, satisfies `2<p<w`, and
   `w=2p-1` is an admissible seed-2 output;
3. `U^2(w)=4w-3<=h`;
4. for every forward-closed `T` containing `2`, if `w notin T` and
   `U^2(w) in T`, then at least one of `U(w),U^2(w)` is a seed-2 boundary
   child of `T`, and that boundary is at most `h`.

### Proof

Hard-shaped integers are even, so `uv=h+1` is odd and both factors are odd.
Neither factor is `3`: otherwise (13) itself would be a usable distinct
seed-3 factorization, contrary to hardness.  Hence both are at least `5`.

If an allowed odd integer `w` is `3 mod 6`, then `(w+1)/2` is `2 mod 3`; if
it is `5 mod 6`, then `(w+1)/2` is `0 mod 3`.  Thus `p=(w+1)/2` is allowed.
Since `w>=5`, the factorization `w+1=2p` has distinct allowed factors.
This also proves that a hard parent is never splitless.

Let `z` be the other factor.  Since `z>=5`,

\[
 h-(4w-3)=wz-1-4w+3=w(z-4)+2>0,                      \tag{14}
\]

which proves the two-step bound.  Finally, closure under the seed `2` makes
membership nondecreasing along

\[
        w\longrightarrow U(w)\longrightarrow U^2(w). \tag{15}
\]

If the first vertex is absent and the last is present, one of the two edges
is a `0 -> 1` boundary.  Equation (14) keeps it below `h`.  QED.

This is a uniform arithmetic lemma, but its re-entry hypothesis cannot be
removed.

## 5. Exact arithmetic falsifier to local re-entry

Let `G` be the least arithmetic closure generated by `2,3`.  At cutoff `74`,

\[
        74+1=5\cdot15                                  \tag{16}
\]

is the complete admissible factor list of the hard-shaped hole `74`.
However,

\[
        15,\quad U(15)=29,\quad U^2(15)=57             \tag{17}
\]

are all absent from `G`.  Hence the factor component of the missing endpoint
`15` supplies no boundary through `74`.

The complete global counts at that cutoff are

\[
 \{\text{hard holes}\}=\{54,74\},
 \qquad
 \{\text{seed-2 boundary children}\}=\{41,69\}.       \tag{18}
\]

Thus `74` is paid, if at all, by capacity from an unrelated arithmetic
component.  A proof that assigns every hard hole to a first exit in one of
its own endpoint chains is false even for the actual least closure.

The exact script additionally checked every one of the `1373` admissible
hard factorizations through `10010` against the hard-parent/two-step lemma.
This finite check is only an audit; the proof above is uniform.

## 6. Consequence for C56

The finite C56 certificates cannot be consequences of any theorem whose
only inputs are:

- topological acyclicity;
- two fixed seeds and fixed splitless nodes;
- binary Horn closure;
- a distinguished unary chain;
- the fact that hard parents are non-splitless chain children; or
- total unimodularity of the resulting constraint matrix.

Any uniform C56 dual must use additional arithmetic cross-factor clauses to
move capacity between unrelated seed-2 components.  Section 5 shows that
even the existence of a nearby endpoint-chain exit is not such an invariant.

## 7. Reproduction

~~~powershell
python problems/424/fanout/wave5/C58_horn_dual.py `
  --output problems/424/fanout/wave5/C58_horn_dual.json

python -O problems/424/fanout/wave5/C58_horn_dual.py `
  --output problems/424/fanout/wave5/C58_horn_dual_replay.json
~~~

The checker uses exact integers and `fractions.Fraction`; it uses no
floating-point acceptance and contains no optimization oracle.

~~~text
C58_horn_dual.py
319798ACAA7E2E982084D17F77415F3F55DEF0F7AC787CF5E7A0D4C2565B387A

C58_horn_dual.json
1EE58C9A495B2B45EE7439FB613BD3622BE06208594B6AD09C6215105351465F

C58_horn_dual_replay.json
1EE58C9A495B2B45EE7439FB613BD3622BE06208594B6AD09C6215105351465F
~~~
