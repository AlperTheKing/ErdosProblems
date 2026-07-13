# P19: same-parity three-sum-free Sidon sets

## Verdict

The asymptotic target

\[
  \max E\ge (3-o(1))|E|^2                                      \tag{1}
\]

is not proved or disproved here. This lane does, however, give an exact
infinite falsifier to a natural stability bridge:

> **False bridge (quadratic-span top-third localization).** If
> $E$ is a same-parity Sidon set with $E\cap3E=\varnothing$ and
> $\max E=O(|E|^2)$, then all but $o(|E|)$ elements of $E$ lie
> above $(\max E)/3$.

There are infinitely many such sets with

\[
  \max E < 4|E|^2,
  \qquad
  \left|E\cap\left[1,{\max E\over3}\right]\right|
     \ge \left({1\over6}-o(1)\right)|E|.                \tag{2}
\]

The construction is a residue-separated lift of a Bose--Chowla modular
Sidon set [1,2]. It is exact, includes diagonal pair sums, and allows repeated
summands in $3E$. Thus a successful top-third argument must use the
*numerical near-extremal hypothesis* $\max E\le(3+o(1))|E|^2$, not merely
quadratic span.

There is a second exact falsifier: checking only that the maximum element is
not a three-sum is insufficient, even for a Sidon set of one parity. A
seven-element example has $\max E\notin3E$ but three smaller elements in
$E\cap3E$.

The surviving formulation is consequently a structured-hole problem: the
condition does not provide one hole in a threefold sumset, but an entire
translate of the high part of the ruler. Neither P13's weak occupation law
nor a one-hole coverage theorem retains this information.

## 1. Exact normalization

Let

\[
  Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},\qquad G\ge1,
\]

and put

\[
  E=G+2Z,\qquad L=\max E=G+2W.                           \tag{3}
\]

Then all elements of $E$ are positive and have one parity. The identities

\[
 {e_j-e_i\over2}=z_j-z_i,
 \qquad
 {e_i+e_j\over2}=G+z_i+z_j                              \tag{4}
\]

show that the following are equivalent:

1. $E$ is Sidon for unordered sums, including $e_i+e_i$, and
   $E\cap3E=\varnothing$;
2. $Z$ is Sidon and
   $D^+(Z)\cap(G+S(Z))=\varnothing$, where diagonals belong to $S(Z)$;
3. $Z$ is Sidon and
   $Z\cap(G+3Z)=\varnothing$, with repetitions allowed in $3Z$.

For the last equivalence, a collision is exactly

\[
 z_j-z_i=G+z_a+z_b
 \quad\Longleftrightarrow\quad
 z_j=G+z_i+z_a+z_b.                                    \tag{5}
\]

In particular, define

\[
  \mathcal H_G(Z)=\{z-G:z\in Z,\ z\ge G\}.
\]

The full condition is the structured-hole inclusion

\[
  \boxed{\mathcal H_G(Z)\subseteq[0,W-G]\setminus3Z.}   \tag{6}
\]

This records up to $p$ correlated holes. Replacing (6) by the single
necessary condition $W-G\notin3Z$ loses load-bearing information.

The terminology is compatible with Bajnok--Ruzsa [3]: $E\cap3E=\varnothing$
is literal $(3,1)$-sum-freeness, with repeated summands allowed. In the odd
subcase, parity also gives $E\cap2E=\varnothing$, so Sidonicity plus (6)
is the corresponding positive-integer weight-four independence condition.

## 2. The exact coefficient-2 baseline

The direct signed-ruler count reaches coefficient $2$, and no more. This
is included to isolate precisely what the falsifiers below do not prove.

For $1\le h<p$, take all differences of index lag at most $h$:

\[
 \mathcal D_h=\{z_{i+r}-z_i:1\le r\le h, 0\le i<p-r\}.
\]

Sidonicity makes these

\[
 M_h=hp-{h(h+1)\over2}                                  \tag{7}
\]

positive integers distinct. Hence their sum is at least

\[
 {M_h(M_h+1)\over2}.                                    \tag{8}
\]

If $g_j=z_{j+1}-z_j$, then a fixed gap $g_j$ occurs at most $r$
times among lag-$r$ differences. Therefore

\[
 \sum_{d\in\mathcal D_h}d
 \le\sum_{r=1}^h r\sum_jg_j
 ={h(h+1)\over2}W.                                      \tag{9}
\]

Combining (8)--(9) gives the exact inequality

