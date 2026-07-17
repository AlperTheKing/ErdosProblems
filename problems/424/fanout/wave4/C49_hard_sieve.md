# C49: direct analytic hard-hole sieve

## Verdict

The requested estimate

\[
 H(X)-Q(X)\le M(\lfloor(X+1)/3\rfloor)-S(X)+o(X)
\]

and the stronger estimate \(H(X)\le Q(X)+o(X)\) are **not proved** in
this lane.

There is one unconditional asymptotic gain which deals correctly with
large blocker fibers.

> **Bounded-pair sieve theorem.** For every fixed integer \(R\ge 1\),
> \[
> \#\{h\le X:h\text{ is hard and }|\mathcal P(h)|\le R\}=o(X).
> \]
> Here \(\mathcal P(h)\) is the set of distinct admissible unordered
> factorizations of \(h+1\).

Thus the unique-split part of the large blocker-\(11\) fiber is \(o(X)\);
no bounded capacity is assigned to blocker \(11\). Sources in the same
fiber with unbounded pair count remain in the high-complexity class.

The remaining direct first-moment sieve has a quantified logarithmic
exponent gap. For rank-two hard sources its available incidence budget is
\(O(X\sqrt{\log X})\), whereas a typical hard successor has only

\[
 (\log X)^{(\log 2)/2+o(1)}
\]

admissible pairs. Since \((\log 2)/2=0.34657\ldots<1/2\), no pair-count
threshold makes both sides \(o(X)\). Closing C49 requires a correlated
pair estimate, or an improvement of at least

\[
 (\log X)^{(1-\log 2)/2-o(1)}
\]

over the raw first-moment incidence bound.

Exact computation also finds a useful decomposition which survives every
cutoff through \(10^6\), but is not proved:

\[
 K(X)\le Q(X),\qquad J(X)\le E(X).
\]

Here \(J\) consists of hard sources for which every admissible pair has two
hole endpoints, and \(K=H-J\). A natural pseudoforest proof of \(J\le E\)
is exactly false: its first cycle occurs at \(666=23\cdot29-1\), and one
component already has cyclomatic number \(77\) by \(10^4\).

## 1. Setup

Use the notation of C13, C16, C25, and C44:

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},\qquad
 \mathcal M=\mathcal A\setminus G.
\]

For an allowed \(n\), let

\[
 \mathcal P(n)=
 \{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=n+1\},
 \qquad P(n)=|\mathcal P(n)|.
\]

The obstruction rank \(\rho\) is C44 equation (1). C44 proves that every
hard source has rank at least two and has a critical odd blocker \(q\)
with

\[
 q\le {h+1\over5},\qquad
 \rho(q)=\rho(h)-1,\qquad
 p={q+1\over2}\in\mathcal M,\quad
 \rho(p)\le\rho(h)-2.
\]

The argument below does not assign unit capacity to \(q\) or \(p\).

C25 proves that the odd successor \(N=h+1\) of a hard source has one of
the following shapes:

\[
 N\equiv1\pmod6,
 \qquad\text{or}\qquad
 N\equiv3\pmod{18}.
 \tag{1}
\]

In the second case \(v_3(N)=1\). In both cases, if

\[
 \Omega_2(N)=\sum_{\substack{\ell\ {\rm prime}\\\ell\equiv2\ (3)}}v_\ell(N),
\]

then \(\Omega_2(N)\) is even.

## 2. Bounded-pair hard sources have density zero

### Lemma 1 (pair count controls the \(2\bmod3\) prime count)

For every hard source \(h\), with \(N=h+1\),

\[
 \boxed{\Omega_2(N)\le4P(h)+2.} \tag{2}
\]

#### Proof

Put \(t=\Omega_2(N)\). List the \(t\) prime occurrences congruent to
\(2\bmod3\), with multiplicity, as \(r_1,\ldots,r_t\). For every odd
index \(j\in\{1,3,\ldots,t-1\}\), define \(d_j=r_1\cdots r_j\).
Then \(d_j\equiv2\bmod3\).

If \(v_3(N)=0\), the complementary divisor \(N/d_j\) also has an odd
number of \(2\bmod3\) prime occurrences, so both factors are
\(2\bmod3\). If \(v_3(N)=1\), the complement is divisible by \(3\).
Thus in either case \((d_j,N/d_j)\) is admissible unless the factors are
equal.

