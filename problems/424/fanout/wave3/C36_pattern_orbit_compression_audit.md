# C36: pattern-orbit compression audit

## Verdict

The fixed-block orbit theorem is correct, with two necessary conventions:

1. words are in the repository's outermost-first orientation; and
2. each selected six-block is a consecutive interval of positions.

With $B=\lfloor k/2\rfloor$, let $r(w)$ be the number of selected
blocks of $w\in\Omega_k$ equal to either

\[
 U=552223,\qquad V=232552.
\]

For every $k\ge2$, the argument gives the explicit theorem

\[
 \boxed{
 \frac{D_k}{W_k}
 \le \mathbb E_{w\in\Omega_k}2^{-r(w)}
 \le
 \left(\frac{887394817}{887503681}\right)^{\lfloor k/2\rfloor}
 \le \exp\!\left(-\frac{36288}{887503681}k\right),
 }
 \tag{1}
\]

where $W_k:=|\Omega_k|$. Thus a hypothetical lower bound
$D_k\gg W_k/\sqrt{k}$ is false.

This does **not** falsify the actual R-D mass gate

\[
 D_k\ge c\frac{Q^k}{\sqrt{k}},
 \qquad Q=2^{15}3^{10}5^6=30233088000000.       \tag{M}
\]

Indeed, the fixed-block exponent in (1) is far too small compared with the
multinomial surplus. More strongly, the full contextual congruence generated
by $U=V$, allowing arbitrary and overlapping occurrences and arbitrarily
many rewrites, still has more than $Q^k$ classes on the subsequence
$k\in25\mathbb N$. Therefore this relation alone cannot supply a
class-count upper bound that kills (M). This is not a lower bound on $D_k$:
additional affine relations may merge those congruence classes. The status of
(M) is unchanged.

## 1. Orientation and contextual validity

Write $q_2=0,q_3=1,q_5=3$, and for an outermost-first word
$w=w_1\cdots w_n$ define

\[
 L_w=L_{w_1}\circ\cdots\circ L_{w_n}.
\]

Its offset is

\[
 d(w)=\sum_{i=1}^n q_{w_i}\prod_{h<i}w_h.             \tag{2}
\]

Both displayed words have count vector $(3,1,2)$, slope $600$, and

\[
\begin{aligned}
 d(U)&=3+5\cdot3+(5\cdot5\cdot2\cdot2\cdot2)\cdot1
      =218,\\
 d(V)&=2\cdot1+(2\cdot3\cdot2)\cdot3
            +(2\cdot3\cdot2\cdot5)\cdot3
      =218.
\end{aligned}                                        \tag{3}
\]

Hence

\[
                 L_U(t)=L_V(t)=600t+218.              \tag{4}
\]

This orientation is essential. If the displayed letters are instead applied
chronologically from left to right, the offsets are respectively $433$ and
$136$, so there is no relation.

For arbitrary outer and inner contexts $A,C$, concatenation gives

\[
 L_{AUC}=L_A\circ L_U\circ L_C
        =L_A\circ L_V\circ L_C=L_{AVC}.               \tag{5}
\]

Thus replacement in a consecutive subword is context-valid on both sides.
An arbitrary set of six nonconsecutive coordinates would not have this
property.

## 2. Exact orbit count

Fix $B$ pairwise disjoint consecutive six-position intervals. For each
$1\le j\le B$, define an involution $\tau_j$ on $\Omega_k$: it swaps
$U$ and $V$ in interval $j$, and fixes a word when that interval is
neither $U$ nor $V$.

The maps $\tau_j$ commute because their intervals are disjoint. They
preserve the global letter counts, and (5) shows that they preserve the full
affine map. If

\[
 r(w)=\#\{j:\text{block }j\text{ of }w\text{ is }U\text{ or }V\},
\]

then exactly $B-r(w)$ generators fix $w$, while the other $r(w)$
coordinates toggle independently. Consequently

\[
             |\operatorname{Orb}(w)|=2^{r(w)}.        \tag{6}
\]

The value of $r$ is constant on each orbit. If $N_k$ is the number of
these fixed-slot orbits, orbit-stabilizer counting gives the exact identity

\[
 N_k=\sum_{\mathcal O}1
    =\sum_{w\in\Omega_k}\frac1{|\operatorname{Orb}(w)|}
    =\sum_{w\in\Omega_k}2^{-r(w)}.                    \tag{7}
\]

