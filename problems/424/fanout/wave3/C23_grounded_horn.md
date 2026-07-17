# C23: grounded Horn / chain-boundary contraction

## Verdict

No proof or true-\(G\) counterexample was found.

The useful reduction is sharper than the original preservation proposal.
For a forward-closed allowed set \(S\) containing \(2,3\), let
\[
 F(S)=\{2,3\}\cup
 \{ab-1:a<b,\ a,b\in S,\ a,b\text{ allowed}\}.
\]
The remaining statement is:

> **Unconditional image lemma.** For every such \(S\) and every \(X\),
> \(H_{F(S)}(X)\leq Q_{F(S)}(X)\).

Here \(H_S(X)\) counts hard-shaped even holes of \(S\) through \(X\), and
\[
 Q_S(X)=\#\{m:2m-1\leq X,\ m\notin S,\ 2m-1\in S\}.
\]
This lemma needs no hypothesis \(H_S\leq Q_S\). Since \(F(G)=G\), it
immediately contains the desired true-\(G\) inequality.

Exact CP-SAT maximization over every forward-closed source \(S\) and every
hard cutoff through \(5000\) gives maximum
\[
 \max_{S,x\leq 5000}\bigl(H_{F(S)}(x)-Q_{F(S)}(x)\bigr)=0.
\]
There is no finite counterexample through \(5000\). At the fixed endpoint
\(X=10000\), the exact optimum is \(-68\). The simultaneous all-prefix
\(X=10000\) run is not exact: it found value \(0\) with upper bound \(7\).

The main rigorous output below is an exact chain-transition identity and
an equivalent sorted-prefix dominance lemma. The latter is the
irreducible open step.

## 1. Why \(H_G\leq Q_G\) proves the two-scale contraction

Let \(M(X)\) be the number of allowed holes of \(G\), \(E(X)\) the
splitless holes, and \(R(X)=M(X)-E(X)\). Put
\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,\qquad
 Z=\left\lfloor\frac{X+1}{3}\right\rfloor.
\]

Every allowed odd hole \(n>3\) has the admissible factorization
\[
 n+1=2\frac{n+1}{2}.
\]
Its parent \(m=(n+1)/2\) must also be a hole. Conversely, for every hole
\(m\leq Y\), the child \(2m-1\leq X\) is either an odd hole or belongs to
\(G\). Therefore, if \(O(X)\) counts odd holes,
\[
 O(X)+Q_G(X)=M(Y).                                      \tag{1}
\]

An even reducible hole is called 3-easy when
\[
 n+1=3m,\qquad m\text{ allowed},\quad m\ne 3.
\]
Its parent \(m\) is a hole, so the number of 3-easy holes through \(X\)
is at most \(M(Z)\). The other reducible even holes are exactly the hard
holes counted by \(H_G(X)\). Hence (1) gives
\[
 R(X)\leq M(Y)-Q_G(X)+M(Z)+H_G(X).
\]
Thus
\[
 H_G(X)\leq Q_G(X)
 \quad\Longrightarrow\quad
 R(X)\leq M(Y)+M(Z).                                    \tag{2}
\]
This is the C16 two-scale contraction.

## 2. Grounded descending approximants

Let \(A\) be the set of all allowed integers and define
\[
 S_0=A,\qquad S_{k+1}=F(S_k).
\]

**Lemma 2.1.** Every \(S_k\) is forward closed, \(S_{k+1}\subseteq S_k\),
and
\[
 \bigcap_{k\geq0}S_k=G.
\]

**Proof.** The set \(A\) is forward closed because an allowed product
has residue \(0\) or \(1\pmod 3\), so \(ab-1\) is allowed. If \(S\) is
forward closed, every supported output lies in \(S\), hence
\(F(S)\subseteq S\). If \(x,y\in F(S)\), then \(x,y\in S\), and \(xy-1\)
has the witness pair \(x,y\) in \(S\); therefore \(F(S)\) is forward
closed.

