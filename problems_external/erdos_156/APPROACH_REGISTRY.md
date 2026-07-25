# Erdős Problem 156 — Approach Registry

## Exact target

For every sufficiently large integer \(N\), construct a Sidon set
\(A\subseteq[1,N]\) that is maximal under inclusion and satisfies
\[
|A|\le C N^{1/3}
\]
for an absolute constant \(C\).

Here Sidon means that \(a+b=c+d\), with \(a,b,c,d\in A\), implies equality
of the unordered pairs.  Maximal means that \(A\cup\{m\}\) is not Sidon for
every \(m\in[1,N]\setminus A\).

## DIRECT ROUTE A — remove the union-bound loss from Ruzsa's lift

1. **Exact final deliverable.** An explicit or probabilistic construction,
   with all constants and quantifiers proved, of a maximal Sidon
   \(A\subseteq[1,N]\) having \(O(N^{1/3})\) elements.
2. **Current frontier lemma or finite certificate.** Let
   \(q=p^2+p+1\), let \(B=\{b_0,\ldots,b_p\}\subseteq\mathbb Z/q\mathbb Z\)
   be a Singer Sidon set, and let \(M=\lfloor(N-\max B)/q\rfloor+1\).
   Prove that when \(p^3\ge C_0N\) there are
   \(d_i\in\{0,\ldots,M-1\}\) such that every
   \(m\in[1,N]\) whose residue is not in \(B\) has a witness
   \[
   m+(b_w+qd_w)=(b_u+qd_u)+(b_v+qd_v),
   \]
   with the nontriviality conditions needed to make adding \(m\) violate
   the Sidon property.
3. **Explicit logical bridge.** The Singer congruence makes the lifted set
   \(A_0=\{b_i+qd_i\}\) Sidon.  The frontier lemma saturates every
   nonexceptional residue.  Extend \(A_0\) to a maximal Sidon set \(A\).
   Ruzsa's distinct-difference argument gives only \(O(p)\) added elements
   in the exceptional residues.  Thus \(|A|=O(p)=O(N^{1/3})\).
4. **Next falsifiable action.** Reconstruct Ruzsa's exact bad events from
   pages 55–58.  Compute their variable supports, dependency/codegree graph,
   and conditional failure probabilities.  Test lopsided LLL, resampling,
   alteration, and deterministic covering.  Produce either a proved
   \(p^3\ge C_0N\) saturation lemma or a rigorous obstruction showing that
   each of these mechanisms still needs \(p^3\gg N\log N\).
5. **Exit condition.** Stop Route A if the bad events depend on essentially
   all lift variables and every audited correlation/alteration mechanism
   retains the logarithm, unless a new deterministic covering invariant is
   stated with a direct proof plan.  Record
   `DEAD: Ruzsa lift has no log-removal mechanism`.

## DIRECT ROUTE B — bounded-size saturation as an exact design

1. **Exact final deliverable.** The same maximal Sidon construction with
   \(O(N^{1/3})\) elements.
2. **Current frontier lemma or finite certificate.** For infinitely many
   prime powers \(p\), produce a family of lift values \(d_i\in[0,M)\),
   \(M=\Theta(p)\), for which all admissible Singer triple equations cover
   every required pair \((r,t)\) of residue and quotient.
3. **Explicit logical bridge.** The certificate is exactly the frontier
   lemma of Route A for \(N=\Theta(p^3)\); monotonicity and Bertrand-type
   prime selection extend the construction to every sufficiently large
   \(N\), after which Ruzsa's exceptional-class completion adds \(O(p)\).
4. **Next falsifiable action.** Formulate the finite incidence design without
   symmetry assumptions and solve/audit small \(p\) instances only to test
   candidate algebraic rules.  Any rule must be proved for all \(p\); finite
   success alone is not a result.
5. **Exit condition.** Stop if computation yields only unrelated finite
   certificates, an unbounded parameter cascade, or a rule whose verification
   is equivalent to exhaustive coverage.  No large search is authorized
   without a conjectured algebraic rule and two independent verifiers.

## Known result and non-results

- Ruzsa proved \(O((N\log N)^{1/3})\) using independent random lifts and a
  union bound over \(m\le N\).
- Improving a probability estimate for one fixed \(m\) without simultaneous
  coverage does not resolve the problem.
- A small maximal Sidon set in another group does not by itself embed into
  \([1,N]\) with the required maximality.
- A finite construction, favorable objective value, or unchecked SAT output
  is not an asymptotic proof.

## Adversarial checks

- Audit the convention for repeated summands in the Sidon definition.
- Verify every witness really makes \(A\cup\{m\}\) non-Sidon and does not use
  the same unordered pair twice.
- Track boundary effects in \(b_i+qd_i\in[1,N]\).
- Do not assume independence after selecting overlapping Singer triples.
- Prove the \(O(p)\) exceptional-residue completion under the exact convention
  used in the target.
- Re-run a live novelty search before any resolution claim.

## Route status update — dependency audit

- **Route A: DEAD for LLL, lopsided-matching, and Moser--Tardos.** Exact bad-event probabilities are exp(-Theta(p/M)); full supports are all p+1 variables, and same-residue matching events form a forced lopsided clique. These mechanisms retain p/M >> log M. A deterministic covering invariant remains Route B.

## Final route status

- **Route A: DEAD.** The exact alteration bound is
  \[
  \mathbb E U\le N\exp(-p/(64M)),
  \]
  and maximal completion costs at most
  \[
  p+1+U+2\lfloor(N-1)/q\rfloor.
  \]
  First-moment alteration, independent rounds, resampling, and conditional
  expectation therefore retain the logarithm.
- **Route B finite-seed/radix mechanism: DEAD.** The apparent cubic finite
  pattern fails at the exact \(N=72,k=6\) test, and every nontrivial radix
  product has an explicit Sidon parallelogram.
- **Route B Singer-fiber mechanism: DEAD under the direct-route guard.**
  At least \(p(p-1)/2\) residue fibers have quotient capacity at most
  \(\lfloor(p+2)/2\rfloor\), so any successful lift must satisfy
  \(p^3\ge(2-o(1))N\). No algebraic rule or invariant supplies simultaneous
  near-bijective coverage. The remaining statement is the original
  all-residue saturation problem in equivalent form.

`DEAD: reformulation maze — no deterministic invariant bridges the
one-block Singer lift to simultaneous all-residue quotient coverage.`
