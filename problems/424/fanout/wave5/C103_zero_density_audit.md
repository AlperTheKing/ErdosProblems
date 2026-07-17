# C103: zero-density audit

## Verdict

No proof that

\[
 \liminf_{X\to\infty}\frac{|G\cap[1,X]|}{X}=0
\]

was found, and the exact census does not supply a proved sparse subsequence.
There is, however, a rigorous obstruction to the proposed derivation-tree,
entropy, and uncorrected multiplicative-table routes:

> **C103 obstruction.** Counting all admissible derivation trees is already
> superlinear on an explicit sequence of cutoffs, using only licensed affine
> spines with multipliers `2,3,5`. The evaluation map on these trees has
> fibers of unbounded, explicitly exponential average size relative to the
> cutoff. Moreover, the direct root-factor renewal inequality is
> supercritical at every exponent at most one, since
> `1/2+1/3+1/5=31/30>1`.

Thus a tree-complexity upper bound for full `G` must include a global
canonicalization or collision theorem. A bounded-multiplicity encoding,
leaf counting alone, a fixed-depth union, or replacement of generated
factors by their residue envelope cannot prove zero lower density.

## 1. Exact complexity recurrence

For a generated value `n`, let `h(n)` be its minimum derivation-tree height
and let `ell(n)` be its minimum number of leaves. The seeds have

\[
 h(2)=h(3)=0,\qquad \ell(2)=\ell(3)=1.
\]

Because every child of a nonseed value is smaller than that value, the exact
ascending recurrences are

\[
\begin{split}
 h(n)&=1+\min_{ab=n+1\atop a,b\in G,\ a<b}\max(h(a),h(b)),\\
 \ell(n)&=\min_{ab=n+1\atop a,b\in G,\ a<b}(\ell(a)+\ell(b)).
\end{split}                                                    \tag{1}
\]

The minimum is undefined exactly when `n` is not generated.

### Lemma 1 (sharp leaf-value floor)

If a nonleaf admissible derivation tree has `L` leaves and value `v`, then

\[
                         v\ge 2^L+1.                           \tag{2}
\]

The bound is sharp for every `L>=2`.

**Proof.** For `L=2`, distinctness forces the children to be `2,3`, so the
value is `5=2^2+1`. Suppose the root subtrees have `i,j` leaves. If one is a
leaf, its value is at least `2`; the other, when nonleaf, is at least
`2^j+1`, giving

\[
                   2(2^j+1)-1=2^{j+1}+1.
\]

If both are nonleaves, induction gives

\[
 (2^i+1)(2^j+1)-1
 =2^{i+j}+2^i+2^j\ge 2^{i+j}+1.
\]

Finally, `v_2=5` and `v_{L+1}=2v_L-1` are licensed derivations and give
`v_L=2^L+1`. QED.

Consequently every derivation of a value at most `X` has at most
`floor(log_2(X-1))` leaves. Lemma 1 is the strongest possible uniform
improvement based only on leaf count: the `2`-spine attains equality.

## 2. Affine-spine entropy barrier

Put

\[
 T_d(x)=dx-1,\qquad D=\{2,3,5\}.
\]

The values `2,3,5,9` lie in `G`, with `5=2*3-1` and `9=2*5-1`. Starting
from `9`, every word in the maps `T_2,T_3,T_5` is licensed: the current
value remains greater than `5`, and hence is distinct from the selected
multiplier.

Define

\[
 Q=2^{15}3^{10}5^6=30233088000000.                            \tag{3}
\]

Let `Omega_m` be the words containing exactly `15m` letters `2`, `10m`
letters `3`, and `6m` letters `5`. Then

\[
 W_m:=|\Omega_m|=\frac{(31m)!}{(15m)!(10m)!(6m)!}.            \tag{4}
\]

### Theorem 2 (superlinear admissible-tree count)

Let `T(X)` be the number of syntactically distinct admissible derivation
trees whose values are at most `X`. For `X_m=9Q^m`,

