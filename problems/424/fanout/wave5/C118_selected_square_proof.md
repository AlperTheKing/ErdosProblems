# C118: selected-square proof lane

## DIRECT ROUTE

1. **Exact final deliverable.** For one fixed
   \(2/3<c<\log 2\), with
   \[
   m_X=\left\lfloor(\log X)^{c/2}\right\rfloor,
   \]
   prove unconditionally that the C114 square block satisfies
   \[
   B_{m_X}(X)=o(m_X^3).
   \]
   A permitted fallback is a strictly weaker proved estimate which still
   gives \(\Sigma_D(X)/D=o(1)\), with every exponent displayed.
2. **Current frontier lemma or finite certificate.** Bound the selected-block
   root load by an explicit arithmetic charge built from the certifying hard
   source, its missing endpoint chain, and its complementary divisors.  The
   charge must sum to \(o(m_X^3)\); a Hall, energy, or layer-cake restatement
   is not a deliverable.
3. **Logical bridge.** C114.1 gives
   \[
   (2m_X+1)T_{(m_X+1)^2}(X)\le B_{m_X}(X).
   \]
   Hence C114.2 gives \(\Sigma_D(X)/D=o(1)\) for
   \(D=(m_X+1)^2\).  C99.3 absorbs the low-pair sources because
   \(c<\log 2\), and C99.5 absorbs the structural roots because
   \(c>1/2\).  Thus the C85 contraction gives \(H(X)=o(X)\).
4. **Next falsifiable action.** Reconstruct root-load upgrades in an exact
   prefix and test each proposed source, endpoint-chain, gap, or divisor
   charge at the first upgrade where it is claimed.  Reject a charge at its
   first integer counterexample before attempting a proof.
5. **Exit condition.** Stop with a proof of the selected-square estimate, a
   weaker proved estimate with the displayed C99 exponent bridge, or an exact
   obstruction identifying the missing arithmetic implication.  A finite
   failure kills only its stated charge.

## Guard note

The five fields above are the C114 `DIRECT ROUTE` specialized to the assigned
selected-square lane.  At lane start, the shared
`problems/424/APPROACH_REGISTRY.md` did not yet contain the C114/C118 route;
this file records the route without editing outside C118 ownership.

## Status

The C114 implication is accepted by its audit.  The selected-square
antecedent remains open.  This lane gives an exact obstruction to the
divisor-rich-multiple proof route and exact counterexamples to the local
charges tested below.  It does not give a counterexample to the C114
asymptotic condition.

## 1. Verdict

No unconditional bound

\[
                         B_{m_X}(X)=o(m_X^3)                 \tag{1}
\]

is proved here.  The arithmetic relaxation suggested by divisor-rich
multiples is too weak in a quantified sense.  If one retains only

1. the seed-chain identity \(p=1+2^k(r-1)\);
2. the divisibility \(p\mid h+1\);
3. the C99 residue shape \(h+1\equiv1\pmod3\); and
4. at least \(D+1\) allowed complementary factor pairs,

then the resulting relaxed selected-square block satisfies

\[
 {\widetilde B_{m_X}(X)\over m_X^3}\longrightarrow\infty.  \tag{2}
\]

More precisely,

\[
 \widetilde B_{m_X}(X)
 \gg {m_X\log X\over\log m_X}.                         \tag{3}
\]

Thus divisor richness, endpoint-chain lacunarity, and divisor moments do
not supply the needed \(1/m_X\) root-density saving.  The omitted condition
is load-bearing: the source must be an actual hole, every allowed pair must
be blocked by an actually missing endpoint, and the selected endpoint root
must be an actual reducible hole.

The finite scan also rejects every tested attempt to pay a selected root by
one side of its certifying factorization or by reusable historical co-roots.
The only surviving finite statements are either analytically insufficient
or equivalent to the already-open C108/C110 packing gate.

**DEAD: reformulation maze -- the divisor-rich-multiple model has no bridge
from arithmetic pair count to the actual all-pairs missing-endpoint
condition, and its relaxed square block violates (1) by (2).**

