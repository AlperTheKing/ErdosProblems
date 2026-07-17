# C29: critical carry transform for the growing-block offset mass

## Verdict

No proof or asymptotic falsifier for the mass gate was obtained.

A new exact lemma does, however, put the canonical ray into a critical
probabilistic form. For the inverse offset branches there is an explicit
positive superharmonic function

\[
        \phi(d)=d+\frac{28}{59}.
\]

Its Doob transform turns every word producing a fixed offset into an
equiprobable path of a concrete killed Markov chain. The canonical mass gate
now follows from one explicit \(k^{-1/2}\) Markov-renewal/local-limit bound,
stated in Theorem 3 below. This is the reduced frontier.

Finite-block pressure, exact rewrite identities through length 14, independent
and correlated carry automata, and the exact support data through \(k=5\) were
also tested. None gives an asymptotic falsifier.

## 1. Definitions and orientation

Write

\[
L_m(t)=m t+q_m,\qquad (q_2,q_3,q_5)=(0,1,3).
\]

For \(v=(a,b,c)\), let \(R_v(d)\) be the number of words with those
letter counts and offset \(d\), and put

\[
D_v=\#\{d:R_v(d)>0\},\quad
M_v=2^a3^b5^c,\quad
W_v=\frac{(a+b+c)!}{a!b!c!}.
\]

Words in the recurrence code are written outermost letter first. Thus the
repository identity

    T_322255 = T_255232

is

    552223 = 232552

in recurrence orientation; both sides have offset \(218\).

The exact recurrence is

\[
R_v(d)=
 {\bf1}_{2\mid d}R_{v-e_2}(d/2)
 +{\bf1}_{d\equiv1(3)}R_{v-e_3}((d-1)/3)
 +{\bf1}_{d\equiv3(5)}R_{v-e_5}((d-3)/5).
\tag{1}
\]

## 2. Two elementary structural lemmas

### Lemma 1: concatenation injection

For all count vectors \(u,v\),

\[
             D_{u+v}\ge D_uD_v.                       \tag{2}
\]

**Proof.**
An outer block with map \(M_ut+d_u\) followed by an inner block with
map \(M_vt+d_v\) has offset

\[
                       d_u+M_ud_v.
\]

Since \(0\le d_u<M_u\), reduction modulo \(M_u\) recovers \(d_u\), and
then the quotient recovers \(d_v\). The map
\((d_u,d_v)\mapsto d_u+M_ud_v\) is injective. \(\square\)

This was exhaustively checked on 83,477 offset pairs with total word length at
most 8.

### Lemma 2: adjacent-swap formula

Let \(P\) be the multiplier of the outer prefix preceding adjacent letters
\(i,j\). Swapping those letters changes the offset by

\[
P\big((i-1)q_j-(j-1)q_i\big).                         \tag{3}
\]

For the ordered pairs \(23,25,35\), the unscaled differences are respectively
\(1,3,2\). Hence the offset is strictly monotone under every adjacent swap
that moves a smaller letter outward. In particular, every collision fiber is
an antichain in the multiset weak order.

The suffix cancels because the two adjacent products have the same slope;
the outer prefix multiplies their constant-term difference by \(P\).
Equation (3) passed 30,618 exhaustive swap checks at word length 8.

The antichain statement alone is much too weak for the exponential support
needed here.

## 3. The critical affine carry lemma

Put

\[
S=\frac{31}{30},\qquad C=\frac{28}{59},\qquad
\phi(d)=d+C.
\]

For a nonnegative function \(f\) on the nonnegative integers, define

\[
(\mathcal Tf)(d)=\frac1S
\sum_{\substack{m\in\{2,3,5\}\\d\equiv q_m\pmod m}}
f\left(\frac{d-q_m}{m}\right).                        \tag{4}
\]

### Theorem 1: exact superharmonic potential

For every \(d\ge0\),

\[
                         \mathcal T\phi(d)\le\phi(d),  \tag{5}
\]

with equality exactly when \(d\equiv28\pmod {30}\).

