# GPT Pro Digest: Support-to-Multiplicity Blocker

Date: 2026-06-11 Europe/Istanbul

Question:
prove or refute the support-to-multiplicity lemma for a touched mate Kempe
component in a genuine 6-regular `(4,1)` target:

- type `(1,1)` should force `e_H(K,C) <= 4`;
- type `(2,2)` should force `e_H(K,C) <= 2`.

GPT Pro verdict:

- No proof of support-to-multiplicity from the current ingredients.
- Boundary-support-criticality plus one-deletion `L_a`-criticality controls
  only the support set `R_C(K)`, not the multiplicities of edges from `K` to
  colour `C`.
- The desired bounds are equivalent to the internal-density condition
  `e(K) >= 3|K| - 3` for both terminal types.

Finite obstruction supplied by GPT Pro:

- Vertices ordered as `(a,a',alpha,b,b',beta,c,c',gamma)`.
- Colour classes:
  `A={a,a',alpha}`, `B={b,b',beta}`, `C={c,c',gamma}`.
- Edges:
  `ab'`, `ac`, `a gamma`,
  `a' beta`, `a' gamma`,
  `alpha b`, `alpha beta`, `alpha c`,
  `bc`, `bc'`, `b gamma`,
  `b'c'`, `b' gamma`,
  `beta c'`, `beta gamma`.
- The `(A,B)`-Kempe component through `a'` is
  `K={a',alpha,b,beta}`, the odd path `a' - beta - alpha - b`.
- `K` has terminal type `(1,1)` and `e_H(K,C)=7>4`.
- `K` is boundary-support-critical for both `L_a` and `L_b'`.
- `H` is one-deletion-list-critical for `L_a` and for `L_b'`.

Independent C++ verification:

- Added verifier:
  `experiments/sixreg/verify_gpt_obstruction.cpp`.
- Compiled with:
  `g++ -O2 -std=c++20 problems\944\experiments\sixreg\verify_gpt_obstruction.cpp -o problems\944\experiments\sixreg\verify_gpt_obstruction.exe`
- Output confirms:
  `e_H(K,C)=7`,
  support-criticality for `L_a` and `L_b'`,
  `L_a` and `L_b'` are critical under all one-vertex deletions,
  other terminal list assignments are not all critical,
  and `N(c') subset N(gamma)`.

Target-level failures of the obstruction:

- Not 6-regular after adding the deleted vertex `v`.
- Has a forbidden comparable same-colour nonedge:
  `N_H(c') subset N_H(gamma)`.
- Not globally critical for all six terminal assignments.

Next reduced lemma proposed by GPT Pro:

Dual/four-terminal domination:

- Type `(1,1)`: if a touched mate component is support-critical for both
  opposite assignments and `e_H(K,C) >= 5`, then either a same-colour
  comparable nonedge exists or some required one-deletion list-colouring fails.
- Type `(2,2)`: if a touched mate component is support-critical for all four
  relevant terminal assignments and `e_H(K,C) >= 3`, then either a comparable
  nonedge exists or some required one-deletion list-colouring fails.

Status:

- VERIFIED NUMERICALLY/T1 for the finite obstruction claims checked by C++.
- OPEN for the proposed domination lemmas.
- No complete #944 proof.