Every orbit lies in one affine-map fiber. All words in $\Omega_k$ have
the same slope $Q^k$, so affine-map fibers and offset fibers coincide.
Different toggle orbits may have the same offset; therefore the inequality
has the required direction:

\[
                 D_k\le N_k=W_k\mathbb E2^{-r}.       \tag{8}
\]

## 3. Uniform conditional probability

Take $B=\lfloor k/2\rfloor$, and reveal the selected blocks in a fixed
order. Let $\mathcal F_{j-1}$ record the exact letters in the first
$j-1$ revealed blocks. Given a positive-probability history, let
$a,b,c$ be the remaining numbers of $2,3,5$, and let $N=a+b+c$.
The current ordered block is sampling without replacement, so, with
$(x)_s=x(x-1)\cdots(x-s+1)$,

\[
 \Pr(I_j=1\mid\mathcal F_{j-1})
 =\frac{2(a)_3b(c)_2}{(N)_6},                         \tag{9}
\]

where $I_j$ indicates that the block is $U$ or $V$. The factor $2$
is exact because $U,V$ are distinct ordered words with the same content.

For $k\ge2$ and $j\le B$, the number $s=6(j-1)$ of already revealed
letters satisfies

\[
 s\le 6(B-1)\le3k-6.                                 \tag{10}
\]

Thus, even if all exposed letters came from one species,

\[
 a\ge12k+6,\qquad b\ge7k+6,\qquad c\ge3k+6,
 \qquad N\le31k.                                     \tag{11}
\]

It follows directly from (9) that every exact history obeys

\[
\begin{aligned}
 \Pr(I_j=1\mid\mathcal F_{j-1})
 &\ge
 \frac{2(12k)^3(7k)(3k)^2}{(31k)^6}\\
 &=\frac{217728}{887503681}=:p_0.                    \tag{12}
\end{aligned}
\]

This also implies the same bound under the coarser conditioning that records
only earlier good/bad indicators, by averaging over exact histories.

No independence is needed. Since

\[
 2^{-r}=\prod_{j=1}^B\left(1-\frac{I_j}{2}\right),
\]

(12) gives

\[
 \mathbb E\left[1-\frac{I_j}{2}\mid\mathcal F_{j-1}\right]
 \le1-\frac{p_0}{2}.
\]

Successive conditioning therefore yields

\[
 \mathbb E2^{-r}\le(1-p_0/2)^B
 =\left(\frac{887394817}{887503681}\right)^B.         \tag{13}
\]

Finally $B\ge k/3$ for every $k\ge2$, and $1-x\le e^{-x}$, proving
the final exponential estimate in (1).

### Small-$k$ and parity check

For $k=2m$, the largest prior exposure is $6(m-1)=3k-6$. For
$k=2m+1\ge3$, it is $6(m-1)=3k-9$. Hence (10) covers both parities.
Also $6B\le3k<31k$, so the fixed intervals fit. At $k=1$, $B=0$:
the orbit argument gives only $D_1/W_1\le1$, and the claimed uniform
conditional step is correctly restricted to $k\ge2$.

## 4. Correct comparison with the R-D gate

Stirling's formula at the canonical composition gives

\[
 W_k
 \sim \frac{\sqrt{31}}{60\pi k}
 \left[Q\left(\frac{31}{30}\right)^{31}\right]^k.    \tag{14}
\]

The word-count surplus over $Q^k$ has natural-log rate

\[
 \sigma=31\log(31/30)=1.01648450751272\ldots.         \tag{15}
\]

The explicit fixed-block bound removes only

\[
 -\frac12\log(1-p_0/2)
 =0.0000613353384766\ldots                             \tag{16}
\]

per unit $k$. Equivalently, for even $k$, (1) and (14) give an upper
bound with exponential base relative to $Q^k$

\[
 \left(\frac{31}{30}\right)^{31}
 \sqrt{\frac{887394817}{887503681}}
 =2.763293242341748\ldots>1.                          \tag{17}
\]

Thus (1) is exponentially strong relative to $W_k$, but its resulting
upper bound is still exponentially larger than $Q^k$. It gives no
contradiction to (M).

The constant $p_0$ is deliberately crude. The next section removes any
question that a sharper placement, overlapping occurrences, or adaptive
rewriting with the same relation might cross the $Q$-threshold.

## 5. The full $U=V$ congruence is still too large

Let $\equiv_R$ be the smallest contextual word congruence generated by
$U=V$, and let $C_k$ be its number of classes in $\Omega_k$. Quotienting
by all consequences of this single relation gives

