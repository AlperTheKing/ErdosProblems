# C30: one-step preservation audit

## Verdict

The requested preservation lemma was neither proved nor exactly falsified.
No density theorem is claimed.

What is proved is an exact seed-2-chain transition identity. It reduces the
claim to one sorted-prefix dominance statement with no hidden local terms.
The latter is still open. Exact CP-SAT found no countermodel at any hard
cutoff through 2000, and exact fixed-endpoint optimization remained negative
through 100000. Those are finite statements only.

The stronger unconditional image statement

\[
 H_{F(S)}(X)\le Q_{F(S)}(X)                              \tag{UI}
\]

also survived every exact C30 gate. Since \(F(G)=G\), (UI) already contains
the desired inequality for the least generated set. Thus proving (UI), or
the equivalent sorted dominance below, would solve the open core rather than
merely tidy up the induction.

The official page still listed problem 424 as open with no claimed partial
solution on 2026-07-13:
https://www.erdosproblems.com/424. The OEIS entry A005244 lists the basic
sequence and references but no preservation theorem.

## 1. Definitions

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}.
\]

For a forward-closed \(S\subseteq\mathcal A\) containing \(2,3\), put

\[
 F(S)=\{2,3\}\cup\{ab-1:a<b,\ a,b\in S\}.
\]

Let \(K\) be the set of hard-shaped integers from C23: an element of \(K\)
is an even allowed \(n\) having an admissible factorization of \(n+1\), but
not an admissible seed-3 factorization. Then

\[
 H_S(X)=|K\cap[2,X]\setminus S|
\]

and, with \(T(m)=2m-1\),

\[
 Q_S(X)=|\{m:T(m)\le X,\ m\notin S,\ T(m)\in S\}|.
\]

Write \(D_S(X)=Q_S(X)-H_S(X)\).

## 2. Closure and chain thresholds

**Lemma 2.1.** If \(S\) is forward closed, then \(F(S)\subseteq S\) and
\(F(S)\) is forward closed.

**Proof.** Every supported output belongs to \(S\), giving the inclusion.
If \(x,y\in F(S)\), then \(x,y\in S\), so \(xy-1\) has the witness pair
\(x,y\) in \(S\) and belongs to \(F(S)\). The seeds are included by
definition. \(\square\)

Every allowed integer has a unique seed-2-chain representation

\[
 n=T^j(r)=2^j(r-1)+1
\]

with an allowed even root \(r\). Membership in a forward-closed \(S\) is
upward closed on each chain, because \(m\in S\) implies \(T(m)\in S\).
Thus a chain is empty or has a first member followed by every successor.

Put

\[
 U=S\setminus F(S).
\]

**Lemma 2.2.** Each chain contains at most one member of \(U\), namely its
first \(S\)-member. If that first member is \(c\), then the first
\(F(S)\)-member is either \(c\) or \(T(c)\).

**Proof.** A supported first member stays. If it is unsupported, it is
removed, while \(T(c)\) has the source witness \((2,c)\). Every later chain
member already has its seed-2 witness in \(S\). \(\square\)

This proves the structural hint exactly: a finite boundary moves from \(c\)
to either \(c\) or \(2c-1\), and removing an occupied even root \(r\) creates
the boundary child \(2r-1\).

## 3. Exact transition identity

Partition \(U\) as follows:

\[
 U_o=\{u\in U:u\text{ odd}\},
\]

\[
 U_h=\{u\in U:u\text{ is a hard even root}\},
\]

and \(U_n=U\setminus(U_o\cup U_h)\). Put
\(Y=\lfloor(X+1)/2\rfloor\).

**Theorem 3.1 (transition identity).** For every cutoff \(X\),

\[
 Q_{F(S)}(X)
 =Q_S(X)-|U_o\cap[2,X]|+|U\cap[2,Y]|,                  \tag{1}
\]

\[
 H_{F(S)}(X)
 =H_S(X)+|U_h\cap[2,X]|.                               \tag{2}
\]

Consequently,

\[
 D_{F(S)}(X)
 =D_S(X)-|(U_o\cup U_h)\cap(Y,X]|+|U_n\cap[2,Y]|.     \tag{3}
\]

**Proof.** An old boundary disappears exactly when its odd child lies in
\(U_o\). Every removed first chain member \(u\) creates the new boundary
\(T(u)\), which lies through \(X\) exactly when \(u\le Y\). These births are
distinct, and none was an old boundary because its parent belonged to
\(S\). This proves (1). Since \(F(S)\subseteq S\), the new hard holes are
exactly the removed hard roots, proving (2). Subtraction and cancellation of
the removed points at or below \(Y\) gives (3). \(\square\)

The requested step is therefore equivalent to the following inequality at
every cutoff:

\[
 D_S(X)+|U_n\cap[2,Y]|
 \ge |(U_o\cup U_h)\cap(Y,X]|.                          \tag{ETD}
\]

The source hypothesis gives only \(D_S(X)\ge0\). It does not separately
bound the exposed unsupported odd thresholds and hard roots on the right of
(ETD). No valid argument closing that gap was found.

## 4. Sorted-prefix formulation

Define multisets of keys

\[
 \mathcal C(S)=
 \{\text{boundary children of }S\}\uplus\{T(u):u\in U\},
\]

