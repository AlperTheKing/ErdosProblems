# Literature-lag rescout — 2026-07-13

## Verdict

The current official database has several genuine June-2026 literature lags. Four recent primary manuscripts state theorems that directly cover Problems #593, #1177, #550, and #768; a fifth theorem directly disproves the proposed linear asymptotic in #1061. These are novelty-gate failures, not targets for a new proof campaign.

No direct bounded target is nominated. The requested focused checks found no 2025–2026 theorem settling #617 or #993, while local history shows that both have already consumed substantial exact-search or proof effort. The closest new papers for #993 prove only special families or failure of log-concavity, not failure of unimodality.

All 2026 “resolution” papers below are recent arXiv preprints. This audit checks the exact stated hypotheses against the official problem quantifiers; it is not an independent line-by-line referee verification of their proofs.

## Audit method

1. Read the root `AGENTS.md` and applied the DIRECT-PROOF GUARD: a literature hit must bridge immediately to the original quantifiers, not to a surrogate.
2. Compared the current official YAML database (`C:\tmp\erdosproblems_current.yaml`) with the live official pages. The pages still label #593, #1177, #550, #768, and #1061 `OPEN`; #617 and #993 are `FALSIFIABLE`.
3. Queried the arXiv API for
   `(all:Erdos OR all:Erdős) AND all:problem AND submittedDate:[202501010000 TO 202607132359]`.
   The response contained all 395 matching records, not a truncated first page. Numbered solution claims and terminology-specific matches were then screened manually.
4. Downloaded and read the full primary PDFs for every load-bearing claim. Exact theorem statements, rather than abstracts or search snippets, are recorded below.
5. Ran focused title/phrase searches for #617 and #993 and checked the cited 2025–2026 primary papers.
6. Searched local history with `rg`. There are no dedicated `problems/<n>` directories for the seven audited problem numbers, but `handoff.md`, `docs_newmath/tried_log.md`, `LEDGER.md`, `search617/`, `search993/`, and `docs_993/` contain extensive prior work on #617 and #993.

## Direct official-status lags

### #593 — full theorem match

- Official statement: characterize the finite 3-uniform hypergraphs occurring in every 3-uniform hypergraph of uncountable chromatic number.
- Primary source: Eric Li, *A Resolution of Erdős Problems 593 and 1177: Obligatory Triple Systems and Exact Spectra*, arXiv:2606.24882v1, 23 June 2026, Theorem 1.1.
- Exact hypotheses and conclusion: for every finite triple system (F), occurrence in every uncountably chromatic triple system is equivalent to the following intrinsic conditions after deleting isolated vertices:
  1. (F) is linear;
  2. every hyperedge-node of the Levi graph of (F) is incident with a bridge;
  3. every Berge cycle of (F) has even length.
- Bridge: the quantified class of finite (F) and the host condition are exactly those of the official problem, and the conclusion is an iff characterization.
- Decision: `DEAD: arXiv:2606.24882v1, Theorem 1.1 claims the exact classification.`
- Official page: <https://www.erdosproblems.com/593>
- Primary paper: <https://arxiv.org/abs/2606.24882>

### #1177 — full three-clause theorem match

- Primary source: the same paper, Corollary 1.4.
- Exact hypotheses: (G,H) are finite 3-uniform hypergraphs; (F_G(kappa)) is the class of (G)-free 3-uniform hypergraphs of exact chromatic number (kappa); (kappa,lambda) are uncountable cardinals.
- Exact conclusions, in official order: **yes, no, yes**.
  1. If (F_G(\aleph_1)\ne\varnothing), it contains a system of cardinality at most (2^{2^{\aleph_0}}).
  2. The proposed intersection assertion is false. An explicit pair is: (G) is two triples sharing a pair and (H) is the loose 7-cycle. Both avoidance classes are nonempty but their intersection is empty.
  3. If (F_G(\kappa)\ne\varnothing) for one uncountable (kappa), then (F_G(\lambda)\ne\varnothing) for every uncountable (lambda).
- Bridge: these are the three live-page assertions with the same exact-chromatic-number convention. The paper also notes that they imply the older “uncountably chromatic” wording.
- Decision: `DEAD: arXiv:2606.24882v1, Corollary 1.4 claims all three clauses, including an explicit counterexample to clause 2.`
- Official page: <https://www.erdosproblems.com/1177>

### #550 — full theorem match

- Official statement: for fixed (m_1\le\cdots\le m_k), all sufficiently large (n), every (n)-vertex tree (T), and (G=K_{m_1,\ldots,m_k}), prove
  \[
  R(T,G)\le (\chi(G)-1)(R(T,K_{m_1,m_2})-1)+m_1.
  \]
- Primary source: Eric Li, *A Resolution of Erdős Problem 550 on Tree versus Complete Multipartite Ramsey Numbers*, arXiv:2606.23659v1, 22 June 2026, Theorem 1.1.
- Exact theorem: fix (k\ge2) and integers (1\le m_1\le\cdots\le m_k). There exists (n_0=n_0(m_1,\ldots,m_k)) such that for every (n\ge n_0) and every (n)-vertex tree (T),
  \[
  R(T,K_{m_1,\ldots,m_k})\le(k-1)(R(T,K_{m_1,m_2})-1)+m_1.
  \]
