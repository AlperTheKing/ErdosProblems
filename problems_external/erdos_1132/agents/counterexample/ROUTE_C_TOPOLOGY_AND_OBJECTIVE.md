# Route C: topology test and exact finite block objective

## 1. Tao's interval-intersection conclusion does not by itself kill a
point-finite schedule

Enumerate all nonempty rational open intervals contained in \((-1,1)\) as
\[
  I_j=(a_j,b_j),\qquad j\geq 1.
\]
For \(s\geq j\), put \(\delta_j=b_j-a_j\) and define the rational open
interval
\[
  V_{s,j}=
  \left(
    a_j+\frac{\delta_j}{s+2}-\frac{\delta_j}{4(s+2)^2},
    a_j+\frac{\delta_j}{s+2}+\frac{\delta_j}{4(s+2)^2}
  \right).
\]
Then \(V_{s,j}\subset I_j\).  For \(1\leq q\leq s\), define
\[
  U_{s,q}=\bigcup_{1\leq j\leq q}V_{s,j}.
\]

### Proposition 1

The sets \(U_{s,q}\) have both of the following properties.

1. For each fixed \(q\), the family \((U_{s,q})_{s\geq q}\) is
   point-finite.
2. For every nonempty open interval \(I\subset(-1,1)\), there is an integer
   \(q_I\) such that \(U_{s,q_I}\cap I\ne\varnothing\) for every
   \(s\geq q_I\).

### Proof

For fixed \(j\), both endpoints of \(V_{s,j}\) converge to \(a_j\) from the
right, while \(a_j\notin V_{s,j}\).  If \(x>a_j\), then the right endpoint
is eventually smaller than \(x\); if \(x\leq a_j\), then \(x\) never lies in
\(V_{s,j}\).  Thus \((V_{s,j})_{s\geq j}\) is point-finite.  For fixed
\(q\), \(U_{s,q}\) is the union of only the first \(q\) such families, so it
is point-finite.

Given \(I\), choose \(I_j\subset I\) from the rational basis and take
\(q_I=j\).  For every \(s\geq j\),
\(V_{s,j}\subset U_{s,j}\cap I\), proving the second assertion.
\(\square\)

Consequently, the qualitative content of Tao's local theorem—every fixed
interval has some finite interval-dependent defect budget at which every
sufficiently late high set meets that interval—is compatible with
point-finiteness at each fixed budget.  A Baire-category contradiction would
require one fixed budget that forces intersections with a basis of every
open interval.  Tao's theorem does not supply such a uniform budget.

This proposition is only a topology model.  It does not assert that
Lebesgue high sets can be placed inside these sets by nested node insertion.

## 2. Exact insertion identity

Let the current prefix be \(X=(x_1,\ldots,x_N)\), with node polynomial
\[
  P(z)=\prod_{i=1}^N(z-x_i).
\]
Append a block \(Y=(y_1,\ldots,y_M)\), and for \(1\leq t\leq M\) write
\[
  Q_t(z)=\prod_{j=1}^t(z-y_j),\qquad R_t(z)=P(z)Q_t(z).
\]
For every \(x\) distinct from the nodes, the exact Lebesgue function of the
intermediate prefix of length \(N+t\) is
\[
\begin{split}
L_{N+t}(x)
={}&|P(x)Q_t(x)|
\sum_{i=1}^N
\frac{1}{|x-x_i|\,|P'(x_i)|\,|Q_t(x_i)|}\\
&+|P(x)Q_t(x)|
\sum_{j=1}^t
\frac{1}{|x-y_j|\,|P(y_j)|\,|Q_t'(y_j)|}.
\end{split}
\tag{1}
\]
At a node, the corresponding removable value is used; in particular the
Lebesgue function equals \(1\) at every node.

Identity (1) follows directly from
\[
  R_t'(x_i)=P'(x_i)Q_t(x_i),\qquad
  R_t'(y_j)=P(y_j)Q_t'(y_j).
\]

## 3. Exact finite block objective

For a stage \(s\), a prefix \(X\), proposed rational-open containers
\((U_{s,q})_{1\leq q\leq s}\), and an appended block \(Y\), the
theorem-closing finite objective is the simultaneous family
\[
  L_{N+t}(x)\leq \frac{2}{\pi}\log(N+t)-q
  \quad
  \text{for all }
  \begin{cases}
    1\leq t\leq M,\\
    1\leq q\leq s,\\
    x\in(-1,1)\setminus U_{s,q}.
  \end{cases}
\tag{2}
\]
The left side in (2) must be evaluated by (1) for every intermediate prefix,
not only at \(t=M\).

For rational nodes and rational container endpoints, a proposed certificate
for (2) can be replayed interval by interval.  After splitting at all nodes,
container endpoints, and sign changes of the Lagrange basis polynomials, the
absolute values have fixed signs and \(L_{N+t}\) is a polynomial of degree
at most \(N+t-1\).  Its maximum on each closed component is attained at an
endpoint or a real zero of its derivative.  Sturm isolation plus certified
interval bounds for \(\pi\) and \(\log(N+t)\) gives a rigorous finite replay
whenever the proposed certificate includes a positive rational margin.
Without such a margin, an equality case need not be decidable merely by
successively tightening numerical intervals.

The unresolved construction question is whether any prefix can be extended
by a block satisfying (2) for a point-finite container schedule.  The
topology alone neither proves nor refutes this insertion claim.

## 4. Clustered appended blocks have the opposite localization behavior

### Proposition 2

Let \(P(z)=\prod_{i=1}^N(z-x_i)\) be a fixed prefix polynomial, let
\(c\in(-1,1)\setminus\{x_1,\ldots,x_N\}\), and fix distinct real numbers
\(z_1,\ldots,z_m\), where \(m\geq2\). Append
\[
  y_j(\varepsilon)=c+\varepsilon z_j,\qquad 1\leq j\leq m.
\]
If \(K\) is any compact subset of
\((-1,1)\setminus(\{x_1,\ldots,x_N\}\cup\{c\})\), then there are constants
\(C_K>0\) and \(\varepsilon_K>0\) such that
\[
  \inf_{x\in K}L_{N+m}^{(\varepsilon)}(x)
  \geq C_K\varepsilon^{-(m-1)}
  \qquad(0<\varepsilon<\varepsilon_K).
\]

### Proof

For \(y_j=c+\varepsilon z_j\), cancellation of its own factor gives
\[
 |\ell_{y_j,N+m}^{(\varepsilon)}(x)|
 =
 \frac{|P(x)|}{|P(c+\varepsilon z_j)|}
 \frac{\prod_{r\ne j}|x-c-\varepsilon z_r|}
 {\varepsilon^{m-1}\prod_{r\ne j}|z_j-z_r|}.
\]
On \(K\), the factors \(|P(x)|\) and
\(|x-c-\varepsilon z_r|\) are uniformly bounded below for sufficiently
small \(\varepsilon\), while \(|P(c+\varepsilon z_j)|\) is uniformly
bounded above. The fixed factors \(|z_j-z_r|\) are nonzero. Thus the
displayed expression is at least \(C_K\varepsilon^{-(m-1)}\), and
\(L\geq|\ell_{y_j}|\). \(\square\)

Thus appending a microscopic cluster does not place its high set near the
cluster. It makes the Lebesgue function diverge on every compact set away
from the old nodes and cluster center. The same calculation applies to each
intermediate clustered prefix containing at least two new nodes, with
exponent \(t-1\). This falsifies the clustered-block implementation of (2).
Any surviving Route C construction must distribute each appended block
macroscopically and control both sums in (1).