\[
 \mathcal D(S)=
 \{\text{hard holes of }S\}\uplus U_o\uplus U_h.
\]

Equations (1)-(2) give, exactly,

\[
 |\mathcal C(S)\cap[2,X]|-|\mathcal D(S)\cap[2,X]|
 =D_{F(S)}(X).                                           \tag{4}
\]

If the sorted keys are \(c_1\le c_2\le\cdots\) and
\(d_1\le d_2\le\cdots\), then (UI) for every prefix is equivalent to

\[
 c_i\le d_i\quad\text{for every demand index }i.        \tag{SD}
\]

This is the precise unresolved lemma. It is not a direct missing-factor
matching: C16 and C24 already show the isolated source at 54 and the forced
fiber at 11.

## 5. Exact falsifier results

`C30_preservation_sat.py` uses Boolean source variables, exact Horn closure,
exact AND/OR image gates, and exact boundary variables. Since every parent
of \(n\) is smaller than \(n\), a feasible finite prefix extends to an
infinite forward-closed source without changing any modeled fact.

The independently replayed exact results are:

| model | cutoff(s) | status | maximum \(H_F-Q_F\) |
|---|---:|---|---:|
| unconditional image, every hard cutoff | \(\le2000\) | 147/147 OPTIMAL | no positive cutoff |
| unconditional image, endpoint | 500 | OPTIMAL | -6 |
| unconditional image, endpoint | 10000 | OPTIMAL | -68 |
| unconditional image, endpoint | 100000 | OPTIMAL | -1555 |
| requested prefix premise, positive-existence | \(\le500\) | INFEASIBLE | no countermodel |
| requested prefix premise, positive-existence | \(\le10000\) | UNKNOWN | no conclusion |

The `UNKNOWN` row is recorded specifically to prevent treating a timeout as
an infeasibility proof. The simultaneous optimization encodings at 10000
also returned only `FEASIBLE` zero-excess witnesses.

Dropping source closure gives the exact first failure at \(X=54\), with
source \(\{2,3\}\). Closure is therefore load-bearing: it forces the core
chain \(5,14,41\) used by the first boundary certificate.

## 6. Splitless-free relaxation and dead construction

Every image \(F(S)\) excludes structurally splitless nonseeds. A broader
relaxation therefore optimized \(H_T-Q_T\) over every forward-closed
splitless-free \(T\). It found:

| model | cutoff(s) | status | maximum \(H_T-Q_T\) |
|---|---:|---|---:|
| every hard cutoff | \(\le2000\) | 147/147 OPTIMAL | no positive cutoff |
| endpoint | 10000 | OPTIMAL | -42 |
| endpoint | 100000 | OPTIMAL | -1301 |

This remains finite evidence, not a lemma.

A concrete attempt started from \(G\) and filled upper-band reducible
nonhard parents of existing boundaries. Odd parents do not delete capacity:
filling 21, for example, moves the boundary from 41 down to 21. Restricting
to even nonhard roots gives a valid closed perturbation. The exact C++ replay
through \(10^8\) found

\[
 H=3{,}368{,}726,\quad Q=5{,}948{,}614,\quad R=25{,}463,
\]

so the perturbed surplus is

\[
 Q-H-R=2{,}554{,}425>0.
\]

This kills that construction as a source of a counterexample through the
tested range; it proves no asymptotic statement.

## 7. Independent verification

`C30_verify.py` does not call CP-SAT. It enumerates every source subset
through 26, retains the 256 forward-closed sources, reconstructs each image,
and checks (1)-(3) at all 25 cutoffs. It reports

```text
closed_sources=256
identity_checks=6400
image_failures=0
```

It also replays 294 exact scan cutoffs, five fixed optima, the exact
`INFEASIBLE`/`UNKNOWN` distinction, and the \(10^8\) construction totals.

Reproduction from the repository root:

```powershell
python problems/424/compute/wave3/C30_preservation/C30_verify.py

python problems/424/compute/wave3/C30_preservation/C30_preservation_sat.py `
  --stop 2000 --workers 64 --time-limit 30 --assumption none `
  --output problems/424/compute/wave3/C30_preservation/unconditional_first_failure_2000.json

python problems/424/compute/wave3/C30_preservation/C30_preservation_sat.py `
  --limit 100000 --workers 64 --time-limit 300 --assumption none `
  --output problems/424/compute/wave3/C30_preservation/unconditional_100000.json

python problems/424/compute/wave3/C30_preservation/C30_splitless_free_sat.py `
  --limit 100000 --workers 64 --time-limit 300 `
  --output problems/424/compute/wave3/C30_preservation/splitless_free_100000.json

g++ -O3 -std=c++20 -Wall -Wextra -Wpedantic `
  problems/424/compute/wave3/C30_preservation/C30_tail_removal.cpp `
  -o problems/424/compute/wave3/C30_preservation/C30_tail_removal.exe

problems/424/compute/wave3/C30_preservation/C30_tail_removal.exe `
  100000000 `
  problems/424/compute/wave3/C30_preservation/tail_removal_1e8.json
```

The C30 result is therefore a rigorous reduction and falsifier boundary,
not the proof or exact counterexample requested. The remaining work is
exactly (ETD), equivalently (SD).
