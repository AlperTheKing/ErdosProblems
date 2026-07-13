# P106: exact positive-defect falsifier to RM97

## Verdict

RM97 is false under positive defect.  In fact, its scalar consequence

\[
                         T_F\leq C_S+V_b                         \tag{1}
\]

is already false.  An exact endpoint Sidon witness has

\[
 (p,h,b,\delta,C_S,T_F,V_b)=(67,6572,1,129,199,221,20),          \tag{2}
\]

and hence

\[
                         221>199+20=219.                          \tag{3}
\]

Thus its 420 canonical-plus-loose intervals cannot inject into its 418
RM97 slots, independently of any matching algorithm.

This is a positive-defect, `b=1` falsifier, not a literal-hole falsifier.
Its difference support meets `B+B+1` in 124 labels.  The specialization of
RM97 to the literal hole is not decided here.

The witness also answers the proposed minimal-closure route.  A minimal
Hall-deficient interval is

\[
                         J=[-1444,4730].                           \tag{4}
\]

It contains 411 intervals and 410 slots.  The P83 endpoint transfers close
inside this window, and the 193 fold equations participating in the closure
have exact rational rank 66 on 68 variables.  The closure is therefore
affinely rigid.  Positive defect does not exclude it: the primitive
realization itself has positive defect, while its 20 collision slots are two
short of the global scalar requirement.  Positive defect excludes only the
collision-free rescalings of this closure.

## 1. Exact witness

Take

```text
B = [1, 128, 245, 327, 657, 703, 958, 977, 999, 1057, 1107,
     1363, 1675, 1677, 1841, 1883, 1916, 2103, 2141, 2235,
     2645, 2681, 2829, 2899, 3041, 3217, 3227, 3235, 3272,
     3431, 3707, 3733, 3851, 4115, 4149, 4307, 4347, 4481,
     4641, 4761, 4778, 4951, 5043, 5129, 5193, 5197, 5309,
     5577, 5631, 5679, 5803, 5901, 5917, 5924, 6053, 6141,
     6153, 6263, 6341, 6369, 6401, 6425, 6431, 6445, 6497,
     6510, 6571].
```

There are exactly

\[
                         {67\cdot68\over2}=2278
\]

unordered pair sums with repetition, and exact enumeration finds 2278
distinct values.  Hence `B` is integer Sidon.  Also `max(B)=6571=h-1`, and

\[
 {3p^2-p+2\over2}-h=6701-6572=129>0.                            \tag{5}
\]

Exact fold and loose-triangle enumeration gives the remaining entries of
(2).  The 20 collision slots have explicit certificates

\[
             a+c+1=y-x,\qquad x,y\in B,quad x<y,                 \tag{6}
\]

stored fold by fold in `positive_rm97_falsifier_certificate.json`.

The construction starts with the 60-mark `q=2` lift of P88 and inserts

```text
128, 958, 1916, 3272, 4778, 5924, 6510.
```

The parent has

```text
(p, delta, C_S, T_F, V_b) = (60, -1201, 182, 200, 0)
intervals - slots          = 18.
```

The seven insertions raise the defect baseline by 1330 and reduce the scalar
excess from 18 to 2, but they do not remove it.

## 2. Residual intervals and P83 transfers

For a canonical fold

\[
 F=(a,c,u,v),\qquad a\leq c<u\leq v,\qquad a+c+h=u+v,
\]

put

\[
 q_F=a+c+b,\qquad L_F=h-b-v,\qquad U_F=h-b-u.                    \tag{7}
\]

For every canonical or loose shadow triple `(a,c,u)`, put

\[
 \tau=u-a-c-b,\qquad \lambda=h-b-u,
 \qquad I=[\min(\tau,\lambda),\max(\tau,\lambda)].              \tag{8}
\]

RM97 supplies the slots `L_F,U_F` and one extra copy of `L_F` when
`q_F` is a represented positive difference.

For a loose triangle in P83 normal form,

\[
\begin{array}{lll}
 F_0=(a,c,u+R,s),&F_Z=(a,c+Z,u,s+R+Z),
 &F_X=(a+X,c,u,s+R+X),
\end{array}
\]

direct substitution gives

\[
\begin{array}{c|cc}
 &L&U\\ \hline
F_0&\tau+R&\lambda-R\\
F_Z&\tau-Z&\lambda\\
F_X&\tau-X&\lambda.
\end{array}                                                       \tag{9}
\]

Thus the two arm intervals share `lambda`, while the base and loose
intervals are concentric:

\[
                    (\tau+R)+(\lambda-R)=\tau+\lambda.           \tag{10}
\]

Their endpoint hulls are nested.  These identities were checked on all 221
loose triangles of the witness.

There is also an exact fixed-`u` cycle law.  If arm folds `i,j` have low
pairs `(a_i,c_i),(a_j,c_j)` and the directed loose edge `i -> j` has base
low pair `(a_i,c_j)`, then