\[
 W\ge {M_h(M_h+1)\over h(h+1)}.                         \tag{10}
\]

With $h=\lfloor\sqrt p\rfloor$,

\[
 W\ge p^2-O(p^{3/2}),
 \qquad
 L=G+2W\ge2p^2-O(p^{3/2}).                              \tag{11}
\]

The missing unit of $p^2$ must therefore come from the structured
three-sum holes (6), not from Sidonicity alone.

## 3. An infinite quadratic-span falsifier to top-third localization

We first recall the required modular Sidon object, including its proof.

### Lemma 1 (Bose--Chowla modular ruler)

For every prime power $q$, with $n=q^2-1$, there is a $q$-element
set $C\subseteq\mathbb Z_n$ whose unordered two-sums, diagonals included,
are unique modulo $n$.

### Proof

Let $K=\mathbb F_{q^2}$, choose $\theta\in K\setminus\mathbb F_q$,
and let $\gamma$ generate $K^*$. For $a\in\mathbb F_q$, define
$c_a\in\mathbb Z_n$ by

\[
  \gamma^{c_a}=\theta+a.
\]

If $c_a+c_b=c_c+c_d$ modulo $n$, then

\[
  (\theta+a)(\theta+b)=(\theta+c)(\theta+d).
\]

Comparing the coefficients of $1,\theta$ gives

\[
 a+b=c+d,\qquad ab=cd.
\]

Thus the two unordered pairs are equal, including when either pair is a
diagonal. QED.

Translate $C$ by $t\in\mathbb Z_n$, and let $B_t\subseteq[0,n-1]$
be the least nonnegative representatives of $C+t$. Modular Sidonicity
implies literal integer Sidonicity of every $B_t$.

Put

\[
 K_q=\left\lfloor{q(q-1)-1\over6}\right\rfloor.         \tag{12}
\]

Averaging over the $n$ translations gives

\[
 {1\over n}\sum_{t\in\mathbb Z_n}|B_t\cap[0,K_q]|
 ={q(K_q+1)\over n}
 =\left({1\over6}-o(1)\right)q.                         \tag{13}
\]

Choose a translation attaining at least this average, write $B=B_t$,
and let $W=\max B$. Its $\binom q2$ positive differences are distinct
integers in $[1,W]$, so

\[
  W\ge {q(q-1)\over2}.                                  \tag{14}
\]

Now define

\[
  E=1+4B.                                                \tag{15}
\]

This is a $q$-element set of positive odd integers. It is Sidon because
an equality between two unordered sums in $E$, after subtracting $2$
and dividing by $4$, is an equality between two unordered sums in $B$.
Moreover,

\[
 E\equiv1\pmod4,\qquad 3E\equiv3\pmod4,                 \tag{16}
\]

so $E\cap3E=\varnothing$. Equation (16) includes triples with repeated
summands.

Let $L=\max E=1+4W$. Since $W\le n-1=q^2-2$,

\[
 L\le4q^2-7<4q^2.                                      \tag{17}
\]

For every $b\le K_q$, equations (12) and (14) give

\[
 6b\le q(q-1)-1\le2W-1.
\]

This is exactly

\[
  1+4b\le {1+4W\over3}={L\over3}.                      \tag{18}
\]

Consequently (13) proves

\[
 \left|E\cap[1,L/3]\right|
 \ge {q(K_q+1)\over q^2-1}
 =\left({1\over6}-o(1)\right)q.                        \tag{19}
\]

Equations (15)--(19) prove the announced infinite falsifier (2).

### Consequence

Neither $E\cap3E=\varnothing$, Sidonicity, nor the additional assumption
$\max E=O(p^2)$ forces top-third concentration. A valid stability lemma
may still hold under the contradiction hypothesis

\[
  \max E\le(3-\varepsilon)p^2,                           \tag{20}
\]

but the constant in (20) must be used quantitatively. Omitting it is a
false strengthening, not a harmless simplification.

## 4. Exact falsifier to a maximum-only three-sum check

Take

\[
 Z=\{0,2,3,9,13,31,36\},\qquad G=6.                    \tag{21}
\]

Its complete unordered two-sum certificate is

\[
\begin{aligned}
S(Z)=\{&0,2,3,4,5,6,9,11,12,13,15,16,18,22,26,31,33,34,\\
       &36,38,39,40,44,45,49,62,67,72\}.
\end{aligned}                                           \tag{22}
\]

