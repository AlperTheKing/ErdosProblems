# Direct Route B: one-interval extension obstruction

## Source

Terence Tao, *Local Bernstein theory, and lower bounds for Lebesgue
constants*, arXiv:2603.21453.  The downloaded arXiv source archive has
SHA-256

```text
5F5E38BB0CC3F52B623791D89FADA6C81F35402896F206610CCB35C9047DEAF0
```

The exact statement used below is Theorem `main` (Main theorem), part (i), in
`tao_src/trunc_duffin_schaeffer.tex`.  It states that for every fixed
non-trivial interval \(I\subset[-1,1]\), there are constants \(K_I<\infty\)
and \(N_I\) such that, for every \(n\geq N_I\) and every set of \(n\)
distinct nodes in \([-1,1]\),
\[
  \sup_{x\in I}L_n(x)\geq \frac{2}{\pi}\log n-K_I.
\]
The constant may depend on \(I\), but it is uniform in the node set.

## Proposition: the registered one-interval extension lemma is false

Fix a non-trivial closed interval \(I\subset(-1,1)\).  Let \(K_I,N_I\) be
as above and choose any defect budget \(B>K_I\), for example
\(B=K_I+1\).  Then no finite prefix of distinct nodes can be extended to
any prefix of length \(n\geq N_I\) satisfying
\[
  L_n(x)\leq \frac{2}{\pi}\log n-B
  \qquad\text{for every }x\in I.
\]

### Proof

Every extension of length \(n\) is simply a set of \(n\) distinct nodes in
\([-1,1]\), so Tao's theorem supplies \(x_n\in I\) with
\[
  L_n(x_n)\geq \frac{2}{\pi}\log n-K_I
             > \frac{2}{\pi}\log n-B.
\]
This contradicts the proposed uniform upper bound on \(I\).  The argument
does not depend on the initial prefix or on how the appended nodes are
clustered.  It also defeats a claim requiring the upper bound at every
intermediate prefix, since it already defeats the claim at the terminal
prefix. \(\square\)

## Consequence for Direct Route B

The current frontier lemma permits arbitrary assigned defect budgets on a
fixed rational interval.  Applying it with \(B>K_I\) would contradict the
proposition.  Thus clustered or Chebyshev-like appended blocks cannot prove
that lemma.  This is exactly the route's registered exit condition: a
universal local lower bound forces a fixed-defect high point inside every
protected interval for every sufficiently long extension.

This does **not** prove Erdős Problem 1132 and does **not** rule out every
possible pointwise counterexample.  A pointwise counterexample could have
the high point \(x_n\) move with \(n\), while the interval constants \(K_I\)
diverge as \(I\) shrinks.  What is ruled out is the registered
uniform-on-prescribed-interval prefix-extension mechanism.
