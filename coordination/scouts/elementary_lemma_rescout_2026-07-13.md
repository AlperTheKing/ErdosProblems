# Elementary direct-route rescout — 2026-07-13

## Verdict

No remaining `VERIFIABLE` or `DECIDABLE` entry in the 2026-07-13 database passes the mandatory direct-proof gate with a lemma tree of depth at most two. I recommend **no attack from this slice**. In particular, I did not start a new proof/search or create a problem directory.

This is not a claim that the problems are impossible. It is the narrower, auditable conclusion that none currently has all of:

1. a terminal finite certificate or theorem;
2. one load-bearing lemma with an explicit bridge to the full statement;
3. a falsifiable next action whose success would finish the problem; and
4. a manageable exit condition that does not merely open another finite range.

The three superficially best `DECIDABLE` candidates, #742, #475, and #551, fail exactly at item 4. Their large-parameter theorems do not leave a small, explicit, terminal remainder.

## Requested #742 / #475 / #551 comparison

### #742: Murty–Simon diameter-2-critical conjecture — reject

Exact deliverable: prove every diameter-2-critical graph on (n) vertices has at most (n^2/4) edges.

Füredi's primary theorem is only a sufficiently-large-(n) theorem: Z. Füredi, *The maximum number of edges in a minimal graph of diameter 2*, J. Graph Theory 16 (1992), 81–98, DOI [10.1002/jgt.3190160110](https://doi.org/10.1002/jgt.3190160110). Haynes–Henning quote the effective scale as (n>n_0), where (n_0) is a tower of 2s of height about (10^{14}), and record Fan's theorem only for (n\le 24) and (n=26): [primary-source discussion and exact hypotheses](https://d-nb.info/1372512942/34), pp. 1–2.

Thus an (n=25) certificate does **not** settle #742; it leaves every order (27\le n\le n_0). Local history independently reached the same obstruction. The retained search closes only 15 of 25 residual column ordinals inside one hard row of one profile; the estimated full hierarchy has about 8,972 profiles. See `docs_newmath/tried_log.md`, lines 230–250, and `docs_newmath/gpt_742_murty_simon.md`, lines 23–27. This is a bounded-family cascade with no terminal bridge, so the direct-proof guard requires exit.

### #475: Graham rearrangement conjecture — reject

Pham–Sauermann's exact main theorem is: for every (0<\alpha<1), there exists (C_\alpha>0) such that every (S\subseteq\mathbb Z_p\setminus\{0\}) with (C_\alpha\le |S|\le p^{1-\alpha}) has a valid ordering. Combined with other asymptotic ranges, this proves the conjecture only for all sufficiently large primes: H. T. Pham and L. Sauermann, *On Graham's rearrangement conjecture*, Theorem 1.2, [arXiv:2602.15797](https://arxiv.org/abs/2602.15797).

Neither the theorem nor the four-range synthesis supplies a numerical terminal prime bound. Extracting one would require tracking several asymptotic constants and then checking every subset of every smaller prime. That is not a depth-two certificate. The official page states only “all sufficiently large primes” and the known edge ranges (t\le12) and (p-3\le t\le p-1): [#475](https://www.erdosproblems.com/475). Local history already records this as confirm-only and nonterminal.

### #551: cycle-versus-clique Ramsey numbers — reject

Keevash–Long–Skokan prove that there exists an absolute (C\ge1) such that
\[
r(C_\ell,K_n)=(\ell-1)(n-1)+1
\quad\text{when}\quad
n\ge3,\qquad \ell\ge C\frac{\log n}{\log\log n}.
\]
This is Theorem 1.1 of P. Keevash, E. Long, and J. Skokan, *Cycle-complete Ramsey numbers*, [arXiv:1807.06376](https://arxiv.org/abs/1807.06376).

Because #551 assumes ℓ≥n, this implies the conjecture for sufficiently large (n), but the paper gives no numerical (C) suitable for a finite verification campaign. Even after extracting one, the residue consists of exact Ramsey nonexistence checks over all relevant colourings, not one bounded certificate. The official discussion explicitly says the problem is finitary but still open: [#551 thread](https://www.erdosproblems.com/forum/thread/551).

Conclusion of the comparison: #742 has a known but fantastically large remainder; #475 and #551 do not even expose a practical numerical remainder. None is terminal.

## Complete audited slice

The database entries remaining after the requested exclusions were

`7, 19, 307, 364, 366, 475, 506, 547, 551, 556, 580, 647, 672, 742, 848`.

| # | Current direct deliverable | Novelty/local-history gate | Direct-gate result |
|---:|---|---|---|
| 7 | One explicit distinct covering system with all moduli odd | Hough–Nielsen force a modulus divisible by 2 or 3; BBMST rule out the stronger odd-squarefree version. Official page has 21 comments and an active worker: [#7](https://www.erdosproblems.com/7). | Reject: famous explicit-certificate problem, but no depth-two construction mechanism. |
| 19 | Prove the Erdős–Faber–Lovász statement for every (n) | KKKMO prove only every sufficiently large (n); Hindman covers (n<10). The current official thread explicitly says the finite cases remain: [#19 thread](https://www.erdosproblems.com/forum/thread/19); primary theorem: [Annals 198 (2023)](https://annals.math.princeton.edu/2023/198-2/p02). | Reject. Correction to local `tried_log.md`: the current official status is `DECIDABLE`, not fully proved. The missing interval is not numerically exposed. |
| 307 | Exhibit finite prime sets (P,Q) with ((\sum1/p)(\sum1/q)=1) | Any witness uses at least 60 distinct primes. Local `open307/` and `search307/` contain 80 files; logged exact restricted searches include 3,299,537, 1,101,785, and 6,166,727 checked states and no witness, plus no 2-cycle through (10^8). [#307](https://www.erdosproblems.com/307). | Reject: witness lottery; failure cannot prove “no”. |
| 364 | Exhibit three consecutive powerful integers | No example below (7.38\times10^{28}); abc would give only finiteness. [#364](https://www.erdosproblems.com/364). | Reject: no finite frontier lemma. |
| 366 | Exhibit 2-full (n) with 3-full (n+1) | Local `search366/` exhausted its recorded 64-bit restricted family with `FOUND=0`. The often-cited (12167=23^3,12168=2^3 3^2 13^2) has the 3-full member first and is **not** a witness for the directed statement. [#366](https://www.erdosproblems.com/366). | Reject: exact candidate search has no completeness bridge. |
| 475 | Valid ordering for every subset of every prime field | See comparison above. | Reject: asymptotic synthesis, no numerical terminal remainder. |
| 506 | Determine the minimum number of circles for every (n) under the intended nondegeneracy condition | Elliott/Purdy–Smith give the sharp expression only for (n>393), and the intended hypotheses are themselves ambiguous. [#506](https://www.erdosproblems.com/506). | Reject: continuous geometric classification for (n\le393), not a single finite certificate. The natural extension route is explicitly false; see the counterexample below. |
| 547 | Prove (R(T)\le2n-2) for every nontrivial (n)-vertex tree | Zhao proves all sufficiently large (n), while current work still handles structural classes; one official worker is active. [#547 thread](https://www.erdosproblems.com/forum/thread/547). | Reject: no explicit/manageable finite threshold; checking one order cannot close the problem. |
| 551 | Exact (r(C_k,K_n)) for all (k\ge n\ge3) | See comparison above. | Reject: existential constant and exact Ramsey remainder. |
| 556 | Prove (R_3(C_n)\le4n-3) for every (n) | KSS prove sufficiently large odd (n); Benevides–Skokan prove sufficiently large even (n). The official thread says the finite verification remains open: [#556 thread](https://www.erdosproblems.com/forum/thread/556). | Reject: two nonnumerical asymptotic thresholds and hard multicolour Ramsey checks. |
| 580 | Embed every tree on at most (n/2) vertices under the half-high-degree hypothesis | Zhao proves the statement only for sufficiently large (n); this is the Loebl–Komlós–Sós frontier. [#580](https://www.erdosproblems.com/580). | Reject: no explicit small terminal interval or depth-two structural lemma. |
| 647 | Exhibit (n>24) with \(\max_{m<n}(m+\tau(m))\le n+2\) | Public exact certificate rules out (n\le 615{,}736{,}321{,}200{,}000{,}000), and every candidate is forced into prime-chain families. Four official workers are active: [#647 thread](https://www.erdosproblems.com/forum/thread/647). Local `search647/` also searched to (10^{12}). | Reject: the remaining prime-tuple obstruction is not a terminal construction lemma; more interval search is forbidden by the maze guard. |
| 672 | Exhibit a positive coprime arithmetic progression of length (k\ge4) whose product is a perfect power | GHP rule out (4\le k\le34); Bennett–Siksek rule out a remote large-(k), huge-prime-exponent range. Local `search672/` found no candidate in its recorded (N_{max}=200000,K_{max}=8) family. [#672](https://www.erdosproblems.com/672). | Reject: deep Diophantine witness problem, no bounded exhaustive family. |
| 742 | Prove Murty–Simon for all orders | See comparison above. | Reject: (n=25) is not a bridge to the full theorem; 27 through a 2-tower remain. |
| 848 | Prove the (7\pmod{25}) class is extremal for every (N) | Sawhney's primary Proposition 1.1 is only “there exists (N_0)”: [note](https://www.math.columbia.edu/~msawhney/Problem_848.pdf). Forum work gives an explicit threshold still around (2.64\times10^{17}) and contains 48 comments; local `search848/` reaches 20,000. [#848 thread](https://www.erdosproblems.com/forum/thread/848). | Reject: enormous finite cascade, already heavily AI-raced; precisely the prohibited pattern. |

## Concrete falsifier returned: #506's naive bridge fails at (n=8)

Let
\[
S=\{(\pm1,\pm1),(\pm2,\pm2)\}.
\]
This set is neither collinear nor cocircular. It determines exactly **18** circles, whereas the Purdy–Smith large-(n) expression gives
\[
1+\binom{7}{2}-\left\lfloor\frac72\right\rfloor=19.
\]
Therefore the proposed depth-one bridge “extend the (n>393) extremal formula verbatim to all smaller (n)” is false.

Exact verification is elementary. Of the 56 triples of points, exactly eight are collinear: four triples on (y=x) and four on (y=-x). For every remaining triple ((x_i,y_i)), canonicalize the integer null vector
\[
(a,b,c,d)\ne0,\qquad a(x_i^2+y_i^2)+bx_i+cy_i+d=0
\]
by dividing by its gcd and choosing (a>0). The 48 noncollinear triples yield 18 distinct keys: ten keys occur four times and eight occur once. Equivalently, (S) has ten 4-point circles and eight 3-point circles. Hence (10+8=18). I independently recomputed all 56 triples with exact integer determinants; the resulting multiplicity histogram is `{1: 8, 4: 10}`.

This configuration was also posted in the official discussion, so it is a route-killing object, not a novelty claim: [#506 thread](https://www.erdosproblems.com/forum/thread/506).

## Exit decision

No candidate in this status slice has a direct route satisfying all five registry fields. Starting another SAT formulation, asymptotic improvement, threshold lowering, or order-by-order campaign would violate the direct-proof guard. Preserve the existing searches; select outside this slice only if another scout supplies a genuinely terminal bridge.
