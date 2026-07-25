# Research Intelligence Briefing: Five Gating Questions for the Sunflower/PMF Program

## Executive Summary

This briefing addresses five research questions ordered by leverage for the MendozaLab sunflower/PMF program. The literature-check question (Q1) has an immediate, actionable answer: **the exact value \(M(\infty, 3, 3)\) is not pinned down in the literature as a finite integer**, and the density-theoretic question (what is the supremum \(c_3\) of the exponential growth rate of sunflower-free 3-uniform families as \(n \to \infty\)) remains wide open. Computational measurements like \(c_3 \geq 2.449\) are consistent with current knowledge and would constitute publishable observations if properly reported. Q2 (morphism triangulation across #166 and #755) is complicated by recent developments: Erdős problem #166 was marked as **solved** in the Thomas Bloom database as of late 2025, narrowing its utility as a "second leg." Q3–Q5 (Mendoza's Limit, transfer-matrix engineering, k-dependence) are structurally unblocked from a literature standpoint but IP-gated per the prime directive. The meta-question about provisional filing is correctly identified as the true program bottleneck.

***

## Q1 — Literature Check: Is \(M(\infty, 3, 3)\) Known?

### What the literature actually measures

The Erdős–Rado sunflower conjecture asks: for fixed petal count \(r\) and set size \(w\), does every \(w\)-uniform family of more than \((C_r)^w\) sets contain an \(r\)-sunflower?  In the specific case \(w = 3, k = 3\) (3-uniform families, 3-petal sunflowers), two distinct quantities are tracked in the literature:[^1][^2]

1. **Small-\(n\) exact values** \(m(n, 3)\): the maximum size of a 3-sunflower-free family of 3-subsets of \([n]\).
2. **Asymptotic growth rate** \(c_3\): the constant such that the maximum family size grows like \(c_3^n\) as \(n \to \infty\), conjectured to satisfy \(c_3 < 2\).

These are related but not identical to the notation \(M(\infty, 3, 3)\). The literature uses \(\phi(s, w)\) or \(f(w, r)\) for the extremal quantity in the infinite-ground-set limit, and this limit is **not known** for \(w = 3, r = 3\).[^3][^4]

### Current best bounds (as of April 2026)

The best-known upper bound on the growth rate is \((1.889)^n\) (Naslund–Sawin 2016, improving Ellenberg–Gijswijt cap-set resolution applied to the weak Erdős–Szemerédi sunflower conjecture). The best lower bound on the maximum sunflower-free family for fixed small \(n\) comes from explicit constructions:[^5][^6]

- \(m(7, 3) \geq 30\) and \(m(8, 3) \geq 45\) are claimed computationally in a January 2026 preprint, with the formula \(m(n,3) = (8/3) \cdot (3/2)^{n-1}\) fitting computational data at 98.8% accuracy through \(n = 8\).[^7]
- The conjectural asymptotic growth rate from these data points is approximately \((3/2)^n \approx 1.5^n\).[^7]
- The Alweiss–Lovett–Wu–Zhang (2019) breakthrough improved the upper bound to \(O(w \log k)^w\) (with subsequent refinements by Rao and Tao to \((Cp \log k)^k\)).[^8][^9][^1]

### Is \(c_3 \geq 2.449\) publishable?

The measured lower bound \(c_3 \geq 2.449\) from the PMF computation would need to be checked against the known lower bound. If the density-of-states estimator genuinely produces families larger than any previously reported for given \(n\), this is either a new construction result or a benchmarking confirmation. The key gate: the **exact maximum for \(w = 4, k = 3\)** is even less characterized in the literature — Kupavskii–Noskov (arXiv:2511.17142, Nov 2025) obtains exact results for the Duke–Erdős forbidden sunflower problem for core size 1, uniformity \(k \geq 5\), and odd petal count, but leaves the \(w = 3, 4\) cases as still requiring asymptotic or computational treatment. A careful measurement at \(w = 3\) and \(w = 4\) with the PMF apparatus could thus stand as a genuinely novel lower bound result.[^10][^11]

### Verdict for Q1

The exact value \(M(\infty, 3, 3)\) is **not known**; the conjecture itself is open. The closest pinned-down quantities are small-\(n\) exact values through \(n \approx 8\) from 2025–2026 computational work, and the asymptotic bounds \((1.5)^n \lesssim c_3 \lesssim (1.889)^n\) implied by those constructions and cap-set methods. A well-documented \(c_3\) lower bound from the PMF/lattice-gas estimator is **not redundant** and would be a publishable observation. The \(w = 4\) case is even more open and higher-value to report.[^7]

***

## Q2 — Morphism Triangulation: Erdős #166 and #755

### Problem #166 status

Erdős problem #166 concerns a Ramsey-theory question about sum-free sets in graphs. As of the Thomas Bloom database (erdosproblems.com), problem #166 appears under "solved" in the forum tracking of the graphs problem collection. The related Erdős–Moser sum-free set problem — whether any \(N\)-element set of integers contains a sum-free subset of size \(> N/3\) — was **resolved** by Bedert (2025), who proved the lower bound \(N/3 + c \log\log N\). The sum-free set theory for this specific conjecture is now closed. This partially deflates the morphism-triangulation argument: applying the identical PMF machinery to a solved problem would be **confirmatory** rather than generative, though it could serve as a calibration check for the transfer-matrix approach.[^12][^13][^14][^15]

### Problem #755 status

Erdős problem #755 concerns equilateral triangles formed by point sets in \(\mathbb{R}^6\). The erdosproblems.com database notes this was solved "in a strong form," per the snippet for problem #755. The related Sidon set Erdős problem #707 (whether every finite Sidon set embeds in a perfect difference set) was **disproved** in 2025 by explicit counterexample \(\{1, 2, 4, 8, 13\}\), formally verified.[^16][^17][^18]

The annotation in Math/CLAUDE.md maps #755 to \(B_h[g]\) sequences, which is the Sidon-generalization literature where \(F_h(g, N)\) denotes the maximum size of a \(B_h[g]\) sequence in \([1, N]\). Upper and lower bounds for \(F_h(g, N)\) remain open for \(h \geq 3\) beyond leading-term asymptotics, so the \(B_h[g]\) question proper is still alive. However, the specific Erdős problem catalog entry for #755 may refer to a different formulation.[^19][^20]

### Morphism triangulation assessment

The morphism epistemology rule (one problem = curve-fitting, three problems = evidence for structure) requires the third test to be on a **genuinely open** extremal problem with the same formal structure: an exponential-growth-rate estimator applied to a constraint predicate governing a combinatorial family. Suitable candidates:

- **\(B_2\) (Sidon) sets**: \(F_2(1, N)\) is the Sidon maximum; the correct asymptotic is conjectured but not proven. The partition function analogy (density of admissible sum-free patterns under a modular constraint) maps cleanly to the transfer-matrix framework.[^21]
- **Cap sets**: The cap set problem in \(\mathbb{F}_3^n\) is **solved** (Ellenberg–Gijswijt 2016), but the quantitative structure of near-extremal cap sets is still studied.[^6]
- **3-AP-free sets in \([N]\)**: Related to Kelley–Meka 2023 progress, but the exact extremal density is now tightly constrained, reducing novelty value.

The practical recommendation: if Math/CLAUDE.md lists #166 and #755 as Tier 1 targets, verify their current open/solved status before allocating sessions. At least one of the two appears to be (partly or fully) resolved; replacing one with the open Sidon \(B_2\) extremal problem would preserve the three-problem triangulation structure while keeping the morphism test meaningful.

***

## Q3 — Mendoza's Limit \(M_L\): Sunflower Core-Closure Channel

### Formal structure of the question

The Mendoza Limit \(M_L = I \cdot k_B T \ln 2 / c^2\) applied to a combinatorial channel requires specifying what "information \(I\)" means for the sunflower core-closure operation: for a family \(\mathcal{F}\) of \(w\)-sets with \(|\mathcal{F}| = m\), the Shannon cost \(I(m, w, k)\) of certifying that a new \(k\)-sunflower core has been closed.

The natural encoding: each set in \(\mathcal{F}\) is a binary vector of length \(\binom{n}{w}\); a new core closure event requires signaling which of the \(\binom{n}{w-k+1}\) possible cores has been saturated. The information per closure event scales as:

\[I_{\text{closure}} \approx \log_2 \binom{n}{w-k+1} - \log_2 |\mathcal{F}_{\text{saturated cores}}|\]

As \(m \to m_{\text{extremal}}\), the density of available unsaturated cores decreases (the "geometry-exhausted regime" in the Geometric Shielding Principle terminology), which increases the per-closure information cost. This matches the qualitative behavior of the PMF growth-rate decay.

### Literature status

No paper in the current literature explicitly links Landauer-type information bounds to the combinatorial sunflower extremal density. The nearest related work is Rao's 2019 information-theoretic proof of the robust sunflower lemma, which uses Shannon entropy arguments to bound sunflower-free family sizes. Rao's approach bounds the **number of sets** using entropy, not a Landauer energy cost, so the Leg 4 / \(M_L\) formulation would be novel. The question of whether \(M_L\) binds the measured \(c_3\) lower bound vs. binds only asymptotically is thus an **open empirical question** that the existing PMF data could immediately address, and the result either way is original.[^9][^8]

***

## Q4 — Transfer Matrix Engineering: TT-Rank and DMRG Feasibility

### Current state of the code vs. what is needed

The file `sunflower_transfer_matrix.cpp` implements exhaustive backtracking, not a true transfer matrix. A canonical-order transfer matrix with state = last \(L\) subsets in lexicographic order, for some manageable \(L\), would give polynomial-per-layer cost and unlock \(n = 9, 10\) for \(w = 3\) and \(n = 8\) for \(w = 4\) — the precise range needed to confirm or refute the saturation hypothesis on more than two data points.[^7]

### TT-rank scaling question

The tensor-train (TT) rank scaling of the sunflower transfer matrix governs DMRG feasibility. For the sunflower constraint at \(w = 3, k = 3\), the transfer matrix connects states over successive layers of the lex ordering of 3-subsets of \([n]\). The number of distinct "dangerous" partial configurations (sunflower-threatening intersections involving the last \(L\) sets) grows as a function of the petal structure. For \(k = 3\), each new set can create a new sunflower with any two previously added sets sharing the same pairwise intersection — the relevant state space is the set of "pending core records" of size \(O(w^2 L^2)\). Whether this yields polynomial TT-rank in \(W\) (the PMF integrability criterion) requires explicit analysis, but the combinatorial structure is sparse: most pairs of 3-subsets in lex order have empty intersection, so the effective state space per layer is likely \(O(n^2)\) rather than exponential. This is encouraging for DMRG feasibility but needs formal verification.[^22][^23]

### Algorithmic path

The concrete path to \(n = 9, 10\) for \(w = 3\):
1. Define state \(S_i\) = multiset of pairwise intersections of the last \(L = O(w)\) accepted sets.
2. Define the transfer function: given \(S_i\), determine which 3-subsets can be appended without creating a 3-sunflower.
3. Use dynamic programming over states, with the partition function \(Z(n, w, k) = \sum_{\mathcal{F} \text{ valid}} e^{\beta |\mathcal{F}|}\) computed layer by layer.
4. Measure growth-rate decay and extract \(c_3\) via the density-of-states estimator.

***

## Q5 — k-Dependence: What Does \(c_k\) Look Like for \(k = 4, 5, 6\)?

### What theory predicts

The sunflower conjecture is that for each fixed \(r\), there exists \(C_r\) such that any \(w\)-uniform family of more than \(C_r^w\) sets contains an \(r\)-sunflower. The constant \(C_r\) should depend on \(r\) (petal count) but the conjecture says nothing specific about how \(C_r\) grows with \(r\). The Alweiss–Lovett–Wu–Zhang bound gives \(C_r = O(r \log w)\) (after Rao's simplification), implying \(C_r\) grows linearly in \(r\). If the PMF estimator measures \(c_k\) (using \(k\) for petal count in your notation) for \(k = 4, 5, 6\), and if \(c_k\) grows roughly linearly in \(k\), that would be consistent with the ALWZ bound and support a stronger claim. If \(c_k\) plateaus or grows sub-linearly, that would be empirically interesting in its own right.[^24][^25][^1][^9]

### Computational path and IP gate

Generalizing the current code from the hardcoded \(k = 3\) fast path to general \(k\) requires implementing the \(k\)-wise intersection check. This is an \(O\binom{m}{k}\) check per candidate set, which becomes expensive for large \(m\) and \(k = 5, 6\), but for small \(n\) (and thus small \(m\)) is tractable. The IP gate is real: the PMF/transfer-matrix method is the differentiating feature, and public reporting of \(c_k\) measurements made with that machinery should await provisional filing. The brute-force path (no PMF) can be published independently, though it adds less novelty.[^7]

***

## Meta-Question: Provisional Filing as the True Program Gate

The analysis confirms Ken's framing: the ErdosAtlas provisional filing status is the **single gating question** for the research program's publishable output this week. Of the five questions:

| Question | Literature status | IP gate? | Publishable this week? |
|---|---|---|---|
| Q1: \(M(\infty, 3, 3)\) exact value | Not known; bounds exist | No | **Yes** — \(c_3\) lower bound + \(w=4\) measurement |
| Q2: Morphism triangulation (#166, #755) | #166 partly solved; #755 status mixed | Partially | Only as calibration; replace with Sidon \(B_2\) |
| Q3: Mendoza's Limit / Leg 4 | Fully open; no prior literature | Yes (PMF framework) | After provisional |
| Q4: Transfer matrix engineering | Fully open | Yes (PMF integrability) | After provisional |
| Q5: \(c_k\) for \(k = 4, 5, 6\) | Fully open | Yes (PMF method) | After provisional (brute-force only otherwise) |

The literature check (Q1) costs one computation run and one literature survey (this query). It gates everything downstream by establishing whether the PMF measurements are confirmatory or novel. The answer is: **they are novel** — the \(w = 3, k = 3\) extremal density is not pinned down, and \(w = 4\) is even less characterized.[^10][^7]

The morphism triangulation (Q2) should use the Sidon \(B_2\) problem or another genuinely open target rather than #166, whose core sum-free conjecture is now settled. This is a minor redirection, not a structural problem.[^13][^12]

Q3–Q5 are correctly identified as IP-blocked until provisional filing. No research sessions should be allocated to those paths under the prime directive.

**Immediate recommended action**: Run the \(w = 3\) and \(w = 4\) density-of-states measurement, document the extremal families found, compare against the Mitchell 2026 computational bounds \(m(7,3) \geq 30, m(8,3) \geq 45\), and draft a short observation note. File provisional. Then unlock Q3–Q5 in sequence.[^7]

---

## References

1. [[1908.08483] Improved bounds for the sunflower lemma - arXiv](https://arxiv.org/abs/1908.08483) - The famous sunflower conjecture states that the bound on the number of sets can be improved to c^w f...

2. [Improved bounds for the sunflower lemma - Annals of Mathematics](https://annals.math.princeton.edu/2021/194-3/p05) - The famous sunflower conjecture states that the bound on the number of sets can be improved to 𝑐 𝑤 f...

3. [[PDF] Sunflowers in set systems of bounded dimension - UCSD Math](https://mathweb.ucsd.edu/~asuk/Sunflower0321.pdf) - Let fr(k) be the minimum positive integer m such that every family of k-sets whose size is at least ...

4. [[PDF] The Sunflower-Free Process - arXiv](https://www.arxiv.org/pdf/2509.16355.pdf) - Abstract. An r-sunflower is a collection of r sets such that the intersection of any two sets in the...

5. [Sunflower (mathematics) - Wikipedia](https://en.wikipedia.org/wiki/Sunflower_(mathematics)) - A mathematical sunflower can be pictured as a flower. The kernel is the brown part, the intersection...

6. [Polymath 10 Emergency Post 5: The Erdos-Szemeredi Sunflower ...](https://gilkalai.wordpress.com/2016/05/17/polymath-10-emergency-post-5-the-erdos-szemeredi-sunflower-conjecture-is-now-proven/) - Results by Erdos and Szemeredi give that the Erdos Rado sunflower conjecture implies the Erdos-Szeme...

7. [Sunflower Conjecture Research Update: m(n,3) Formula - LinkedIn](https://www.linkedin.com/posts/codysmitchell_github-sproutseedssunflower-conjecture-activity-7417375629257392128-emuh) - New Research: A Conjectured Formula for the Sunflower Problem in Combinatorics I'm excited to share ...

8. [[PDF] Improved Bounds for the Sunflower Lemma](https://par.nsf.gov/servlets/purl/10221621) - Erdős and Rado conjectured in the same paper that the bound in. Lemma 1.2 can be drastically improve...

9. [[PDF] Discrete Mathematics Note on sunflowers](https://par.nsf.gov/servlets/purl/10224759) - In 2019, there was a breakthrough on the sunflower conjecture: using iterative encoding arguments, A...

10. [Exact results and the structure of extremal families for the Duke ...](https://arxiv.org/html/2511.17142v1) - One of the most famous problems in Extremal Set Theory is the Erdős–Rado [erdos1960intersection] sun...

11. [Exact results and the structure of extremal families for the Duke - arXiv](https://arxiv.org/abs/2511.17142) - Exact results and the structure of extremal families for the Duke--Erdős forbidden sunflower problem...

12. [Graduate Student Solves Classic Problem About the Limits of Addition](https://www.quantamagazine.org/graduate-student-solves-classic-problem-about-the-limits-of-addition-20250522/) - Erdős knew that any set of integers must contain a smaller, sum-free subset. Consider the set {1, 2,...

13. [[PDF] 100 OPEN PROBLEMS Contents 1. Sum-free sets, product ... - People](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) - This collection of open problems has been circulated since 2018 when, encouraged by Sean Prendiville...

14. [UK graduate student resolves a Paul Erdős problem from 1965 ...](https://www.reddit.com/r/mathematics/comments/1kw0psq/uk_graduate_student_resolves_a_paul_erd%C5%91s_problem/) - UK graduate student resolves a Paul Erdős problem from 1965 about how common "sum-free" sets are. Nu...

15. [General Erdős Discussion](https://www.erdosproblems.com/forum/thread/General%20Erd%C5%91s%20Discussion) - 2.47 - [352], open 2.48 - [1154], open (new). Ramsey theory. 3.49 - [78], open 3.50 - [77], open 3.5...

16. [[PDF] Forbidden Sidon subsets of perfect difference sets, featuring a ...](https://borisalexeev.com/pdf/erdos707.pdf) - Erdős posed many problems about Sidon sets, especially regarding their sizes, many of which are stil...

17. [Erdős Problem #755](https://www.erdosproblems.com/755) - Erdős believed this conjectured upper bound should hold even if we count equilateral triangles of an...

18. [Go - Erdős Problems](https://www.erdosproblems.com/latex/755) - The number of equilateral triangles of size $1$ formed by any set of $n$ points in $\mathbb{R}^6$ is...

19. [[PDF] Bh[g] SEQUENCES Javier Cilleruelo and Jorge Jiménez-Urroz](http://matematicas.uam.es/~franciscojavier.cilleruelo/Papers/Bh%5Bg%5D%20sequences.pdf) - Introduction. Given a sequence of integers A, we define Rh(A;k) as the number of representations of ...

20. [[PDF] A Complete Annotated Bibliography of Work Related to Sidon ...](https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS11/pdf/) - Some open problems concerning Bh-sequences are also discussed in this paper.” Translating into the n...

21. [Sidon sets and sum-product phenomena - Cosmin Pohoata](https://pohoatza.wordpress.com/2021/01/23/sidon-sets-and-sum-product-phenomena/) - One of the most classical problems in additive combinatorics is to determine s_{+}(\left\{1,\ldots,N...

22. [Density Matrix Renormalization Group Algorithm (DMRG)](https://tensornetwork.org/mps/algorithms/dmrg/) - The DMRG algorithm works by optimizing two neighboring MPS tensors at a time, combining them into a ...

23. [Tensor-Train Decomposition | SIAM Journal on Scientific Computing](https://epubs.siam.org/doi/10.1137/090752286) - A simple nonrecursive form of the tensor decomposition in d dimensions is presented. It does not inh...

24. [[PDF] Near-sunflowers and focal families - Math (Princeton)](https://web.math.princeton.edu/~nalon/PDFS/near2.pdf) - A recent breakthrough due to Alweiss, Lovett, Wu and Zhang [3] improved the bound to (log k)(1+o(1))...

25. [[PDF] The Story of Sunflowers - University of Washington](https://homes.cs.washington.edu/~anuprao/pubs/SunflowerCentenial.pdf) - In 2019, Alweiss, Lovett, Wu and. Zhang [3] made a significant breakthrough. They proved that a fami...

