# P38: reflected-core stability

## Verdict

The proposed conclusion

\[
 |R|=o(|A|)\qquad\text{whenever}\qquad
 |A|^2>(4/3+\eta)N                                      \tag{S}
\]

cannot serve as a reduction to the fully reflected case.  There is an
exact span-preserving deletion operation with the following consequence:

> If a fully reflected asymptotic counterexample exists with any fixed
> positive density margin, then an asymptotic counterexample exists with a
> smaller fixed positive margin and with \(|R|/|A|\) bounded away from zero.

Thus a theorem asserting (S) for every fixed \(\eta>0\) would already rule
out every fully reflected asymptotic counterexample.  It is strictly stronger
than the proposed remaining fully reflected problem, not a preliminary
stability reduction to that problem.

This is a conditional falsification of (S), because an unconditional
asymptotic falsifier to (S) would itself disprove the proposed constant.
The obstruction to using (S) as a reduction is unconditional and exact.
It preserves the minimal span, includes the midpoint case, and uses no
limit interchange or real-valued computational gate.

Two natural finite bridges were also falsified exactly:

1. adjoining every missing reflected partner need not preserve
   admissibility;
2. the geometric span outside the core need not pay
   \(\tfrac34(k^2-|P|^2)\).

The exact census scripts and outputs are in `problems/864/compute/p38/`.

## 1. Notation and accepted reflection identities

Let \(A\) be admissible, let \(\sigma\) be its repeated sum, and put

\[
 P=A\cap(\sigma-A),\qquad R=A\setminus P,
\]

\[
 |P|=c=2p+\delta,\qquad |R|=u,\qquad k=c+u,
\]

where \(\delta=1\) exactly when \(\sigma/2\in A\).  If
\(L=\max A-\min A\), P09 gives the exact difference packing

\[
 p(p+\delta)+cu+\binom u2\le L.                         \tag{1}
\]

Every positive difference represented by a pair touching \(R\) is unique
and is disjoint from every internal-core difference.  The coupling for a
core pair \(\{x,\sigma-x\}\) and \(v\in R\) is

\[
\begin{cases}
 |v-x|+|v-(\sigma-x)|=\sigma-2x,&x<v<\sigma-x,\\
 \big||v-x|-|v-(\sigma-x)|\big|=\sigma-2x,&
 v<x\text{ or }v>\sigma-x.
\end{cases}                                             \tag{2}
\]

These identities are fully compatible with a positive-proportion residual.
The obstruction below explains why: admissibility is hereditary under
deletion, while reflection of the surviving set is not.

## 2. Exact one-sided deletion lemma

**Lemma P38.1 (hereditary reflected deletion).**  Let \(F\) be an admissible
set which is fully reflected about \(\sigma/2\).  Write

\[
 F=\{x_i,\sigma-x_i:1\le i\le p\}
   \mathbin{\dot\cup}
   (\{\sigma/2\}\text{ if }\delta=1),                  \tag{3}
\]

with \(x_i<\sigma/2\), and let \(K=|F|=2p+\delta\).
Choose \(t\) off-diagonal pairs and delete exactly one point from each.
Call the resulting set \(A\).  If \(p-t+\delta\ge2\), then:

\[
\begin{aligned}
 A&\text{ is admissible},\\
 k:=|A|&=K-t=2p+\delta-t,\\
 |A\cap(\sigma-A)|&=2(p-t)+\delta,\\
 |A\setminus(\sigma-A)|&=t,\\
 r_A(\sigma)&=p-t+\delta.                              \tag{4}
\end{aligned}
\]

If a pair containing neither endpoint is chosen each time, then

\[
 \min A=\min F,\qquad \max A=\max F,\qquad
 \operatorname{span}(A)=\operatorname{span}(F).         \tag{5}
\]

**Proof.**  Since \(A\subseteq F\), every sum fibre of \(A\) is a subfibre
of the corresponding sum fibre of \(F\).  Hence deletion cannot create a
second repeated sum, so \(A\) is admissible.  Each untouched pair contributes
two points to the new reflected core and one representation of \(\sigma\).
Each broken pair contributes its surviving point to \(R\), and the midpoint,
when present, contributes one point and one diagonal representation.  This
proves (4).  Protecting the endpoint pair proves (5).  QED.

