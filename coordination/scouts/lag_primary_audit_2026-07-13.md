# 2026 literature-lag primary-source audit

Date: 2026-07-13 (Europe/Istanbul)

Scope: statement-level novelty audit only. I read the displayed theorem/corollary statements in the arXiv v1 PDFs and compared their quantifiers and hypotheses with the current official Erdős Problems pages. `FULL SOLUTION` below means: *if the preprint's proof is correct*, its stated theorem answers every mathematically precise clause of the current official formulation. It is not a referee report or an independent correctness certification.

Classification key:

- `FULL SOLUTION`: the stated result has the same (or stronger) quantifiers and conclusion as the official problem.
- `DECIDABLE ONLY`: only a decision procedure or finite reduction is supplied, without the requested truth value.
- `PARTIAL`: only a strict subcase or one indispensable but non-final subquestion is settled.
- `MISMATCH`: a changed hypothesis, convention, or conclusion prevents implication of the official statement.

## Verdicts

| Official problem | Primary preprint | Verdict | Required finite remainder |
|---|---|---|---|
| #593 | arXiv:2606.24882v1, Theorem 1.1 | **FULL SOLUTION** (statement match) | none |
| #1177 | arXiv:2606.24882v1, Corollaries 1.3/1.4 and 7.1/7.2 | **FULL SOLUTION** (answers: yes, no, yes) | none |
| #550 | arXiv:2606.23659v1, Theorem 1.1 | **FULL SOLUTION** (statement match) | none; small `n<n_0` are outside the official “sufficiently large” target |
| #1061 | arXiv:2606.25849v1, Theorem 1.1 | **FULL SOLUTION** of the precise `S(x)~cx?` question, negatively | none; the exact order of `S(x)` remains unknown but is not needed to negate the displayed conjecture |

No item is merely `DECIDABLE ONLY`, and no theorem changes the load-bearing quantifiers. All three documents are v1 preprints, so these are prior claims that close a novelty gate, not results certified here as correct.

## #593 versus arXiv:2606.24882v1

Primary URLs:

- Official statement: https://www.erdosproblems.com/593
- Paper PDF: https://arxiv.org/pdf/2606.24882v1
- Paper abstract/metadata: https://arxiv.org/abs/2606.24882

### Official quantifiers

The official problem asks for a characterization of the finite 3-uniform hypergraphs `F` satisfying

`for every 3-uniform H, if chi(H)>aleph_0, then F embeds in H`.

### Paper theorem

Theorem 1.1 quantifies over **every finite triple system `F`** and makes the preceding property equivalent to each of the following exact characterizations:

1. `F` belongs to the smallest class `B` containing the private-vertex expansion `J^+` of every finite bipartite graph `J` and every finite edgeless system, and closed under finite disjoint unions and one-point amalgamations.
2. After isolated vertices are removed, `F` is linear, every hyperedge-node of its Levi graph is incident with a bridge, and every Berge cycle has even length.

The paper's conventions (Section 2.1) use simple hypergraphs and injective, non-induced embeddings. Its “uncountable chromatic number” is exactly `chi(H)>aleph_0`. Isolated vertices are explicitly handled rather than silently excluded.

### Line-by-line implication

- finite 3-uniform source: exact match (“finite triple system”);
- arbitrary 3-uniform host: exact match;
- host chromatic hypothesis `>aleph_0`: exact match;
- occurrence/containment: injective non-induced containment, the standard convention used by the problem;
- requested output “characterize”: supplied both constructively (`B`) and intrinsically (Levi bridges/even Berge cycles).

**Verdict: FULL SOLUTION (statement match).** There is no finite exceptional family left to classify.

## #1177 versus arXiv:2606.24882v1

Primary URLs:

- Official statement: https://www.erdosproblems.com/1177
- Paper PDF: https://arxiv.org/pdf/2606.24882v1
- Paper abstract/metadata: https://arxiv.org/abs/2606.24882

The official page defines `F_G(kappa)` as the 3-uniform hypergraphs of chromatic number **exactly** `kappa` that omit the finite 3-uniform `G`, and states three assertions.

### Clause (1): bounded witness at `aleph_1`

Official: for every finite `G`,

`F_G(aleph_1) != empty => exists X in F_G(aleph_1), |X| <= 2^(2^(aleph_0))`.

Paper: Corollary 1.4(1), proved in Corollary 7.2(1), states exactly this implication. The proof distinguishes the structural cases; its largest stated witness bound is the requested `2^(2^(aleph_0))` (some cases receive the stronger `2^(aleph_0)` bound). No continuum hypothesis is assumed; the paper records the ZFC cardinal calculation.

Result: **yes**, exact match.

### Clause (2): simultaneous avoidance

Official: for every finite `G,H`, nonemptiness of both `F_G(aleph_1)` and `F_H(aleph_1)` should imply nonemptiness of their intersection.

Paper: Corollary 1.4(2)/7.2(2) gives an explicit counterexample:

- `G=T_0` consists of two triples sharing a pair; `T_0`-free means linear;
- `H=C_7^(3)` is the loose/private-vertex 7-cycle;
- each exact-`aleph_1` avoidance class is nonempty;
- their intersection is empty because every uncountably chromatic linear triple system contains `C_7^(3)`.

Result: **no**, with finite explicit `G,H`. This resolves rather than weakens the assertion.

### Clause (3): transfer between uncountable cardinals

Official: for every finite `G` and all uncountable cardinals `kappa,lambda`,

`F_G(kappa) != empty => F_G(lambda) != empty`.

