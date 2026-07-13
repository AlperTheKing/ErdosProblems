# P45: exact signed carry identities

## Verdict

There is an exact identity strictly finer than support inclusion-exclusion.
With the notation below,

\[
 \boxed{\delta=M_1+M_2-u+a_0+c_0.}                    \tag{1}
\]

Here \(M_k\) is the number of literal integer pairs
\((s,d)\in S\times D\) with \(s+d=kh-b\), \(u\) is the number of residues
missed by both \(S_h\) and \(-b-D_h\), and \(a_0,c_0\) count doubled sum and
shifted-difference fibers, respectively, which miss the other support.
Thus (1) retains the multiplicity discarded by inclusion-exclusion.

There is also an independent exact energy identity. Let \(A_{11}\) and
\(A_{22}\) count doubled sum fibers of two diagonal and two off-diagonal
sums, respectively, and let \(A_{12}\) count mixed fibers in either order.
Then

\[
 \boxed{a=A_{11}+A_{12}+A_{22},\qquad
        c=A_{11}+2A_{12}+4A_{22}.}                     \tag{2}
\]

In particular,

\[
 a\le c\le4a,\qquad 0\le4a-c=3A_{11}+2A_{12}\le2p.    \tag{3}
\]

The literal geometry has a sharper four-set description in terms of low
and high sum lifts and positive and negative difference lifts. It yields
exact first-moment identities as well as count identities. The obstruction
is not based on the unweighted quantity \(M_1-M_2\): on the 37 audited
profiles with \(p\ge72\) and \(\delta>0\), the overlap and signed count are
on the \(p^2\) scale, while raw, transformed, and centered signed residue
moments are all on the \(hp^2\) scale. A finite twin also reverses the signs
of both the raw and centered sum-residue moments while preserving every
unsigned count in (1), (2), and (19). Identity (1) and the weighted
obstruction, rather than an asymptotic bound, are the result of this lane.

## 1. Conventions and representation multiplicities

All sums and differences in this note are literal integers. Put

\[
 S=B+B=\{x+y:x,y\in B\},\qquad D=B-B.
\]

The diagonal sums \(2x\) are in \(S\). Integer Sidonicity gives

\[
 |S|=\binom{p+1}{2},\qquad |D|=p(p-1)+1,
\]

and hence

\[
 \delta=|S|+|D|-h.                                    \tag{4}
\]

For \(s\in S\), let

\[
 q(s)=\#\{(x,y)\in B^2:x+y=s\}
     =\begin{cases}1,&s=2x,\\2,&s=x+y,\ x\ne y.
       \end{cases}                                    \tag{5}
\]

For \(d\in D\), let

\[
 v(d)=\#\{(z,w)\in B^2:z-w=d\}
     =\begin{cases}p,&d=0,\\1,&d\ne0.
       \end{cases}                                    \tag{6}
\]

Thus the fully ordered carry count is

\[
 Q_k=\sum_{\substack{s\in S,d\in D\\s+d=kh-b}}q(s)v(d)
    =\#\{(x,y,z,w)\in B^4:x+y+z-w=kh-b\}.              \tag{7}
\]

No distinctness is imposed in (7). It includes diagonal \(x=y\), the case
\(z=w\), and every other repeated choice among the three positive
summands. In particular,

\[
 -b\notin3B-B\quad\Longleftrightarrow\quad M_0=Q_0=0, \tag{8}
\]

with repetitions included on both sides.

If \(e_k\) is the number of literal carry-\(k\) pairs whose sum \(s\) is a
diagonal and

\[
 z_k=\begin{cases}q(kh-b),&kh-b\in S,\\0,&kh-b\notin S,
       \end{cases}
\]

then the exact conversion between literal and ordered counts is

\[
 \boxed{Q_k=2M_k-e_k+(p-1)z_k.}                        \tag{9}
\]

The last term is precisely the extra multiplicity of \(d=0\).

## 2. Energy identity for \(a\) and \(c\)

For a residue \(r\in\mathbb Z/h\mathbb Z\), define the ordered modular
sum and difference multiplicities

\[
 R_+(r)=\sum_{s\equiv r\pmod h}q(s),\qquad
 R_-(r)=\sum_{d\equiv r\pmod h}v(d).
\]

Counting ordered solutions of \(x+y=z+w\) modulo \(h\) in the two
orientations gives the additive-energy identity