\[
 \frac{T(X_m)}{X_m}
 \ge \frac{W_m}{9Q^m}
 \ge \frac{(31/30)^{31m}}{9(31m+1)^2}
 \longrightarrow\infty.                                     \tag{5}
\]

In particular, an upper bound obtained by counting all admissible trees
cannot be `o(X)`, or even `O(X)`.

**Proof.** Applying a word in `Omega_m` to `9` gives a value strictly less
than `9Q^m`. Distinct words give distinct trees: at each spine node the child
with value in `D` identifies the last letter, while the other child has
value greater than `5`, so the word can be read backwards from the tree.
Thus `T(X_m)>=W_m`.

For the second inequality, use the multinomial distribution with

\[
 (q_2,q_3,q_5)=\left(\frac{15}{31},\frac{10}{31},\frac6{31}\right)
\]

and `31m` trials. Its exact mean type `(15m,10m,6m)` is a mode. There are at
most `(31m+1)^2` types, so the probability of this type is at least the
reciprocal of that number. Therefore

\[
 W_m\ge \frac1{(31m+1)^2}
 \left(\frac{31}{15}\right)^{15m}
 \left(\frac{31}{10}\right)^{10m}
 \left(\frac{31}{6}\right)^{6m}.                             \tag{6}
\]

Dividing the exponential factor in (6) by `Q^m` gives the exact identity

\[
 \frac{1}{Q^m}
 \left(\frac{31}{15}\right)^{15m}
 \left(\frac{31}{10}\right)^{10m}
 \left(\frac{31}{6}\right)^{6m}
 =\left(\frac{31}{30}\right)^{31m}.                          \tag{7}
\]

Equations (6) and (7) prove (5). QED.

### Corollary 3 (collision burden)

Let `R_m(v)` count words in `Omega_m` evaluating to `v` from `9`. Then

\[
 \max_v R_m(v)\ge \frac{W_m}{9Q^m}
 \ge\frac{(31/30)^{31m}}{9(31m+1)^2}\to\infty.               \tag{8}
\]

This is pigeonhole applied to at most `9Q^m` integer output slots. Hence no
bounded-to-one tree decoder survives even on this affine-spine subfamily.
A canonical one-tree-per-value scheme is not ruled out, but constructing it
requires the global collision information that raw tree complexity omits.

The exact certificate records `W_m>9Q^m` first at `m=8`. The elementary
lower bound in (5) exceeds one at `m=15`; two exact integer inequalities in
the artifact, together with monotonicity of
`(31m+1)/(31m+32)`, certify it for every `m>=15`.

## 3. Root-renewal obstruction

Write `A(X)=|G intersect [1,X]|`. Choosing a root factorization for each
nonseed member and then forgetting collisions gives, for `X>=24`,

\[
 A(X)\le 2+
 \sum_{a\in G\atop 2\le a\le\sqrt{X+1}}
 A\left(\left\lfloor\frac{X+1}{a}\right\rfloor\right).       \tag{9}
\]

If one tries to close (9) inductively with `A(Y)<=C Y^theta`, its renewal
coefficient is at least

\[
 2^{-\theta}+3^{-\theta}+5^{-\theta}
 \ge \frac12+\frac13+\frac15=\frac{31}{30}>1
 \qquad(\theta\le1).                                         \tag{10}
\]

Therefore the standard single-exponent tree or divisor recurrence cannot
prove any sublinear bound for full `G`. This does not prohibit a
collision-corrected recurrence; it identifies the missing term precisely.
At the canonical type scale, that correction must absorb at least the
factor in (8).

## 4. Multiplicative-table envelope

The exact membership recurrence can be written as the set identity

\[
 G\cap[4,X]
 =\{ab-1\le X:a,b\in G,\ 2\le a<b\}.                         \tag{11}
\]

Let `R` be the residue envelope consisting of positive integers congruent
to `0` or `2` modulo `3`. Replacing both copies of `G` in (11) by `R` loses
all useful density information:

\[
 \left|\{ab-1\le X:a,b\in R,\ 2\le a<b\}\right|
 =\frac{2X}{3}+o(X).                                         \tag{12}
\]

Indeed, if `N=ab` is `1 mod 3`, a prime divisor `p=2 mod 3` supplies the
split `p*(N/p)`, except for a square. If `3|N`, either `3*(N/3)` works, or,
after removing the unique factor `3`, a prime divisor `2 mod 3` supplies a
split. The exceptions are contained in primes, squares, and fixed multiples
of integers having no prime divisor `2 mod 3`. The last set has density zero
because the reciprocal sum of primes `2 mod 3` diverges. This is the
splitless estimate already proved in C13, now read as a saturation theorem
for the ambient multiplicative table.

Thus Ford-type or entropy estimates applied only after replacing generated
factors by their congruence envelope cannot improve the existing `2/3`
upper bound. A viable negative argument must preserve recursive membership
information at unbounded scales.

## 5. Exact computation

`C103_zero_density_probe.cpp` implements (1) by exact ascending divisor
enumeration. It also counts all root witnesses and records exact density
extrema; no floating-point operation enters membership or any count.

| limit | `A(limit)` | max minimum height | max minimum leaves |
|---:|---:|---:|---:|
| `100000` | `39843` | `14` | `16` |
| `1000000` | `457599` | `17` | `19` |
| `10000000` | `4952270` | `19` | `23` |
| `100000000` | `51899129` | `20` | `26` |

The four counts reproduce the existing exact census checkpoints. At
`10^8`, among `51,899,127` nonseed members:

- `43,659,183` have a root witness using `2`, `3`, or `5`;
- `8,239,944` have no such root witness (the first is `125`);
- `31,933,606` have at least two distinct root factor pairs;
- the total number of root factor pairs is `123,849,749`.

These are exact finite facts, not asymptotic estimates. Likewise, the
checked power-of-two ratios rise from
`480838/1048576` at `2^20` to `34597621/67108864` at `2^26`; they do not
constitute a candidate sparse subsequence with a proof mechanism.

Artifacts:

- `problems/424/compute/wave5/C103_zero_density_probe.cpp`
- `problems/424/compute/wave5/C103_zero_density_probe_100k.json`
- `problems/424/compute/wave5/C103_zero_density_probe_1e6.json`
- `problems/424/compute/wave5/C103_zero_density_probe_1e7.json`
- `problems/424/compute/wave5/C103_zero_density_probe_1e8.json`
- `problems/424/compute/wave5/C103_entropy_certificate.py`
- `problems/424/compute/wave5/C103_entropy_certificate_100.json`
- `problems/424/compute/wave5/C103_verify.py`

The verifier independently recomputes the closure, minimum complexities,
root witnesses, checkpoints, and density extrema through `100000`, and
recomputes every multinomial integer in the entropy certificate.

## 6. Prior-work boundary and final status

C13 already proves that splitless residue-allowed outputs are `o(X)`. C36
and the R2 digest already record the canonical word-count surplus
`W_m/Q^m`; they use it to audit a proposed positive-density mass gate. The
new C103 point is the negative-method consequence: the same surplus gives
the explicit superlinear tree theorem (5), the unbounded evaluation-fiber
bound (8), and the supercritical full-root recurrence (10). Lemma 1 supplies
the sharp target-seed leaf floor and shows that improving value growth alone
cannot remove this obstruction.

Accordingly, the negative direction remains logically open, but the four
requested generic mechanisms do not currently yield it:

1. unquotiented derivation-tree complexity is superlinear by Theorem 2;
2. raw entropy has the same `31/30` supercritical barrier;
3. the residue-envelope multiplicative table has density `2/3+o(1)`;
4. exact standard cutoffs through `10^8` provide no proved sparse sequence.

Any surviving zero-density route must prove a global collision quotient for
all derivation shapes, not only fixed affine or bounded-depth subsystems, or
exhibit an arithmetic sparse sequence with an independent asymptotic sieve.
