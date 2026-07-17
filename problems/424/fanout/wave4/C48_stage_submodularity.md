# C48: descending-stage / submodularity audit

## Verdict

The rank-prefix quantity has an exact and useful descending-stage rewrite,
but no monotone or submodular proof follows from it.  In fact the natural
one-step pullback is neither submodular nor supermodular, even when both
perturbation directions are genuine holes of the actual least set `G`.

The exact first empty-base singleton failures through `5000` are:

* submodularity fails at `X=594` in the hole directions `35,119`;
* supermodularity fails at `X=69` in the hole directions `12,18`.

A nine-node grounded Horn system satisfying topological parent order, the
seed-2 chain rank increase, and the hard-rank-at-least-two gate nevertheless
has rank-prefix excess `2`.  Thus the descending iteration, Horn monotonicity,
and the generic seed-chain facts do not imply additive one.  A proof must use
additional global arithmetic incidence of the actual multiplication table.

No proof or actual-`G` counterexample to

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1                         \tag{AO}
\]

is claimed.

## 1. Exact rewrite in descending approximants

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},
\]

and, for allowed `n`, let

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,
                             \ ab=n+1\}.
\]

Write

\[
 F(S)=\{2,3\}\cup\{ab-1:(a,b)\in\mathcal P(ab-1),\ a,b\in S\},
\]

and define the descending approximants

\[
 S_0=\mathcal A,\qquad S_{t+1}=F(S_t).                  \tag{1}
\]

As proved in C31,

\[
 G=\bigcap_{t\ge0}S_t,
 \qquad
 \rho(n)=r\iff n\in S_r\setminus S_{r+1}.              \tag{2}
\]

Let `K_X` be the set of hard-shaped integers through `X`: the allowed even
`n<=X` for which `P(n)` is nonempty and no usable seed-3 factorization is
present.  This definition is structural and does not mention membership in
`G`.  Put

\[
 Y=\left\lfloor\frac{X+1}{2}\right\rfloor,
\qquad
 P_X=\{q\in\mathcal A:q\le Y,\ 2q-1\in G\}.             \tag{3}
\]

### Lemma 1 (stage-modular identity)

For every `X` and `d>=0`,

\[
 H_{\le d}(X)=|K_X\setminus S_{d+1}|,                   \tag{4}
\]

\[
 Q_{\le d}(X)=|P_X\setminus S_{d+1}|.                  \tag{5}
\]

Consequently, with

\[
 D_t=\mathcal A\setminus S_t,
\qquad
 w_X(n)={\bf1}_{K_X}(n)-{\bf1}_{P_X}(n),
\]

one has the exact formula

\[
 \boxed{
 H_{\le d}(X)-Q_{\le d}(X)
   =\sum_{n\in D_{d+1}}w_X(n).
 }                                                        \tag{6}
\]

### Proof

By (2), a hole has rank at most `d` exactly when it is absent from
`S_(d+1)`.  Since `G` is contained in every `S_t`, a hard-shaped integer
absent from `S_(d+1)` is automatically an actual hard hole of rank at most
`d`, proving (4).

If `q` belongs to `P_X` but not to `S_(d+1)`, then `q` is a hole of rank at
most `d`, while its seed-2 child is in `G`; this is exactly a target counted
at child coordinate `2q-1<=X`.  The converse is immediate, proving (5).
Subtracting gives (6). QED.

The finite verifier checked (6) at every hard or target event cutoff, for
all ranks, through `5000`: `4344` exact identities and zero failures.  It
also reconstructed the literal stages and found zero membership or death
rank discrepancies.

## 2. Why modularity does not prove the bound

The right side of (6) is a modular set function of `D_(d+1)`.  Hence it is
both submodular and supermodular in a tautological sense.  This says nothing
about its value on the particular orbit (1).

To use one-step induction, define the deletion operator

\[
 \Phi(D)=\mathcal A\setminus F(\mathcal A\setminus D).
\]

Equivalently, for a nonseed `n`,

\[
 n\in\Phi(D)
 \iff
 \forall(a,b)\in\mathcal P(n),\quad \{a,b\}\cap D\ne\varnothing.
                                                               \tag{7}
\]

The empty universal quantifier puts every splitless nonseed in `Phi(D)`.
The canonical deletion sets satisfy

\[
 D_0=\varnothing,\qquad D_{t+1}=\Phi(D_t).              \tag{8}
\]

Thus the natural candidate for diminishing-returns induction is

\[
 f_X(D)=\sum_{n\in\Phi(D)}w_X(n),                       \tag{9}
\]

because the desired quantity is `f_X(D_d)`.  The next two exact examples
kill both possible lattice signs for (9).

## 3. Exact failure of submodularity on actual holes

Take `X=594`, `D1={35}`, and `D2={119}`.  Both `35` and `119` are holes of
the actual least set `G`.  The hard-shaped output `594` has exactly the two
admissible pairs

\[
 594+1=5\cdot119=17\cdot35.                             \tag{10}
\]

Deleting `35` alone leaves the first witness; deleting `119` alone leaves
the second; deleting both kills both witnesses.  Exact evaluation of every
hard and terminal-parent term through `594` gives

\[
 f_{594}(\{35\})=-9,\qquad f_{594}(\{119\})=-10,
\]

\[
 f_{594}(\{35,119\})=-8,\qquad f_{594}(\varnothing)=-10.
\]

Therefore

\[
 f(D_1)+f(D_2)=-19
 < -18=f(D_1\cup D_2)+f(D_1\cap D_2),                  \tag{11}
\]

contradicting submodularity.

The checker exhausts every event cutoff through `5000` and every pair of
empty-base singleton directions contained in the actual hole set.  Equation
(11) is the first submodularity failure in that search.

