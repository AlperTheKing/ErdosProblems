# Fan-averaging variance inequality — exact reduction to one scalar inequality (BD-TARGET)

**Goal.** For every NONUNIQUE bad edge f (|cyc(f)|≥2) on a γ-min connected-B max cut:
`N·(N − row_f) ≥ var_f`,  where `S(v)=Σ_g p_g(v)`, `row_f=Σ_v p_f(v)S(v)`, `ℓ_f=Σ_v p_f(v)`,
`var_f=Σ_v p_f(v)(S(v) − row_f/ℓ_f)²`.  (Since var_f≥0 this is the fan-averaging half of ROWSUM-O.)

## The reduction (RIGOROUS, two pieces)

Write `μ := row_f/ℓ_f = mean_f`, and over the support `supp(p_f)` (= vertices on f's B-geodesics)
let `M := max_{v∈supp} S(v)`, `m := min_{v∈supp} S(v)`. Let `π_f(v) := p_f(v)/ℓ_f` (a probability measure,
since Σ_v p_f(v)=ℓ_f). Then `var_f = ℓ_f · Var_{π_f}(S)` and `μ = E_{π_f}[S] ∈ [m,M]`.

**Piece 1 — Bhatia–Davis (UNCONDITIONAL elementary theorem, PROVED).**
For any prob. measure π and bounded variable X with `m ≤ X ≤ M` and mean μ:
`Var_π(X) ≤ (M−μ)(μ−m)`.
*Proof.* `(M−X)(X−m) ≥ 0` pointwise ⟹ `E[(M−X)(X−m)] ≥ 0` ⟹ `E[X²] ≤ (M+m)μ − Mm` ⟹
`Var = E[X²] − μ² ≤ (M+m)μ − Mm − μ² = (M−μ)(μ−m)`. ∎ (Exact-tight at 2-point measures; verified.)
Hence `var_f ≤ ℓ_f (M−μ)(μ−m)`.

**Piece 2 — BD-TARGET (the SINGLE remaining inequality, OPEN).**
`ℓ_f (M−μ)(μ−m) ≤ N (N − row_f)`.

Combining: `var_f ≤ ℓ_f(M−μ)(μ−m) ≤ N(N−row_f)`. ∎ (modulo BD-TARGET)

## Exact validation (Fraction) on the standing gate — `_wf_var_reduce.py`
- **BD step** (Var ≤ (M−μ)(μ−m)): 0 violation (it is a theorem; sanity = pass).
- **BD-TARGET**: 0 violation over the full triangle-free census N≤11 (ALL γ-min connected-B max cuts,
  268864 nonunique rows), the iterated Mycielskian M(Grötzsch)=N23 and M(C11)=N23 (the finite-depth killers),
  Grötzsch, M(C7),M(C9), bridges, and all C_{2k+1}[t] blow-ups tested.
- **FINAL** N(N−row_f) ≥ var_f: 0 violation on the same gate; worst margin EXACTLY 0 (tight) at the uniform
  blow-ups C5[2],C5[3] and several N=10 census graphs ⟹ any proof of BD-TARGET must be sharp.

## The residual gap — BD-TARGET does NOT split locally (honest)
BD-TARGET is a product `A·B ≤ N(N−row)` with `A=ℓ_f(M−μ)`, `B=(μ−m)`. Every tempting two-factor split was
refuted by an EXACT witness on the standing gate (so none can prove BD-TARGET):

| candidate split | meaning | status |
|---|---|---|
| S3  `ℓ_f(M−μ) ≤ N−row` i.e. `ℓ_f·M ≤ N` | upper spread ≤ deficit | **FALSE** (M(C7) edge (0,8): ℓ·M=25 > N=7) |
| S3' `M−μ ≤ N−row` (with S2 below) | | **FALSE at N=23** (M(Grötzsch) edge (0,1): M−μ=935/126−735094/184275 > 23−row) |
| S5a `ℓ_f(M−μ) ≤ N` | | **FALSE** (M(C9) edge (13,18)) |
| S5b `μ−m ≤ N−row` | | **FALSE at N=23** (M(Grötzsch) edge (21,22)) |
| S6  `row·(M+N−μ) ≤ N²` (prior STRONG) | | **FALSE at N=23** (M(Grötzsch) edge (21,22)) |

The ONLY local pieces that survive the full gate are:
- **S1** `M = Smax_f ≤ N` (in fact `S(v) ≤ N` for ALL v — 0 violation on the whole gate), and
- **S2** `ℓ_f(μ−m) ≤ N` (equivalently `row_f − ℓ_f·Smin_f ≤ N`; weaker than ROWSUM-O).

But S1∧S2 give only `bd ≤ (M−μ)·N`, and the complementary bound `M−μ ≤ N−row` (S3') is exactly the piece
that DIES at N=23. So BD-TARGET cannot be obtained by bounding the two BD-factors separately; it requires the
joint global control of `Smax_f` (and `Smin_f`) by the load deficit `N−row_f` — the SAME global odd-girth ≥ 5
anti-concentration content as ROWSUM-O. Indeed BD-TARGET ⟹ var_f≥0-conclusion ⟹ row_f ≤ N (ROWSUM-O for
nonunique f), so BD-TARGET is **strictly stronger** than the open ROWSUM-O.

## Sharper packaging — the exact quadratic q (sympy + Fraction verified)
Set `q(x) := ℓ_f·x² − ℓ_f·(N+a+b)·x + (N² + ℓ_f·a·b)` with a=Smin_f, b=Smax_f. Then IDENTICALLY (sympy):
- `N(N − ℓ_f·x) − ℓ_f(b−x)(x−a) = q(x)`   ⟹   **BD-TARGET ⟺ q(μ) ≥ 0**, μ=row_f/ℓ_f.
- Endpoint identities: `q(a) = N(N − ℓ_f·a)`,  `q(b) = N(N − ℓ_f·b)`.
- Vertex of q at `x* = (N+a+b)/2 ≥ b` (since b−a ≤ N) ⟹ q is **convex and DECREASING on [a,b]**.

Consequences (all EXACT-validated 0-fail, census≤10 + Myc N≤23 + blow-ups, 23287 nonunique rows, `_wf_qident.py`):
- BD-TARGET ⟺ q(μ)≥0 ⟺ `row_f² − ℓ_f(N+a+b)·row_f + (ℓ_f N² + ℓ_f² a b) ≥ 0` ⟺ `row_f ≤ smaller root of q`.
  This is literally a sharpened upper bound on row_f (and forces row_f ≤ N), confirming BD-TARGET ≥ ROWSUM-O.
- WHY every split dies: q decreases across [a,b] and crosses 0 BEFORE x=b, so the only endpoint that helps is x=a:
  `q(a)≥0 ⟺ ℓ_f·Smin_f ≤ N` ("S3-low") HOLDS (23287/23287). The other endpoint `q(b)≥0 ⟺ ℓ_f·Smax_f ≤ N` ("S3'")
  is FALSE (C5[1,5,2,2,5] N=15, f=(6,8): ℓ·b=20>15, q(b)=−75<0; yet q(μ)=8669/125>0 since μ=48/25≪b). So q(μ)≥0
  relies ENTIRELY on the actual μ being bounded away from b — no μ-free certificate exists.
- μ-FREE discriminant `DISC: ℓ_f(N+a+b)² ≤ 4(N²+ℓ_f a b)` (⟺ min_x q ≥ 0) is FALSE already on C5 at N=7 (0/22, `_wf_disc.py`).

## Status
PARTIAL. Rigorous reduction: variance inequality ⟸ [Bhatia–Davis, PROVED] + [BD-TARGET, OPEN], and BD-TARGET ⟺
the EXACT quadratic `q(μ)≥0` ⟺ `row_f ≤ smaller-root(q)` (sympy+Fraction proven identities). BD-TARGET
exact-validated 0-fail on the standing gate (incl. iterated-Mycielskian killer) but has no local/finite-depth
certificate: every two-factor split AND the μ-free discriminant are refuted by EXACT witnesses (N≤7..23), because
q is convex-decreasing on [a,b] and goes negative before x=b. BD-TARGET ⟹ ROWSUM-O, so it is ≥ ROWSUM-O in
hardness — the variance route is an exact REPACKAGING of the conjecture's odd-girth anti-concentration core, not a
weakening. Files: `_wf_var_reduce.py`, `_wf_qident.py`, `_wf_disc.py`, `_wf_s3fast.py`, `_wf_cu.py`,
`_wf_bhatia.py`, `_fanavg_var_gate.py`.
