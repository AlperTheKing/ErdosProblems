# Audit of R1: Cartesian degeneracy and multi-star lemma

## Accepted finite lemma
Let D be a finite subset of G0. For each d in D let V_d be a finite subset of G2 cap [1,floor(X/d)]. Put

M = sum_d |V_d|,
S = sum_{d,e in D, d != e} |d V_d cap e V_e|,

where the second sum is ordered. If M >= eta X and S <= L M, then

|G cap [1,X]| >= M/(1+L) >= eta X/(1+L).

Proof: with r(n)=#{d:n in dV_d}, sum r=M and sum r^2=M+S. Cauchy gives |supp r| >= M^2/(M+S) >= M/(1+L). Each n in supp r equals db with d in G0 and b in G2, hence d != b and n-1 belongs to G2. Translation by -1 is injective.

## Accepted obstruction, conditional only on the cited uniform table bound
Let P=|U||V|, M=max U, N=max V, m=min(M,N), n=max(M,N). Since the maxima occur, MN<=X. If P>=cX and E(U,V)<=C P^2/X, then E<=CP because P<=MN<=X. If the rectangular multiplication table obeys |[1,m].[1,n]|=o(mn) uniformly as m tends to infinity, Cauchy forces m=O_{c,C}(1). The bounded side then gives |G cap [1,X]|>=cX/B.

The explicit B formula in the raw response is not accepted until its precise rectangular Ford citation and constants are checked. The qualitative degeneracy follows from C05's dyadic Ford derivation, pending Fable's independent source/range audit.

## Status
The multi-star lemma is exact but is only a reformulation of the correlated-edge energy criterion. The remaining theorem-strength step is to construct, from the closure of {2,3}, such stars for every large X with fixed eta>0 and L<infinity.