No completion or compression assertion is hidden here.  The construction
only deletes points from an already admissible set.

## 3. Density consequence

The preceding lemma gives the exact finite density identity

\[
 {k^2\over N}=left(1-{t\over K}\right)^2{K^2\over N},
 \qquad {u\over k}={t\over K-t}.                         \tag{6}
\]

Now suppose there is a sequence of fully reflected admissible sets \(F_n\)
in their minimal ambient intervals, with \(K_n=|F_n|\to\infty\), such that

\[
 \liminf_{n\to\infty}{K_n^2\over N_n}
 \ge {4\over3}+\eta_0                                  \tag{7}
\]

for some \(\eta_0>0\).  Set \(D_0=4/3+\eta_0\), and choose a rational

\[
 0<\theta<{\eta_0\over4D_0}.                            \tag{8}
\]

Delete one nonendpoint partner from each of
\(t_n=\lfloor\theta p_n\rfloor\) pairs.  The endpoint pair is protected,
so (5) preserves the minimal ambient interval exactly.  Since
\(K_n=2p_n+\delta_n\),

\[
 {t_n\over K_n}\longrightarrow{\theta\over2},
 \qquad
 {u_n\over k_n}\longrightarrow{\theta\over2-\theta}>0. \tag{9}
\]

Also \((1-\theta/2)^2\ge1-\theta\), so (6)--(8) give

\[
\begin{aligned}
 \liminf_{n\to\infty}{k_n^2\over N_n}
 &\ge (1-\theta)D_0\\
 &>D_0-\eta_0/4
 ={4\over3}+{3\eta_0\over4}.                           \tag{10}
\end{aligned}
\]

Equations (9)--(10) are the claimed obstruction: the descendants clear a
fixed above-threshold gate and have a fixed positive residual proportion.
The calculation uses the rational choice (8); no square-root or floating
comparison is needed.

**Corollary P38.2.**  If (S) holds for every fixed \(\eta>0\), then no fully
reflected asymptotic counterexample exists.  Hence (S) cannot be proved as
an input whose purpose is to reduce the problem to fully reflected sets.

The same argument applies to a limsup counterexample after taking a
subsequence on which (7) holds.

## 4. Why span transfer does not repair the reduction

Let

\[
 L_P=\max P-\min P.
\]

If one hoped to combine a sharp theorem for the reflected core with a
purely geometric residual payment, the direct bridge would be

\[
 L-L_P\ge {3\over4}(k^2-c^2).                            \tag{11}
\]

Indeed, adding (11) to
\(L_P\ge\tfrac34c^2-o(k^2)\) would give the desired global span bound.
But in Lemma P38.1, protect the endpoint pair.  Then the surviving core
still contains both endpoints, so

\[
 L_P=L,\qquad k^2-c^2=2Kt-3t^2.                          \tag{12}
\]

For \(t=\Theta(K)\), (11) fails by \(\Theta(K^2)\).  This gives an
asymptotic falsifier to (11) from any fully reflected family, including the
known threshold family; no hypothetical counterexample is needed for this
span obstruction.

There is also a six-point finite witness in the exact census:

\[
 A=\{0,5,9,13,15,16\}\subseteq[0,16],\qquad\sigma=18.    \tag{13}
\]

Its only repeated sum is

\[
 5+13=9+9=18.
\]

Here

\[
 P=\{5,9,13\},\quad R=\{0,15,16\},\quad
 k=6,\ c=3,\ u=3,\ L=16,\ L_P=8.                       \tag{14}
\]

It clears even the \(\eta=1/2\) gate, since

\[
 {36\over17}>{11\over6}
 \quad\Longleftrightarrow\quad216>187.                  \tag{15}
\]

But (11), cleared by four, would require \(32\ge81\).

## 5. Reflecting the residual is not licensed

There is a same-span five-point obstruction:

\[
 A_0=\{0,1,5,7,8\}\subseteq[0,8],\qquad \sigma=8,        \tag{16}
\]

whose only repeated sum is \(0+8=1+7=8\).  Its core is
\(\{0,1,7,8\}\) and its residual is \(\{5\}\).  The missing partner is
\(3\), which is already inside \([0,8]\), but

\[
 A_0^*=A_0\cup\{3\}=\{0,1,3,5,7,8\}                    \tag{17}
\]

