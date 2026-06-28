# C-alltie: proof from NO-Q-ONLY + exact obstruction to a direct transport proof

**Statement (C-alltie).** Fix a gamma-min connected-B max cut. If O = {v : T(v) > N} is nonempty,
T(z) = 0, and z is B-adjacent to v with T(v) = N, then the K-component of v meets O.

## Result 1 (PROVEN): C-alltie is a corollary of NO-Q-ONLY.

NO-Q-ONLY (= COND1_proof.md residual lemma): the K-graph {vw : K[v,w] > 0} restricted to the
load-bearing set L = {v : T(v) > 0} is connected (equivalently: no bad-edge-carrying K-component lies
entirely in Q).

**Proof of NO-Q-ONLY ⟹ C-alltie.** T(z) = 0 ⟺ p_g(z) = 0 for every bad edge g (each ℓ(g) ≥ 5 > 0,
p_g ≥ 0) ⟺ no bad-edge geodesic passes through z ⟺ z is K-isolated (K[z,·] = Σ_g p_g(z)p_g(·) = 0).
The hypotheses give a saturated v with T(v) = N > 0, so v ∈ L, and O ≠ ∅ gives an o with T(o) > N > 0,
so o ∈ L. By NO-Q-ONLY, L is a single K-component, hence v and o lie in the same K-component:
Kcomp(v) ∋ o ∈ O. ∎

So C-alltie holds whenever NO-Q-ONLY holds; it is NOT an independent lever.

## Result 2: there is NO independent (local / discharging / transport) proof of C-alltie.

Three exact experiments rule out the local handles the target proposed:

1. **The dead neighbor gives no local structure.** (T1) "a saturated v with a dead B-neighbor is an
   endpoint of some bad edge" is FALSE: 7 of 22 non-vacuous N=11 (all gamma-min cuts) cases have v
   purely interior. (`_calltie_charge.py`.)

2. **A Q-only K-component with a saturated vertex need NOT be critical.** The load-bearing component L
   (which does contain O) has ρ(K|_L) ≈ 8.54 < N = 11 at J??CBAPFvo? while containing a saturated
   vertex (row sum N) and an overloaded vertex (row sum 12.75). The Perron "max-row-sum = ρ ⟺ constant
   row sums" equivalence therefore does NOT force criticality, so the irreducibility-lever route
   (critical ⟹ nonneg eigenvector vanishing on O ⟹ Perron contradiction) is INAPPLICABLE to C-alltie.
   (`_calltie_forceqonly.py`.)

3. **The local data is fully consistent with the contrapositive.** Delete the unique O vertex o*=10
   from K at J??CBAPFvo?. The residual K' on L\O is symmetric, entrywise ≥ 0, PSD; A' = N·I − K' has
   smallest eigenvalue ≈ +4.62 (nonsingular M-matrix), ρ(K') ≈ 6.38 < N, deficit(K') = Σ(N − rowsum)
   ≈ +47.3 ≥ 0, with v=9 carrying row-sum 9.09 and z=5 a K'-isolated dead B-neighbor. Every local
   invariant (deficit ≥ 0, ρ ≤ N, K-closedness, saturated-ish vertex with dead boundary neighbor) is
   satisfied. The ONLY thing making v=9 actually saturated (T = N) is the deleted K-link K[9,10] = 1.91
   to O — which is exactly the conclusion C-alltie asserts. No local energy/Perron certificate recovers
   that link. (`_calltie_obstruction.py`.)

## The precise obstruction

C-alltie's content is purely **connectivity**: the saturated v must be K-routed to O. Unlike the
critical-component case, there is no spectral/energy slack to exploit — a Q-only K-component carrying a
saturated vertex (and a dead boundary B-neighbor) is admissible under every LOCAL constraint
(K-closedness, ρ(K|_C) ≤ N, deficit ≥ 0, off-diagonal sign, handshake budget Σ_{e∋v}μ(e) = 2N − D(v)).
What forbids it is the GLOBAL fact that the gamma-min max-cut never realizes a second nontrivial
K-component: in every census instance (N ≤ 11, all gamma-min cuts) and every adversarial gluing tried,
there is exactly ONE nontrivial K-component and it contains O. That single global fact IS NO-Q-ONLY, the
same odd-girth ≥ 5 anti-concentration obstruction as ROWSUM-O. C-alltie inherits it verbatim and adds no
new leverage.

## Verification (exact Fraction)

- C-alltie: 0 violations over the full census N ≤ 11, ALL gamma-min cuts (22 non-vacuous cases at N=11,
  0 below); loads-cut N ≤ 11; N=12 leaf caveat; Mycielskians N = 11, 23. (`_calltie_find.py`,
  `_satzmu_AC.py`.)
- A-alltie (the partner lemma, supplying the dead neighbor): 0 violations, 1011 non-vacuous cases over
  census N ≤ 11 all gamma-min cuts. (`_calltie_logic.py`.)
- In every non-vacuous case the saturated v is even 1-step K-adjacent to O (K[v,o] > 0; min direct
  K-leak +1.53). (`_calltie_critical.py`.) This is a strictly stronger empirical fact, equally
  global-only.

Files: `_calltie_probe.py`, `_calltie_find.py`, `_calltie_mech.py`, `_calltie_charge.py`,
`_calltie_critical.py`, `_calltie_forceqonly.py`, `_calltie_obstruction.py`, `_calltie_logic.py`,
`_calltie_adversary.py`.