There are \(t/2\) candidate indices. At most one gives equal factors.
The prefix products are strictly increasing, so one unordered pair is
produced by at most two indices. Therefore

\[
 P(h)\ge {t/2-1\over2},
\]

which is equivalent to (2). QED.

The bound is sharp: \(N=5^6=15625\) has
\(\Omega_2(N)=6\) and one distinct admissible pair.

### Lemma 2 (fixed \(2\bmod3\) prime complexity is sparse)

For every fixed \(K\),

\[
 \#\{n\le X:\Omega_2(n)\le K\}=o(X). \tag{3}
\]

#### Proof

For \(y\ge2\), let \(\mathscr P_y\) be the primes
\(\ell\le y\), \(\ell\equiv2\bmod3\), and put

\[
 W_y(n)=\sum_{\ell\in\mathscr P_y}{\bf1}_{\ell\mid n},
 \qquad
 A_y=\sum_{\ell\in\mathscr P_y}{1\over\ell}.
\]

For fixed \(y\), averaging over \(n\le X\) and then taking \(X\to\infty\)
gives

\[
 {\bf E}W_y\longrightarrow A_y,
 \qquad
 {\rm Var}(W_y)\longrightarrow
 \sum_{\ell\in\mathscr P_y}{1\over\ell}
 \left(1-{1\over\ell}\right)\le A_y.
\]