- Bridge: (chi(K_{m_1,\ldots,m_k})=k), so the formulas and quantifiers coincide verbatim.
- Decision: `DEAD: arXiv:2606.23659v1, Theorem 1.1 claims the exact statement.`
- Official page: <https://www.erdosproblems.com/550>
- Primary paper: <https://arxiv.org/abs/2606.23659>

### #768 — full asymptotic and exact constant

- Official statement: if (A) is the set of positive integers (n) such that for every prime (p\mid n) there is a divisor (d>1) of (n) with (d\equiv1\pmod p), determine whether
  \[
  \frac{|A\cap[1,x]|}{x}
   =\exp(-(c+o(1))\sqrt{\log x}\log\log x)
  \]
  for some (c>0).
- Primary source: Eric Li, *The Sylow Divisor Condition: a Resolution of Erdős Problem 768*, arXiv:2606.24872v1, 23 June 2026, Theorem 1.1.
- Exact theorem: writing (A(x)=|A\cap[1,x]|),
  \[
  \lim_{x\to\infty}
  \frac{\log(x/A(x))}{\sqrt{\log x}\log\log x}
  =\frac{1}{2\sqrt{\log 2}}.
  \]
  Equivalently, the official asymptotic holds with (c=1/(2\sqrt{\log2})).
- Bridge: the divisor condition and scale are exactly the official ones; this was confirmed from the paper's TeX source so the radical covers only (log x), as on the official page.
- Decision: `DEAD: arXiv:2606.24872v1, Theorem 1.1 gives the exact requested asymptotic and constant.`
- Official page: <https://www.erdosproblems.com/768>
- Primary paper: <https://arxiv.org/abs/2606.24872>

### #1061 — exact refutation of the proposed linear asymptotic

- Official statement: count ordered pairs ((a,b)\in\mathbb N^2) with (a+b\le x) and (sigma(a)+\sigma(b)=\sigma(a+b)); in particular, ask whether their number (S(x)) is asymptotic to (cx) for some (c>0).
- Primary source: Eric Li, *A resolution of Erdős Problem 1061 on the sum-of-divisors function*, arXiv:2606.25849v1, 24 June 2026, Theorem 1.1.
- Exact theorem: for every fixed (R>0),
  \[
  \lim_{x\to\infty}\frac{S(x)}{x(\log x)^R}=+\infty.
  \]
  The paper counts ordered pairs and separately proves there are no diagonal solutions, so the convention matches the page.
- Bridge: this implies (S(x)\not\sim cx) for every finite (c>0), directly answering the displayed conjectural subquestion in the negative.
- Scope caution: it does **not** give an exact order for the broader opening question “How many solutions are there?” Therefore this is a decisive novelty hit against attacking the (S(x)\sim cx) conjecture, but should not be paraphrased as an exact asymptotic count unless the site owner treats refuting that conjecture as complete resolution.
- Decision: `DEAD for the linear-asymptotic target: arXiv:2606.25849v1, Theorem 1.1.`
- Official page: <https://www.erdosproblems.com/1061>
- Primary paper: <https://arxiv.org/abs/2606.25849>

## Focused check: #617 balanced (r)-colourings

### Exact current frontier

The official assertion is universal over (r\ge3): every (r)-edge-colouring of (K_{r^2+1}) has an ((r+1))-vertex set missing a colour. In the original primary paper, Erdős and Gyárfás prove the assertion for (r=3) and (r=4): Lemma 1 handles (K_{10}) with three colours and Lemma 2 handles (K_{17}) with four colours. They also construct balanced colourings on (K_{r^2}) from affine planes, so replacing (r^2+1) by (r^2) is impossible in infinitely many orders.

- Primary source: P. Erdős and A. Gyárfás, “Split and balanced colorings of complete graphs,” *Discrete Mathematics* 200 (1999), 79–86, DOI <https://doi.org/10.1016/S0012-365X(98)00323-9>.
- 2025–2026 search result: no paper was found that proves the universal assertion or gives a finite counterexample. Exact-title searches, “balanced ((r,2))-coloring,” (K_{r^2+1}), and “Erdős Problem 617” returned the 1999 paper, unrelated notions of balanced colouring, and the official page; the 395-record arXiv audit produced no direct #617 result.
- Local overlap: `handoff.md` records a calibrated (r=5), (K_{26}) SAT/SMS campaign. Direct SAT remained unknown on easier calibration instances; 111 of 120 cubes timed out at 300 seconds, and the projected full search was months to years. `LEDGER.md` marks #617 `PARKED`, requiring a search-collapsing theorem before resumption.
- Target decision: no nomination. A single balanced 5-colouring of (K_{26}) would be a bounded disproof certificate, but neither the literature nor local history supplies an immediate path to that certificate. Restarting brute force would violate the workflow's tractability gate.
- Official page: <https://www.erdosproblems.com/617>

