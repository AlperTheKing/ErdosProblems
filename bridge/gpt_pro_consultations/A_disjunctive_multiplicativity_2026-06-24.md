# GPT Pro: DISJUNCTIVE MULTIPLICATIVITY at order 9 — the route to close Step-2 (band d_mono <= 2/25)

chat 6a3b5aba. GPT's JUDGMENT: sup_{x in [0.2486,0.3197]} f(x) < 2/25 (the band IS LOOSE; the band sup is
STRICTLY below 2/25). No published determination of f(x)=sup{d_mono(W): tri-free, d_edge(W)=x}. Do NOT pursue
d_mono<=d_edge/5 (false over general graphons), do NOT increase moment order. Keep order-9 + a finite
branch-and-bound layer enforcing GRAPHON MULTIPLICATIVITY (realizability) slice by slice.

## Why the order-9 SDP is loose (the exact obstruction)
A convex mixture L = sum_i lambda_i phi_{W_i} is positive and satisfies EVERY PSD moment condition, but
generally L(F⊔H) - L(F)L(H) = Cov_i(t(F,W_i), t(H,W_i)) != 0. The missing condition is NOT positivity at higher
order — it is the RANK-ONE / DISSOCIATION condition (M): a single graphon has t(F⊔H,W)=t(F,W)t(H,W); a mixture
violates it (nonzero covariance). No convex moment cone distinguishes a homomorphism from a mixture of them.

## The fix: finite disjunction + McCormick envelopes of multiplicative identities (all order <= 9)
p := t(K2,W) = d_edge(W). Split the band into rational intervals p in [a,b]. The core constraint, for s=t(2K2,W)=p^2:
   (MC-2)  s >= 2ap - a^2 ;  s >= 2bp - b^2 ;  s <= (a+b)p - ab
The last is equivalently the INTERVAL LOCALIZER  t((K2-a)(b-K2), W) >= 0. A linear a<=p<=b does NOT exclude a
mixture whose components lie outside [a,b]; (MC-2) DOES: for a mixture L, (MC-2) => L(2K2)-L(K2)^2 <=
(L(K2)-a)(b-L(K2)) <= (b-a)^2/4. So a density branch of width h=b-a forces the density VARIANCE <= h^2/4.
Also add McCormick v_H = t(H⊔K2,W) = u_H * p for every triangle-free H on <=7 vertices (H⊔K2 expands exactly
into the 9-vertex basis), linearized on [a,b].

## ADAPTIVE branching (the algorithm)
1. Solve order-9 SDP -> fooling optimum L*.
2. Sigma_{F,G} = L*(F⊔G) - L*(F)L*(G) over connected tri-free F,G on <=4 vertices (the mixture covariance).
3. Top eigenvector c -> Q = sum_F c_F F (order <=4 statistic, so Q^2 is order <=8). If sigma_Q^2 = L*(Q^2)-L*(Q)^2 > 0:
4. Branch t(Q,W) in [a,b] with width b-a < 2 sigma_Q, add
   t(Q^2) >= 2a t(Q) - a^2 ;  t(Q^2) >= 2b t(Q) - b^2 ;  t(Q^2) <= (a+b) t(Q) - ab.
   (optionally McCormick between Q and every H of order <=5, since QH is order <=9.)
5. Re-solve each branch; the variance constraint excludes the mixture, bound tightens. Branch-and-bound until
   all branches give bound < 2/25. Final verifier checks only RATIONAL linear identities + rational PSD
   decompositions (floats only for the search).

## KILL CRITERION (falsifiable)
If the residual optimum eventually satisfies L(F⊔G)=L(F)L(G) for all statistics whose products fit in order 9,
YET remains >= 2/25, then the order-9 realizability route is EXHAUSTED (need a genuinely new combinatorial
inequality). But if the plateau is caused by a nontrivial real-graph mixture (memory confirms x* IS such a
mixture), this disjunctive-multiplicativity refinement attacks EXACTLY the missing condition. "The one route I
would pursue before concluding order 9 is fundamentally insufficient."

## NEXT (my audit/prototype): test the simplest version FIRST — add the edge-density interval localizer
## t((K2-a)(b-K2),W)>=0 on a NARROW sub-band [a,b] to the order-9 SDP and check if eta goes negative (bound <
## 2/25). If the simplest Q=K2 variance constraint tightens, the route is validated; then the adaptive Q
## (top covariance eigenvector) strengthens it. Machinery: prove_cert.cutting_plane + a new interval localizer.