**Proof.**
For every real \(d\),

\[
\begin{aligned}
\frac{30}{31}\left[
\phi(d/2)+\phi((d-1)/3)+\phi((d-3)/5)\right]
&=d-\frac{28}{31}+\frac{90}{31}C\\
&=d+C=\phi(d).
\end{aligned}                                        \tag{6}
\]

For integer \(d\ge1\), every omitted, arithmetically unavailable term in
(6) is positive. The only small issue is the formal \(m=5\) term:
\(\phi(-2/5)=22/295>0\) at \(d=1\) and
\(\phi(-1/5)=81/295>0\) at \(d=2\). Therefore deleting unavailable
branches gives (5). At \(d=0\), the only branch is the \(m=2\) self-loop,
and \((30/31)C<C\).

Equality requires all three branches, which is equivalent by the Chinese
remainder theorem to \(d\equiv28\pmod {30}\). \(\square\)

The constant is forced: at a triple-branch integer, an affine potential
\(d+C'\) can satisfy the all-branch inequality only if
\(59C'\le28\). Thus \(28/59\) is the largest positive intercept in this
affine family, and it is the unique one making the full real identity
harmonic.

### Theorem 2: exact killed-chain representation

For each available inverse edge

\[
d\longrightarrow d'=\frac{d-q_m}{m},
\]

set

\[
K(d,d')=\frac1S\,\frac{\phi(d')}{\phi(d)}.             \tag{7}
\]

By Theorem 1, the row sum is at most one. Add the missing mass as a jump to
a cemetery state. This defines a killed Markov chain \(X_j\).

Let \(N_m(n)\) count the inverse edges of type \(m\) used in its first \(n\)
steps. Then for every \(v=(a,b,c)\), \(n=a+b+c\), and every \(d\),

\[
\Pr_d\!\left(
 X_n=0,\ (N_2(n),N_3(n),N_5(n))=v
\right)
=R_v(d)S^{-n}\frac{\phi(0)}{\phi(d)}.                 \tag{8}
\]

**Proof.**
Every inverse path counted by \(R_v(d)\) has probability

\[
\prod_{j=0}^{n-1}
\left(S^{-1}\frac{\phi(X_{j+1})}{\phi(X_j)}\right)
=S^{-n}\frac{\phi(0)}{\phi(d)}.
\]

The product telescopes and is independent of the path. Summing over the
\(R_v(d)\) paths proves (8). \(\square\)

The probability bound \(1\) gives the unconditional exact corollary

\[
R_v(d)\le
\frac{59}{28}S^n\left(d+\frac{28}{59}\right).          \tag{9}
\]

The linear factor in \(d\) makes (9) insufficient by itself. Its value is
the exact change of measure (8), not the raw upper bound.

## 4. A single sufficient local-limit frontier

Take the canonical vector and slope

\[
v_k=(15k,10k,6k),\qquad n=31k,\qquad
Q=2^{15}3^{10}5^6.
\]

The asymptotic branch probabilities in (7) are

\[
p_m=\frac{30}{31m},
\qquad (p_2,p_3,p_5)=\frac1{31}(15,10,6),              \tag{10}
\]

which is exactly the canonical composition.

### Theorem 3: concrete sufficient estimate

Suppose there is an absolute \(C_0\) such that, for every \(k\ge1\) and
every \(d\ge0\),

\[
\Pr_d\!\left(X_{31k}=0,\ N(31k)=v_k\right)
\le
\frac{C_0\phi(0)}{\phi(d)\sqrt{k}}.                   \tag{LL}
\]

Then there is \(c>0\) such that

\[
                         D_{v_k}\ge c\,\frac{Q^k}{\sqrt{k}}. \tag{11}
\]

**Proof.**
Equation (8) and (LL) give

\[
\max_dR_{v_k}(d)\le C_0\,\frac{S^{31k}}{\sqrt{k}}.     \tag{12}
\]

Stirling's formula gives the exact leading scale

\[
W_{v_k}
\sim
\frac{\sqrt{31}}{60\pi k}\,
Q^kS^{31k}.                                           \tag{13}
\]

Finally,

\[
D_{v_k}\ge
\frac{\sum_dR_{v_k}(d)}{\max_dR_{v_k}(d)}
=\frac{W_{v_k}}{\max_dR_{v_k}(d)}
\gg\frac{Q^k}{\sqrt{k}}.
\quad\square
\]

Thus the remaining load-bearing statement is not the original support gate:
it is the explicit killed-chain estimate (LL), with transition kernel (7)
and equality/cemetery structure fixed by Theorem 1.

A plausible proof technology is a Markov-renewal local limit plus a ballot
estimate. This is not asserted as proved. The endpoint condition fixes the
logarithmic radial displacement, leaving one Gaussian composition direction;
that explains the required \(k^{-1/2}\) rather than the ordinary
three-letter multinomial \(k^{-1}\).

## 5. Exact falsifier machinery

### 5.1 Finite-block quotient pressure

For a block length \(L\), define the exact polynomial

\[
P_L(x,y,z)=
\sum_{a+b+c=L}D_{a,b,c}x^ay^bz^c.                    \tag{14}
\]

Splitting every word into \(s\) consecutive length-\(L\) blocks gives

\[
D_{3k,2k,k}
\le [x^{3k}y^{2k}z^k]P_L(x,y,z)^s,
\qquad Ls=6k.                                         \tag{15}
\]

This follows because each block is determined up to one of its \(D_u\)
affine maps. Distinct block sequences may collide, so (15) is an upper
bound. Any positive rational evaluation of (14) whose resulting exponential
base is strictly below \(360\) would rigorously falsify the ray on an
infinite subsequence.

Exact support enumeration through \(L=12\) gave an optimized rational
coefficient base

    L=12: 424.9324692728857 = 1.1803679702 * 360.

It does not falsify the gate.

### 5.2 Exact rewrite-language pressure

Every equal-count identity was oriented from its lexicographically larger
word to its smaller word. A lex-minimal representative cannot contain an
oriented left side. Therefore the words avoiding any finite set of such
left sides form a rigorous regular-language upper bound for every \(D_v\).

All \(3^{14}\) words were enumerated exactly. Removing contextual rules left
2,454 primitive forbidden words and a 9,212-state Aho-Corasick automaton.
For every count vector through length 14, its avoidance count equaled the
exact number of affine classes; this is an exhaustive implementation check
at those lengths, not a completeness claim beyond length 14.

A positive-vector Collatz-Wielandt evaluation gave

    rewrite length <=14: base <= 408.3787475905756
    ratio to 360:         1.134385409973821

The strict inequality needed for a falsifier was not reached.

### 5.3 Carry-state bounds

An independently-maximized residue relaxation was proved valid and checked
on 87,490 exact endpoints. It is exponentially too lossy:

    Q=150, k=20: normalized bound 7.437694303e21
    Q=900, k=12: normalized bound 8.628339796e8

Keeping the three parent residues correlated gives much smaller finite LP
estimates at the canonical weight \(30/31\). The table reports exact rational
feasible upper factors generated from the numerical LP potentials:

| modulus | reachable states | correlated factor |
|---:|---:|---:|
| 30 | 22 | 1.619215584 |
| 150 | 106 | 1.549683565 |
| 900 | 522 | 1.349219791 |
| 4,500 | 2,558 | 1.319264057 |
| 22,500 | 12,744 | 1.308624622 |

All tested factors remain above the critical value 1. The LP lower brackets
are numerical rather than formal dual infeasibility certificates, so this is
a finite nondecision, not a theorem against all periodic potentials.
Theorem 1 supplies the exact nonperiodic critical object.

## 6. Exact data audit

The favorable ray now has five exact points:

| \(k\) | \(D_{3k,2k,k}\) | \(\sqrt{6k}D/360^k\) |
|---:|---:|---:|
| 1 | 60 | 0.408248290464 |
| 2 | 13,068 | 0.349296912860 |
| 3 | 3,542,949 | 0.322176345589 |
| 4 | 1,054,111,467 | 0.307455421497 |
| 5 | 330,159,210,305 | 0.299069097824 |

The \(k=5\) value is the independently tiled exact result from
C28_exact_mass_gate.md. The decreasing sequence is compatible with a
positive limit and is not an asymptotic proof.

Checks performed in C29:

- 30 exact symbolic residue inequalities;
- 1,000,001 direct integer potential checks;
- 87,491 exact multiplicity checks through word length 10;
- 53,722 killed-chain subprobability checks;
- 30,618 adjacent-swap checks;
- 83,477 concatenation-injection checks;
- all \(3^{14}=4,782,969\) formal words in the rewrite census.

## 7. Prior-art comparison

Shamazov and Talambutsa, [On orbit sets generated by semigroups of
one-dimensional affine functions](https://arxiv.org/abs/2507.06875),
Theorem 5, obtain an \(x/\log x\) lower bound for three generators under
freeness and the critical equality \(\sum1/a_i=1\). Here
\(\sum(1/2+1/3+1/5)=31/30>1\), and exact relations occur, so that theorem
does not supply (LL) or the fixed-count support bound.

Kolpakov and Talambutsa,
[On free semigroups of affine maps on the real line](https://arxiv.org/abs/2105.09387),
provide the general nonfreeness framework used in the existing route audit.
The explicit potential (6), killed kernel (7), and reduction (LL) are not
stated in the audited sources.

General local-limit results such as Herve and Ledoux,
[A local limit theorem for densities of the additive component of a finite
Markov Additive Process](https://arxiv.org/abs/1306.5353), and
[Conditioned local limit theorems for random walks defined on finite Markov
chains](https://arxiv.org/abs/1707.06129), assume a finite internal chain.
Kernel (7) has a countably infinite contracting state and state-dependent
killing. Verifying a replacement spectral/regeneration hypothesis uniformly
in the starting offset is part of (LL), not an automatic citation.

## 8. Reproduction

    python problems/424/compute/wave3/C29_block_pressure.py --max-length 12 --swap-length 8 --concat-length 8 --output problems/424/compute/wave3/C29_block_pressure_L12.json

    python problems/424/compute/wave3/C29_rewrite_pressure.py --max-rule-length 14 --output problems/424/compute/wave3/C29_rewrite_pressure_L14.json

    python problems/424/compute/wave3/C29_residue_multiplicity.py --moduli 30,150 --kmax 20 --brute-length 10 --output problems/424/compute/wave3/C29_residue_multiplicity_Q150_K20.json

    python problems/424/compute/wave3/C29_correlated_carry.py --moduli 4500,22500 --check-limit 100000 --output problems/424/compute/wave3/C29_correlated_carry_Q22500.json

    python problems/424/compute/wave3/C29_harmonic_potential.py --check-limit 1000000 --word-length 10 --output problems/424/compute/wave3/C29_harmonic_potential_1e6.json

Script SHA-256 values recorded inside the JSON outputs:

    C29_block_pressure.py       eec779af110fe0a0d66a97d4dff73351acdf6546d65f1dc0055893903ea01df5
    C29_rewrite_pressure.py     640f6af3429250ee582ea2ecaebd17659ab5e775b7f160d8b24fe40562ff211f
    C29_residue_multiplicity.py c442abaa473a3ffd469d115d3ff1c021b521ac42fc47e076aaf6ca2bcbe05772
    C29_correlated_carry.py     1f582e8b6f9115f8708def129a8c9f1866dc48cfc7983fe885e38df3b8a9a191
    C29_harmonic_potential.py   2b35811b59f804c51e6e317d7ff0b746c54d76cb5c7f792d918624b43f9f2b6e

## Final frontier

Prove or falsify (LL) for the explicit substochastic kernel (7). A proof
must exploit the exact harmonic identity and quantify the cumulative loss
from unavailable congruence branches. A counterexample sequence to (LL)
would kill this max-multiplicity mechanism, although it would not by itself
falsify the weaker support gate.