## Focused check: #993 tree independence-polynomial unimodality

No 2025–2026 primary source found in this audit settles all trees or forests.

1. David Galvin, *Trees with non log-concave independent set sequences*, arXiv:2502.10654v2, Theorems 1.3 and 2.1:
   for sufficiently large (t), explicit trees (T_t), and more generally (T_{m,t,1}) with (t\le m\le2^{t/16}), violate a specified log-concavity inequality near the far tail. This disproves stronger log-concavity claims, not unimodality; the constructed sequences may remain unimodal.
2. Grace M. X. Li, *Unimodality of independence polynomials of two family of trees*, arXiv:2603.03025v1, Theorems 1.4 and 1.5:
   for all (m,n\ge1), the two particular families (T_{3,m,n}) and (T^*_{3,m,n}) have unimodal independence polynomials. This is a genuine infinite-family theorem but does not cover arbitrary trees.
3. Takayuki Hibi, Selvi Kara, and Dalena Vien, *Symmetric and unimodal independence polynomials of trees*, arXiv:2604.18824v1:
   the paper studies existence of trees with symmetric unimodal independence polynomials; its introduction explicitly says the all-tree conjecture remains open as of April 2026.
4. Brett Reynolds, *Mean bounds, structural reductions, and exhaustive verification for tree independence polynomial unimodality*, Zenodo preprint v3, DOI <https://doi.org/10.5281/zenodo.19100781>:
   reports exhaustive verification of all 8,691,747,673 unlabeled trees on at most 29 vertices, plus conditional structural reductions, and explicitly states that the conjecture remains open.

Local overlap is decisive: `docs_newmath/tried_log.md` marks #993 `UNAVAILABLE`; `handoff.md` records multiple exact counterexamples to proposed uniform strengthening lemmas, while the surviving (m=2,3) family results overlap the published Li/Galvin scope. `search993/` and `docs_993/` preserve the partial Lean and computation artifacts. No bounded order is known whose successful exclusion would prove the universal conjecture.

Target decision: no nomination. Another finite verification or another special-family theorem has no stated bridge to all trees and would trigger the reformulation-maze exit.

- Official page: <https://www.erdosproblems.com/993>
- Primary papers: <https://arxiv.org/abs/2502.10654>, <https://arxiv.org/abs/2603.03025>, <https://arxiv.org/abs/2604.18824>

## Near misses that must not be misclassified

- **#731:** arXiv:2606.29062v1 proves dyadic tail bounds and rules out an asymptotic equivalent only for a newly defined class of *dyadically regular* functions. The official word “reasonable” is informal and the paper's extra regularity hypothesis is not part of a precise original quantifier. This is a substantial conditional formalization, not an unconditional exact match. Do not attack via further normalization classes.
- **#400:** arXiv:2606.23661v2 proves a density-one lower bound and a pointwise upper bound for (g_k(n)), leaving a nonzero gap between constants. It proves neither requested asymptotic.
- **#684:** arXiv:2606.08216v1 proves the normal order of the first threshold crossing for almost all (n), and explicitly says this is not the pointwise worst-case assertion in the official problem.
- **#478:** arXiv:2604.26429v5, Theorem 1.1, claims there are no socialist primes other than (5). That settles a subsidiary question mentioned in the official remarks, not the main asymptotic (|A_p|\sim(1-1/e)p).

These four are exactly the sort of asymptotic or restricted-hypothesis surrogate that the DIRECT-PROOF GUARD forbids promoting into a new attack without a closing theorem.

## Reproducibility

SHA-256 hashes of the primary PDFs actually read:

- `2606.24882.pdf`: `93191B28CECBE4268A58553FF2C60779DC85A585BC633F604165269F0D2B3A42`
- `2606.24872.pdf`: `080C1FA4AAE65192A12C27DBA1B6D22FAA6797DEBE9AE1D603F6AA67189909C9`
- `2606.23659.pdf`: `2B59E7DF22B46E14AA53EBFE9E93FBC286E4B833F7BCE004122476AAAB088E1F`
- `2606.25849.pdf`: `AE820BC001F52589276FFD0CD146C547E9BC4D4DC3C7B60331A4803FD8C2812B`
- `2603.03025.pdf`: `3A155EA5A3C0B8944319076C28A4E8F1245EC4E8A3F3230B9DBDEB8C2F152D4F`
- `2502.10654.pdf`: `3A848A39FC9AFDC4BE22D673031CEE9ACE862EF2FBB46CF0C551E5E3C5D17C89`

## Selection recommendation

Do not select #593, #1177, #550, #768, or the linear-asymptotic version of #1061: current primary manuscripts already state the terminal theorems. Do not select #617 or #993 as an “easy” replacement: the focused literature audit found no closing theorem, and local exact work records concrete computational or structural walls. This rescout supplies novelty-gate kills, but no candidate meeting the direct bounded-target gate.