\[
 \sum_rR_+(r)^2=\sum_rR_-(r)^2.                        \tag{10}
\]

Before reduction modulo \(h\), both sides equal

\[
 p+4\binom p2=p^2+p(p-1)=2p^2-p.                      \tag{11}
\]

Every fiber of \(S\to S_h\) and \(D\to D_h\) has size at most two. A
doubled difference fiber contains two nonzero differences, each of weight
one; the fiber containing \(0\) cannot double. Therefore folding \(D\)
increases (11) by \(2c\). A doubled sum fiber \(\{s,s+h\}\) increases it
by \(2q(s)q(s+h)\). Equation (10) gives the sharper identity

\[
 \boxed{c=\sum_{\substack{s,s+h\in S}}q(s)q(s+h)},     \tag{12}
\]

which is exactly (2). At most \(p\) diagonal sums occur among all folded
pairs, so \(2A_{11}+A_{12}\le p\); this proves (3). No modular Sidon
assumption was used.

## 3. The carry-fiber table

For each residue \(r\), put

\[
 \sigma_r=\#\{s\in S:s\equiv r\pmod h\},\qquad
 \tau_r=\#\{d\in D:d\equiv-b-r\pmod h\}.               \tag{13}
\]

Both numbers lie in \(\{0,1,2\}\). They cannot both equal two. Indeed,
write the two lifts as \(s_0,s_0+h\) and \(d_0,d_0+h\). Their four pair
sums occupy three consecutive carry levels, with the middle level twice.
The ranges \(0\le s\le2h-2\), \(-(h-1)\le d\le h-1\), and \(b\in\{1,2\}\)
allow only levels \(0,1,2\). The three levels would therefore be
\(0,1,2\), contradicting (8). Hence

\[
 \boxed{\sigma_r\tau_r\le2.}                           \tag{14}
\]

If \(\sigma_r=\tau_r=1\), the residue supplies one literal pair at one of
levels \(1,2\). If \(\{\sigma_r,\tau_r\}=\{1,2\}\), its two pairs differ
by \(h\), so it supplies exactly one pair at each level. It follows that
each residue supplies at most one pair to a fixed level.

Let \(R_i\) be the number of overlap residues supporting level \(i\) only,
and let \(R_{12}\) support both. Then

\[
 M_1=R_1+R_{12},\qquad M_2=R_2+R_{12},\qquad
 R=R_1+R_2+R_{12}.                                    \tag{15}
\]

Let \(a_\cap,c_\cap\) count doubled sum and shifted-difference fibers
inside the other support, and let

\[
 a_0=a-a_\cap,\qquad c_0=c-c_\cap.                    \tag{16}
\]

By (14), the two kinds of doubled fiber are disjoint. The preceding table
also proves

\[
 \boxed{R_{12}=a_\cap+c_\cap.}                         \tag{17}
\]

Finally, let

\[
 u=\left|\mathbb Z/h\mathbb Z\setminus
       \bigl(S_h\cup(-b-D_h)\bigr)\right|.              \tag{18}
\]

Exact inclusion-exclusion says

\[
 R-u=|S_h|+|D_h|-h=\delta-a-c.                         \tag{19}
\]

Combining (15), (17), and (19) gives

\[
\begin{aligned}
 M_1+M_2
   &=R+R_{12}\\
   &=\delta+u-a_0-c_0,
\end{aligned}
\]

which proves (1). Equivalently, if \(n_{ij}\) counts residues with
\((\sigma_r,\tau_r)=(i,j)\), then \(n_{22}=0\) and

\[
 \delta=-n_{00}+n_{20}+n_{02}+n_{11}+2n_{21}+2n_{12}. \tag{20}
\]

This is stronger than (19): it identifies the exact multiplicity carried
by every overlap and every doubled fiber rather than retaining only their
supports.

### 3.1 Four-set lift decomposition and moments

Identify \(\mathbb Z/h\mathbb Z\) with \(\{0,\ldots,h-1\}\), and split the
literal lifts into

\[
\begin{aligned}
 L&=\{s\in S:s<h\},&
 H&=\{s-h:s\in S,\ s\ge h\},\\
 P&=\{d\in D:d\ge0\},&
 N&=\{d+h:d\in D,\ d<0\}.
\end{aligned}                                         \tag{F1}
\]

Put \(T(r)=-b-r\pmod h\), represented in
\(\{0,\ldots,h-1\}\). The map \(T\) is an involution, and