This follows directly by expanding \(W_y^2\); divisibility by two fixed
distinct primes has limiting density \(1/(\ell\ell')\).

If \(\Omega_2(n)\le K\), then \(W_y(n)\le K\). Chebyshev gives

\[
 \limsup_{X\to\infty}
 {1\over X}\#\{n\le X:\Omega_2(n)\le K\}
 \le {A_y\over(A_y-K)^2}.
\]

The reciprocal sum over primes \(2\bmod3\) diverges, so the right side
tends to zero as \(y\to\infty\). QED.

### Theorem 3 (bounded-pair sieve)

For each fixed \(R\),

\[
 H_{\le R}^{\rm pair}(X)
 :=\#\{h\le X:h\text{ hard},\ P(h)\le R\}=o(X).
 \tag{4}
\]

#### Proof

Lemma 1 puts every successor \(h+1\) counted by the left side in

\[
 \{N\le X+1:\Omega_2(N)\le4R+2\}.
\]

Lemma 2 says this set has density zero. Translation by one preserves the
estimate. QED.

This includes every unique-split family \(h=q\,a-1\), even when a fixed
critical blocker \(q\), such as \(q=11\), receives arbitrarily many
sources. It does not assert that the full blocker-\(11\) fiber has bounded
pair count.

## 3. The first-moment ceiling

For \(r\ge2\), let \(H_r^\rho(X)\) count hard sources of obstruction
rank exactly \(r\). Selecting one critical blocker from C44 gives the
exact fiber-aware inequality

\[
 H_r^\rho(X)\le
 \sum_{\substack{q\le(X+1)/5\\q\ {\rm odd},\ q\in\mathcal M\\
                  \rho(q)=r-1}}
 \left\lfloor{X+1\over q}\right\rfloor .
 \tag{5a}
\]

Indeed, the selected blocker satisfies \(h+1=q\,a\) with \(a\ge5\), and
for fixed \(q\) the cofactor \(a\) determines \(h\). This is the direct
analytic use of the critical-blocker scale. It counts the entire
blocker-\(11\) fiber by possible cofactors; it never assigns bounded
capacity to \(11\).

Let

\[
 L_1(X)=\#\{q\le X:q\in\mathcal M,\ \rho(q)\le1\}.
\]

### Lemma 4 (rank-one sieve bound)

The standard upper-bound sieve gives

\[
 L_1(X)\ll {X\over\sqrt{\log X}}. \tag{5}
\]

#### Proof

Rank-zero holes are exactly the splitless holes counted by \(E\). C13
shows that their successors either avoid all ordinary primes
\(2\bmod3\), or belong to a square exception. The standard
dimension-\(1/2\) upper-bound sieve gives

\[
 E(X)\ll {X\over\sqrt{\log X}}.
\]

A reducible rank-one hole cannot be hard, by C44 Lemma 4. If it is odd,
its forced seed-2 parent has rank zero; if it is seed-3-easy, its forced
seed-3 parent has rank zero. Both parent maps are injective. Hence

\[
 L_1(X)\le
 E(X)+E(\lfloor(X+1)/2\rfloor)+E(\lfloor(X+1)/3\rfloor),
\]

which proves (5). QED.

Partial summation gives

\[
 \sum_{\substack{q\le X\\q\in\mathcal M,\ \rho(q)\le1}}
 {1\over q}\ll\sqrt{\log X}. \tag{6}
\]

### Lemma 5 (exact rank-two incidence inequality)

Let \(H_2^\rho(X)\) be the hard sources of obstruction rank exactly two.
Then

\[
 \boxed{
 \sum_{h\in H_2^\rho(X)}P(h)
 \le
 \sum_{\substack{q\le X+1\\q\in\mathcal M,\ \rho(q)\le1}}
 \left\lfloor{X+1\over q}\right\rfloor
 \ll X\sqrt{\log X}.
 } \tag{7}
\]

#### Proof

For rank two, the rank recurrence says that every admissible pair has a
missing endpoint of rank at most one. Charge the pair to one such endpoint.
For a fixed endpoint \(q\), every charged source has
\(h+1=q\,a\le X+1\), so there are at most
\(\lfloor(X+1)/q\rfloor\) possibilities. Summing proves the exact first
inequality; (6) proves the second. QED.

This is aggregate: a blocker may have a large fiber.

### Lemma 6 (typical admissible-pair supply)

Let

\[
 \omega_2^{(1)}(N)
 =\#\{\ell\equiv2\pmod3:v_\ell(N)=1\}.
\]

For a successor of either shape in (1),

\[
 P(N-1)+1\ge 2^{\omega_2^{(1)}(N)-2}
 \quad\text{when }\omega_2^{(1)}(N)\ge2. \tag{8}
\]

Moreover, outside a set of \(o(X)\) integers \(N\le X\),

\[
 \omega_2^{(1)}(N)
 =\left({1\over2}+o(1)\right)\log\log X. \tag{9}
\]

#### Proof

Choose any odd-cardinality subset of the primes counted by
\(\omega_2^{(1)}(N)\), and take their product. It is \(2\bmod3\), while
the complementary divisor is allowed by (1) and the even parity of
\(\Omega_2(N)\). There are \(2^{t-1}\) such subsets. An unordered pair is
produced at most twice and at most one equal-factor case is discarded,
giving (8).

For (9), apply Turan--Kubilius to the additive indicator
\({\bf1}_{v_\ell(N)=1}\). Its mean is

\[
 \sum_{\substack{\ell\le X\\\ell\equiv2\ (3)}}
 \left({1\over\ell}-{1\over\ell^2}\right)
 ={1\over2}\log\log X+O(1),
\]

and its variance is \(O(\log\log X)\). QED.

Consequently, for every fixed \(c<(\log2)/2\), all but \(o(X)\) relevant
successors satisfy

\[
 P(N-1)\ge(\log X)^c. \tag{10}
\]

Combining (7) and (10) only gives

\[
 \#H_2^\rho(X)
 \le o(X)+O\!\left(X(\log X)^{1/2-c}\right).
 \tag{11}
\]

The error in (11) needs \(c>1/2\) to be \(o(X)\), whereas (10) requires
\(c<(\log2)/2\). The interval is empty. Thus the direct
pair-threshold/first-moment sieve cannot close from the splitless estimate.
A successful refinement must exploit correlations among low-rank endpoints.

## 4. Exact mixed/all-hole decomposition

Define

\[
 J_X=\{h\in H_X:
       a,b\in\mathcal M\text{ for every }(a,b)\in\mathcal P(h)\},
 \qquad K_X=H_X\setminus J_X.
\]

At every integer cutoff through \(10^6\), the exact checker finds

\[
 K(X)-Q(X)\le0,\qquad
 J(X)-E(X)\le0,\qquad
 J(X)-\bigl(M(\lfloor(X+1)/3\rfloor)-S(X)\bigr)\le0.
 \tag{12}
\]

These are finite gates, not proofs.

| \(X\) | \(H\) | \(J\) | \(K\) | \(Q\) |
|---:|---:|---:|---:|---:|
| \(10^2\) | 2 | 0 | 2 | 3 |
| \(10^3\) | 41 | 8 | 33 | 46 |
| \(10^4\) | 518 | 108 | 410 | 593 |
| \(10^5\) | 5108 | 1004 | 4104 | 6783 |
| \(10^6\) | 45583 | 7083 | 38500 | 67537 |

At \(10^6\), the critical-blocker-\(11\) fiber has \(7043\) sources:
\(4932\) have a unique admissible pair, \(4411\) have prime cofactor, and
\(5367\) have generated cofactor. It is never treated as bounded.

| maximum \(P(h)\) | all hard | all-hole \(J\) | mixed \(K\) |
|---:|---:|---:|---:|
| 1 | 25427 | 6130 | 19297 |
| 2 | 42544 | 7074 | 35470 |
| 4 | 45420 | 7083 | 38337 |
| 8 | 45580 | 7083 | 38497 |
| 16 | 45583 | 7083 | 38500 |

## 5. Exact falsifier to the component proof

A tempting proof of \(J\le E\) makes a graph on holes:

* a splitless hole contributes no edge;
* an inherited odd, seed-3, or mixed hard hole contributes one parent edge;
* an all-hole hard source contributes two edges to one admissible pair.

If every component were a pseudoforest, edge counting would give \(J\le E\).
The checker chooses a pair minimizing the resulting cyclomatic number.

This certificate fails. The first cycle is created at

\[
 666+1=23\cdot29.
\]

By \(10^4\), one component has cyclomatic number \(77\); by \(10^6\), the
maximum is \(6110\). Thus neither a forest nor this strongest greedy
pseudoforest implementation explains (12). A proof of \(J\le E\) needs
global cancellation rather than this component Euler characteristic.

## 6. A precise conditional sieve for \(J\)

Let

\[
 \mathscr G_2=\{\ell:\ell\text{ prime},\ \ell\equiv2\pmod3,\ \ell\in G\}.
\]

Apart from \(O(\sqrt X)\) equal-factor cases, every successor \(N=h+1\)
of an all-hole source avoids all primes in \(\mathscr G_2\). If such a
prime \(\ell\) divides \(N\), then \(N/\ell\) is allowed by (1), and the
distinct pair \((\ell,N/\ell)\) has a generated endpoint, contrary to the
definition of \(J\).

Consequently,

\[
 \sum_{\ell\in\mathscr G_2}{1\over\ell}=\infty
 \quad\Longrightarrow\quad J(X)=o(X) \tag{13}
\]

by finite-prime inclusion-exclusion.

No divergence theorem for generated primes is known here. Equation (13)
is a precise theorem-strength obstruction, not a completed step.

## 7. Reproduction and exactness

All acceptance arithmetic is integral. From the repository root run:

    python problems/424/compute/wave4/C49_hard_sieve/probe_hard_sieve.py --limit 1000000 --thresholds 100,1000,10000,100000 --output problems/424/compute/wave4/C49_hard_sieve/pair_sieve_1e6.json

    python problems/424/compute/wave4/C49_hard_sieve/verify_pair_count.py --limit 1000000 --output problems/424/compute/wave4/C49_hard_sieve/pair_bound_independent_1e6.json

The independent verifier does not reconstruct \(G\). It scans all
\(113571\) reducible odd successors of the two hard residue shapes through
\(10^6\). It finds no failure of either

\[
 \Omega_2(N)\le4P(N-1)+2
\]

or

\[
 P(N-1)+1\ge2^{\omega_2^{(1)}(N)-2}.
\]

The first inequality is attained by \(N=15625=5^6\).

SHA-256:

    probe_hard_sieve.py                  9105B6D6E85BD3098DB7724F69CB824C97F142B9A5B46C711484660B134403E6
    pair_sieve_1e6.json                  6D912172ED3E93DAC7F02B77D0C107A50808B7A4D46D716ABD2D1C52875A5215
    verify_pair_count.py                 4DB3B85E3EFD9A33AA000FBC0BEECE49C472ACF825651A8F68C3814EFAA93959
    pair_bound_independent_1e6.json      BF8DEA6ED1DC318E2CCE74705ECA213C5FC6C7261DBCD036C892EEBCA55EB161
