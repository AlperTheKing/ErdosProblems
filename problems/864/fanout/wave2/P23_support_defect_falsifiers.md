# P23: support-defect falsifiers

## Verdict

Put

\[
 Q_H(A,N):={M_H\over N}\left(1+{2Z_H\over H^2}\right),
 \qquad
 M_H=|A-\{0,\ldots,H-1\}|,
\]

and

\[
 Z_H=\sum_{d=1}^{H-1}(H-d)(\nu_A(d)-1),\qquad
 \nu_A(d)=\#\{(a,b)\in A^2:a-b=d\}.
\]

The unconditional pointwise frontier

\[
 Q_H(A,N)\le {4\over3}+o(1)                         \tag{1}
\]

is false.  More strongly, its existential/adaptive mesoscopic version is
false.  There is an explicit infinite admissible family \(A_p\) such that,
for **every** choice of scales satisfying

\[
 p=o(H_p),\qquad H_p=o(p^2),                         \tag{2}
\]

one has

\[
 {M_{H_p}(A_p)\over N_p}=1+o(1),\qquad
 \liminf_p {Z_{H_p}(A_p)\over H_p^2}\ge {1\over4},  \tag{3}
\]

and hence

\[
 \boxed{\liminf_p Q_{H_p}(A_p,N_p)\ge {3\over2}.}   \tag{4}
\]

Since \(\sqrt{N_p}\asymp p\), (2) is precisely the proof-scale condition
\(\sqrt N=o(H)\), \(H=o(N)\).  Thus choosing \(H\) after seeing \(A_p\)
does not rescue (1).

This does **not** disprove Erdos Problem 864.  The family has

\[
 {|A_p|^2\over N_p}\longrightarrow1,
\]

strictly below the conjectural \(4/3\).  A support-defect coupling explicitly
conditioned on \(|A|^2/N\ge4/3-o(1)\), or containing a density term, remains
alive.  What is dead is an unconditional pointwise or adaptive-\(H\) claim
using only \(M_H/N\) and \(Z_H/H^2\).

## 1. Exact arithmetic

For \(A=\{a_0<\cdots<a_{k-1}\}\), the thickening is a union of integer
intervals of length \(H\), so

\[
 \boxed{M_H=H+\sum_{i=0}^{k-2}\min(H,a_{i+1}-a_i).} \tag{5}
\]

If \(A\) is admissible, the standard reflected-difference argument gives
\(\nu_A(d)\le2\) for every \(d>0\).  Thus every summand in \(Z_H\) is a
nonnegative integer and \(Z_H\) is exactly the weighted set of duplicated
positive differences.

The verifier

`problems/864/compute/p23/support_defect_verifier.py`

uses (5), literal unordered pair sums including diagonals, and prefix sums of
the integer difference multiplicities.  It decides (1) from the sign of

\[
 3M_H(H^2+2Z_H)-4NH^2,                              \tag{6}
\]

not from decimal output.  The self-test compares (5) with an explicitly
materialized Minkowski difference on all 510 subsets through ambient size 8
and all 4,606 tested \((A,H)\) profiles.

## 2. Dense cyclic Sidon base

Let \(p\) be an odd prime, let \(g\) be a primitive root modulo \(p\), and
put

\[
 m=p(p-1).
\]

For \(1\le x\le p-1\), let \(c_x\in\{0,\ldots,m-1\}\) be the CRT solution

\[
 c_x\equiv x\pmod{p-1},\qquad c_x\equiv g^x\pmod p. \tag{7}
\]

Equivalently, if \(q_x=[g^x]_p\in\{1,\ldots,p-1\}\), the verifier uses the
exact representative

\[
 c_x=q_x+p\,[x-q_x]_{p-1}.
\]

Set \(C_p=\{c_x:1\le x<p\}\), so \(|C_p|=p-1\).

### Lemma 1 (Ruzsa cyclic Sidon property)