\[
 S_h=L\cup H,\quad D_h=P\cup N,\quad
 a=|L\cap H|,\quad c=|P\cap N|.                       \tag{F2}
\]

For a tagged intersection \(r\in X\cap T(Y)\), where
\(X\in\{L,H\}\) and \(Y\in\{P,N\}\), the actual lifts are

\[
 s=r+h\,1_{X=H},\qquad d=T(r)-h\,1_{Y=N}.              \tag{F3}
\]

Let \(\eta(r)=1_{\{b=2,\ r=h-1\}}\). Since

\[
 r+T(r)=h-b+h\eta(r),
\]

the exact carry law is

\[
 \boxed{\frac{s+d+b}{h}
 =1+\eta(r)+1_{X=H}-1_{Y=N}.}                         \tag{F4}
\]

Define \(\partial_b=\{h-1\}\) for \(b=2\), and
\(\partial_b=\varnothing\) for \(b=1\). As tagged multisets of literal
solutions, the carry layers are

\[
\begin{aligned}
 \mathcal I_0
   &=(L\cap T(N))\setminus\partial_b,\\
 \mathcal I_1
   &=((L\cap T(P))\setminus\partial_b)
     \sqcup(H\cap T(N))
     \sqcup((L\cap T(N))\cap\partial_b),\\
 \mathcal I_2
   &=(H\cap T(P))
     \sqcup((L\cap T(P))\cap\partial_b).
\end{aligned}                                         \tag{F5}
\]

Here \(\sqcup\) retains solution tags when one residue supports two layers.
The hole hypothesis is exactly \(\mathcal I_0=\varnothing\). Thus the
uncorrected formulas are exact for \(b=1\), but for \(b=2\):

1. \(r=h-1\) in \(L\cap T(N)\) is carry 1, not carry 0.
2. \(r=h-1\) in \(L\cap T(P)\) is carry 2, not carry 1.

Both corrections occur under the stated hypotheses. For
\(B=\{2,3,5\},h=6,b=2\), the tag \((s,d)=(5,-1)\) is the first correction.
For \(B=\{0,3\},h=4,b=2\), the tag \((s,d)=(3,3)\) is the second.

Write

\[
 LP=L\cap T(P),\quad LN=L\cap T(N),\quad
 HP=H\cap T(P),\quad HN=H\cap T(N),
\]

and put

\[
 \epsilon_P=1_{\{b=2,\ h-1\in LP\}},\qquad
 \epsilon_N=1_{\{b=2,\ h-1\in LN\}}.
\]

Taking cardinalities in (F5) gives

\[
\boxed{\begin{aligned}
 |LN|&=\epsilon_N,\\
 M_1&=|LP|+|HN|+\epsilon_N-\epsilon_P,\\
 M_2&=|HP|+\epsilon_P,\\
 M_1-M_2&=|LP|+|HN|-|HP|+\epsilon_N-2\epsilon_P.
\end{aligned}}                                        \tag{F6}
\]

The last line is recorded but is not used as an unweighted conclusion.
For first moments, put \(\mu(A)=\sum_{r\in A}r\), and define

\[
 J_k=\sum_{r\in\mathcal I_k}r,\qquad
 K_k=\sum_{r\in\mathcal I_k}T(r).
\]

Then

\[
\boxed{\begin{aligned}
 J_1&=\mu(LP)+\mu(HN)+(h-1)(\epsilon_N-\epsilon_P),\\
 J_2&=\mu(HP)+(h-1)\epsilon_P,\\
 J_1-J_2
   &=\mu(LP)+\mu(HN)-\mu(HP)
     +(h-1)(\epsilon_N-2\epsilon_P).
\end{aligned}}                                        \tag{F7}
\]

The transformed-difference moments satisfy

\[
\boxed{\begin{aligned}
 J_1+K_1&=(h-b)M_1+h\epsilon_N,\\
 J_2+K_2&=(h-b)M_2+h\epsilon_P,\\
 K_1-K_2&=(h-b)(M_1-M_2)+h(\epsilon_N-\epsilon_P)
          -(J_1-J_2).
\end{aligned}}                                        \tag{F8}
\]

Retain the centered signed moment integrally as

\[
 2\widehat J=2(J_1-J_2)-(h-1)(M_1-M_2).               \tag{F9}
\]

Finally, the actual lift moments are

