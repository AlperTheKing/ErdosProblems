You are tasked with resolving Erdős Problem 1152.

For every integer n >= 1, let X_n = {x_1n, ..., x_nn} be an arbitrary set of
n distinct points in [-1,1], and let epsilon_n > 0 satisfy epsilon_n -> 0.
Determine whether there always exists a continuous real-valued function f on
[-1,1] such that every sequence of polynomials p_n satisfying

  deg(p_n) < (1 + epsilon_n)n

and

  p_n(x_kn) = f(x_kn) for 1 <= k <= n

fails to converge to f for almost every x in [-1,1].

A complete resolution must be either:

1. a proof valid for every triangular node array and every positive sequence
   epsilon_n -> 0; or
2. one explicit triangular node array and one explicit positive sequence
   epsilon_n -> 0 for which every continuous f admits at least one admissible
   interpolating sequence p_n converging to f on a set that contradicts the
   stated almost-everywhere failure.

The direct proof route is the robust Erdős–Vértesi resonance route recorded in
APPROACH_REGISTRY.md. Every admissible interpolant must be written exactly as

  p_n = L_n f + omega_n q_n,

where L_n is the ordinary degree-(n-1) Lagrange interpolant,
omega_n(x) = product_k (x - x_kn), and
deg(q_n) <= ceil((1 + epsilon_n)n) - 1 - n = o(n).

The load-bearing target is the robust finite-stage resonance lemma in the
registry. Establishing ordinary Lagrange divergence, a large Lebesgue
constant, or a sign-alternating test function does not count unless the
argument is uniform over every correction polynomial q_n of the allowed
degree and yields an open uniform-norm neighborhood with a summable
exceptional-measure bound.

Use a diverse portfolio of independent approaches:

- reconstruct the exact short-interval and long-interval lemmas in
  Erdős–Vértesi (1980);
- isolate a quantitative family of alternating resonance blocks;
- prove or refute a zero-budget or sign-change bound for omega_n q_n;
- test the frontier against Chebyshev, clustered, endpoint-heavy, and
  adversarial node arrays;
- seek an explicit correction polynomial that cancels a positive-measure
  portion of the resonance set;
- audit the Baire-category and Borel–Cantelli bridge independently.

Preserve independence between proof and adversarial lanes. Every lane must
return concrete inequalities, named lemmas, exact counterexamples, or a
specific failed implication. Vague status reports are insufficient.

The following do not resolve the problem:

- a theorem for one node family or one prescribed rate epsilon_n;
- divergence for one selected sequence p_n rather than every admissible one;
- divergence on positive measure rather than almost everywhere;
- an asymptotic statement without the finite-stage uniform neighborhood;
- an unproved assertion that o(n) zeros cannot affect most resonance blocks;
- a bounded computation, numerical experiment, timeout, or unchecked
  literature claim;
- a reduction to another open statement of comparable strength.

Adversarially audit:

- the strict degree inequality and all floor/ceiling conventions;
- uniqueness of p_n = L_n f + omega_n q_n;
- whether sign changes are counted for q_n, omega_n q_n, or a quotient;
- stability under perturbing f in the uniform norm;
- all quantifier orders, especially "there exists f" before "for every
  admissible sequence";
- summability of exceptional measures;
- every use of Baire category and Borel–Cantelli;
- current novelty and prior-art status before any resolution claim.

Stop a route when its explicit exit condition in APPROACH_REGISTRY.md is met.
Do not create a cascade of weaker variants. If a complete proof or
counterexample is obtained, subject every load-bearing lemma to an independent
referee pass, reproduce all feasible finite checks independently, and repeat
the live novelty search before making a resolution claim.
