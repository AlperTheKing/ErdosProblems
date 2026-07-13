# Canonical minimizer referee result

Let `Omega` be a nonempty finite set. For `w in Omega`, let `S,A,C,U` be the scoped score, active-vertex count, active-component count, and selected-union size. Let `R` be an injective row signature in a finite linear order. Minimize `K(w)=(S(w),A(w),C(w),U(w),R(w))` lexicographically, increasingly.

## Strongest unconditional lemma

There is a unique minimizer `w*`. For every `eta`: `S(w*)<=S(eta)`; under equality of `S`, `A(w*)<=A(eta)`; under equality of `S,A`, `C(w*)<=C(eta)`; under equality of `S,A,C`, `U(w*)<=U(eta)`; and under equality of the first four coordinates, `R(w*)<=R(eta)`. Equality throughout implies `eta=w*`.

Proof: the finite nonempty image of `K` has a least element. Failure of any displayed implication makes the first differing coordinate smaller for `eta`. Injectivity of `R` proves uniqueness. Thus no competitor may preserve every earlier coordinate and reduce the next one.

## Exact falsifier: tie-breakers do not force Hall

Take `Omega={w}`, demand set `D(w)={d}`, source set empty, and empty availability relation. Assign exact integer metrics `(S,A,C,U,R)=(1,1,1,1,0)`. Then `w` is the unique global minimizer of every proposed tie-break key, but Hall fails on `X={d}` since `|X|=1>0=|N(X)|`. Hence none of these tie-breakers, nor uniqueness, forces Hall in the finite abstract model. This falsifier does not claim triangle-free maximum-cut shortest-row realizability.

## Explicit proof gap

The real graph model still needs a realizability-specific exchange: from a deficient owner shore at a Hall-failing score minimizer, construct a tuple improving this lexicographic key. R29 rules out requiring a one-row exchange. R25--R29 contain no proof of the required simultaneous exchange; canonical tie-breaking alone cannot supply it.
