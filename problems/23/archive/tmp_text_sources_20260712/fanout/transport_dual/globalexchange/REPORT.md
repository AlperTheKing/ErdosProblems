# Global simultaneous owner-shore exchange

## Exact theorem (proved reduction)

Let `Omega = Π i, Fin (rows_i.length)` be the finite row-choice space, let `S : Omega -> Nat` be `scopedObligationScore G c`, and fix `omega`. For an owner shore `A`, put

`D_A = |scopedOwnerDemandSet G c omega A|`, `C_A = |scopedOwnerSourceSet G c omega A|`, and `delta_A = D_A-C_A` (as an integer).

**Rational global-exchange theorem.** If `delta_A > 0` and there are nonnegative rational weights `lambda(x)` (`x : Omega`) with finite total `Z = sum_x lambda(x) > 0` satisfying

`sum_x lambda(x) * (S(omega)-S(x)) >= delta_A`,

then `omega` is not a global minimizer of `S`. Equivalently, for the probability `mu(x)=lambda(x)/Z`, it is enough that

`E_mu[S] <= S(omega) - delta_A/Z < S(omega)`.

Proof: if every `S(x) >= S(omega)`, every summand `lambda(x)(S(omega)-S(x)) <= 0`, contradicting the positive right side. Thus some simultaneous replacement `x` has `S(x)<S(omega)`. This proof is exact rational averaging and imposes no Hamming-radius bound.

A useful normalized target is `Z=1`:

`HallFailure(omega,A) -> exists mu : RatDist Omega, E_mu[S] <= S(omega)-(D_A-C_A)`.

This target directly implies that every global minimizer satisfies scoped Hall. It is stronger than necessary by the quantitative defect; any strictly positive transported drop suffices.

## Owner-shore transport interpretation

Each unit of deficient old shore demand is a token. A multi-coordinate certificate may split each token rationally among complete choices `x`, crediting it by the **global drop potential** `S(omega)-S(x)`. Credits are pooled across coordinates before capacity is checked. The displayed inequality says the pooled credits cover all `delta_A` unmatched tokens. Unlike `CoordinateReplacementInjection`, the target is not a disjoint union indexed by one coordinate and therefore permits collisions created by one changed row to be cancelled by component deactivation or collision removal caused by other changed rows.

## Relation to R29

R29 proves all 459,004 nontrivial Hamming-one replacements have score at least 30,813 versus baseline 30,811. Hence no distribution supported on Hamming-one choices can satisfy a positive-drop certificate. It does not refute the theorem or its transport target: `lambda` may have unbounded simultaneous support. Proving the 2943 tuple globally minimal would refute the missing owner-shore production lemma, but this lane did not re-gate or optimize that cage.

## Exact test and falsifiers

`test_exchange.py` enumerates all `4*6*6=144` complete row tuples of the repository's order-10 scoped Hall-failure fixture `I?`fBO]]?`, using integer score/flow routines and `Fraction` for expectations. For the named failing choice `(1,1,1)`: `S=19`, deficient shore `{8,9}`, `D_A-C_A=2`, global minimum `0`, and the uniform distribution on all complete tuples has `E[S]=19/72`. Therefore the normalized candidate holds with exact margin

`19-2-19/72 = 1205/72 > 0`.

This is one complete 144-tuple fixture test, not a census-wide theorem test.

The candidate is false for bare abstract incidence data: take two choices, constant score `S=1`, one shore with demand `2` and source capacity `1`. It has defect `1` but every distribution has expected score `1`, so no positive-drop certificate exists. Thus Hall deficiency and cardinalities alone cannot prove the production lemma; a graph-realizability/component-change axiom is essential.

## Proof gap

The open statement is the **owner-shore distribution production lemma**: from an inclusion-minimal deficient shore in an exact graph-derived row system, construct rational `lambda` whose pooled global-drop potential is positive (quantitatively, at least the defect). Existing one-coordinate locality, HitNeed nonincrease, persistent-component embedding, and coordinate collision bounds do not yet supply this pooled inequality. In particular, no argument here proves that the uniform distribution works universally, nor that R29 admits a descending joint trade.

## SHA-256

- `test_exchange.py`: `9752256A5BC106D5A5F433CA00E93A55ACD4C6B1162B736247FA1CB36C00E655`
- `test_output.json`: `2105CF67C4335722B4571AB489C08E98ED39297C0B5C8C94E82CBECD1FD09956`
- `ActiveScopedCoordinateTransport.lean`: `2821EB83265C85DC41F42EDD2B31DAE11FE60256B257E6C129BBB6E882AB5706`
- `_codex_scoped_variation_anatomy.py`: `A2A10E6241CB7D5254DB8530C44D510C3E36779876BA7B219BDCE49E5FA3ED62`
- `WALL_ATTACK_R29_GPTPRO56.md`: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