Every \(S_k\) is a forward-closed set containing the seeds, so
\(G\subseteq S_k\). For the reverse inclusion, induct on \(n\). If
\(n\notin G\), every admissible pair \(ab=n+1\) has at least one parent
outside \(G\). Those parents are smaller than \(n\), hence by induction
each is absent from some \(S_k\). There are finitely many pairs, so at
one common stage every pair has an absent parent. Then \(n\) is absent
at the next stage. Thus \(n\notin\bigcap_k S_k\). \(\square\)

Define the death rank
\[
 d(n)=\min\{k\geq1:n\notin S_k\},
\]
with \(d(n)=\infty\) for \(n\in G\). The preceding proof also gives the
exact recurrence
\[
 d(n)=
 \begin{cases}
 1,&n\text{ has no admissible pair},\\
 1+\displaystyle\max_{ab=n+1}\min(d(a),d(b)),
   &n\notin G\text{ has a pair},\\
 \infty,&n\in G.
 \end{cases}                                             \tag{3}
\]
This was independently checked against explicit stages through \(500\)
and used for the rank audit through \(10^7\).

## 3. Seed-2 chains and one-step boundary motion

Let \(T(x)=2x-1\). Every allowed integer has a unique representation
\[
 n=T^j(r)=2^j(r-1)+1
\]
with an allowed even root \(r\). Indeed, repeatedly invert \(T\) while
\(n\) is odd; allowedness is preserved, and uniqueness follows from
\(j=v_2(n-1)\).

If \(S\) is forward closed and contains \(2,3\), then membership on each
chain is upward closed. For \(x>2\),
\[
 x\in S\quad\Longrightarrow\quad T(x)=2x-1\in S,
\]
and \(T(2)=3\) is a seed. Thus each chain has either no member or a first
member \(c\), followed by every \(T^j(c)\).

Put
\[
 U=S\setminus F(S).
\]

**Lemma 3.1 (boundary moves by at most one).** On a chain with finite
first \(S\)-member \(c\), the first \(F(S)\)-member is either \(c\), when
\(c\) is supported in \(S\), or \(T(c)\), when it is not.

**Proof.** Since \(F(S)\subseteq S\), no point before \(c\) can enter
\(F(S)\). If \(c\) is supported, it is in \(F(S)\). Otherwise
\(c\in U\), but \(T(c)\) has the witness pair \(2,c\) in \(S\), so
\(T(c)\in F(S)\). The seed chain causes no exception because \(2,3\)
are put into \(F(S)\) explicitly. \(\square\)

Consequently, \(U\) contains at most one point on each chain, always its
old first member. If \(u\in U\) is odd, its predecessor is absent from
\(S\), so \(u\) itself is a boundary child counted by \(Q_S\). If \(u\)
is even, it is the root of its chain. In both cases \(T(u)\) is a new
boundary child of \(F(S)\).

This proves the structural observation in the prompt, including the
case in which a removed hard root \(r\) creates the boundary \(2r-1\).

## 4. Exact transition identity

Partition \(U\) into
\[
 U_o=\{u\in U:u\text{ odd}\},\quad
 U_h=\{u\in U:u\text{ is a hard even root}\},\quad
 U_n=U\setminus(U_o\cup U_h).
\]
Let \(Y=\lfloor(X+1)/2\rfloor\), and write
\[
 D_S(X)=Q_S(X)-H_S(X).
\]

**Lemma 4.1.** For every forward-closed \(S\),
\[
 \begin{aligned}
 Q_{F(S)}(X)
   &=Q_S(X)-|U_o\cap[2,X]|+|U\cap[2,Y]|,\\
 H_{F(S)}(X)
   &=H_S(X)+|U_h\cap[2,X]|.                              \tag{4}
 \end{aligned}
\]

**Proof.** A source boundary survives unless its child is unsupported.
The unsupported source boundary children are exactly \(U_o\), and each
is replaced by its child under \(T\). Every removed even root also
creates its child under \(T\). The birth \(T(u)\) lies through \(X\)
exactly when \(u\leq Y\). These births are distinct, and none was a
source boundary because its parent \(u\) belonged to \(S\). This proves
the first line. Since \(F(S)\subseteq S\), a new hard hole is exactly a
hard member removed from \(S\), namely an element of \(U_h\). This proves
the second line. \(\square\)

