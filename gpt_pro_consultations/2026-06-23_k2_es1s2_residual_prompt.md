# GPT Pro Consultation Prompt - 2026-06-23 K2/T2 E+S1+S2 Residual

Context: Erdos Problem #23 STEP-1 finite theorem only. We are proving
`a(30)<=36`, i.e. no 30-vertex triangle-free graph has
`beta(G)=e(G)-MaxCut(G) >= 37`. Do not try to prove the full all-n conjecture.

Current global reduction:

- Exact-codegree-two reroot branch: `K=2`, `T=2`.
- Four labels on `R`: `E=0`, `S1=1`, `S2=2`, `D=3`.
- We include q14 for safety and disable H14 anti-tightness unless explicitly
  stated.
- q6-q9 are closed.
- q10 support `{E,D}` has three side instances:
  - idx95 `(q,A,B,cnt)=(10,6,10,4,0,0,6)` closed by complete state-count
    certificate V540.
  - idx96 `(10,7,9,4,0,0,6)` is running with C++ `64 x 1`; current live
    rows are all `INFEASIBLE`, no `FEASIBLE` or `UNKNOWN`.
  - idx97 `(10,8,8,4,0,0,6)` is prepared but not launched until idx96 closes.
- After V537-V540, q11-q14 still have 263 residual profile-side instances.

The smallest structural bottleneck is support `E+S1+S2` with no D vertices.
There are exactly three residual profile-side instances:

```
idx  q   A  B  c0 c1 c2 c3  support
270  13  6  7  1  6  6  0   E+S1+S2
344  14  6  6  1  6  7  0   E+S1+S2
360  14  6  6  2  6  6  0   E+S1+S2
```

Known scale evidence:

```
idx270 sample1000:
  base_total=72014
  sample_orbits=17662
  sample_raw=31181
  sample_tasks=7046648
  extrapolated tasks ~= 507457309
  eR range 18..31, M_floor range 30..56

idx344 sample10:
  base_total=706436
  sample_orbits=164
  sample_raw=2457
  sample_tasks=59287
  extrapolated tasks ~= 4188247113
  eR range 21..31, M_floor range 38..57
```

The direct labelg quotient task grid is therefore too large unless we add a
new structural or quotient-level cut first.

Current exact state-count checker architecture (`state_count_6195_cpsat.py`):

- Variables are count quotients over legal A/B states, not labelled A/B rows:
  `A_I, B_I` for independent R-subsets `I`.
- Exact `sum A_I=|A|`, `sum B_I=|B|`, exact `M=sum |I|(A_I+B_I)`.
- Exact `alpha_r`, `beta_r`; optional exact `MA`, `MB`.
- Exact A/B law at count level:
  - `I cap J = empty` contributes complete A-B block.
  - `|I cap J|=1` is forbidden.
  - `p = sum_I A_I * sum_{J disjoint I} B_J`.
- Root-opposite codegree:
  - every used A-state has at least two disjoint B-state copies;
  - every used B-state has at least two disjoint A-state copies.
- Per-state degree cuts: `deg_B(I)+|I| >= R0-1`, symmetric for B.
- Typewise A/R, B/R, A/A, B/B, and R/R nonedge-codegree constraints.
- Full Psi cuts over all R masks.
- Exact-two-root unpaired U1/U2/U3 cuts over all R masks.
- Optional projection cuts `--projection-cuts`.
- Optional defect-block projection `--defect-block-labels`.
- Optional quotient-cut separation: full weighted state-quotient cut lazily.
- Anti-tightness is disabled in the safe K2 reroot runs.

Important: do NOT use either rejected lemma:

- terminal-touch degree equality;
- `C`-tight endpoint degree equality.

H14 anti-tightness can be suggested only as conditional on an independently
audited q14 closure through edge 143; for this prompt prefer unconditional
K2/T2 cuts.

What we need:

Find the next mathematically safe strengthening for the `E+S1+S2` residual
branches above, preferably before full fixed-skeleton state task materialization.
The answer should be concrete enough to encode and verify.

Useful target forms:

1. A profile-level scalar contradiction or strong filter using the fact that
   labels are only `E,S1,S2`, allowed R-edges are `E-E`, `E-S1`, `E-S2`,
   and `S1-S2`.
2. A skeleton-level cut for `E+S1+S2` that avoids enumerating hundreds of
   millions of state tasks.
3. A P-free count-quotient inequality, e.g. a new cut over `alpha`, `beta`,
   `p`, `M`, R-boundaries, or label blocks.
4. A reusable projected quotient/min-cut separator specialized to one or two
   empty-label vertices.
5. A small exact branch decomposition that would turn idx270/344/360 into a
   manageable finite certificate.
6. A falsification attempt: construct a scalar or quotient witness surviving
   current constraints, so we can identify the truly missing condition.

Please give:

- the precise lemma or cut statement;
- a proof sketch using only triangle-freeness, nonedge-codegree >=2, beta>=37
  cut inequalities, and the K2/T2 reroot setup;
- exact CP-SAT or C++-checker encoding guidance;
- which of idx270, idx344, idx360 it should hit first;
- any assumptions that would make it conditional.

Avoid broad advice like "run more SAT". The key question is how to compress or
kill `E+S1+S2` before direct full task-grid enumeration.