## 2. Exact event decomposition

For a root in bin \(j\), put

\[
 \Phi_m(q,j)=
 \bigl[\min\{q,j^2,(m+1)^2\}-m^2\bigr]_+.             \tag{4}
\]

At a hard-source event \(h\), let \(q_h^-(r)\) and \(q_h^+(r)\) be the
root load immediately before and after processing \(h\).  Since these loads
only increase, C114 equation (4) has the exact telescoping form

\[
 B_m(X)=\sum_{h\le X}\sum_{\substack{r:\ q_h^+(r)>q_h^-(r)}}
 {\Phi_m(q_h^+(r),j(r))-\Phi_m(q_h^-(r),j(r))\over2^{j(r)}}. \tag{5}
\]

This identity was used only to test source-event charges.  It is not offered
as a replacement target for (1).

## 3. Exact failures of local arithmetic charges

For a root upgrade certified by a missing endpoint \(p\mid N=h+1\), write

\[
 s=N/p,\qquad k=v_2(p-1),\qquad d=d(h),\qquad q=d-1.
\]

Divisor submultiplicativity gives the valid but one-sided dichotomy

\[
                    \tau(p)\tau(s)\ge\tau(N)\ge2d.    \tag{6}
\]

Neither side can be selected uniformly, and requiring both sides to pay a
square-root layer is false.

| proposed charge | first exact failure | failed integer inequality |
|---|---|---|
| cofactor pays \(d\) | \(h=1154,r=116,p=231,s=5\) | \(\tau(s)=2<4=d\) |
| both sides pay \(\sqrt{2d}\) | same event | \(\min(8,2)^2=4<8=2d\) |
| chain exponent pays \(\sqrt q\) | same event | \(k^2=1<3=q\) |
| endpoint pays \(d\) | \(h=52436,r=114,p=227,s=231\) | \(\tau(p)=2<4=d\) |
| smaller source roots pay \(\sqrt q\) | \(h=4674,r=54\) | \(1^2<2=q\) |
| smaller historical co-roots pay \(\sqrt q\) | \(h=55674,r=1638\) | \(1^2<2=q\) |
| all historical co-roots pay \(\sqrt q\) | \(h=947052,r=13928\) | \(1^2<2=q\) |
| individual left gap pays \(\sqrt q\) | bin \(6\), roots \(114,116\) | \(\lceil\sqrt7\rceil=3>2\) |

Every row involving \(h\) is an actual hard source in the reconstructed
least closure.  These finite certificates kill only the displayed charges.
They do not falsify (1).

Two diagnostics have no failure through \(10^6\):

\[
 \tau(r+1)^2\ge q_X(r),
 \qquad
 A(h)^2\ge d(h)-1,                                   \tag{7}
\]

where \(A(h)\) is the number of all distinct witness roots at the source.
Neither gives a sufficient analytic estimate.

For the first diagnostic, fix \(a<\log2\).  Turan--Kubilius and Chebyshev
give, outside \(O(Y/\log\log Y)\) integers in \([Y,2Y]\),

\[
 \omega(n)\ge(1-\eta)\log\log Y
\]

for every fixed \(\eta>0\).  Hence

\[
 \tau(n)\ge2^{\omega(n)}>(\log Y)^a                 \tag{8}
\]

for almost all \(n\), after choosing \((1-\eta)\log2>a\).  In C114,
\(m_X=(\log X)^{c/2+o(1)}\) and \(c/2<\log2\).  Therefore the condition
\(\tau(r+1)>m_X\) describes a density-one arithmetic superset and supplies
no dyadic root saving.

For the second diagnostic, the \(A(h)\) labels are source-local.  Replacing
them by distinct historical labels is exactly false at \(h=947052\), as the
table shows.  Summing them therefore recreates C114's missing cross-source
load bound.  Finally, the surviving selected-prefix inequality is exactly a
nested-slot Hall condition of C108-MOVE-PACK, not an arithmetic proof of it.

## 4. Scalable divisor-rich-multiple obstruction

