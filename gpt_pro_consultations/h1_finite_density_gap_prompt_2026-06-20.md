# GPT Pro Consultation Prompt: H1 finite-density gap for Erdős #23 Step 1

CONTEXT.

We are proving the finite theorem

```
H1: a(30) <= 36
```

where for a graph `G`,

```
beta(G) = e(G) - MaxCut(G),
```

so H1 says: no triangle-free graph on 30 vertices has `beta(G) >= 37`.

This is Step 1 only.  Do not try to prove the full Erdős #23 conjecture for all
orders; a separate agent is working on the bridge from H1 to all `n`.

CURRENT VERIFIED FINITE WORK.

The project has a large rooted low-codegree finite certificate for the medium
window, using a nonedge root `xy` with common-neighbour set `C`, `k=|C|`,
exclusive root neighbourhoods `A,B`, and residual `R`.  Many branches are
closed by exact CP-SAT/state-count certificates.  Recent important audit:

- The apparent q13/r0=8/t=2 `a6b7` branch was invalid for n=30 because the
  rooted partition count is

  ```
  2 + k + na + nb + q = 2 + 3 + 6 + 7 + 13 = 31.
  ```

  It is now marked diagnostic only and verifier/runner code rejects
  `2+k+na+nb+q != 30`.

- The visible valid q13/k=3/t=3 branches are closed at profile level:

  ```
  r0=8, (na,nb)=(5,7): 257/257 INFEASIBLE
  r0=8, (na,nb)=(6,6): 249/256 plus 7/7 hard rerun INFEASIBLE
  r0=8, (na,nb)=(7,5): 256/256 INFEASIBLE
  r0=9, (na,nb)=(6,6): 93/94 plus hard profile 74088 INFEASIBLE
  ```

- A large q13 profile `6195` family through `e_R=16` is closed:

  ```
  search23/state_count_6195_er16_clean_infeasible_union.tsv
  expected=59823
  unique_infeasible=59823
  missing=0
  noninf_keys=0
  malformed=0
  ```

UNTRUSTED / FORBIDDEN CUT.

Do not use the experimental "terminal-touch equality" or `terminal_closure`.
It was rejected as mathematically unjustified.  The only safe reroot-related
replacement currently accepted is the anti-tightness inequality:

```
For r not in U_i:
D(r) + |U_i| + d_R(r,U_i) >= 17,
D(r)=alpha_r+beta_r+d_R(r)+|L(r)|.
```

MAIN BLOCKER.

The proof state previously used Balogh--Clemen--Lidicky (BCL) density
reductions to restrict the n=30 search to roughly

```
109 <= e(G) <= 139.
```

But the BCL density theorems are asymptotic: the stated results hold only for
`n >= n0`, and the project does not know `n0 <= 30`.  Therefore H1 is not yet
proved unless we replace this with a finite-n argument or exact finite
certificates.

We need to close the omitted edge ranges for triangle-free 30-vertex graphs:

```
low range:  74 <= e(G) <= 108
high range: 140 <= e(G) <= 225
```

(`e <= 73` is trivial since beta <= e/2 < 37, and Mantel gives e <= 225.)

AVAILABLE FACTS / TOOLS.

1. Vertex deletion inequality:

```
beta(G) <= beta(G-v) + floor(d(v)/2).
```

2. Known finite McKay/OEIS values:

```
a(23)=20
```

and the McKay 23-vertex extremals with beta=20 have edge counts 100..105.

3. A project memo claims `a(25)=25`, but that proof itself relies on the same
asymptotic BCL high-density input at n=25, so do NOT use it as an unconditional
finite theorem unless you also repair that gap.

4. Wang--Yang--Zhao / Andrasfai-type input used in the current proof state:
if a triangle-free graph on 30 has minimum nonedge-codegree at least 4, then it
is homomorphic to C5, hence beta <= e/5.  Thus any counterexample with
beta>=37 can be maximalized and then has a nonedge with common-neighbour count
1..3, provided the maximalization remains in the edge universe being searched.
This part was previously combined with the BCL high-density cap, so check
circularity carefully.

5. Direct low-codegree SAT without structural reduction was too hard in a
medium-density smoke test.  However, high-density or low-density edge ranges
may admit simpler finite arguments.

QUESTION.

Find the shortest rigorous path to eliminate the finite BCL gap for H1:

1. Give a finite, gap-free proof that every triangle-free 30-vertex graph with
   `e >= 140` has `beta <= 36`; OR give a sharply scoped exact finite
   certificate/encoding that would be small enough to run and audit.

2. Give a finite, gap-free proof that every triangle-free 30-vertex graph with
   `74 <= e <= 108` has `beta <= 36`; OR give a sharply scoped exact finite
   certificate/encoding that would be small enough to run and audit.

3. If neither is available, identify a smaller structural lemma that would
   replace the asymptotic BCL use.  Examples: finite high-density stability,
   deletion-to-23 with edge-count restrictions, bounded low-degree peeling
   combined with beta loss, exact root-degree branching, or a max-cut
   discharging lemma.

REQUIREMENTS.

- Be adversarial.  Do not assume BCL asymptotic theorems are valid at n=30.
- Do not use the untrusted terminal-touch equality.
- State every additional theorem/citation precisely; if you are unsure it
  exists or applies at n=30, say so.
- Prefer concrete inequalities or finite certificates over vague strategy.
- If proposing computation, specify exact variables, constraints, branching
  parameters, and what certificate would make the result independently
  checkable.
- End by listing the weakest steps and the smallest next experiment.