Every nonzero oriented difference in \(C_p\) has at most one
representation modulo \(m\).  Consequently the least representatives
\(C_p\subset[0,m-1]\) form a literal integer Sidon set, diagonals included.

### Proof

Suppose

\[
 c_x-c_y\equiv c_u-c_v\pmod m,
 \qquad x\ne y,\quad u\ne v.
\]

Modulo \(p-1\), both index differences equal some nonzero \(h\).  Modulo
\(p\), after writing \(x=y+h\) and \(u=v+h\),

\[
 g^y(g^h-1)=g^v(g^h-1).
\]

Primitivity and \(h\not\equiv0\pmod{p-1}\) make \(g^h-1\ne0\), so
\(g^y=g^v\), hence \(y=v\) and then \(x=u\).  Unique nonzero oriented
differences imply the Sidon sum condition.  An integer collision would also
be a modular collision.  This includes a collision between two diagonals,
which would otherwise give two oriented representations of the same
half-modulus difference.  QED.

Notice the exact density

\[
 {|C_p|^2\over m}={(p-1)^2\over p(p-1)}={p-1\over p}\longrightarrow1.
                                                               \tag{8}
\]

## 3. Congruence-compressed reflection

Fix an integer \(r\ge2\).  Define

\[
 B_{p,r}=rC_p,\qquad
 \sigma_{p,r}=2r(m-1)+1,                                  \tag{9}
\]

and

\[
 A_{p,r}=B_{p,r}\cup(\sigma_{p,r}-B_{p,r}),\qquad
 N_{p,r}=\sigma_{p,r}+1.                                  \tag{10}
\]

The case \(r=2\) is the obstruction in (3)--(4).

### Lemma 2 (exact admissibility)

For every odd prime \(p\) and every \(r\ge2\), \(A_{p,r}\) is admissible.
Its unique repeated unordered sum is \(\sigma_{p,r}\), with exactly \(p-1\)
representations.

### Proof

The block \(B_{p,r}\) is Sidon by Lemma 1.  Also

\[
 \max B_{p,r}\le r(m-1),\qquad
 \sigma_{p,r}>2\max B_{p,r},                              \tag{11}
\]

so the lower and reflected blocks are disjoint.  Their three sum types are

\[
 B+B,\qquad \sigma+(B-B),\qquad 2\sigma-(B+B).             \tag{12}
\]

Within the first and third types, Sidonicity gives uniqueness.  Within the
middle type, every nonzero difference is unique, while difference zero gives
the \(p-1\) pairs \(b+(\sigma-b)=\sigma\).

Every element of \(B\) is divisible by \(r\), whereas
\(\sigma\equiv1\pmod r\).  A collision between the first and middle types,
or between the middle and third types, would express \(\sigma\) as an
integer combination of elements of \(B\), hence as a multiple of \(r\), a
contradiction.  Finally the first type lies below \(\sigma\) and the third
lies above \(\sigma\) by (11).  All diagonal pairs occur inside the Sidon
blocks and were included.  QED.

The family is deliberately subextremal:

\[
 {|A_{p,r}|^2\over N_{p,r}}\longrightarrow {2\over r}.      \tag{13}
\]

For \(r=2\), (13) equals 1.

## 4. Uniform mesoscopic obstruction

For the ordinary Sidon set \(C=C_p\), define