Define the following relaxation.  An even root \(r\) is admitted at scale
\(X,D\) when there are integers \(h\le X\) and \(k\ge1\) such that

\[
 p=1+2^k(r-1)\mid h+1,
 \qquad h+1\equiv1\pmod3,
 \qquad d_{\mathcal A}(h)\ge D+1,                    \tag{9}
\]

where \(d_{\mathcal A}(h)\) counts the allowed distinct complementary
factor pairs of \(h+1\).  No closure state is imposed in (9).  Let
\(\widetilde q_X(r)\) be the maximum of \(d_{\mathcal A}(h)-1\) over these
certificates, and define \(\widetilde B_m\) from C114 equation (4) with
\(q_X\) replaced by \(\widetilde q_X\).

### Proposition C118.1 (the relaxation saturates dyadic bins)

Fix \(m\), and let \(\ell\) be the least positive odd integer such that

\[
                         2^{\ell-1}\ge(m+1)^2+1.       \tag{10}
\]

Let \(q_1<\cdots<q_\ell\) be the first \(\ell\) odd primes congruent to
\(2\pmod3\), and put \(M=\prod_iq_i\).  For every integer \(t\) satisfying

\[
 r=6t,\qquad p=12t-1>M,\qquad (p,M)=1,                \tag{11}
\]

the value

\[
                         h=pM-1                       \tag{12}
\]

is a certificate in (9) with

\[
 d_{\mathcal A}(h)\ge2^{\ell-1}\ge(m+1)^2+1,
 \qquad \widetilde q_X(r)\ge(m+1)^2                  \tag{13}
\]

whenever \(h\le X\).  In every denominator bin
\(2^j\le r-1<2^{j+1}\) lying between (11) and the cutoff \(h\le X\), the
number of these roots is

\[
 {2^j\over6}\prod_{i=1}^{\ell}\left(1-{1\over q_i}\right)
 +O(2^\ell)
 \gg {2^j\over\ell}.                                  \tag{14}
\]

#### Proof

For every odd-cardinality subset \(S\subseteq\{1,\ldots,\ell\}\), put

\[
                         a_S=\prod_{i\in S}q_i.
\]

Both \(a_S\) and \(pM/a_S\) are \(2\pmod3\), because \(\ell\) is odd,
\(p=12t-1\equiv2\pmod3\), and the total product \(pM\) is
\(1\pmod3\).  Also \(a_S\le M<p\), so

\[
                         a_S^2<Mp.
\]

Thus \((a_S,pM/a_S)\) is an allowed distinct complementary pair.  The
\(2^{\ell-1}\) odd subsets give distinct pairs and prove (13).  Moreover,

\[
 p-1=2(6t-1)=2(r-1),
\]

where \(r-1\) is odd.  Hence the seed-chain root of \(p\) is exactly \(r\).

The bin condition restricts \(t\) to an interval of length
\(2^j/6+O(1)\).  For each \(q_i\), the condition \(q_i\nmid12t-1\) removes
one residue class modulo \(q_i\).  Inclusion-exclusion and the Chinese
remainder theorem therefore give the first expression in (14), with one
flooring error for each of the \(2^\ell\) subsets.  Since the \(q_i\) are
distinct increasing integers at least \(i+4\),

\[
 \prod_{i=1}^{\ell}\left(1-{1\over q_i}\right)
 \ge\prod_{i=1}^{\ell}{i+3\over i+4}
 ={4\over\ell+4}.                                     \tag{15}
\]

For \(j\ge m+1\), equation (10) makes \(2^\ell\) negligible compared with
\(2^j/\ell\), proving the final estimate in (14).  QED.

### Corollary C118.2 (the relaxed selected block diverges)

Fix \(2/3<c<\log2\) and put

\[
                         m=m_X=\lfloor(\log X)^{c/2}\rfloor.
\]

Then equations (2)-(3) hold.

#### Proof

Equation (10) gives \(\ell=O(\log m)=O(\log\log X)\).  The prime number
theorem in the progression \(2\pmod3\) gives

\[
 \log M=O(\ell\log\ell)=o(\log X).                  \tag{16}
\]

