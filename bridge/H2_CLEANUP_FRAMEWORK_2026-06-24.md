# (H2) cleanup framework — the f(eps) threshold, and why the simple cleanup is range-extension not closure

## Exact C5[n] peeling (verified, grounds the framework)
C5[n] (parts V0..V4 size n, complete bipartite between cyclically-consecutive parts): beta(C5[n])=n^2
(verified n=1,2 brute). S = one vertex per part => G-S = C5[n-1], beta=(n-1)^2; increment = 2n-1 (verified
n=2: 4-1=3; n=3: 9-4=5). The max-cut of C5[n] leaves exactly ONE consecutive-part bundle monochromatic (n^2 mono).

## Increment formula
For any 5-set S, take sigma' = a max-cut of G-S (mono = beta(G-S)), extend by placing each v in S on its
better side. Then beta(G) <= beta(G-S) + sum_{v in S} min(d_X(v), d_Y(v)) + e(S), where d_X,d_Y count v's
neighbours in G-S on each side of sigma'. On C5[n] with S=one/part this equals exactly 2n-1.

## Deviation for a near-C5 minimal counterexample (band, n>=37, beta=n^2+s, s>=1, s<=25 n^2 delta/2)
STAB gives partition P0..P4 with m_bad <= f(eps)*N^2 misplaced edges (off the consecutive-C5 pattern), eps=delta.
Increment(G,S) <= 2n-1 + (extra mono from misplaced edges incident to S). Since the increment is an INTEGER and
the target 2n-1 is the exact C5[n] value, we need the extra contribution = 0 at the >=2 "tight" parts (the parts
incident to the odd/monochromatic bundle). The simple cleanup picks a CLEAN vertex (0 misplaced edges) in each
tight part. #clean(P_i) >= |P_i| - mu(P_i), sum_i mu(P_i) <= 2 m_bad, worst part mu <= 2 m_bad <= 50 f n^2.

## THRESHOLD: f(delta) < 1/(50 n)  -- n-DEPENDENT => RANGE EXTENSION, NOT a closure
- f(eps)=eps (linear stability): f(delta)=6.07e-5 -> closes n < 1/(50 f) ~ 330 (N < 1647).
- f(eps)=sqrt(eps): f(delta)=7.8e-3 -> n < 3 (useless).
- NO fixed stability rate closes ALL n with the simple cleanup: m_bad ~ f*n^2 grows, dirtying every part for
  large n. So the self-tight wall RELOCATES (Step-2 was right). Cert+integrality: N<=180. +STAB(linear)+simple
  cleanup: N<~1647. Full conjecture (all n): NOT closed this way.

## What a FULL closure requires (the genuine open (H2) core)
A ROBUST cleanup that does NOT need a clean vertex: charge the misplaced edges incident to S to the GLOBAL cut
(show the near-optimal cut of G-S cuts >=80% of S's boundary edges, ~8n-4 of ~10n-5, EVEN with dirty S),
extracting >50% from triangle-freeness + alignment. This is exactly the ">50% extraction" the PEELING_LEMMA
sec3 flags as "the whole game", now localized to: near-C5 G, large n, per-step. Whether it closes is open
(= the relocated self-tight wall). Stability sharpens the target (S = pseudo-part representative) but the
charging must beat the +s with deviation <= 0 for arbitrarily large n.

## Honest status
cert+integrality => a(5n)<=n^2 for n<=36 (SOLID). +STAB+simple-cleanup => a finite range extension (N<~1647 if
linear stability). FULL conjecture: reduced to the robust per-step charging for near-extremal large-n G -- a
single, precisely-pinned open problem, but genuinely open (the wall, relocated not removed).