There are $28=\binom{8}{2}$ displayed values, so $Z$ is Sidon with
diagonals included. Direct enumeration of the 84 unordered triples gives
69 distinct values and, in particular,

\[
  W-G=30\notin3Z.                                       \tag{23}
\]

Nevertheless,

\[
 9=6+0+0+3,qquad
 13=6+2+2+3,qquad
 31=6+3+9+13.                                           \tag{24}
\]

Thus $Z\cap(G+3Z)\ne\varnothing$. In the $E$-normalization,

\[
 E=6+2Z=\{6,10,12,24,32,68,78\}.                       \tag{25}
\]

It is a same-parity Sidon set and

\[
 78\notin3E,
\]

but

\[
 24=6+6+12,qquad
 32=10+10+12,qquad
 68=12+24+32.                                           \tag{26}
\]

Hence the concrete bridge

\[
 \max E\notin3E\quad\Longrightarrow\quad E\cap3E=\varnothing
\]

is false even after imposing same parity and literal Sidonicity. In ruler
language, one cannot replace the structured family (6) by its endpoint
$W-G$.

## 5. Independent elementary finite audit

The following carry-free family was checked symbolically and by literal
enumeration. For every odd prime $q$, let

\[
 b_i=2qi+[i^2]_q\quad(0\le i<q),\qquad
 E_q=\{1+4b_i:0\le i<q\},                               \tag{27}
\]

where $[i^2]_q\in[0,q-1]$ is the least residue.

If $b_i+b_j=b_k+b_l$, then

\[
 2q(i+j-k-l)=[k^2]_q+[l^2]_q-[i^2]_q-[j^2]_q.
\]

The right side has absolute value strictly below $2q$; hence
$i+j=k+l$. Reduction modulo $q$ then gives
$ij=kl$, so the unordered pairs coincide. Thus (27) is Sidon, including
diagonals, while $E_q\cap3E_q=\varnothing$ follows from (16).

Its maximum is exactly

\[
 8q^2-8q+5,                                              \tag{28}
\]

because $b_{q-1}=2q(q-1)+1$, and this exceeds every earlier $b_i$.
For every

\[
 0\le i\le\left\lfloor{q-3\over3}\right\rfloor,
\]

the bound ([i^2]_q\le q-1) gives

\[
 3(1+4b_i)\le8q^2-8q+5=\max E_q.                        \tag{29}
\]

Thus at least $\lfloor(q-3)/3\rfloor+1$ elements lie below one third of
the maximum. Literal enumeration for every odd prime $5\le q\le59$
confirmed all pair sums distinct, no intersection with $3E_q$, formula
(28), and the stated low-third count. The symbolic derivation, not this
finite audit, proves the family for every odd prime.

## 6. What remains open

The construction in Section 3 has coefficient $4$, not a coefficient below
$3$, so it is not a disproof of (1). The exact remaining assertion can be
stated without weak limits:

> If $Z\subseteq[0,W]$ is a $p$-element Sidon ruler and $G\ge1$
> satisfies the structured-hole condition (6), prove
> 
> \[
>   G+2W\ge(3-o(1))p^2,
> \]
> 
> or construct an infinite exact counterfamily.

P13 shows that weak occupation measures permit microscopic checkerboarding,
and Section 3 shows that broad top-third localization is false even at
quadratic span. Section 4 shows that one endpoint hole is also insufficient.
The next viable lemma must therefore use all of the correlated holes
$z-G$, together with the fact that the same Sidon ruler generates both
the holes and $3Z$. A residue-class or interval-density statement that
does not retain this coupling cannot close the coefficient $3$.

## References

1. R. C. Bose and S. Chowla, **Theorems in the additive theory of
   numbers**, *Commentarii Mathematici Helvetici* **37** (1962/63),
   141--147. DOI: [10.1007/BF02566968](https://doi.org/10.1007/BF02566968).

2. M. B. Nathanson, **The Bose--Chowla argument for Sidon sets**,
   *Journal of Number Theory* **238** (2022), 133--146.
   DOI: [10.1016/j.jnt.2021.08.005](https://doi.org/10.1016/j.jnt.2021.08.005);
   [arXiv:2104.12711](https://arxiv.org/abs/2104.12711).

3. B. Bajnok and I. Z. Ruzsa, **The independence number of a subset of an
   abelian group**, *Integers* **3** (2003), Paper A02, 23 pp.
   [EuDML 122918](https://eudml.org/doc/122918);
   [arXiv:1512.03037](https://arxiv.org/abs/1512.03037).