\[
\begin{aligned}
 \sum_{\mathcal I_1}s&=J_1+h|HN|,&
 \sum_{\mathcal I_1}d&=K_1-h(|HN|+\epsilon_N),\\
 \sum_{\mathcal I_2}s&=J_2+h|HP|,&
 \sum_{\mathcal I_2}d&=K_2.
\end{aligned}                                         \tag{F10}
\]

Adding each row gives \((h-b)M_1\) and \((2h-b)M_2\), respectively.
These are multiplicity-sensitive identities: a residue in both carry
layers contributes once to each tagged moment.

## 4. Exact \(p=168\) audit

For the stated sample, the residue split immediately gives

\[
 M_1=7622+586=8208,\qquad M_2=1888+586=2474.           \tag{21}
\]

The independent audit refines the remaining terms to

\[
\begin{array}{c|rrrr}
 &a_\cap&a_0&c_\cap&c_0\\ \hline
 \text{count}&207&46&379&591.
\end{array}                                            \tag{22}
\]

Thus \(R_{12}=207+379=586\). Also

\[
 u=10096-(4772-253-970)=6547.                          \tag{23}
\]

Identity (1) now reads, with no omitted residue term,

\[
 4772=8208+2474-6547+46+591.                           \tag{24}
\]

The 253 doubled sum fibers consist of 232
off-diagonal/off-diagonal and 21 mixed diagonal/off-diagonal fibers.
Hence (2) reads

\[
 970=232\cdot4+21\cdot2.                               \tag{25}
\]

There are \(e_1=91,e_2=41\) diagonal-sum carry pairs. Both levels contain
a \(d=0\) pair; its sum weights are \(z_1=2,z_2=1\). Formula (9) gives the
fully ordered counts, including all repetitions,

\[
 Q_1=2(8208)-91+167(2)=16659,\qquad
 Q_2=2(2474)-41+167=5074.                              \tag{26}
\]

The four-set data for this sample are

\[
\begin{aligned}
 (|L|,|H|,|P|,|N|)&=(2580,11616,14029,14028),\\
 (|LP|,|HN|,|HP|,|LN|)&=(2208,6000,2474,0),\\
 (\mu(LP),\mu(HN),\mu(HP),\mu(LN))
   &=(72754982,53638873,59882692,0).
\end{aligned}                                         \tag{26a}
\]

Both boundary indicators vanish. Consequently (F6)--(F9) give

\[
\begin{aligned}
 (J_1,J_2)&=(126393855,59882692),\\
 (K_1,K_2)&=(181233777,32840354),\\
 2\widehat J&=-81887994.
\end{aligned}                                         \tag{26b}
\]

Thus the signed count \(5734\), raw sum-residue moment \(66511163\),
transformed-difference moment \(148393423\), and centered moment
\(-40943997\) are all macroscopic on their natural scales. In particular,
centering reverses the sign without making the moment lower order.

## 5. Thirty-seven-profile moment audit

The checker reconstructs every fully reflected source row and then selects
the 37 profiles with \(p\ge72\) and \(\delta>0\). All 37 have
\(M_1-M_2>0\). Their exact normalized extrema are

\[
 \frac{5491}{15876}
 \le \frac{R}{p^2}
 \le \frac{2123}{5476},\qquad
 \frac{691}{5408}
 \le \frac{M_1-M_2}{p^2}
 \le \frac{1385}{5476}.                               \tag{A1}
\]

The raw sum-residue moments satisfy

\[
 \frac{14923}{683436}
 \le \frac{|J_1-J_2|}{hp^2}
 \le \frac{697279}{7403552},                           \tag{A2}
\]

and the transformed-difference moments satisfy

\[
 \frac{2704911}{25514944}
 \le \frac{|K_1-K_2|}{hp^2}
 \le \frac{293741}{1850888}.                           \tag{A3}
\]

Even after centering,

\[
 \frac{1189}{45360}
 \le \frac{|\widehat J|}{hp^2}
 \le \frac{13020095}{277620336}.                       \tag{A4}
\]

Thus overlap and signed layer imbalance stay on the \(p^2\) scale, and
all three first-moment statistics stay on the \(hp^2\) scale throughout
this finite audit. This is exact finite evidence, not an asymptotic
Theta theorem. The boundary totals are
\(\sum\epsilon_P=0\) and \(\sum\epsilon_N=4\). The four nonzero
\(\epsilon_N\) profiles are ruzsa-natural-68ea4faa8a24,
singer-natural-a0f7ec19574b, singer-natural-fb93340eb02a, and
singer-natural-7270f9d3002f. Hence omitting the \(b=2\) correction changes
actual audited profiles, not merely a degenerate toy case.