Paper: Corollary 7.1 states the stronger exact-spectrum dichotomy: for every finite `G`, the set of uncountable exact chromatic cardinals admitting a `G`-free system is either empty or **all** uncountable cardinals. Corollary 7.2(3) then states the official implication with the same quantifiers.

Result: **yes**, exact match.

**Verdict: FULL SOLUTION (truth values yes, no, yes).** There is no finite-cardinal or finite-hypergraph remainder. The paper explicitly addresses the current exact-chromatic formulation, not only the older “uncountably chromatic” wording.

## #550 versus arXiv:2606.23659v1

Primary URLs:

- Official statement: https://www.erdosproblems.com/550
- Paper PDF: https://arxiv.org/pdf/2606.23659v1
- Paper abstract/metadata: https://arxiv.org/abs/2606.23659

### Official quantifiers

For fixed positive part sizes `m_1<=...<=m_k`, for sufficiently large `n`, and every `n`-vertex tree `T`, with `G=K_{m_1,...,m_k}`, prove

`R(T,G) <= (chi(G)-1)(R(T,K_{m_1,m_2})-1)+m_1`.

Since all `k` vertex classes are nonempty, `chi(G)=k`.

### Paper theorem

Theorem 1.1 says:

- fix an integer `k>=2` and integers `1<=m_1<=...<=m_k`;
- there exists `n_0=n_0(m_1,...,m_k)`;
- for every `n>=n_0`;
- for every `n`-vertex tree `T`;
- the identical inequality holds with coefficient `k-1`.

Thus the paper makes “sufficiently large” explicit as an existential threshold depending only on the fixed part sizes and is uniform over all trees of that order. It does not impose bounded degree or any extra hypothesis on `T`. The `k=2` case is included (and is immediate); no class of positive part sizes is omitted.

**Verdict: FULL SOLUTION (statement match).** The unproved values `n<n_0` are not a remainder of the official problem, which only asks for sufficiently large `n`. The threshold is existential rather than numerically explicit, but the official statement asks for no effective bound.

## #1061 versus arXiv:2606.25849v1

Primary URLs:

- Official statement: https://www.erdosproblems.com/1061
- Paper PDF: https://arxiv.org/pdf/2606.25849v1
- Paper abstract/metadata: https://arxiv.org/abs/2606.25849

### Official question

Let

`S(x)=#{(a,b) in N^2 : a+b<=x and sigma(a)+sigma(b)=sigma(a+b)}`.

The mathematically precise displayed question is whether there exists a constant `c>0` such that `S(x)~cx`.

### Paper theorem

Theorem 1.1 quantifies over **every fixed real `R>0`** and proves

`lim_{x->infinity} S(x)/(x(log x)^R)=+infinity`.

Therefore `S(x)/x -> +infinity` already by any fixed positive `R`, and in particular `S(x)` cannot be asymptotic to `c x` for any finite `c>0`. The paper counts ordered positive-integer pairs, matching the current formal convention. Remark 1.2 proves there are no diagonal solutions, so the unordered count is exactly half and has the same conclusion if that convention were intended.

### Scope caveat

The theorem is a very strong lower bound, not an asymptotic formula or matching upper bound. Consequently it does not determine the open-ended “How many?” in the sense of finding the exact order of growth. It does, however, conclusively answer the page's precise conjectural clause `S(x)~cx?` in the negative; the Formal Conjectures encoding also treats that existential asymptotic statement as the target truth value.

**Verdict: FULL SOLUTION of the precise official yes/no question, negatively.** Exact asymptotic order is a further non-finite research question, not a finite remainder and not needed to refute the proposed linear asymptotic.

## Reproducibility and SHA-256

Hashes below are over the exact bytes downloaded on 2026-07-13. PDF URLs include `v1`, so the audited manuscripts are immutable arXiv versions. Official-page HTML is a dated dynamic snapshot and its hash is only a reproducibility marker for this audit.

| URL / local snapshot name | Bytes | SHA-256 |
|---|---:|---|
| `https://arxiv.org/pdf/2606.24882v1` / `2606.24882v1.pdf` | 665985 | `93191b28cecbe4268a58553ff2c60779dc85a585bc633f604165269f0d2b3a42` |
| `https://arxiv.org/pdf/2606.23659v1` / `2606.23659v1.pdf` | 542724 | `2b59e7df22b46e14aa53ebfe9e93fbc286e4b833f7bce004122476aaab088e1f` |
| `https://arxiv.org/pdf/2606.25849v1` / `2606.25849v1.pdf` | 712464 | `ae820bc001f52589276ffd0cd146c547e9bc4d4dc3c7b60331a4803fd8c2812b` |
| `https://www.erdosproblems.com/593` / `erdos593.html` | 33566 | `a3c26aec942b2b479801ab1dfe5c69d31985cc3f83e610f44a1c5b6e2e9dc24d` |
| `https://www.erdosproblems.com/1177` / `erdos1177.html` | 33516 | `c5a13b9b07077b33d7c92a77152ff02e7f1c63eed6768c322c673a85913d402d` |
| `https://www.erdosproblems.com/550` / `erdos550.html` | 33461 | `66b77d1763a81f43a33ddd5ceba39d577ad9283c372a1c5c860a76e3af5aadb` |
| `https://www.erdosproblems.com/1061` / `erdos1061.html` | 33712 | `6d345361b08956bdb6cf545d73f1f8114781033d67a1bb291be43326ccbd2e09` |

## Novelty-gate consequence

On theorem-statement matching alone, all four official OPEN entries have direct 2026 prior claims covering their precise targets. They should therefore be excluded from a new-proof target list unless the task is explicitly to referee and repair one of these v1 preprints. A proof-validity audit could later overturn a claim, but merely observing that the official status has not yet been updated does not restore novelty.