\[
 W_h(C)=\sum_{\substack{c>c'\\c-c'<h}}(h-c+c').            \tag{14}
\]

Let \(b=p-1\).  The exact sliding-window identity and Cauchy--Schwarz give

\[
 b^2h^2\le M_h(C)\bigl(bh+2W_h(C)\bigr).                  \tag{15}
\]

Sidonicity makes the represented positive differences distinct, so

\[
 W_h(C)\le {h(h-1)\over2}.                                \tag{16}
\]

Equations (15)--(16), together with \(M_h(C)\le m+h-1\), imply the exact
bounds

\[
 {b^2h\over b+h-1}\le M_h(C)\le m+h-1,                   \tag{17}
\]

and

\[
 {1\over2}\left({b^2h^2\over m+h-1}-bh\right)
 \le W_h(C)\le {h(h-1)\over2}.                            \tag{18}
\]

Therefore, uniformly along every sequence \(b=o(h)\), \(h=o(m)\),

\[
 M_h(C)=m+o(m),\qquad W_h(C)=\left({1\over2}+o(1)\right)h^2.
                                                               \tag{19}
\]

Now let \(H\) satisfy (2) and put \(h=\lfloor H/r\rfloor\).  From (5),

\[
 rM_h(C)\le M_H(rC)\le rM_{h+1}(C).                       \tag{20}
\]

The hulls of \(B-[0,H-1]\) and \((\sigma-B)-[0,H-1]\) overlap in at most
\(H-1\) integer positions, by (11).  Hence

\[
 2M_H(B)-(H-1)\le M_H(A)\le N+H-1.                        \tag{21}
\]

Equations (19)--(21) give

\[
 {M_H(A_{p,r})\over N_{p,r}}=1+o(1).                      \tag{22}
\]

Every positive difference \(r(c-c')\) inside \(B\) has a second
representation in the reflected block.  Thus (14), with
\(h=\lfloor H/r\rfloor\), gives the exact lower bound

\[
 Z_H(A_{p,r})\ge rW_h(C),                                 \tag{23}
\]

because \(H-r(c-c')\ge r(h-c+c')\).  Combining (19), (22), and (23),

\[
 \liminf {Z_H(A_{p,r})\over H^2}\ge {1\over2r},
 \qquad
 \liminf Q_H(A_{p,r},N_{p,r})\ge1+{1\over r}.             \tag{24}
\]

For \(r=2\), (24) is (3)--(4).  For \(r=3\), this mechanism already
saturates \(4/3\); larger fixed dilations give a smaller lower bound.

The word "every" in (2) matters.  If an adaptive theorem selected one
mesoscopic \(H_p=H(A_p)\) for each member of the family, the selected scales
would still form a sequence covered by (19)--(24).  Therefore (4) rules out
the existential version, not merely an inequality at one prescribed scale.

## 5. Exact finite certificates

The JSONL certificate suite regenerates every construction from its integer
parameters and then independently counts all unordered sums and positive
differences.  Representative first-scale rows are:

| construction | \(p\) | \(|A|\) | \(N\) | \(H\) | \(M_H/N\) | \(Z_H/H^2\) | \(Q_H\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| parity-compressed Ruzsa | 101 | 200 | 40398 | 1010 | 1.004282 | 0.253647 | 1.513748 |
| parity-compressed Ruzsa | 211 | 420 | 177238 | 2954 | 1.010432 | 0.255050 | 1.525854 |
| parity-compressed Ruzsa | 401 | 800 | 641598 | 8020 | 1.011532 | 0.247574 | 1.512391 |

For the \(p=101\), \(H=1010\) comparison sweep:

| tested class | \(M_H/N\) | \(Z_H/H^2\) | \(Q_H\) |
|---|---:|---:|---:|
| ordinary Ruzsa Sidon | 1.074257 | 0 | 1.074257 |
| reflected Erdos--Freud | 0.735045 | 0.465010 | 1.418652 |
| unbalanced reflection, half core | 0.734808 | 0.103458 | 0.886852 |
| compressed core plus lower residual | 0.999381 | 0.049972 | 1.099262 |
| four-arc multicluster reflection | 0.628447 | 0.072164 | 0.719149 |
| affine/mixed dilation \(r=2\) | 1.004282 | 0.253647 | 1.513748 |
| affine/mixed dilation \(r=3\) | 0.983448 | 0.167828 | 1.313547 |
| affine/mixed dilation \(r=4\) | 0.920848 | 0.125546 | 1.152065 |
| inverse-conic admissible family | 1.039754 | 0.096967 | 1.241397 |

The Erdos--Freud row is a finite-scale overshoot; its rigorous asymptotic
profile is \((M_H/N,Z_H/H^2)\to(2/3,1/2)\), so \(Q_H\to4/3\).  It is a
sharpness family, not the strict obstruction.  Unbalancing, deleting a
reflected core while retaining a lower residual, and selecting four separated
arcs all reduced \(Z_H\) in the tested instances.  The strict asymptotic
failure comes from congruence compression.

The affine phase scan checked 64 exact \((u,t)\) transforms of the \(p=101\)
cyclic set.  Its winner \((u,t)=(13,0)\) had

\[
 \min\{Q_{1010},Q_{2020}\}
 ={31389015721\over20604999900}> {4\over3}.                 \tag{25}
\]

### Certified small domain

The exhaustive search certified all

\[
 2^{20}=1,048,576
\]

endpoint-normalized subsets of \([0,21]\).  Exactly 3,302 are admissible.
The minimax winner over \(H\in\{5,6,7\}\) is

\[
 A=\{0,2,5,6,15,16,19,21\},                               \tag{26}
\]

whose only repeated sum is 21, with four representations.  Its exact rows
are

\[
 (Q_5,Q_6,Q_7)=\left({9\over5},2,{169\over77}\right).      \tag{27}
\]

This is a fixed-scale finite falsifier only: \(H/N\) does not tend to zero.
It must not be used to claim the adaptive asymptotic obstruction, which is
supplied instead by (9)--(24).

## 6. What remains viable

The following claims are dead:

1. an unconditional pointwise inequality of the form (1);
2. any support-defect law forcing \(Z_H/H^2=o(1)\) when
   \((N+H-1-M_H)/N=o(1)\);
3. an unconditional assertion that every admissible set has *some*
   mesoscopic \(H\) satisfying (1).

The following are not addressed by the obstruction:

1. (1) under an explicit near-extremal hypothesis such as
   \(|A|^2/N\ge4/3-o(1)\);
2. a coupling that also retains \(|A|^2/N\), exceptional multiplicity, or
   unit-lattice residue information;
3. a theorem selecting \(H\) outside the regime \(\sqrt N=o(H)\), \(H=o(N)\),
   although such a scale does not directly remove the error terms in the
   occupied-thickening argument.

## 7. Reproduction

```text
python problems/864/compute/p23/support_defect_verifier.py self-test
python problems/864/compute/p23/support_defect_verifier.py certificate-suite --primes 101 211 401 --output problems/864/compute/p23/certificates.jsonl
python problems/864/compute/p23/support_defect_verifier.py exhaustive --ambient-n 22 --h 5 6 7 --output problems/864/compute/p23/exhaustive_N22.json
```

Generated artifact hashes:

```text
certificates.jsonl  D4537765E5B6084DE5CD2764FB0FB77C4E992A15D8230E8BFA1A10533D59CAD6
exhaustive_N22.json 29D5F6E3026F8E7DB72A47F680F40F7AFA05DD25F24447E4D1DEFA568282DCCC
```

## Erratum: this report does not falsify the centered P02 defect

The implementation in this report stores only positive duplicated weight

    D_H=sum_{nu_A(d)=2}(H-d),

whereas the P02/P20 centered identity uses

    Z_H=D_H-Q_H,
    Q_H=sum_{nu_A(d)=0}(H-d).

Accordingly, the displayed definition Z_H=sum(H-d)(nu_A(d)-1) near the
start of this report is inconsistent with the implementation and with the
later claim that every summand is nonnegative. All exact computations here
remain valid for D_H, but conclusions claiming to falsify the centered
P02/P20 product are withdrawn.

At p=503 and H=ceil(N^(2/3)), an independent audit gives

    D_H=25058720,
    Q_H=25569511,
    Z_H=-510791.

Thus this family fails the duplicate-only C20 analogue but satisfies the
actual centered C20 inequality with cleared margin -305894457730641. See

    problems/864/compute/p20/verify_p23_falsifier.py

The family remains a valid warning against bounds using positive duplicate
mass alone. It is not a counterexample to centered support-defect coupling.
