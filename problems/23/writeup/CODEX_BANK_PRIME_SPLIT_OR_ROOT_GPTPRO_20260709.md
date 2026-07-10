## Proposed move: **bank-prime split-or-root**

Source: GPT-Pro response relayed by the user on 2026-07-09.

Replace broad **root-locality** with the strictly weaker statement that only a *bank-indecomposable positive closed cut* must be root-local.

Let the sign convention be

[
\operatorname{def}(X)
:= \operatorname{HallLHS}(X)-\operatorname{HallRHS}(X),
]

where `HallRHS` already includes the particular external-bank allocation carried by (X). Thus `0 < def X` is exactly a `FullBankHall` violation.

### Exact target lemma

Fix a well-founded rank (\rho) on full-bank cut states. Ideally use support cardinality; if exchanges can preserve support, make (\rho) a checked topological rank on the finite canonical state space.

Define `ProperBankSplit X Y Z` to mean:

1. (Y) and (Z) are admissible globally closed full-bank cuts.
2. (\rho(Y)<\rho(X)) and (\rho(Z)<\rho(X)).
3. There is a genuine `ClosedCutExchange` witness relating (X,Y,Z).
4. The bank assigned to (Y) and (Z) is a **single split of (X)'s bank**, together with whatever bank the exchange identity releases. Neither child receives a fresh full bank.
5. The remaining exchange term is discharged by the existing `W1` lemma.
6. Recomputing the closed-cut exchange identity and the W1 discharge gives

[
\operatorname{def}(X)
\leq \operatorname{def}(Y)+\operatorname{def}(Z).
\tag{†}
]

The proposed lemma is:

```lean
theorem FullBank.closed_positive_split_or_root
    (X : FullBankCut data)
    (hX : X.Admissible)
    (hclosed : X.Closed)
    (hpos : 0 < hallDefect X) :
    ProperBankSplit rank X ∨
      ∃ (r : Root) (br : RootBank data),
        br ≤ X.bankOwnedBy r ∧
        X.PositiveRoot r ∧
        RootClosed r (X.rootBlock r) ∧
        0 < rootHallDefect r (X.rootBlock r) br
```

The crucial point in the second disjunct is that `br` is the **bank restriction inherited from (X)**. The root block must not be tested after being replenished with an independent full bank.

Equivalently:

> Every positive globally closed cut that is prime under proper, bank-conserving closed-cut decompositions has a positive closed root block.

This is the precise weakening of root-locality I would pursue.

## Why this closes Gap #1

Assume `FullBankHall` fails.

Closed-Hall completeness produces an admissible globally closed (X) with (\operatorname{def}(X)>0). Apply the dichotomy.

If the root branch occurs, it contradicts the already-available closed-root Hall/chart result.

If the split branch occurs, (†) and (\operatorname{def}(X)>0) imply

[
\operatorname{def}(Y)>0
\quad\text{or}\quad
\operatorname{def}(Z)>0.
]

Choose the positive child. Its rank is strictly smaller. Well-founded induction therefore reaches the root branch, giving the same contradiction.

Consequently `FullBankHall` holds. The existing finite rational Farkas equivalence can then be used only at the final interface to obtain

```lean
Ell5FullBankRelaxedCover_exists
```

There is no Farkas-dual argument inside the proof of Hall itself.

For a checked `FullBankGlobalPackage`, the new payload is simply:

```lean
rank     : CanonicalCutState → Nat
classify : ∀ X, X.Closed → 0 < hallDefect X →
  RootWitness X ⊕ ProperBankSplit rank X
```

The generic Lean theorem is a short well-founded induction.

## Why the known counterexamples do not directly hit it

Bare SSE asks for favorable behavior of one shortest support. Local lens/switch arguments ask for one local modification with nonnegative gain.

This lemma asks for neither. A non-root-local obstruction may split into two smaller closed cuts even when every individual local switch loses. Neither child needs to have defect as large as the parent; only their **sum** must dominate it. The external bank is accounted for globally across both children.

Thus the known SSE and lens counterexamples become immediate regression tests rather than conceptual obstructions.

## Finite exact gate

For each canonical admissible globally closed cut state (X), compute two exact quantities.

The root score is

[
R(X)=
\max_{\substack{r,b_r\\
b_r\leq \operatorname{bankOwnedBy}_X(r)\\
\operatorname{RootClosed}(r,\operatorname{block}_rX)}}
\operatorname{rootDef}(r,\operatorname{block}_rX,b_r).
]

The split score is

[
S(X)=
\max_{\substack{Y,Z,e,b_Y,b_Z,b_{W1}\\
\rho(Y),\rho(Z)<\rho(X)\\
e:\operatorname{ClosedCutExchange}(X,Y,Z)\\
\text{exact bank conservation}\\
\text{W1 admissible}}}
\left(
\operatorname{def}(Y)+\operatorname{def}(Z)-\operatorname{def}(X)
\right).
]

The gate condition is exactly

[
\operatorname{def}(X)>0
\quad\Longrightarrow\quad
R(X)>0\ \lor\ S(X)\geq0.
\tag{Gate}
]

Implementation recipe:

1. Enumerate discrete supports, roots, closures, and closed-cut exchanges modulo the existing symmetries.
2. For each fixed discrete choice, solve only the bank allocation problem as a rational LP. Clear denominators and recheck the optimum with exact integers or `Fraction`.
3. Do not trust a serialized `defect_dom` Boolean. The verifier must recompute (†) from the closed-cut exchange identity, bank conservation, and W1.
4. Run all known SSE/local-lens counterexamples first. Each must satisfy either (R>0) or (S\geq0).
5. Then enumerate by increasing support size and root-orbit count.

A decisive counterexample to the lemma is a single exact state (X) with

[
\operatorname{def}(X)>0,\qquad
R(X)\leq0,\qquad
S(X)<0.
]

The exported artifact should include (X), its bank vector, every root closure/defect, and the exact negative rational value of the best split slack. That would kill this route cleanly rather than merely showing that a search failed.

When the current Ell5 canonical quotient is genuinely finite, a successful gate directly supplies the ranked `classify` table for `FullBankGlobalPackage`. If the enumeration is only by bounded graph size, the same gate remains a strong falsifier, but not by itself a proof.
