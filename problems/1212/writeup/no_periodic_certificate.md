# The No-Periodic-Certificate Theorem for Erdős #1212
(Verified partial result; 2026-06-10. Status: T1 — two independent derivations (GPT-5.5 Pro consult 2 +
independent re-derivation by orchestrator); s=0 exhaustion data corroborates. Negative/structural result:
closes one natural proof route for the YES direction; does not resolve #1212.)

## Setting
Erdős #1212 [Er80, p.114] asks for an infinite nearest-neighbour path through visible lattice points
(gcd(x,y)=1) with min(x,y)>1 and at least one coordinate composite at every vertex.

**Periodic Certificate Lemma** (reduction; verified). Let g,h,v ∈ Z_{>0}, gcd(h,v)=1. Suppose a finite
NN-path Γ = (x_i,y_i)_{i=0..n} satisfies (x_n,y_n) = (x_0+gh, y_0+gv) and, for every i, with
Δ_i := h·y_i − v·x_i:
  (C1) Δ_i ≠ 0 and every prime divisor of Δ_i divides g;
  (C2) no prime divisor of g divides both x_i and y_i;
  (C3) some prime divisor of g divides exactly one of x_i, y_i.
Then the translates Γ + k·(gh, gv), k ≥ k_0, concatenate into an infinite path solving #1212 (YES).
*Proof.* Δ is invariant under (gh,gv)-translation; q | gcd(coords) ⟹ q | Δ_i ⟹ q | g (C1) ⟹ q divides
both x_i,y_i (since q | gh, q | gv), contradicting (C2). The C3 witness prime divides one coordinate of
every translate, making it composite for large k. ∎

## Main theorem
**Theorem (no instantiation).** For every g, h, v as above, no path Γ satisfying (C1)–(C3) exists.

*Proof.* Let P be the set of primes dividing g and m = ∏_{p∈P} p = rad(g).

**Case 1: g odd.** By (C1) every Δ_i is odd (an even Δ_i would force 2 | g). An x-step changes Δ by v and
a y-step changes Δ by h; a step of odd size would flip the parity of Δ, which is forbidden since all Δ_i
are odd. As gcd(h,v)=1, at least one of h, v is odd; that step type therefore never occurs. But the path
must realize net displacement (gh, gv) with gh, gv ≥ 1 > 0 in BOTH coordinates — the banned direction has
nonzero required displacement. Contradiction. ∎(Case 1)

**Case 2: g even (2 ∈ P).** Claim: any vertex with x ≡ 0 (mod m) is isolated among protected vertices.
Let (x,y) satisfy (C1)–(C3) with m | x. Every p ∈ P divides x, so (C2) forces p ∤ y for all p ∈ P; in
particular y is odd and coprime to m. Consider its neighbours:
- (x±1, y): x is even (2 | m | x), so x±1 is odd; also x±1 ≡ ±1 (mod p) for every p ∈ P, so no p ∈ P
  divides x±1, and no p ∈ P divides y. Hence no prime of g divides either coordinate — (C3) fails.
- (x, y±1): y is odd, so y±1 is even; x is even — both coordinates divisible by 2 ∈ P — (C2) fails.
So no neighbour of (x,y) is protected; the path cannot pass through (x,y), and cannot skip it either:
the net x-displacement of Γ is gh ≥ g ≥ m, the x-coordinate changes by ±1 at x-steps, so by the
intermediate value property the path attains every integer x-value in an interval of length ≥ m, in
particular some x ≡ 0 (mod m), at an actual vertex of Γ. That vertex is either unprotected (contradiction)
or protected-but-isolated (contradiction, since it has a path-neighbour). ∎

## Corroboration (machine-verified)
- Exhaustive SCC searches of the certificate state graph (states (x mod m, y mod m, Δ); backtracking
  allowed): P ∈ {{2,3},{2,3,5},{2,3,5,7},{2,3,5,7,11}}, all coprime (h,v) ≤ 10, |Δ| ≤ 20000: every cycle
  has zero net displacement (s=0).
- Window-completeness: every certificate-cycle edge requires a 3-term-AP window of P-smooth numbers with
  step ≤ 10; enumeration of all 120,895 11-smooth numbers ≤ 10^15 shows every such window has top ≤ 1000
  (extremals d·{98,99,100}); hence the searches above were cycle-complete and the s=0 law is proven by
  exhaustion for those parameter ranges, independently of the Theorem.

## Interpretation
The wall x ≡ 0 (mod m) is an artifact of *fixed finite protection*: in the true graph, x+1 carries fresh
prime factors outside P. Any YES-construction must therefore let its protecting primes grow with scale
while remaining finitely specified — or the YES direction needs analytic inputs (rough-number supply in
short windows) currently at open-problem strength (Maier–Pomerance-scale Jacobsthal bounds).