\[
 L_i=u-a_i-c_i-b,qquad \tau_{ij}=u-a_i-c_j-b,
\]

so

\[
 \tau_{ij}-L_i=c_i-c_j,
 \qquad \tau_{ij}-L_j=a_j-a_i.                                  \tag{11}
\]

Both transfers telescope on a directed cycle, giving

\[
                   \sum \tau_{ij}=\sum L_i.                      \tag{12}
\]

The falsifier therefore obeys the proposed nesting and closure identities;
those identities do not imply RM97.

## 3. Minimal Hall windows

Exact enumeration of all windows whose endpoints are residual interval
endpoints finds 15 deficient windows and two inclusion-minimal ones:

\[
                    [-1444,4730],\qquad[-1276,4894].              \tag{13}
\]

For the first minimal window, the exact census is

```text
contained canonical intervals   191
contained loose intervals       220
contained intervals total       411
L slots in J                    199
U slots in J                    191
collision slots in J             20
slots total                     410
Hall deficit                      1
crossing canonical intervals      8
strictly containing intervals     0
```

All 20 collision slots lie in `J`.  Of the 220 contained loose intervals,
215 have their concentric P83 base interval in `J`, while five transfer
across its boundary.  Thus the failure is not caused by collision capacity
sitting elsewhere: all available correction is already charged to the
minimal window, and one unit of Hall deficit remains.

The second minimal window contains 413 intervals and 412 slots.  It has 193
canonical and 220 loose intervals, all 199 lower slots, 193 upper slots, and
all 20 collision slots.

## 4. Affine closure and the defect gate

For the first window, take every fold supporting a contained loose interval
and every fold whose canonical interval is contained.  This uses 193 of the
199 fold equations

\[
                         x_a+x_c+h-x_u-x_v=0.                     \tag{14}
\]

on 67 mark variables and `h`.  Exact modular elimination gives

```text
prime       closure rank   full rank
1000003          66           66
1000033          66           66
```

A nonzero modular minor proves rational rank at least 66.  Common translation
of all marks and the displayed coordinate vector together with `h` are two
independent rational null vectors, proving rank at most 66.  Hence

\[
              \operatorname{rank}_{\mathbb Q}=66,
              \qquad\operatorname{nullity}_{\mathbb Q}=2.       \tag{15}
\]

Every rational realization of this closure is therefore affine.  The gcd of
the witness differences is one, so every integral endpoint-normalized
realization is

\[
                         x\longmapsto qx+(q-1),
                         \qquad h\longmapsto qh                 \tag{16}
\]

for a positive integer `q`.

At `q=1`, (16) is the witness itself: `delta=129`, `V_1=20`, and the scalar
excess is 2.  For every `q>=2`, all marks are `-1 mod q`, all differences are
`0 mod q`, and every phase label `a+c+1` is `-1 mod q`; hence `V_1=0`.
But already `q=2` has

\[
                         \delta=6701-13144=-6443.                 \tag{17}
\]

This identifies the precise failure of the hoped-for positive-defect
argument.  Positive defect excludes the collision-free scales `q>=2`, but
does not exclude the primitive closed scale `q=1`.  At that scale collisions
exist, yet their number is not enough to repair either (1) or Hall.

## 5. Exact search and verification

The seven additions were found by exact bitset clique search among all 2401
individually admissible insertions into the lifted P88 parent.  Before the
witness, the search visited 9,213,278 nodes, reached 35 pairwise-compatible
seven-cliques, and exactly audited 11 internally Sidon cliques.  The search
need not be exhaustive because the displayed witness is independently
checkable.

`verify_positive_falsifier.py` independently checks:

* all 2278 Sidon pair sums;
* the endpoint and positive-defect calculation;
* `C_S=199`, `T_F=221`, and all 20 represented phase labels;
* rejection by the pre-existing P97 matcher;
* both minimal Hall windows and the first window's exact census;
* all 221 P83 transfer identities;
* the closure and full fold-equation ranks modulo two primes;
* the affine scaling and collision residue calculation.

Run

```powershell
python -B problems/864/compute/p106/search_full_parent_kclique.py `
  --target 7 --output problems/864/compute/p106/full_parent_kclique_7.json
python -B problems/864/compute/p106/analyze_minimal_hall_interval.py `
  --witness problems/864/compute/p106/full_parent_kclique_7.json `
  --output problems/864/compute/p106/positive_falsifier_minimal_hall.json
python -B problems/864/compute/p106/verify_positive_falsifier.py `
  --witness problems/864/compute/p106/full_parent_kclique_7.json `
  --hall problems/864/compute/p106/positive_falsifier_minimal_hall.json `
  --output problems/864/compute/p106/positive_rm97_falsifier_certificate.json
```

The falsifier has SHA-256

```text
e9c01faaddc25c8df00bb49adfdcba99d8f73282d925c1c15ec48976b1c6726b
```

for the comma-separated mark list.
