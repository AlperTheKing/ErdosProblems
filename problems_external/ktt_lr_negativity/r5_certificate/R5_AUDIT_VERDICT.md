# Independent audit verdict — r=5 KTT positivity claims

Auditor: independent reviewer (Claude, Opus 4.8), 2026-07-22. All arithmetic
below is exact (`int` / `fractions.Fraction`); floating point was used only to
search, never to decide. Every number was produced either by a script I ran and
inspected or by code I wrote from the hive/BV definitions, then cross-checked
against **both** project engines (`engine/lr_hive.exe`, `engine/engineB_lrrule.py`).
I did not defer to the original agent; where the dossier and my runs agree the
number is stated once, where they would differ it is flagged.

Target: King–Tollu–Toumazet coefficient positivity (literature item LR(iv);
Gao arXiv:2101.00984; De Loera–McAllister Conj. 4.7) — **OPEN**. Two earlier
claims in this project were later proven FALSE (the "all r=4 vertex cones are
unimodular" census, and "C1: h*_1=0 forces a unimodular simplex"). Neither is
relied upon by anything audited here: every r=5 argument below is **edge/face-
local (ridge = codim-2 face on exactly two facets in the transverse 2D cone) or
a termwise BV-weight bound**, never vertex-cone-unimodularity and never an
`h*`-vector positivity claim. The refuted routes are correctly abandoned.

---

## 1. Bottom line (one sentence)

Every r=5 claim in the dossier reproduces exactly under independent
reconstruction and **none is falsified** — the dilation lemma is elementary and
correct, `e_4≥0` rests on a genuine (independently re-validated) cone-local BV
weight that is `≥1/9>0` termwise, and `e_2..e_6≥0` holds for full-dimensional
r=5 hives — but this is a **valid partial result with fixable
presentation/dependency gaps**, not a proof of KTT: it leaves `e_1` at full-
dimensional r=5 open, **all** non-full-dimensional r=5 hives open, and everything
below the top four coefficients for `r≥6` open, and its most intricate link
(`e_2` via a 513-cone realizability enumeration) is machine-verified rather than
transparently termwise.

---

## 2. Claim-by-claim verdict

### CLAIM 0 — Dilation / PIP scaling lemma: **VERIFIED**

Statement: for a rational period-one polytope `P`, pick `q` with `qP` a lattice
polytope; then `L_{qP}(n)=L_P(qn)`, so `e_k(qP)=q^k e_k(P)`; dilation preserves
the normal fan and every intrinsic normal cone and scales each `k`-face volume by
`q^k`, so applying the lattice-cone local formula to `qP` and dividing by `q^k`
recovers the identical cone-only local formula for `P`, signs agreeing.

Evidence: I read the proof in `../R5_LOCAL_METHOD_GATE.md` (lines 82–160). It is
elementary and correct: `R=qP-v0` is a lattice polytope in the intrinsic lattice
`M_W`; translation/scaling are integral and preserve the face poset, the spaces
`W_F`, the intrinsic normal cones and the fixed complement map, and give
`vol_Z(qF)=q^k vol_Z(F)`; comparing the `n^k` coefficient and dividing by `q^k`
is valid because the result is a genuine polynomial (period one, supplied by
Derksen–Weyman polynomiality — a cited external input, see §5). I confirmed the
period-one/degree facts on the two named examples by exact Lagrange
interpolation of engine-A counts: the half-integral hive `(2,2,1;4,3,2,1;
5,4,3,2,1)` has `L(0..6)=1,5,16,40,85,161,280`, interpolates to
`e=(1,2,17/12,1/2,1/12)` (degree 4 = dim Q, all coefficients >0), and the
degree-4 interpolant through `L(0..4)` re-predicts `L(5)=161,L(6)=280` — a real
period-one check. The lemma is `q`-agnostic; the largest denominator that can
occur is bounded by `max|det|=7` over 6-subsets of `N_5` (I reproduced the det
histogram; see §3), and `q=2` already exercises `e_k(qQ)=q^k e_k(Q)` fully.

### CLAIM 1 — `e_4 ≥ 0` for every full-dimensional r=5 hive: **VERIFIED**

The load-bearing fact is **not** the coset/kernel LP; it is that all 342 ridge-
cone BV weights `alpha` are `≥1/9>0`, whence `e_4 = alpha·Lambda ≥ 0` termwise
(`Lambda ≥ 0` are face volumes). I confirmed every link independently:

- **`alpha` is the genuine BV weight, not a vector fitted to hive witnesses.**
  `alpha5.alpha_pair` computes purely from the 2D transverse-cone geometry
  `(u,v)` via the closed BV form `1/4 − (C/12)(1/A+1/B)` (index-1) /
  `(A'+2B')/(6(A'+B'))` (index-2), and never sees a witness. I validated it
  against a **true 3D-lattice Ehrhart oracle it never saw**: `e_1 = Σ_edges
  alpha(u,v)·relative_length` reproduces the exact interpolated `e_1` on the unit
  cube (`3`, orthogonal cones, `alpha=1/4`) and the standard simplex (`11/6`,
  non-orthogonal cones, including the `alpha=13/36` weight). Both match exactly.
  (`alpha5` legitimately rejects transverse-cone index `≥3`; those never occur
  among the 342 hive ridge pairs — histogram `{index 1: 339, index 2: 3}`.)
- **`e_4 = alpha·Lambda` equals the independent lattice-count `e_4`.** The
  shipped `verify_r5_certificate.py` reports "all local identities = True" on all
  222 witnesses, where each witness `e_4` is taken from lattice-count Ehrhart
  interpolation, cross-checked against both LR engines. I additionally
  interpolated `e_4=13/36` for the smallest full-dim hive `(4,3,2,1;4,3,2,1;
  7,6,4,2,1)` directly from engine-A counts, matching the certificate value.
- **Every sampled `e_4 ≥ 0`.** On 40 independent dim-6 seeds (§3) the minimum
  at-risk coefficient over `e_1..e_4` is `13/36`; no negative `e_4` anywhere.
- The 222-witness / `rank(B)=120` / `dim ker(B)=222` balancing apparatus is
  **correct but not load-bearing**: since `mu=alpha` is already `≥1/9>0`,
  `mu−alpha=0` and `rowspace(B)` is never exercised. The report states this
  plainly ("This LP does not test the failure mode"). Not a defect.

### CLAIM 2 — rank-uniform top FOUR coefficients (`e_D,e_{D-1},e_{D-2},e_{D-3} ≥ 0`, all r): **VERIFIED**

- `e_D = vol_Z > 0` and `e_{D-1} = (1/2)Σ vol_Z(facets) > 0`: classical.
- `e_{D-2}` (codim-2): `uniform_codim2_gate_canonical.py` → PASS, proof bound
  `1/12`, observed min `1/9`, verified `r=3..20` (I re-ran it; index histogram
  `{1: …, 2: 3}` at every rank). The bound is structural: codim-2 cones are 2D
  spanned by two rhombus normals with entries in `{0,±1}` and `‖·‖²≤4`, so the
  `alpha` formula is bounded below by `1/12` for **all** r.
- `e_{D-3}` (codim-3): `uniform_codim3_gram_lemma.py` → PASS (min weight
  `1/264`), a finite Gram-class argument forced by `‖·‖²≤4`, off-diagonal in
  `[-4,4]`.
- **"Exactly four" is genuine, not a lucky pattern.** At codim-4 the BV cell
  weights stop being sign-definite: `r5_codim4_bv_independent_v2.py` exhibits 132
  negative saturated cells (min `−66821/2858240`), so the uniform termwise
  argument provably breaks at the fifth coefficient. Confirmed by running the
  script.

### CLAIM 3 — `e_2,e_3,e_4,e_5,e_6 ≥ 0` for full-dimensional r=5 hives (only `e_1` open in this class): **VERIFIED-WITH-CAVEAT**

- `e_3,e_4,e_5,e_6 ≥ 0`: verified as above (`e_5,e_6` classical; `e_4,e_3`
  termwise `alpha>0`). I re-confirmed `e_2..e_6` all strictly positive on the
  smallest full-dim hive (`e=(1,157/60,949/360,4/3,13/36,1/20,1/360)`, degree 6
  re-predicting `L(7)=2640,L(8)=4719`) and on 40 dim-6 seeds (0 negatives).
- **CAVEAT on `e_2` (codim-4).** `e_2 ≥ 0` is the one sub-claim whose proof is
  **not termwise** and rests on a machine realizability enumeration. I re-ran the
  canonical `r5_codim4_all_rankpreserving_supersets_v2.py` end-to-end (exit 0):
  132 negative saturated cells and 491 negative subdivision cells exist, but all
  **513 realizable pointed full cones are strictly positive, min `739/86400`**,
  reproducing the report and both referees exactly. The positivity of `e_2` is
  therefore **conditional on the completeness of the coverage enumeration**
  (steps 4–5 of `../R5_CODIM4_LOCAL_POSITIVITY_REPORT.md`: that the 96 minimal
  forced rank-4 cones plus their span-direction supersets truly contain every
  realizable codim-4 hive-face normal cone, via exact Farkas slack-closure). That
  completeness argument I re-ran but did not re-derive from first principles; it
  is the least transparent link in the r=5 chain and the natural place a hidden
  gap could live. Marked VERIFIED-WITH-CAVEAT for that reason, not because any
  computation disagreed.

No claim is UNVERIFIED and **no claim is BROKEN.** (One non-canonical script,
`r5_codim4_all_rankpreserving_supersets.py`, aborts on an index-2 cell; it is an
intentionally-preserved superseded driver, documented as such in the codim-4
report, and superseded by the `_v2` driver that passes.)

---

## 3. Exact independent replication numbers (this audit)

| Check | Population | Result |
|-------|-----------|--------|
| Constructor/engine calibration (engine A + engine B) | 40 dim-6 seeds ×7 dilations + 65 nonzero mixed triples ×6 | 0 mismatches vs interpolated polynomials; anchors reproduced |
| Normal atlas `N_5` | all 30 rhombus rows | 27 distinct primitive normals, entries `{-1,0,1}`, 9 antipodal pairs (18 up-to-sign); `342 = C(27,2)−9` ridge types |
| 6-subset `|det|` histogram | `C(27,6)` nonsingular subsets | `{1,2,3,4,5,6,7}`, **max |det| = 7** (⇒ max vertex denominator ≤ 7) |
| Half-integral hive `(2,2,1;4,3,2,1;5,4,3,2,1)` | engine A `L(0..6)` | dim Q = 4, `e=(1,2,17/12,1/2,1/12)`, all >0; deg-4 re-predicts `L(5),L(6)` |
| Smallest full-dim hive `(4,3,2,1;4,3,2,1;7,6,4,2,1)` | engine A `L(0..8)` | dim Q = 6, `e=(1,157/60,949/360,4/3,13/36,1/20,1/360)`, all >0; deg-6 re-predicts `L(7)=2640,L(8)=4719` |
| **BV weight agreement (genuine-weight test)** | true 3D Ehrhart `e_1`: cube + standard simplex | `alpha·length` = interpolated `e_1` **exactly** (`3` and `11/6`), orthogonal + non-orthogonal cones |
| `verify_r5_certificate.py` | e_4 certificate | PASS: rank(B)=120, ker=222, 222 witnesses span ker, all `Lambda∈ker(B)`, **all local identities True**, alpha min `1/9` all>0, mu valid |
| `run_r5_lp.py` | e_4 coset LP | **FEASIBLE**, constructive point `mu=alpha`, `mu_min=1/9`, `M·mu=a`, `mu−alpha=0` (rowspace unused) |
| `uniform_codim2_gate_canonical.py` | r = 3..20 | PASS, proof bound `1/12`, observed min `alpha=1/9` at every rank |
| `uniform_codim3_gram_lemma.py` | Gram superset | PASS (min `1/264`) |
| `r5_codim4_bv_independent_v2.py` | 17550 four-tuples | 132 negative saturated cells (min `−66821/2858240`) — BV **not** sign-definite at codim-4 |
| `r5_codim4_all_rankpreserving_supersets_v2.py` | realizable cones | 96 minimal rank-4 cones → **513 pointed full cones, 0 negative, 0 zero, min `739/86400`** |
| Negative-coefficient scan (mine) | 40 dim-6 seeds (engine A) + 65 mixed nonzero triples (engine B), dims 0–6 | **0 negative coefficients**; min `e_1=157/60`; min at-risk `e_1..e_4 = 13/36` |

LP feasibility: the only LP actually solved (`e_4`) is **trivially FEASIBLE**
(`mu=alpha≥1/9`); the balancing rowspace is never binding. Dilation checks: the
lemma’s `e_k(qQ)=q^k e_k(Q)` identity and `L_{qQ}(n)=L_Q(qn)` are elementary and
were exercised at `q=2` on the half-integral family (dossier reports `q` up to 7
in the atlas; consistent with my `max|det|=7`).

Pinned certificate SHAs (from the report, not re-hashed here):
`e4_certificate.json` = `752ea056…`; `R5_CERTIFICATE.json` = `0299438e…`;
r4 certificate = `c13f8f47…`.

---

## 4. Precise remaining open set + minimum coefficient found

Still **OPEN** (no proof; no counterexample found in any scan):

1. **`e_1` (linear coefficient) at full-dimensional r=5.** Its faces are edges
   with 5-dimensional normal cones; the BV weight there is **not sign-definite**,
   and the codim-5 machinery (≥557 edge types generated by up to 18 of the 27
   normals; `B_1`; its kernel; a spanning witness set; the coset LP) was **not
   built**. Probe minimum found: `e_1 = 157/60 ≈ 2.617`, attained at the smallest
   full-dim hive and reproduced by me on the 40 dim-6 seeds; `e_1` grows with
   volume in every sample. No approach to zero, but no bound.
2. **All non-full-dimensional r=5 hives (dim Q < 6)** below the top-four
   coefficients. The dimension drop happens on Weyl-chamber walls; Horn
   factorization provably does **not** reach them — e.g. `(4,3,3,1;4,2,1,1;
   6,5,4,2,2)` has dim Q = 3 with all 142 essential Horn inequalities strict
   (`../R5_LOWERDIM_HORN_GAP.md`). Genuinely open, correctly listed as such.
3. **Everything below the rank-uniform top four for `r ≥ 6`.**

Minimum genuinely-at-risk low-order coefficient found anywhere in the probe:
**`13/36 ≈ 0.361`** (an `e_4` at dim 6). In the Reeve dimension (dim 3) the
minimum `e_1` seen is `11/6`; over full-dim (dim 6) the minimum `e_1` is
`157/60`. Every at-risk coefficient stays a solid positive distance from 0; no
Reeve-type near-degeneracy was found (hive polytopes are "fat" — small point
count forces small volume, the opposite of the Reeve regime).

Full KTT (a single statement over all `r` at once) is **not** implied by any
finite set of these per-`r` results; a rank-uniform theorem (UHTE, or an
equivalent hive-specific positive decomposition) would be required.

---

## 5. Does "Buch removed" hold? — **YES (VERIFIED)**

Buch's unproved remark "hive corners are integral for `n ≤ 4`" was a hypothesis
of the original r=4 certificate route. It is genuinely **dissolved**, two ways:

- **Empirically moot at r=4:** every r=4 hive tested (project + referees, >8·10⁶
  vertices incl. exhaustive parts ≤5) is a lattice polytope, so `q=1` and the
  dilation is trivial there.
- **Removed as a dependency:** `R4_EDGE_POSITIVITY_CERTIFICATE.md` proves exactly
  "every 3-dim **lattice** polytope with the 15 r=4 normals has `a_1 ≥ 0`." For
  **any** hive `H`, `qH` is such a lattice polytope, so `a_1(qH) ≥ 0`, and the
  PIP scaling lemma (Claim 0) gives `a_1(H) = a_1(qH)/q ≥ 0` with no integrality
  hypothesis on `H`. The lemma is proved and I checked it; the r=4 edge
  certificate’s scope is as stated. Buch is no longer needed as an input.

Caveat inherited from the r=4 audit: this rests on (i) the r=4 edge certificate
replay (independently validated in `../r4_reeve/AUDIT_VERDICT.md`) and (ii) the
cited BV/McMullen locality theorem (not reproved on disk — see below). Those are
citable external inputs, not gaps in the "Buch removed" argument itself.

**Load-bearing uncited/unreproved external inputs (both r=4 and r=5), same as
the r=4 audit:** the hive rule + saturation (Knutson–Tao); polynomiality of
stretched LR coefficients (Derksen–Weyman); and the McMullen / Berline–Vergne
local Ehrhart formula (BV 2007; Ring–Schürmann 2020 for the lattice-tile form).
These are cited theorems, correctly applied (verified empirically to high
confidence), but neither reproved nor machine-checked here.

---

## 6. What is needed to make this submittable — ranked

The cleanest submittable unit is the **robust, termwise core**; the intricate
`e_2` enumeration and everything open should be quarantined out of the headline.

**A. The finished r=4 theorem (first nontrivial case of KTT).** Highest
readiness. From `../r4_reeve/AUDIT_VERDICT.md`, in order:
1. **Commit to the structural (Route B) proof and relegate the certificate
   route.** Route B removes both Buch and the 72-witness apparatus and gives
   `a_1 > 0` strictly. Shipping two "canonical" narratives will draw a reject.
2. **Prove or precisely cite the 2D BV constant-term formula** `alpha = 1/4 −
   (C/12)(1/A+1/B)` (Berline–Vergne 2007 / Ring–Schürmann Def. 1 / Eq. (1)); the
   elementary `alpha ≥ 1/12` bound (`C ≤ min(A,B)`) is then self-contained.
3. **Fix `uniform_codim2_gate.py`** (rank-3 guard bug: `assert minimum is not
   None` fires when no codim-2 pairs exist); the canonical variant already
   passes, so this is cosmetic but blocks reproducibility as committed.
4. **Priority/literature check** vs Coquereaux–Zuber (arXiv:1706.02793, SU(n)
   n=2..6 hive Ehrhart), KTT (SLC 54A 2006), Rassart — confirm the length-≤4
   positivity theorem is unpublished before any novelty claim.
5. **Write out the trivial steps** (`a_0=1`, half-boundary `a_2>0`, dim ≤ 2 via
   point/segment/Pick) that are currently asserted.

**B. The r=5 partial theorem, robust part first.** Add to a paper only what is
transparent:
6. **State and prove the rank-uniform top-four theorem for all r** (`e_D=vol`,
   `e_{D-1}=½ surface`, codim-2 `≥1/12`, codim-3 `≥1/264`) — this is the strong,
   clean, genuinely uniform contribution and the natural headline generalization.
   Write the Gram-class finiteness argument (`‖·‖²≤4`) explicitly.
7. **Write the PIP scaling lemma as a self-contained proposition** (it is the
   paper’s own elementary contribution; §Claim 0 above confirms it) so the
   rational-polytope passage needs no rational-BV theory or denominator bound.
8. **Include `e_4≥0` and `e_3≥0` at r=5** as termwise corollaries (min `1/9`,
   `1/264`) — low risk. Present `e_4`’s 222-witness LP honestly as *not*
   load-bearing (`mu=alpha`), or drop it.
9. **For `e_2` at r=5: either make the coverage enumeration rigorous or omit it.**
   As it stands it is a 513-cone computer-assisted result whose completeness
   (steps 4–5, Farkas slack-closure over 96→513 cones) is not written as a
   theorem with a proof — only as a script. For a submission, either (a) prove
   steps 4–5 rigorously and ship the enumeration as certified supplementary data
   with a second independent implementation, or (b) **omit `e_2`** and claim only
   top-four-uniform + `e_4,e_3` at r=5. Recommend (b) for a first paper.
10. **State scope with surgical honesty:** proved = KTT for length ≤ 4, and for
    full-dimensional r=5 the coefficients `e_3..e_6` (and `e_2` iff (a) above);
    **open** = `e_1` at r=5, all non-full-dimensional r=5, and `r≥6` below the
    top four; the method proves fixed-codimension coefficients only and does
    **not** imply full KTT.

Not needed / do not attempt to headline: a full-KTT claim; any per-`r` cascade
presented as a proof of the conjecture; any reliance on vertex-cone
unimodularity or `h*`-positivity (both refuted in this project).

---

## 7. Exact replay commands

From `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r5_certificate`:

```powershell
python verify_r5_certificate.py            # e_4 cert -> PASS, alpha min 1/9, 222 witnesses span ker B
python run_r5_lp.py                        # e_4 coset LP -> FEASIBLE, mu=alpha, mu_min 1/9
```

From `E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity`:

```powershell
python r5_local_gate.py                             # N_5 det histogram, PIP scaling gate
python uniform_codim2_gate_canonical.py             # codim-2, bound 1/12, r5 min 1/9, r=3..20
python uniform_codim3_gram_lemma.py                 # codim-3, min 1/264 -> PASS
python r5_codim4_bv_independent_v2.py               # 132 negative codim-4 cells (not sign-definite)
python r5_codim4_all_rankpreserving_supersets_v2.py # 513 pointed cones, 0 negative, min 739/86400
python r5_lowerdim_horn_factorization_gap.py        # strict-Horn dim-drop (non-full-dim gap)
```

Engine calibration (both print the same LR coefficient; note engine B needs
**comma-separated** partitions):

```powershell
engine\lr_hive.exe "2,2,1" "4,3,2,1" "5,4,3,2,1"                 # -> 5
python engine\engineB_lrrule.py "2,2,1" "4,3,2,1" "5,4,3,2,1"   # -> 5
engine\lr_hive.exe "4,3,2,1" "4,3,2,1" "7,6,4,2,1"              # -> 8  (smallest full-dim hive, L(1))
```

Independent BV-weight-vs-true-Ehrhart check (this audit; cube -> e_1=3,
simplex -> e_1=11/6, both matching `Σ alpha·length`) is a ~40-line script using
`alpha5.alpha_pair` + `scipy.spatial.ConvexHull` for combinatorics with exact
rational normals/lengths/counts.

---

*End of verdict.*