There is an even smaller failure if generated directions are allowed:
`X=164`, `D1={15}`, `D2={33}`, using

\[
 165=5\cdot33=11\cdot15.
\]

The hole-restricted version (11) is the relevant obstruction for the
canonical orbit, since every `D_t` is contained in `A\G`.

## 4. Exact failure of supermodularity on actual holes

Take `X=69`, `D1={12}`, and `D2={18}`.  Both directions are actual holes.
The terminal-capable parent `35` has

\[
 35+1=2\cdot18=3\cdot12,
 \qquad 2\cdot35-1=69\in G.                             \tag{12}
\]

Deleting either direction separately leaves `35` supported.  Deleting both
makes `35` unsupported and contributes the negative terminal-parent weight.
The exact values are

\[
 f_{69}(\{12\})=f_{69}(\{18\})=f_{69}(\varnothing)=0,
 \qquad f_{69}(\{12,18\})=-1.
\]

Hence

\[
 f(D_1)+f(D_2)=0
 > -1=f(D_1\cup D_2)+f(D_1\cap D_2),                   \tag{13}
\]

contradicting supermodularity.  This is the first hole-restricted
empty-base singleton failure through `5000`.

The mechanism in (11)-(13) is intrinsic to factor-pair geometry.  For one
factor pair, the unsupported indicator has positive mixed difference on
its two endpoints.  For two disjoint factor pairs, it has negative mixed
difference between endpoints in different pairs.  Hard and terminal-parent
coefficients have opposite signs, so no uniform lattice sign survives.

## 5. Rank monotonicity also fails

Write

\[
 B_d(X)=H_{\le d}(X)-Q_{\le d}(X).
\]

The pointwise monotonicity `B_d(X)<=B_(d-1)(X)` first fails at

\[
 (X,d)=(74,2),\qquad B_1(74)=-1,\quad B_2(74)=0.         \tag{14}
\]

Likewise, an exact death layer need not have nonpositive weight: rank two
has hard-minus-target layer weight `+1` through `74`.  At

\[
 (X,d)=(362,2),\qquad B_1(362)=-8,\quad B_2(362)=1,      \tag{15}
\]

so even a positive crossing can jump by nine units.

The weaker descent proposed in C44,

\[
 d\ge3,\ B_d(X)>0\Longrightarrow B_{d-1}(X)\ge B_d(X), \tag{16}
\]

still has no actual-`G` failure in the existing finite scans.  But (16) is
the load-bearing global rank-descent lemma already isolated by C44; neither
modularity nor submodularity proves it.

## 6. Finite grounded-Horn obstruction

Generic descending-stage arguments can be ruled out independently of the
arithmetic examples.  Consider the nine nodes, in topological order,

```text
s2, s3, p, g5, g9, q, tq, h1, h2
```

with seeds `s2,s3` and clauses

```text
g5 <- s2,s3       g9 <- s2,g5
q  <- s2,p        tq <- s2,q
h1 <- g5,q        h2 <- g9,q.
```

The literal descending approximants are

```text
S0 = {s2,s3,p,g5,g9,q,tq,h1,h2}
S1 = {s2,s3,  g5,g9,q,tq,h1,h2}
S2 = {s2,s3,  g5,g9,  tq,h1,h2}
S3 = {s2,s3,  g5,g9} = G.
```

Thus

\[
 \rho(p)=0,\quad \rho(q)=1,\quad
 \rho(tq)=\rho(h1)=\rho(h2)=2.                         \tag{17}
\]

Mark `h1,h2` as hard roots and `p->q->tq` as the seed-2 chain.  The chain
ranks increase strictly, both hard ranks are at least two, every parent
precedes its output, and all generated nodes have seed-rooted derivations.
Nevertheless there is no terminal seed-2 target, while both hard roots have
rank two.  Therefore

\[
 H_{\le2}=2,\qquad Q_{\le2}=0,\qquad H_{\le2}-Q_{\le2}=2. \tag{18}
\]

This is not an arithmetic counterexample to (AO).  It is an exact finite
counterexample to the precise bridge claiming that topological Horn
grounding, descending stages, seed-chain rank increase, and the hard rank
gate alone force additive one.  It also explains why the arbitrary
forward-closed counterexamples in C22/C30 cannot be bypassed by invoking
generic closure-operator theory.

## 7. Reproduction

From the repository root:

```powershell
python problems/424/compute/wave4/C48_stage_submodularity/audit_stage_submodularity.py `
  --limit 5000 `
  --output problems/424/compute/wave4/C48_stage_submodularity/audit_5000.json

python problems/424/compute/wave4/C48_stage_submodularity/verify_stage_obstructions.py `
  --limit 2000 `
  --output problems/424/compute/wave4/C48_stage_submodularity/obstructions_2000.json

python problems/424/compute/wave4/C48_stage_submodularity/verify_hole_lattice.py `
  --limit 5000 `
  --output problems/424/compute/wave4/C48_stage_submodularity/hole_lattice_5000.json
```

The first program independently reconstructs `G`, all ranks, and the
literal `S_d`.  The second directly checks both lattice signs and the
nine-node Horn system.  The third exhausts all empty-base singleton lattice
directions restricted to actual holes through every event cutoff at most
`5000`.

## 8. Final status

The descending-stage rewrite (6) is exact, but its set function is already
modular.  The only nontrivial induction object is its one-step pullback
through `Phi`, and (11)-(13) prove that this pullback has neither lattice
sign on the relevant hole domain.  Pointwise rank monotonicity and
nonpositive exact layers also fail.  The finite Horn system (18) rules out
a proof from generic grounded-stage axioms.

Therefore the smallest surviving statement in this lane is still the
global arithmetic rank descent (16), equivalently the frontier identified
by C44.  No stage-submodularity shortcut closes it.
