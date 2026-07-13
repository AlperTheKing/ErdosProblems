# Erdos Problem 864: integer carry-layer inequality

Let

\[
E=\{G+2z:z\in Z\},\qquad
Z=\{0=z_0<z_1<\cdots<z_{p-1}=W\},
\]

where \(E\) is a positive integer Sidon set satisfying

\[
E\cap(E+E+E)=\varnothing,
\]

with repeated summands permitted in the threefold sumset. Put \(b=1\) if
\(G\) is odd and \(b=2\) if \(G\) is even, and define

\[
\gamma=(G-b)/2,\qquad h=\gamma+W+1,\qquad
B=\gamma+Z\subseteq\{0,\ldots,h-1\}.
\]

Then \(E=b+2B\). Let \(S=B+B\) be the set of distinct integer pair sums,
including diagonal sums, and let \(D=B-B\) be the set of distinct integer
differences. Define

\[
S_h=\{s\bmod h:s\in S\},\qquad
D_h=\{d\bmod h:d\in D\},
\]

and

\[
I=S_h\cap(-b-D_h).
\]

Every element of \(I\) is witnessed at carry level one or two:

\[
s+d=h-b\qquad\hbox{or}\qquad s+d=2h-b,
\]

for some \(s\in S\) and \(d\in D\). Carry level zero is excluded by
\(E\cap(E+E+E)=\varnothing\).

Since \(B\) is Sidon in the integers,

\[
|S|=\frac{p(p+1)}2,\qquad |D|=p(p-1)+1.
\]

Define

\[
a=|S|-|S_h|,\qquad c=|D|-|D_h|,
\]

and

\[
\delta=\frac{3p^2-p+2}{2}-h.
\]

Inclusion-exclusion gives the exact lower bound

\[
|I|\ge\max(0,\delta-a-c).
\]

The desired estimate \(\max E\ge3p^2-o(p^2)\) is equivalent, up to an
additive constant, to \(\delta=o(p^2)\).

The total overlap \(|I|\) itself is not small. For the exact Singer example
with \(p=168\),

\[
h=37481,\quad |S_h|=13943,\quad |D_h|=27087,
\]

\[
a=253,\quad c=970,\quad\delta=4772,
\quad\delta-a-c=3549,\quad |I|=10096.
\]

Its carry decomposition has 7622 residues only at level one, 1888 only at
level two, and 586 at both levels. Thus a proof cannot bound total overlap
by \(O(p^{3/2})\); it must retain the carry level, multiplicity, sign, or a
comparable unit-lattice phase invariant.

Please provide one rigorous, non-circular lemma, with a complete proof,
which implies \(\delta=o(p^2)\) using literal integer Sidonicity and
\(E\cap(E+E+E)=\varnothing\). Useful possible forms include:

1. an exact inequality relating \(\delta\) to a signed or weighted
   difference between the level-one and level-two representation counts;
2. an exact inequality showing that positive quadratic \(\delta\) forces a
   forbidden carry-zero representation;
3. a structural theorem for the modular sum and difference collisions
   contributing to \(a\) and \(c\) that yields \(\delta=o(p^2)\); or
4. a different integer carry-capacity inequality strong enough to imply
   \(h\ge(3/2-o(1))p^2\).

Do not assume modular Sidonicity or any additional reflection symmetry.
Retain all diagonal pair sums and all repeated summands in \(E+E+E\). The
ordinary modular covering count and the support-sensitive centered-codegree
identity are already known and do not close the estimate. If an intermediate
statement is false, give an explicit finite mathematical example and verify
all its properties exactly.