Subtracting the two lines gives two useful exact forms:
\[
 D_{F(S)}(X)
 =D_S(X)-|(U_o\cup U_h)\cap[2,X]|+|U\cap[2,Y]|,           \tag{5}
\]
and, after cancelling the removed points at or below \(Y\),
\[
 D_{F(S)}(X)
 =D_S(X)-|(U_o\cup U_h)\cap(Y,X]|+|U_n\cap[2,Y]|.         \tag{6}
\]

Equation (6) explains both phenomena seen computationally. A late
unsupported odd threshold or hard root consumes one unit of old slack;
an early unsupported nonhard root creates one unit of new slack. The
C22 member \(8\) is precisely the kind of unsupported nonhard root that
closure-only reasoning cannot treat as grounded.

## 5. Equivalent sorted-prefix frontier

The transition identity has a clean Hall-type form. Form two multisets
of integer keys:
\[
 \begin{aligned}
 {\cal C}(S)
   &=\{\text{boundary-child keys of }S\}
     \mathbin{\uplus}\{T(u):u\in U\},\\
 {\cal D}(S)
   &=\{\text{hard-hole keys of }S\}
     \mathbin{\uplus}U_o\mathbin{\uplus}U_h.
 \end{aligned}
\]
By (4), for every cutoff \(X\),
\[
 \#({\cal C}(S)\cap[2,X])-\#({\cal D}(S)\cap[2,X])
 =D_{F(S)}(X).                                           \tag{7}
\]

If the sorted credit and demand keys are
\[
 c_1\leq c_2\leq\cdots,\qquad d_1\leq d_2\leq\cdots,
\]
then \(D_{F(S)}(X)\geq0\) for every \(X\) is equivalent to
\[
 c_i\leq d_i\quad\text{for every demand index }i.         \tag{SD}
\]
Thus the unconditional image lemma is exactly the following statement,
with no loss and no hidden \(P(S)\) assumption:

> **Irreducible sorted-dominance lemma.** For every forward-closed
> allowed \(S\) containing \(2,3\), the multiset \({\cal C}(S)\)
> prefix-dominates \({\cal D}(S)\), equivalently (SD) holds.

A proof of (SD) would finish (2) by taking \(S=G\). A counterexample to
(SD) is exactly a counterexample to unconditional image-\(P\), so this
formulation also gives a precise falsifier gate.

## 6. Exact unconditional image test

preservation_sat.py uses one Boolean \(s_n\) for source membership and
one Boolean \(f_n\) for image membership. For every admissible pair
\(ab=n+1\), it imposes
\[
 s_a+s_b-1\leq s_n
\]
and encodes
\[
 f_n\ \longleftrightarrow\
 \bigvee_{ab=n+1}(s_a\wedge s_b),
\]
with \(f_2=f_3=1\). There is no source-side \(P(S)\) constraint in the
unconditional modes.

This finite model is exact for infinite forward-closed sources. Every
output \(ab-1\) is larger than both parents, so closure and support below
\(L\) depend only on membership below \(L\). Conversely, any feasible
prefix extends by taking its full forward closure above \(L\).

The selected-cutoff model maximizes \(H_{F(S)}-Q_{F(S)}\) over all hard
cutoffs at once. It suffices to select hard cutoffs because the excess
can increase only when a hard-hole event occurs; boundary events can
only decrease it.

| model | quantified cutoffs | status | optimum | bound |
|---|---:|---|---:|---:|
| unconditional selected \(L=2000\) | 147 | OPTIMAL | 0 | 0 |
| unconditional selected \(L=5000\) | 410 | OPTIMAL | 0 | 0 |
| unconditional endpoint \(X=10000\) | one | OPTIMAL | -68 | -68 |
| unconditional selected \(L=10000\) | 878 | FEASIBLE | 0 | 7 |

The exact \(L=5000\) optimizer exhibited equality at \(x=74\), with
sorted credits \(41,69\) and demands \(54,74\). Other solver runs chose
other tied cutoffs, including \(54\) and \(362\). The fixed
\(X=10000\) optimizer has 653 credits and 585 demands, hence slack 68;
its reconstructed sorted lists have no violation.

