The proposed raw-overlap estimate is false:

[
\boxed{\text{There are admissible examples with }\max E=(3+o(1))p^2
\quad\text{and}\quad |I|\gg p^2.}
]

Thus (|I|=O(p^{3/2})) cannot be the load-bearing lemma. The quadratic overlap is almost exactly cancelled by uncovered residues in the modular covering count.

Singer perfect difference sets exist for every prime-power order (q), with parameters (N=q^2+q+1) and (p=q+1). ([arXiv][1]) The argument below is otherwise self-contained.

## 1. Quadratic-overlap theorem

**Theorem.** There is an absolute constant (c>0) and an infinite sequence of triples ((p,Z,G)), with (p\to\infty), such that:

1. (Z={0=z_0<\cdots <z_{p-1}=W}) is a literal integer Sidon set, diagonals included;
2. (G>W), so for (E=G+2Z),
   [
   E\cap(E+E+E)=\varnothing
   ]
   even when the three summands are allowed to repeat;
3. [
   \max E=(3+o(1))p^2;
   ]
4. for the (b,\gamma,h,B,S,D,I) in the question,
   [
   |I|\ge c p^2.
   ]

In particular,

[
\frac{|I|}{p^{3/2}}\longrightarrow\infty
]

along this sequence.

### Construction of (Z)

Let (q) be a prime power, put

[
p=q+1,\qquad N=q^2+q+1=p^2-p+1.
]

Take a Singer perfect difference set (A\subseteq\mathbb Z/N\mathbb Z) of size (p). Thus every nonzero residue has exactly one ordered representation as (a-a'), with (a,a'\in A).

The residue (1) therefore has a unique representation (x-y). Translate (A) by (-x). The translated set contains (0) and (-1=N-1). Let (Z) be its representatives in ({0,\ldots,N-1}). Then

[
0,N-1\in Z,\qquad W=N-1=p^2-p.
]

It is modular Sidon. Indeed, if

[
a+b\equiv c+d\pmod N,
]

then

[
a-c\equiv d-b\pmod N.
]

If this residue is zero, then (a=c) and (b=d). If it is nonzero, uniqueness of ordered differences gives ((a,c)=(d,b)). Hence ({a,b}={c,d}). Consequently all literal integer sums (a+b), including (2a), are distinct.

### Equidistribution of the Singer lift

Let (f=1_Z) on (\mathbb Z/N\mathbb Z), using the unnormalised Fourier transform. For every nontrivial character (k),

[
\begin{aligned}
|\widehat f(k)|^2
&=\sum_{a,a'\in Z}e_N(k(a-a'))\
&=p+\sum_{t=1}^{N-1}e_N(kt)\
&=p-1.
\end{aligned}
]

For every cyclic interval (J\subseteq\mathbb Z/N\mathbb Z), Fourier inversion and the standard Dirichlet-kernel estimate give

[
\left||Z\cap J|-\frac{p|J|}{N}\right|
\leq C\sqrt p\log N=o(p).                                      \tag{1}
]

Therefore the empirical measures

[
\mu_q=\frac1p\sum_{z\in Z}\delta_{z/W}
]

converge weakly to Lebesgue measure on ([0,1]). Their fourth product measures converge as well.

For (0<\eta<1/10), define

[
\Omega_\eta=
\left{(x_1,x_2,x_3,x_4)\in[0,1]^4:
\frac12-\eta
\leq x_1+x_2+x_3-x_4
\leq \frac12-\frac{\eta}{2}
\right}.
]

This set has volume at least a fixed constant times (\eta). Explicitly, restrict (x_1,x_2,x_3) to ([0.30,0.31]). For every such triple, the admissible (x_4)-interval has length (\eta/2) and lies inside ([0,1]). Hence

[
\lambda^4(\Omega_\eta)\geq \frac{\eta}{2,000,000}.             \tag{2}
]

It follows from (1) and product convergence that, for every fixed (\eta) and all sufficiently large (q),

[
#\left{(a,b,u,v)\in Z^4:
\left(\frac aW,\frac bW,\frac uW,\frac vW\right)\in\Omega_\eta
\right}
\geq \frac{\eta p^4}{4,000,000}.                              \tag{3}
]

All quadruples here are ordered and repetitions are retained.

For an integer (\ell), put

[
R(\ell)=
#{(a,b,u,v)\in Z^4:a+b+u-v=\ell}.
]

The quadruples in (3) have

[
\left(\frac12-\eta\right)W
\leq \ell
\leq
\left(\frac12-\frac{\eta}{2}\right)W.                            \tag{4}
]

There are at most (\eta W) possible integers in this interval, once (q) is large. Since (W<p^2), some integer (\ell) in (4) satisfies

[
R(\ell)\geq \frac{p^2}{4,000,000}.                             \tag{5}
]

Now take a sequence (\eta_m\downarrow0), and for each (m) choose a sufficiently large prime power (q_m) for which (3)–(5) hold.

### Choice of (G)

For the selected (\ell), define

[
\gamma=W-\ell,\qquad G=2\gamma+1=2W-2\ell+1.
]

Thus (b=1). From the upper bound in (4),

[
G-W=W-2\ell+1\geq \eta W+1>0,
]

so (G>W).

This immediately audits the threefold condition. If

