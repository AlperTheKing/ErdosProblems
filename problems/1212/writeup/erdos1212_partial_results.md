# Composite-protected paths through visible lattice points: reductions, obstructions, and computations on Erdős problem #1212

(Draft v3, 2026-06-10 — after adversarial review rounds 1–2. Autonomous research artifact: orchestration,
verification, and computation by Claude (Anthropic); mathematical collaboration by GPT-5.5 Pro (OpenAI);
human involvement non-significant. Tier tags: T2 = Lean-verified core, T1 = complete human proof
independently re-derived, T0 = machine-verified computation.)

## 1. The problem

Erdős [Er80, p.114] (= erdosproblems.com #1212, OPEN, no prior partial results): let G be the graph on
visible lattice points {(x,y) ∈ Z²_{>0} : gcd(x,y) = 1}, with edges between points differing by 1 in
exactly one coordinate. Does G contain an infinite path all of whose vertices satisfy

  (i) min(x,y) > 1, and (ii) at least one of x, y composite?

Stewart's prime-pair construction solves the weaker version (condition (i) only); condition (ii) bans
its both-prime anchors. No literature exists on the strengthened question.

Conventions: "composite" means n ≥ 4 with n not prime. Trimming lemma (standard): an infinite walk
that visits every vertex finitely often contains an infinite simple path through a subset of its
vertices (loop-erasure: repeatedly excise the cycle between the first repeated visit); all walks we
construct have coordinate sums tending to infinity with each vertex visited finitely often, so this
applies. We therefore freely construct walks and trim.

## 2. Positive direction: the Composite-Anchor reduction

**Lemma 2.1 (Composite-Anchor Lemma; T1, per-vertex cores T2).** Suppose a₁ < a₂ < ⋯ are composite
integers with
  (V_n) gcd(a_n, s) = 1 for all s ∈ [a_{n+1}, a_{n+2}];
  (H_n) gcd(s, a_{n+2}) = 1 for all s ∈ [a_n, a_{n+1}].
Then the L-paths (a_n, a_{n+1}) → (a_n, a_{n+2}) → (a_{n+1}, a_{n+2}) concatenate into an infinite
walk — hence, after trimming, an infinite path — witnessing YES for #1212. Every vertex lies on a leg
whose frozen coordinate is a composite anchor ≥ 4, so (ii) holds and min(x,y) ≥ min(a₁, a₂) ≥ 4 > 1.
(Per-vertex validity: Lean theorems `vertical_leg_valid`, `horizontal_leg_valid` in
erdos1212_cores.lean — compiled, 0 sorry, axioms ⊆ {propext, Classical.choice, Quot.sound}.)

**Lemma 2.2 (roughness criterion; T1).** Let P⁻ denote the least prime factor.
(a) (sufficiency for V) If a_{n+2} − a_n < P⁻(a_n), then (V_n) holds: for p | a_n the largest multiple
of p that is ≤ a_{n+2} is at most a_n (since the next multiple after a_n is a_n + p > a_{n+2}), and a_n
itself lies below the interval.
(b) (sufficiency for H) If a_{n+2} − a_n < P⁻(a_{n+2}), then (H_n) holds automatically: for
p | a_{n+2}, the largest multiple of p below a_{n+2} is a_{n+2} − p < a_n, so no multiple of p meets
[a_n, a_{n+1}].
(c) Consequently the single condition family
  (R_n): a_{n+2} − a_n < min(P⁻(a_n), P⁻(a_{n+2}))
implies all (V_n), (H_n). The conditions (V_n) are NOT equivalent to the gap bound in general (e.g.
a_n = 25, a_{n+1} = 32, a_{n+2} = 33 satisfies (V_n) with a_{n+2} − a_n = 8 > 5 = P⁻(25)); (R_n) is a
clean sufficient criterion: an infinite sequence of composites, each two-ahead gap smaller than the
least prime factors at both ends, yields YES.

**Computation 2.3 (T0).** A greedy chain with 2000-rough composite anchors starting at 10⁷ ran for
797,568 anchors (reaching 6.7×10⁷) with zero backtracking; every vertex of every L-path triple was
machine-verified (797,566 triples, 0 violations). An alternative run reached 1.07×10⁸. Code + chain:
problems/1212/experiments/anchor_tree/.

## 3. Negative direction: no periodic certificate

A natural route to discharge the infinitely many conditions of Lemma 2.1 is a periodic certificate
(proposed in our GPT-5.5 Pro collaboration):

**Lemma 3.0 (Periodic Certificate Lemma; T1).** Let g, h, v be POSITIVE integers, gcd(h,v) = 1.
Suppose a finite nearest-neighbour walk Γ = (x_i, y_i)_{i=0..n} in Z²_{>0} satisfies
(x_n, y_n) = (x_0 + gh, y_0 + gv) and, for every i, with Δ_i := h·y_i − v·x_i:
  (C1) Δ_i ≠ 0 and rad(|Δ_i|) | g;
  (C2) no prime divisor of g divides both x_i and y_i;
  (C3) some prime divisor of g divides exactly one of x_i, y_i.
Then for all sufficiently large k₀, the translates Γ + k·(gh, gv), k ≥ k₀, concatenate into an
infinite walk whose vertices are visible (gcd = 1), have min > 1, and have at least one composite
coordinate; trimming yields a YES-path. (Coprimality: if q divides both coordinates of a translate, then q | h·(y_i+kgv) − v·(x_i+kgh) = Δ_i,
so q | g by (C1); and since q | g we have x_i + kgh ≡ x_i and y_i + kgv ≡ y_i (mod q), so q divides
both ORIGINAL coordinates x_i, y_i — contradiction with (C2). Compositeness: the (C3) witness prime q divides
the same coordinate of every translate, and since gh, gv > 0 that coordinate exceeds q for all large
k, hence is composite; similarly min > 1. The finitely many small translates are discarded.)

**Theorem 3.1 (No-Periodic-Certificate; T1, cores T2).** For every positive g, h, v with
gcd(h,v) = 1, no finite nearest-neighbour walk Γ = (x_i, y_i)_{i=0..n} in Z²_{>0} with the period
closure (x_n, y_n) = (x_0 + gh, y_0 + gv) satisfies (C1)–(C3) at every vertex. Hence Lemma 3.0 has
no instantiation. (The closure/displacement hypothesis is essential: isolated single vertices can
vacuously satisfy (C1)–(C3).)

*Proof.* Let P be the set of primes dividing g and m = ∏_{p∈P} p = rad(g).
(Case g odd.) By (C1) every |Δ_i| is odd. An x-step changes Δ by ∓v, a y-step by ±h; since
gcd(h,v) = 1 and g is odd, at least one of h, v is odd, and a step of odd size flips the parity of Δ —
forbidden. So that step type never occurs. But h, v ≥ 1 forces nonzero displacement in BOTH
coordinates (gh, gv ≥ 1). Contradiction.
(Case 2 | g.) Any vertex with x ≡ 0 (mod m) satisfying (C1)–(C3) is isolated among such vertices:
every p ∈ P divides x, so (C2) forces p ∤ y for all p ∈ P (in particular y is odd); its horizontal
neighbours (x±1, y) have both coordinates coprime to m and odd, so (C3) fails there (Lean:
`right_neighbor_witness_free`, `left_neighbor_witness_free`); its vertical neighbours (x, y±1) have
both coordinates even, so (C2) fails there (Lean: `vertical_neighbor_both_even`). The walk's net
x-advance is gh ≥ g ≥ m ≥ 2 with h ≥ 1, and a ±1-step walk attains every intermediate x-value at a
vertex (Lean: `walk_intermediate_value`); the walk's x-range has length ≥ m, hence contains a value
≡ 0 (mod m), attained at some vertex of Γ — which then violates (C1)–(C3) or is isolated while having
a path-neighbour. Contradiction. ∎

**Corroboration (T0; explicitly bounded scope).** Exhaustive SCC searches of the certificate state
graphs — P ⊆ {2,3,5,7,11}, all coprime pairs 1 ≤ h, v ≤ 10, |Δ| ≤ 20000, with backtracking — find
every cycle has zero net displacement. Within these parameter ranges the searches are cycle-complete
in Δ: every certificate-cycle edge requires a 3-term arithmetic progression of P-smooth numbers with
step d = v or h ≤ 10, and an enumeration of all 120,895 11-smooth numbers ≤ 10¹⁵ shows every such
window has largest element ≤ 1000 (the extremal windows are d·{98, 99, 100} for the bounded steps
d ≤ 10). We verified the window enumeration to 10¹⁵; eliminating the remaining tail rigorously would
require a certified S-unit computation, which is unnecessary here because Theorem 3.1 supplies the
general proof — the computation serves as an independent check within its stated range.

## 4. The obstruction, and a conditional resolution

**Proposition 4.1 (sufficient supply target; T1).** Suppose
  (R1) there exist constants C > 0, x₀ and exponents 0 < θ < δ < 1/2 such that for every x ≥ x₀ the interval [x, x + C·x^θ]
  contains a composite b with P⁻(b) > x^δ.
Then an infinite anchor chain satisfying (R_n) exists, so Erdős #1212 has answer YES.
*Proof.* Pick a₁ = some b ∈ [x₁, x₁ + C·x₁^θ] from (R1) with x₁ ≥ x₀ large, and inductively
a_{n+1} := the composite supplied by (R1) for x = a_n + 1; then a_n < a_{n+1} ≤ a_n + 1 + C·(a_n+1)^θ,
hence a_{n+2} − a_n ≤ 2 + 3C·a_n^θ, while P⁻(a_n) > (a_{n-1}+1)^δ ≥ a_{n-1}^δ and
P⁻(a_{n+2}) > a_{n+2}^δ > a_n^δ. Since a_{n-1} ≥ a_n − 1 − C·a_{n-1}^θ ≥ a_n/2 for large n and θ < δ,
we get a_{n+2} − a_n ≤ 2 + 3C·a_n^θ < (a_n/2)^δ for all large n, which gives (R_n); discard the
finitely many initial anchors. ∎
R1 is sufficient, NOT known to be necessary: failure of R1 would not disprove #1212, and YES could
also follow from weaker, structured supply statements. Two further sufficient variants: (R2) a
non-clumping refinement of almost-all short-interval theorems; (R3) an explicit structured anchor
family.

**Status of R1–R3 (GPT-5.5 Pro literature survey + our checks; 2026-06-10).** R1 is not available in
the current literature: known every-interval P₂/E₂ theorems either lack least-prime-factor control or
require interval exponents > 1/2. The closest published results are Matomäki [JLMS 2022,
arXiv:2012.11565] (almost all x: (x − h log X, x] contains integers with Ω ≤ 2 and all prime factors
> X^{1/8}, exceptional measure O(X/h)) and Matomäki–Teräväinen [TAMS 2023, arXiv:2207.05038] (E₂
numbers in almost all (x, x + log^{2.1} x]); these are almost-all statements whose exceptional sets
are not known to avoid clumping into a full window (R2 open), and no known explicit family survives
the block transitions (R3). No choice of the parameter h closes the gap (spacing-vs-budget mismatch
at every h).

**Corollary 4.2 (conditional YES; T1).** Assume the hypothesis (R1) of Proposition 4.1 — a
Maier–Pomerance-strength max-gap statement for rough composites, stated in the every-interval form
∀x ≥ x₀: [x, x + C·x^θ] contains a composite with P⁻ > x^δ (θ < δ < 1/2). Then Erdős #1212 has
answer YES. (We use the every-interval form deliberately: a dyadic-block formulation that controls
only gaps between consecutive selected elements inside each block would not control block-boundary
transitions or non-emptiness.)

## 5. Structural evidence for YES

(T0) The both-prime-deleted graph is shattered at small scales (e.g. (3,4), (4,5), (5,6) are
isolated) but giant components grow with scale: ≈21.5% of valid vertices in [2,3000]² lie in a single
component pair. Combined with the unbounded verified chains of §2, the answer is almost certainly
YES; §4 localizes a sufficient analytic input that remains open.

## 6. Summary

For a problem with an empty published frontier we provide: a clean sufficient reduction (§2: the
single-family roughness criterion (R_n)); an impossibility theorem closing the natural
finite-certificate route (§3); a sufficient open analytic input together with its literature status
(§4); a conditional resolution (Corollary 4.2); and large-scale verified computations (§2, §5).
Lean-checked cores: problems/1212/lean/erdos1212_cores.lean (6 theorems, 0 sorry, axioms ⊆
{propext, Classical.choice, Quot.sound}).

## Reproducibility
T2 items: erdos1212_cores.lean, compiled with `lake env lean` (exit 0) against the Lean 4 / Mathlib
toolchain of google-deepmind/formal-conjectures (2026-06 checkout); 0 sorry, no native_decide; axioms
checked per-theorem with #print axioms (⊆ {propext, Classical.choice, Quot.sound}). T0 items: scripts
and logs in problems/1212/experiments/ (anchor_tree/build_chain.py + build_chain.log + chain.json.gz;
certificate SCC searches in search1212/); exact arithmetic throughout (Python ints, sympy primality).

## Related work (novelty sweep, 2026-06-10)
Visible-lattice literature concerns visibility proportions/random walks (e.g. arXiv:1512.04722,
2210.07464) and the percolative structure of the coprime colouring of Z^d — Vardi (Exp. Math. 1998),
Martineau (ECP 2022, arXiv:1804.06486), arXiv:2509.08452 (2025) — none of which addresses paths
constrained by compositeness of a coordinate (the both-prime-deleted graph) or Erdős's strengthened
question. Searches across Scholar/arXiv (5+ phrasings), OEIS, MathOverflow, and the problem's forum
thread (0 comments) found no prior work on #1212's strengthened form, its reductions, or our
impossibility theorem.

## References
- [Er80] P. Erdős, Some notes on problems and results in number theory, 1980, p.114.
- erdosproblems.com/1212 (T. F. Bloom's database).
- K. Matomäki, Almost primes in almost all very short intervals, J. Lond. Math. Soc. (2022),
  arXiv:2012.11565.
- K. Matomäki, J. Teräväinen, Almost primes in almost all short intervals II, Trans. Amer. Math. Soc.
  (2023), arXiv:2207.05038.
- J. Teräväinen, Almost primes in almost all short intervals, Math. Proc. Camb. Phil. Soc. (2016),
  arXiv:1510.06005.
- H. Iwaniec, On the error term in the linear sieve, Acta Arith. (1971) (Jacobsthal-function bound).
- S. Martineau, On coprime percolation, the visibility graphon, and the local limit of the GCD
  profile, Electron. Commun. Probab. (2022), arXiv:1804.06486.
- C. L. Stewart (prime-pair construction for the weak version, as recounted in [Er80]).
