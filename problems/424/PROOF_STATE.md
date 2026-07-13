# Proof state

## Target

Let `A` be the least set of positive integers containing `2,3` and satisfying
`xy-1 in A` for distinct `x,y in A`. Decide whether its lower density is positive.

## Accepted results

1. `A` is contained in residues `0,2 mod 3`; upper density is at most `2/3`.
2. For `n>=4`, membership is decided exactly by `n+1=dq` with distinct `d,q in A`.
3. Exact block coding gives, for every `X>=9`,
   `A(X) >= (1/6)(X/9)^(log 6 / log 30)`.
4. Exact independent censuses agree through `10^7`; `A(10^8)=51,899,129`.
5. The frozen `{2,3,5}` affine subsystem has density `0.18222202754` at `10^11`;
   no positive- or zero-density theorem for it is proved.
6. Every finite globally residue-decodable block automaton is subcritical:
   its exponent-one weighted spectral radius is strictly below one.
7. Every periodic-domain residue `qZ+r` in the tested composition-cover model
   must satisfy `d | gcd(q,r+2)` for some licensed multiplier `d`.
8. Raw polynomial growth plus dynamic multipliers cannot bootstrap density:
   the distinct-input closure of `{9,10}` has a polynomial lower bound but
   a proved sublinear upper bound.
9. Distinct affine words collide exactly:
   `T_322255(x)=T_255232(x)=600x-381`.

## Frontier

A successful proof must use arithmetic special to seeds `2,3` and prove a
target-specific expansion/collision inequality for the distinct product set

`A = {2,3} disjoint_union ((A restricted-times A)-1)`.

Fixed alphabets, global periodic exact decoding, raw word entropy, and a
generic power-law bootstrap are insufficient.

## Verdict

NOT SOLVED. No explicit `c>0,X0` and no zero-density proof were obtained.

## Missing-set structure (2026-07-13, claude_missing_analysis.py SHA 6e071114…, B=10^7; accepted as data)
- Per-decade missing fraction DECAYS: 0.68 / 0.62 / 0.51 / 0.39 / 0.304 / 0.251 (last = (10^6,10^7]).
  With Codex's 10^8 count, decade (10^7,10^8] ≈ 0.218. Decay ratios 0.77, 0.78, 0.83, 0.87 ≈ log(B)/log(10B)
  ⟹ **O1 (working fit): missing fraction ≈ C / log B with C ≈ 1.6 (log10)** — consistent with d(G) = 2/3
  and log-slow convergence (explains the census climb). NOT proof; guides the route.
- Longest consecutive-allowed missing run = 13, ending at 192 (the early [173,194] window); largest missing
  element at 10^7 = 9,999,996 (≡ 0 mod 12) — missing persists to the boundary but thins.
- **O2 (KEY): residue asymmetry mod 9** — missing counts {0: 393k, 2: 393k, 3: 445k, 5: 62k, 6: 378k,
  8: 43k}: classes 5 and 8 mod 9 are ~7-9x LESS missing than the rest ⟹ G nearly fills n ≡ 5, 8 (mod 9)
  already at 10^7. Mechanism guess: n ≡ 8 mod 9 ⟺ n+1 ≡ 0 mod 9 = product of two multiples of 3; G is rich
  in multiples of 3, so the pair supply is huge.
- **O3: parity/mod-12** — missing heavy at n ≡ 0, 6 (mod 12) (even multiples of 3: 525k/576k), light at
  5 (9k), 9 (40k), 3 (75k) ⟹ odd classes fill much faster (evens need odd*odd products).
- **ROUTE R-A (registered): class-by-class filling via product covering.** First target theorem:
  "every sufficiently large n ≡ 8 (mod 9) lies in G" ⟸ every large multiple of 9 factors as ab with
  a ≠ b, a,b ∈ G (e.g. both ≡ 0 mod 3). Reduces the density question to a MULTIPLICATIVE-BASIS statement
  for G ∩ 3Z (Erdős-multiplication-table flavored). If one full residue class ⊆ G eventually, d(G) ≥ 1/9 > 0
  answers the problem; then bootstrap other classes.

## R-A covering gate (2026-07-13, claude_ra_covering_gate.py SHA 179cc21f…, B=10^6; accepted as data)
- IDENTITY CHECK: covered(n) [∃ a≠b ∈ G, ab = n+1] is EXACTLY membership n ∈ G for n ≥ 4 (definition of
  the closure) — gate numbers agree with the missing-set analysis (class-8 missing 7.9% @10^6 vs 3.87%
  @10^7 ✓ consistent decay).
- **O4: class-8 (mod 9) missing fraction HALVES per decade**: 44% / 27.9% / 14.9% / 7.0% (decades up to
  10^6), 3.9% @10^7 — geometric-ish (ratios 0.63, 0.53, 0.47, ~0.55), FASTER than 1/log. Class 5 similar
  but slower (50/35/20/9.9%).
- Structural reading of "uncovered": n+1 = 9m is uncovered iff EVERY divisor pair (a,b) with the allowed
  sign pattern (both ≡ 0 mod 3, or a ≡ 2 mod 3 with b ≡ 0 mod 9) has a G-hole. Divisors ≡ 1 mod 3 are
  PERMANENTLY unusable (G1). So R-A's target theorem splits: (i) arithmetic supply — a.e. 9m has "many"
  allowed divisor pairs (classical divisors-in-residue-classes); (ii) hole-avoidance — G's holes are too
  thin (decaying per O1/O4) to block all pairs; a self-improving/bootstrap estimate suggests itself
  (holes thin ⟹ more covered ⟹ holes thinner). REGISTERED as the R-A proof skeleton.