\[
                       D_k\le C_k.                    \tag{18}
\]

Both $U$ and $V$ contain the consecutive pattern $552$: it is the
prefix of $U$ and the suffix of $V$. Hence a word avoiding $552$ has
no available $U\leftrightarrow V$ move and is an isolated
$\equiv_R$-class.

Let $A_k$ count words in $\Omega_k$ which start with $3$ and avoid
$552$. The initial $3$ leaves content
$(15k,10k-1,6k)$. The pattern $552$ is unbordered: no nonempty proper
prefix is a suffix. Distinct occurrences therefore do not overlap. Marking
$j$ occurrences and contracting each marked copy to one new symbol gives
exactly

\[
 \frac{(31k-1-2j)!}
 {j!(15k-j)!(10k-1)!(6k-2j)!}
\]

marked words. Inclusion-exclusion proves the exact finite formula

\[
 A_k=\sum_{j=0}^{3k}(-1)^j
 \frac{(31k-1-2j)!}
 {j!(15k-j)!(10k-1)!(6k-2j)!}.                       \tag{19}
\]

Exact integer evaluation of (19) gives

\[
              6A_{25}>7Q^{25},                       \tag{20}
\]

and in fact

\[
              \frac{A_{25}}{Q^{25}}
              =1.1855799446886064\ldots.              \tag{21}
\]

Now concatenate $m$ independently chosen words counted by $A_{25}$.
Every block begins with $3$, so no copy of $552$ can cross a block
boundary: a crossing triple contains that boundary $3$, whereas $552$
contains no $3$. The concatenation lies in $\Omega_{25m}$, still avoids
$552$, and hence is an isolated $\equiv_R$-class. Fixed-length parsing is
injective. Therefore

\[
 C_{25m}\ge A_{25}^m
 >Q^{25m}\left(\frac76\right)^m.                      \tag{22}
\]

The certified excess base per unit $k$ is

\[
                  (7/6)^{1/25}=1.0061850762710147\ldots. \tag{23}
\]

Equation (22) answers the stronger-use question. It covers every sequence
of contextual $U\leftrightarrow V$ replacements, not merely fixed
disjoint slots. The quotient defined by this relation itself remains
exponentially above $Q^k$ on an infinite subsequence, so relation-only
orbit compression cannot falsify (M). It remains possible that other affine
identities merge the isolated $\equiv_R$-classes; (22) makes no assertion
about their actual offsets.

## 6. Exact checker

Artifacts:

- `problems/424/compute/wave3/C36_pattern_orbit_compression/verify_pattern_orbit.py`
- `problems/424/compute/wave3/C36_pattern_orbit_compression/result.json`

Reproduction:

```powershell
python problems/424/compute/wave3/C36_pattern_orbit_compression/verify_pattern_orbit.py `
  --max-k 50 `
  --output problems/424/compute/wave3/C36_pattern_orbit_compression/result.json
```

The run performs the following exact checks:

- both word orientations and the affine identity (4);
- all $13{,}860$ words of the two-block content vector $(6,2,4)$, giving
  $13{,}741$ toggle orbits and exactly
  $\sum_w2^{-r(w)}=13{,}741$;
- every feasible prior depletion vector for each $2\le k\le50$, all above
  the rational $p_0$ in (12);
- formula (19) against brute force on 75 small count vectors comprising
  10,151 words; and
- the exact positive-integer certificate $6A_{25}-7Q^{25}>0$, stored in
  `result.json`.

The checker is supporting verification only. Equations (2)-(13) and
(19)-(22) are the proofs.

## Final classification

| Claim | Audit result |
|---|---|
| $L_U=L_V=600t+218$ | True only in outermost-first orientation |
| Context replacement preserves map and counts | True for consecutive subwords |
| Fixed-slot orbit size is $2^r$ | True |
| Orbit count is \(\sum_w2^{-r(w)}\) | True |
| Uniform conditional lower bound for $k\ge2$ | True with $p_0=217728/887503681$ |
| $D_k/W_k\le\exp(-\Omega(k))$ | True, explicitly (1) |
| Actual gate $D_k\gg Q^k/\sqrt{k}$ is false | **Not established** |
| Contextual rewriting by $U=V$ alone can kill (M) | No: the full relation quotient satisfies (22) |

The precise flaw in the proposed gate conclusion was the substitution of
the multinomial word count $W_k$ for the canonical slope scale $Q^k$.
The orbit theorem survives; the claimed R-D falsification does not.