[
G+2z= (G+2z_1)+(G+2z_2)+(G+2z_3),
]

then

[
z=G+z_1+z_2+z_3\geq G>W,
]

contradicting (z\leq W). This argument does not require the (z_i) to be distinct.

Moreover,

[
\max E=G+2W=4W-2\ell+1.
]

By (4),

[
(3+\eta)W+1\leq \max E\leq(3+2\eta)W+1.
]

Since (W=p^2-p) and (\eta_m\to0),

[
\max E=(3+o(1))p^2.                                              \tag{6}
]

### Conversion of (R(\ell)) into carry-level-one overlap

Here

[
h=\gamma+W+1=2W-\ell+1.
]

For a quadruple counted by (R(\ell)), let

[
t=a+b,\qquad d=u-v,\qquad s=2\gamma+t\in B+B.
]

Then

[
s+d=2\gamma+\ell=2W-\ell=h-1=h-b.                               \tag{7}
]

Thus every such quadruple induces a level-one witness.

Let

[
K_\ell=
#{(t,d):t\in Z+Z,\ d\in Z-Z,\ t+d=\ell},
]

where (Z+Z) is the set of distinct unordered sums, with diagonals retained.

For (d\neq0), literal Sidonicity gives exactly one ordered representation (d=u-v); a sum (t) has at most two ordered representations, and exactly one when it is diagonal. For (d=0), there are (p) ordered representations (u=v), but at most one corresponding sum (t=\ell). Consequently

[
R(\ell)\leq 2K_\ell+2p,
]

and hence

[
K_\ell\geq\frac{R(\ell)-2p}{2}.                                  \tag{8}
]

Two different sums (t_1,t_2\in[0,2W]) give the same residue (s\bmod h) only when (t_1-t_2=\pm h). Since (2W<2h), every residue receives at most two such witnesses. Equations (7) and (8) therefore imply

[
|I|
\geq \frac{K_\ell}{2}
\geq \frac{R(\ell)-2p}{4}
\geq 10^{-8}p^2                                                   \tag{9}
]

for all sufficiently large members of the selected sequence. This proves the theorem.

## 2. Why raw overlap cannot control the deficit

Write

[
\bar S=S\bmod h,\qquad
\bar D=-b-D\bmod h,
]

and define the internal folding losses and the number of uncovered residues by

[
a=|S|-|\bar S|,\qquad
c=|D|-|\bar D|,\qquad
H=h-|\bar S\cup\bar D|.
]

Since

[
|S|=\frac{p(p+1)}2,\qquad
|D|=p(p-1)+1,
]

we have

[
T:=|S|+|D|=\frac{3p^2-p+2}{2}.
]

Exact inclusion–exclusion gives

[
T-h=a+c+|I|-H.                                                    \tag{10}
]

Also (\max E=2h+b-2), so

[
\boxed{
3p^2-\max E
===========

p-b+2\bigl(a+c+|I|-H\bigr).
}                                                                \tag{11}
]

Thus an overlap of order (p^2) is compatible with the conjectured bound whenever it is paired with (p^2) uncovered residues. The Singer family above does exactly that. Any successful carry argument must control the **signed defect**

[
a+c+|I|-H,
]

not (|I|) alone.

## 3. Finite exact certificate

Here is one concrete member, with (p=44):

[
\begin{aligned}
Z={&
0,12,155,187,196,234,315,329,553,574,614,684,704,735,781,818,\
&843,887,967,975,1035,1120,1139,1144,1235,1370,1400,1406,1448,\
&1482,1493,1511,1546,1568,1585,1595,1611,1618,1684,1712,1834,\
&1838,1890,1892}.
\end{aligned}
]

Take

[
W=1892,\qquad G=2003,\qquad b=1,\qquad
\gamma=1001,\qquad h=2894.
]

Exact integer checks give:

[
|Z+Z|=\frac{44\cdot45}{2}=990,
]

so every unordered sum, including all (2z_i), is distinct;

[
|Z-Z|=44\cdot43+1=1893;
]

and (G>W), so (E\cap3E=\varnothing) with repetitions allowed. Furthermore,

[
\max E=G+2W=5787,\qquad 3p^2=5808.
]

For the carry overlap,

[
|I|=614,
]

split exactly as

[
372\text{ level-one only},\qquad
209\text{ level-two only},\qquad
33\text{ at both levels}.
]

The folding data are

[
a=13,\qquad c=44,\qquad H=682.
]

Thus

[
a+c+|I|-H=13+44+614-682=-11,
]

and (11) gives

[
3p^2-\max E
=43+2(-11)
=21,
]

exactly.

So the raw overlap here is already

[
|I|=0.317148\ldots,p^2,
]

while its contribution is cancelled by holes. The same mechanism persists in the infinite Singer family.

This does not settle the (3p^2-o(p^2)) lower bound, which remains part of the open problem. ([Erdős Problems][2]) It does rigorously eliminate the proposed (O(p^{3/2})) overlap route—even at the asymptotically extremal scale (\max E=(3+o(1))p^2).

[1]: https://arxiv.org/abs/2605.03274 "[2605.03274] Formalizing Singer Sidon Constructions and Sidon Set Infrastructure in Lean 4"
[2]: https://www.erdosproblems.com/864 "864 | Erdős Problems"