## 6. Signed-imbalance and moment falsifier



The only signed datum in (15) is

\[
 M_1-M_2=R_1-R_2.                                     \tag{27}
\]

Neither \(a,c,\delta\) nor any other unsigned quantity above fixes its
sign. Take \(h=6,b=2,p=3\) and

\[
 B^-=\{2,4,5\},\qquad B^+=\{2,3,5\}.                  \tag{28}
\]

For both sets, all six unordered sums are distinct, all seven integer
differences have the expected Sidon multiplicity, and
\(-2\notin3B^\pm-B^\pm\). The associated sets are
\(E^-=\{6,10,12\}\) and \(E^+=\{6,8,12\}\); their minimum three-sum is
18, above their maximum element. Direct enumeration gives the identical
unsigned profile

\[
 (a,c,\delta,R,u,R_{12},M_1+M_2)=(1,1,7,5,0,2,7).     \tag{29}
\]

More explicitly,

\[
\begin{aligned}
 S^-&=\{4,6,7,8,9,10\},&
 D^-&=\{-3,-2,-1,0,1,2,3\},\\
 S^+&=\{4,5,6,7,8,10\},&
 D^+&=\{-3,-2,-1,0,1,2,3\}.
\end{aligned}
\]

Intersecting these lists with \(s+d=4\) and \(s+d=10\) gives (30)
directly.

The doubled sum fiber in each case consists of the two diagonal sums
\(4\) and \(10\), so (2) gives \(c=A_{11}=1\); diagonals are essential in
this falsifier. Nevertheless,

\[
 (M_1,M_2)(B^-)=(3,4),\qquad
 (M_1,M_2)(B^+)=(4,3).                                \tag{30}
\]

The fully ordered profiles also reverse:

\[
 (Q_1,Q_2)(B^-)=(7,8),\qquad
 (Q_1,Q_2)(B^+)=(8,7).                                \tag{31}
\]

The weighted sum-residue moments and their centered versions also change
sign:

\[
\begin{aligned}
 (J_1,J_2,\widehat J)(B^-)&=(5,10,-5/2),\\
 (J_1,J_2,\widehat J)(B^+)&=(10,7,1/2).
\end{aligned}                                         \tag{31a}
\]

Moreover, \(B^+\) has \(\epsilon_N=1\): its residue \(5=h-1\) is the
literal \(b=2\) correction in (F5).

Both carry levels in both examples include a \(d=0\) solution, so (31)
also tests repeated summands rather than a distinct-variable surrogate.
The unweighted facts remain exact: \(B^+\) falsifies

\[
 M_1-M_2\le u,                                         \tag{32}
\]

and \(B^-\) falsifies universal level-1 dominance. They are auxiliary,
not the basis of the obstruction. Equation (31a) shows that neither the
raw nor centered first signed sum-residue moment has a sign determined by
the complete unsigned profile (29). The 37-profile audit then shows that
passing to first moments does not make the signed statistic lower order.

For reference, (1) can still be rewritten as the exact diagnostic

\[
 \delta=(M_1-M_2-u)+2M_2+a_0+c_0.                     \tag{33}
\]

Asking directly for
\(M_1+M_2-u+a_0+c_0=o(p^2)\) is circular by (1). No non-circular
inequality implying \(\delta_+=o(p^2)\) was established here, where
\(\delta_+=\max(\delta,0)\). This is the correct one-sided target because
\(\max E=3p^2-p+b-2\delta\). In the hard regime treated by the audit,
\(\delta>0\), the distinction disappears. A successful inequality must use
placement-sensitive information beyond unsigned fibers, and beyond the
uncontrolled first moments in (F7)--(F9).

## 7. Reproducible verification

Run from the repository root:

    python -B problems/864/compute/p45/audit_signed_carry_identity.py

The script independently rebuilds \(S,D,L,H,P,N\), verifies (1), (2),
(9), (15), (17), and (F2)--(F10), and emits
problems/864/compute/p45/audit_signed_carry_identity.json. It reconstructs
the \(p=168\) sample singer-801ada713888, checks both members of the exact
twin (28), and audits all 37 large profiles. The JSON stores every integer
moment, boundary indicator, assertion, and exact reduced rational endpoint
reported in (A1)--(A4).




