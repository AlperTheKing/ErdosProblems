# Erdős Problem 708 — Approach Registry

## Problem

Let \(A\subseteq\{2,3,\ldots\}\) have \(|A|=n\), put
\(M=\max A\), and let \(I\) be any interval of \(M\) consecutive positive
integers.  Prove or disprove that there is a set \(B\subseteq I\) with
\(|B|\le 2n\) and
\[
  \prod_{a\in A}a\mid\prod_{b\in B}b.
\]

The inequality interpretation \(|B|\le g(n)\) is used; the literal equality
wording on the problem page is inconsistent with the stated lower bound.

## DIRECT ROUTE R1 — Two-split divisor matching

1. **Exact final deliverable.** A proof of \(g(n)\le 2n\) for every \(n\),
   using the interpretation above.

2. **Current frontier lemma / finite certificate.** For every
   \(A\subseteq[2,M]\) and every interval \(I\) of \(M\) consecutive positive
   integers, choose for each \(a\in A\) a factorization \(a=u_av_a\), allowing
   a factor \(1\), so that all nonunit factor occurrences in the multiset
   \(\{u_a,v_a:a\in A\}\) have distinct representatives in \(I\), each
   representative divisible by its assigned factor.

3. **Explicit bridge to the final deliverable.** If the frontier lemma holds,
   let \(B\) be the distinct representatives.  Then \(|B|\le2|A|=2n\), and
   \[
     \prod_{a\in A}a=\prod_{a\in A}u_av_a
       \mid\prod_{b\in B}b.
   \]
   Thus the lemma directly proves \(g(n)\le2n\).

4. **Next falsifiable action.** Exhaustively test the lemma for every
   \(2\le M\le10\), every \(A\subseteq[2,M]\), and every interval start modulo
   \(\operatorname{lcm}(1,\ldots,M)\), by enumerating divisor splits and
   checking the resulting bipartite matching.  Independently replay every
   first failure from raw \(A,I\).

5. **Exit condition.** A single verified finite failure kills R1 and is logged
   `DEAD: two-split divisor matching is false at <A,I>`.  If R1 survives the
   finite audit, the next step must be a Hall-type proof with a stated
   neighborhood inequality; repeated encodings or larger bounded searches
   without such an inequality are forbidden.

## Audit requirements

- Treat factor occurrences as distinct even when their numerical values agree.
- Require representatives to be distinct members of \(I\).
- Check divisibility with full prime-power multiplicity.
- Allow \(u_a=1\) or \(v_a=1\), but do not create a matching vertex for \(1\).
- Use two independently implemented checkers for any reported failure.
- A bounded survival result is not evidence that R1 is true.

## Novelty gate snapshot

On 2026-07-23, the official page and discussion thread list the problem OPEN,
with no claimed partial or complete solution and no current worker.  This
snapshot must be refreshed before any discovery claim.

## R1 DEAD (2026-07-23)

- Smallest failure: M=3, A={2,3}, I={5,6,7}.
- The factor occurrences 2 and 3 both have neighborhood {6}, so Hall fails: 1 < 2.
- The original problem survives because B={6}; the distinct-representative frontier forbids legitimate capacity sharing.
- DEAD: two-split divisor matching is false at A={2,3}, I={5,6,7}.

## DIRECT ROUTE R2 — Two-fragment capacitated packing

1. **Exact final deliverable.** A proof of \(g(n)\le 2n\) for every \(n\).

2. **Current frontier lemma / finite certificate.** For every
   \(A\subseteq[2,M]\) and every interval \(I\) of \(M\) consecutive positive
   integers, factor each \(a\in A\) as \(a=u_av_a\), allowing \(1\), and
   assign every labeled nonunit factor to a member of \(I\). Assignments may
   share a member \(b\), but the product of all factors assigned to \(b\)
   must divide \(b\).

3. **Explicit bridge to the final deliverable.** Let \(B\) be the set of used
   interval members. Every \(a\) creates at most two assigned fragments, so
   \(|B|\le2|A|=2n\). Multiplying the capacity constraints gives
   \(\prod_{a\in A}a\mid\prod_{b\in B}b\).

4. **Next falsifiable action.** Exhaust every \(M\le6\), nonempty
   \(A\subseteq[2,M]\), and interval start modulo \(\prod_{a\in A}a\).
   Enumerate all two-factor splits and all capacity-respecting assignments;
   independently replay the first failure from raw prime valuations.

5. **Exit condition.** A verified finite failure kills R2. Survival through
   \(M=6\) authorizes only an attempt to prove a concrete capacitated Hall or
   flow inequality; it does not authorize a larger bounded-search cascade.

R2 is strictly stronger than aggregate product divisibility because it
restricts each \(a\)'s prime-power demand to at most two interval members.