has three repeated sums:

\[
 1+5=3+3=6,\qquad
 0+8=1+7=3+5=8,\qquad
 3+7=5+5=10.                                             \tag{18}
\]

Thus partner completion can fail while preserving the minimal ambient
interval exactly.

For the denser set (13), adjoining all missing partners gives

\[
 A^*=A\cup(18-R)=\{0,2,3,5,9,13,15,16,18\}.             \tag{19}
\]

Direct unordered-sum enumeration, diagonals included, finds the repeated
sum values

\[
 5,15,16,18,20,21,31.                                   \tag{20}
\]

Thus \(A^*\) is not admissible.  In particular,

\[
 0+5=2+3,\qquad 0+15=2+13,\qquad 13+18=15+16.            \tag{21}
\]

So a valid reduction cannot simply complete \(R\), even for a set far above
the proposed asymptotic density.

By contrast, when a set was obtained by deleting partners from a valid
fully reflected host, every descendant is automatically admissible.  The
known ten-point witness

\[
 F=\{0,1,3,8,12,18,22,27,29,30\},\qquad\sigma=30        \tag{22}
\]

has five reflected pairs.  All \(2^5=32\) sets obtained by retaining the
lower representative of every pair and choosing which upper partners to
retain were checked exactly; all 32 are admissible.  Deleting the partners
of \(3,8,12\) gives

\[
 A=\{0,1,3,8,12,29,30\},\quad
 P=\{0,1,29,30\},\quad R=\{3,8,12\},                    \tag{23}
\]

with unchanged span 30 and

\[
 {k^2\over N}={49\over31}>{4\over3},\qquad {u\over k}={3\over7}.
                                                                    \tag{24}
\]

This is finite, not an asymptotic counterexample; its role is to certify
the deletion mechanism and the exact span bookkeeping.

## 6. Exact computational gate

`audit_core_stability.py` and `audit_repeated_gate.py` enumerate every
endpoint-normalized subset

\[
 A\subseteq[0,N-1],\qquad\{0,N-1\}\subseteq A,qquad2\le N\le22.
\]

The domain has exactly

\[
 \sum_{N=2}^{22}2^{N-2}=2{,}097{,}151
\]

subsets.  The incremental unordered-sum gate found 11,969 admissible sets,
of which 8,792 have exceptional multiplicity at least two.  For each leaf,
the audit independently rebuilt \(P,R,p,\delta\), checked
\(r_A(\sigma)=p+\delta\), and checked (1) after clearing by two.

Every density gate was evaluated as the integer inequality

\[
 3b k^2>(4b+3a)N
 \quad\Longleftrightarrow\quad
 {k^2\over N}>{4\over3}+{a\over b}.                     \tag{25}
\]

The exact results are:

\[
\begin{array}{c|r|r|r|r|r}
\eta&\text{gate sets}&u>0&\text{completion fails}&\text{same-span fails}&\text{(11) fails}\\ \hline
0&6605&6370&2638&864&6004\\
1/12&6283&6048&2604&858&5760\\
1/6&6015&5790&2560&838&5556\\
1/4&5781&5556&2522&824&5360\\
1/3&3903&3712&1740&584&3608\\
1/2&1836&1700&774&322&1666
\end{array}                                               \tag{26}
\]

These finite counts do not disprove an asymptotic theorem.  They exactly
falsify the two candidate bridges before any asymptotic proof attempt and
verify the reflection identities over the stated exhaustive domain.

## 7. Corrected frontier

Residual negligibility is the wrong reduction target.  Any viable reduction
must be compatible with hereditary one-sided deletion.  A possible form is
a completion/blocker dichotomy with explicit span accounting:

1. enough missing partners can be adjoined while preserving admissibility,
   producing a denser fully reflected object; or
2. the collisions blocking those adjunctions supply a quantitative label
   charge strong enough to prove the global span bound directly.

The second branch is essential by (16)--(18).  P09's residual-difference
packing and P10's decorated cutoff provide charges after a blocker has been
identified, but neither currently converts the full collection of
completion blockers into the missing leading-order gain.

The P38 lane therefore closes with an exact obstruction, not a proof of
\(|R|=o(k)\): such a proof would already exclude the fully reflected
counterexamples it was meant to leave for the next stage.