Also \(m=o(\log X)\).  Consequently there are
\((1-o(1))\log_2X\) bins satisfying

\[
 m+1\le j,qquad 2^j\gg M,qquad 2^{j+2}M\le X.       \tag{17}
\]

Every root counted in (14) has \(h\le X\), and (13) makes its C114 block
height exactly

\[
                         (m+1)^2-m^2=2m+1.
\]

Summing (14) over the bins in (17) yields

\[
 \widetilde B_m(X)
 \gg (2m+1){\log X\over\ell}
 \gg {m\log X\over\log m}.
\]

Finally,

\[
 {\widetilde B_m(X)\over m^3}
 \gg {\log X\over m^2\log m}
 \gg { (\log X)^{1-c}\over\log\log X}
 \longrightarrow\infty,                              \tag{18}
\]

because \(c<\log2<1\).  QED.

Corollary C118.2 is not a counterexample to C114-SB.  The construction does
not assert that \(h\) is a hole, that \(p\) is missing, or that \(r\) is a
reducible witness root.  It proves that those closure-state facts cannot be
discarded and then recovered from divisor moments.

## 5. Exact finite reproduction

The exact Python scan through \(X=10^6\) reconstructs

| quantity | exact value |
|---|---:|
| hard sources | `45,583` |
| all root-upgrade events | `3,015` |
| positive-\(q\) upgrade events | `2,239` |
| distinct positive-\(q\) reducible roots | `1,776` |
| maximum \(d(h)\) | `9` |
| \(B_1(10^6)\) | `84203/65536` |
| \(B_2(10^6)\) | `12559/16384` |

The hard-source, all-upgrade, positive-root, and maximum-pair totals match
the independent C108 artifact.  Recomputing the square blocks from C108's
threshold vectors gives the same two rational values.

For the finite instance of Proposition C118.1 with

\[
 (q_1,\ldots,q_5)=(5,11,17,23,29),\qquad M=623645,
\]

the denominator bin \(j=20\) contains exactly `110477` roots satisfying
(11), out of capacity `1048576`.  Eight emitted sample sources each contain
the sixteen certified allowed pairs, checked by integer multiplication and
residue tests.  These are arithmetic-relaxation certificates only.

Reproduction:

```powershell
python problems/424/compute/wave5/C118_selected_square_probe.py `
  --limit 1000000 --synthetic-bin 20 `
  --output problems/424/compute/wave5/C118_selected_square_probe_1000000.json

python -O problems/424/compute/wave5/C118_selected_square_probe.py `
  --limit 1000000 --synthetic-bin 20 `
  --output problems/424/compute/wave5/C118_selected_square_probe_1000000.opt.json

python problems/424/compute/wave5/C118_selected_square_verify.py `
  --claim problems/424/compute/wave5/C118_selected_square_probe_1000000.json `
  --reference problems/424/compute/wave5/C108_weighted_token_gate_1000000.json `
  --output problems/424/compute/wave5/C118_selected_square_verify_1000000.json
```

Normal and optimized probe outputs are byte-identical, as are the two
verifier outputs.  The verifier reports `PASS` for all ten checks.  SHA-256:

```text
715098CACB3A408D73BED62240C043CD3B80827A06F6F0B3DF31EB5956FA6DB3
  C118_selected_square_probe_1000000.json
4ADD7A22E574448D1B91399D12CFA40D350F6478C8B01158B1A75F4DF17F9991
  C118_selected_square_verify_1000000.json
```

All six code and output hashes are pinned in
`problems/424/compute/wave5/C118_SHA256SUMS.txt`.

## 6. Precise remaining frontier

The selected-square condition (1) remains open.  Any continuation must use
an actual closure-state theorem which forces anticlustering of reducible
witness roots from the fact that every complementary pair of every
certifying source is blocked.  Divisor richness of \(h+1\), richness of one
endpoint or cofactor, root-chain lacunarity, and generic divisor moments do
not contain that implication.  Replacing it by another arithmetic superset
would repeat the obstruction in Corollary C118.2.
