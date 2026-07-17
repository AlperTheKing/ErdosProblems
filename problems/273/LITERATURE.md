# Literature for Erdős Problem 273


## Gate status (2026-07-13)

**Provisional pass.** No primary source found in the searched literature gives a p >= 5 certificate or a global nonexistence theorem. The official problem page still labels #273 open. A fresh search is required before any public claim.

## Original statement

- P. Erdős and R. L. Graham, *Old and New Problems and Results in Combinatorial Number Theory*, Monographie de L'Enseignement Mathématique 28, Geneva, 1980, printed p. 24 (PDF page 20), [author-hosted scan](https://mathweb.ucsd.edu/~ronspubs/80_11_number_theory.pdf).
- Local scan: `sources/erdos_graham_1980_monograph.pdf`, SHA-256 `0CBF0C32F0AB1E1C71DB5121A88BAC905BF976C4A6AB6BB6D7D9CF9DDD184ED3`.
- Rendered source page: `sources/erdos_graham_p24.png`, SHA-256 `7F460A9C90DB00B329816B5DA43D901792CC3E59A3C5CFF0318F3EE017A9C65B`.
- Hypothesis: the section defines a covering system using `1 < n_1 < ... < n_r`; distinctness is explicit.
- Question: may every `n_i` equal `p-1` for a prime `p >= 5`?
- Baseline sentence: “If p=3 is allowed then Selfridge has given such an example using the divisors of 360.” No residue list or citation accompanies this sentence.

The official [Erdős Problems page](https://www.erdosproblems.com/273) labels the problem OPEN and repeats the same baseline. The [formal-conjectures statement](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/273.lean) uses `StrictCoveringSystem` and leaves both the p >= 5 conjecture and p >= 3 variant unproved (`sorry`).

## Selfridge trace

- J. L. Selfridge, “Covering sets of congruences,” *Notices of the AMS* 10 (1963), p. 348, [full issue](https://www.ams.org/journals/notices/196306/196306FullIssue.pdf). The abstract concerns general covering questions and does not publish the p-1/divisor-360 residues.
- J. L. Selfridge, Proposed Problem 28, *Proceedings of the 1963 Number Theory Conference*, University of Colorado, 1963. Google Books page 96 asks general minimum-modulus and odd-modulus questions; within-volume searches for `360` and the p-1 restriction returned no hit.
- The Erdős–Graham page-24 assertion therefore appears to report an unpublished construction or personal communication. It establishes existence, not a unique residue assignment.

## Exact arithmetic forced by the 360 assertion

The divisors `m | 360` with `m+1` prime are exactly

`2, 4, 6, 10, 12, 18, 30, 36, 40, 60, 72, 180`,

with primes

`3, 5, 7, 11, 13, 19, 31, 37, 41, 61, 73, 181`.

Their reciprocal sum is `23/18`; after excluding `m=2` it is `7/9 < 1`. Thus every p >= 3 construction restricted to divisors of 360 must use modulus 2, while no p >= 5 construction restricted to divisors of 360 can cover by the union bound.

## Primary results with exact scope

- James H. Jordan, “Covering Classes of Residues,” *Canadian Journal of Mathematics* 19 (1967), 514–519, [doi:10.4153/CJM-1967-043-0](https://doi.org/10.4153/CJM-1967-043-0). Definition requires distinct moduli. Theorem 1 gives a 21-class distinct cover with all moduli dividing 360, but moduli including 5, 8, 9, and 15 are not one less than primes; it is not the #273 baseline.
- P. Balister, B. Bollobás, R. Morris, J. Sahasrabudhe, and M. Tiba, “The Erdős covering problem: the density of the uncovered set,” *Inventiones Mathematicae* 228 (2022), Theorem 1.2. Every finite cover by arithmetic progressions contains two moduli with one dividing the other. Therefore any #273 certificate must contain allowed moduli `m | n`, equivalently prime predecessors with `p-1 | q-1`.
- B. Hough and P. P. Nielsen, “Covering Systems with Restricted Divisibility,” *Duke Mathematical Journal* 168(17) (2019), 3261–3295, [doi:10.1215/00127094-2019-0058](https://doi.org/10.1215/00127094-2019-0058), Theorem 1: every distinct cover has a modulus divisible by 2 or 3. This is compatible with #273 because all `p-1` for odd primes are even.
- Z.-W. Sun, “On Covering Numbers,” *INTEGERS* 7(2) (2007), A33, [arXiv:math/0601017](https://arxiv.org/abs/math/0601017). Its constructive theorems select arbitrary distinct divisors of a covering number; they do not force every selected modulus to be `p-1`.
- M. Newman, “Roots of Unity and Covering Sets,” *Mathematische Annalen* 191 (1971), 279–282. Its repeated-largest-modulus obstruction is for exact/disjoint covers, whereas #273 permits overlap.
- J. Harrington, G. Klein, L. Lowrance, and O. Trifonov, “Covering systems where the prime divisors of all moduli are only 2, 3, or 5,” arXiv:2605.18644 (2026). Its smooth-LCM classifications do not impose `m+1` prime and do not resolve #273.

## Reliability exclusion

O. P. Ogunmefun, “Covering System with Restricted Moduli: Theory, Existence and Computational Structure,” WJAETS 17(3) (2025), claims distinct prime-only covers without an exact certificate. Such a finite system cannot cover: for pairwise coprime prime moduli, the CRT selects an integer outside the one chosen residue for every modulus. This source is not relied upon.

## Search record

Queries run across web, arXiv, DOI/publisher pages, Google Books within-volume search, and primary author archives included all requested phrases plus `prime minus one`, `one less than a prime`, Selfridge, Krukenberg, prescribed moduli, restricted divisibility, and covering numbers. No source located a p >= 5 solution or a global negative theorem.