verify_small.py independently reconstructs source closure, computes
\(F(S)\) by trial division, recomputes (4)-(7), and checks the stored
sorted keys. It also enumerates all 256 forward-closed source prefixes
through \(26\) and checks (4) at every cutoff. All 10 tests pass.

## 7. Canonical-stage evidence and a second exact frontier

For the grounded stages \(S_{k+1}=F(S_k)\), put \(U_k=S_k\setminus
S_{k+1}\). The following stronger transition condition was exact-tested:
\[
 H_{S_k}(X)
 +|(U_{k,o}\cup U_{k,h})\cap(Y,X]|
 \leq Q_{S_k}(X).                                        \tag{ETD}
\]
By (6), (ETD) implies \(D_{S_{k+1}}(X)\geq0\) without using the helper
term \(U_{k,n}\cap[2,Y]\).

Every stage and every cutoff through \(10^7\) passes (ETD): 18 nontrivial
transitions, 4,952,270 generated values, 392,961 hard holes, and 637,270
terminal boundary children. Across successive transitions, the last
tight cutoff evolves as \(54,74,186,362\), and no later tight cutoff
appears in that run.

This is evidence, not an induction proof. A proof of (ETD) for the
canonical stages would also suffice, while (SD) is the cleaner
unconditional target requested in the follow-up.

## 8. Falsifier gates and dead simplifications

1. **Forward closure alone is false.** C22 has the first closed-superset
   countermodel at \(X=362\), excess \(1\), with 34 unsupported members
   beginning at \(8\).

2. **A direct missing-factor charge is false.** The hard hole \(54\)
   has only \(55=5\cdot11\); charging it to immediate healing of the
   missing factor does not work.

3. **Death layers do not match separately.** At \(X=74\), death layer
   \(3\) contains hard holes \(54,74\) but only the boundary parent
   \(21\). At \(X=362\), restricting both sides to death rank at most
   \(3\) gives 11 hard holes and 10 boundary parents.

4. **The hypothesis \(P(S)\Rightarrow P(F(S))\) is not the useful
   simplification.** If \(G\) had a first hard failure at \(X\), adding
   the unsupported point \(X\) restores source \(P\) at that prefix,
   while applying \(F\) removes it and recovers the failing \(G\)
   prefix. Preservation is therefore at least as hard as the target.

5. **The unconditional image statement survives the exact gate.** No
   positive image excess exists through any hard cutoff at most \(5000\).
   The exact limit is \(5000\), not \(10000\); the latter all-prefix run
   remains inconclusive with certified upper bound \(7\).

## 9. Reproduction artifacts

- compute/wave3/C23_grounded_horn/grounded_rank_audit.py
- compute/wave3/C23_grounded_horn/preservation_sat.py
- compute/wave3/C23_grounded_horn/verify_small.py
- compute/wave3/C23_grounded_horn/result_1e7.json
- compute/wave3/C23_grounded_horn/unconditional_selected_5000.json
- compute/wave3/C23_grounded_horn/unconditional_endpoint_10000.json
- compute/wave3/C23_grounded_horn/unconditional_selected_10000.json

Core commands:

~~~powershell
python problems/424/compute/wave3/C23_grounded_horn/preservation_sat.py --limit 5000 --assumption unconditional_selected --workers 64 --time-limit 120 --output problems/424/compute/wave3/C23_grounded_horn/unconditional_selected_5000.json

python problems/424/compute/wave3/C23_grounded_horn/preservation_sat.py --limit 10000 --assumption unconditional --workers 64 --time-limit 180 --output problems/424/compute/wave3/C23_grounded_horn/unconditional_endpoint_10000.json

python problems/424/compute/wave3/C23_grounded_horn/verify_small.py
~~~

The proof frontier is therefore not a vague appeal to groundedness. It
is the exact sorted dominance (SD), or equivalently the unconditional
image lemma, with the chain transition identity (4) available as the
local accounting rule and the finite falsifier gate exact through 5000.
