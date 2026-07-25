# Independent audit verdict — claimed r = 4 KTT positivity theorem

Auditor: independent reviewer (Claude, Opus 4.8). All arithmetic below is exact
(`int` / `Fraction`); floating point was used only to search, never to decide.
Every number in this document was produced by code written from the hive
definition and cross-validated against both project engines, not taken from the
author's artifacts. My scripts are persisted at
`problems_external/ktt_lr_negativity/r4_reeve/audit_final/`.

---

## 1. Bottom line (one sentence)

The statement is **true** and the proof strategy is **valid**, but what is on
disk is **a correct theorem with a valid, independently‑reproduced proof that is
not yet self‑contained** — it rests on the published Berline–Vergne / McMullen
local Ehrhart formula (cited, never reproved or machine‑checked), and the
certificate variant additionally leans on Buch's unproved one‑line integrality
remark; these are fixable gaps, not errors, so this is **a proof with fixable
gaps, not a finished stand‑alone proof and not a non‑proof.**

---

## 2. Resolution of the vertex‑cone dispute

**Codex is right; the earlier 589,487,256‑polytope scan is wrong.**

I built the hive polytope for the disputed triple `lam = mu = (12,8,4,0)`,
`nu = (18,14,10,6)` from Buch's border labels, enumerated its vertices exactly,
and found: **11 vertices, all integral**, and at the vertex `(26,38,32)`
(coordinates `(h11,h12,h21)`) exactly six rhombus rows are tight but only three
are facet‑defining, with primitive tangent rays `(0,1,1),(1,0,1),(1,1,0)` of
determinant **2**. Independent confirmation that these are genuine edges:
`(26,38,32)+2·(0,1,1)`, `+2·(1,0,1)`, `+2·(1,1,0)` are all vertices of the same
polytope. Both engines and my lattice count give `c = 50`, so the polytope is
nonempty. **Non‑unimodular (multiplicity‑2) vertex cones therefore occur in
r = 4 hive polytopes**, and the "all simple vertex cones are unimodular" claim of
the 589M scan is false.

Why the earlier scan was wrong (this is identified, not guessed, and matches the
replication and referee findings): `vertex_local.py` / `vcheck.cpp` classified a
vertex as *simple* by counting **distinct tight rows** (`== 3`). The right test
is **exactly three facets / three tangent‑cone extreme rays**. A vertex like
`(26,38,32)` has redundant tight rows (three coordinate inequalities implied by
the three triangle inequalities), so it was silently filed as "non‑simple" and
skipped; every non‑unimodular cone lives in exactly that discarded bucket.
Hence "854,321,098 vertices, all unimodular" is a true statement about a proper
subclass and carries no information about the vertices that matter.

**This kills the "all vertex cones unimodular" route (and any Reeve‑type
`V ≤ m_max` bound), but touches neither proof on disk**, because both are
edge‑local, not vertex‑local: in a 3‑polytope every edge is a ridge lying in
exactly two facets regardless of vertex simplicity, and I verified `B·Λ = 0` and
`Λ·μ = a1` on this very non‑simple polytope (a1 = 7, exercised on its three
index‑2 edges). Vertex integrality itself is unaffected by the scan's bug.

---

## 3. Proof‑chain link status

There are two proofs in the directory. I audit both.

### Route A — the certificate route (`R4_KTT_THEOREM.md`, `R4_EDGE_POSITIVITY_CERTIFICATE.md`), the chain named in the mandate

| Step | Claim | Status | Evidence |
|------|-------|--------|----------|
| A0 | Reduction: nonzero stretch ⇒ Ehrhart polynomial of a ≤3‑dim hive polytope; only `a1` can be negative; `6a1 = 3(c+i) − V`. | **VERIFIED** | `6a1 = 3(c+i) − V` held on **502/502** genuine dim‑3 hives and on the mandated triple (a1=7, c=50, i=12, V=144). |
| A1 | Buch: r = 4 hive polytopes are **lattice** polytopes. | **VERIFIED‑WITH‑CAVEAT** | Fact holds on every case I and the referees tested (0 non‑integral vertices in >8×10⁶ vertices, incl. exhaustive parts ≤ 5). But the source (Buch, *Saturation Conj.*, remark after Ex. 2) gives **no proof** — "it is not hard to show." As a *proof step* it imports an unproved literature assertion. See §5. |
| A2 | Dimensions ≤ 2 are Ehrhart‑positive (point / segment / Pick). | **VERIFIED** | Standard; stated, not written out. |
| A3 | McMullen/BV local formula: `a1(P) = Λ(P)·α`, `α` fixed per unordered facet‑normal pair (99 edge types). | **VERIFIED‑WITH‑CAVEAT** | I reconstructed the edge functional and confirmed `a1 = Λ·α` **exactly on 114 fresh hives** (§3, Route B). It is an *imported theorem*; the supplied checker does **not** verify it — see the caveat in A5/§5. |
| A4 | Facet closure ⇒ `B·Λ(P)=0`; `rank(B)=27`, `dim ker B = 72`. | **VERIFIED** | My own B (natural‑sign `prim(nᵢ×nⱼ)`, +u on facet i, −u on facet j): `rank(B)=27`, `ker=72`, and **all 72 witness edge vectors lie in ker(B)**. |
| A5 | 72 witnesses span `ker B`; `μ ≥ 0`; `M·μ = a`. | **VERIFIED** | `rank(M)=72`, `rowspan(M)=ker(B)` (72+27=99, witnesses in ker), `μ` is a 99‑vector with min 0 and **no negatives**, `M·μ = a` exactly, and each witness `a1 = interp(L₀…₅) = Λ·μ`. |
| A6 | Conclusion `a1(P)=Λ(P)·μ ≥ 0` for every r = 4 hive polytope. | **VERIFIED** | Coset argument is valid (`μ−α ∈ ker(M)=rowspan(B) ⟂ Λ(P)`; value of `α` never needed). Out‑of‑sample: `Λ·μ = a1` on **91/91** fresh dim‑3 hives, 0 mismatches. |

**Net for Route A:** the linear‑algebra spine (A4–A6) is fully reproduced and
correct; the two links it *cannot* stand without, A1 (Buch) and A3 (BV
locality), are imported and — in the case of A1 — imported from a source that
proves nothing.

### Route B — the structural route (`R4_STRUCTURAL_PROOF.md` + `UNIFORM_CODIM2_POSITIVITY.md`), declared "canonical" by `R4_THEOREM_REPLACEMENT_NOTE.md`

| Step | Claim | Status | Evidence |
|------|-------|--------|----------|
| B1 | Rational‑polytope scaling removes the lattice hypothesis for the codim‑2 coefficient (`L_{qP}(n)=L_P(qn)`, coeffs scale by `q^k`). | **VERIFIED** | Standard and valid; this genuinely eliminates the Buch dependency (A1) for `a1`. |
| B2 | Every r = 4 edge coefficient `α ≥ 1/12`; atlas min `1/9`, max `7/18`, the 3 index‑2 pairs `= 5/18`. | **VERIFIED** (for r = 4) | Computed all 99 `α` from the §3–4 Gram formula: min `1/9`, max `7/18`, index‑2 `= 5/18`; and `a1 = Λ·α` **exactly on 114 hives** (incl. the disputed hive, which exercises the index‑2 value). So `a1 = Σ α·len ≥ (1/9)·(total edge length) > 0`. |
| B3 | The BV constant‑term formula `1/4 + (1/12)(⟨x,y⟩/⟨x,x⟩ + ⟨x,y⟩/⟨y,y⟩)` for a 2‑D unimodular feasible cone. | **VERIFIED‑WITH‑CAVEAT** | Empirically exact: reproduces `a1` on 114 hives and gives `1/4` on the unit cube (a1=3 = 12×¼). It is **asserted/cited (Berline–Vergne, Ring–Schürmann), not derived** in the writeup. |
| B4 | Rank‑*uniform* version (`α ≥ 1/12` for all r) + its finite audit `uniform_codim2_gate.py`. | **VERIFIED math / BROKEN script** | Math reproduced independently: ranks 4–20 all give min `α = 1/9`, all `α ≥ 1/12`. But the committed **`uniform_codim2_gate.py` aborts with `AssertionError` at rank 3** — rank 3 has 0 nonparallel pairs (codim‑2 not applicable), `minimum` stays `None`, and line 102 `assert minimum is not None …` fires before any output, so the documented `PASS … observed_min=1/9` is **not produced by the committed script**. This is a one‑line guard bug, not a math hole; the r = 4 corollary is independent of it. |

**Net for Route B:** for r = 4 it is a cleaner and stronger proof (gives `a1 > 0`
strictly, needs neither Buch nor the 72‑witness apparatus), and its r = 4
content is fully verified here; but its stated foundation is a rank‑uniform
theorem whose only shipped audit script does not run to completion, and its one
analytic input (B3) is asserted rather than proved.

Note on my `cert_verify.py`: it prints `witness_edge_vectors_in_ker(B): 72 FAIL`
because that script sign‑canonicalizes `prim`; with the natural‑sign convention
(used in `out_of_sample.py`) all 72 witnesses lie in `ker(B)` and
`rowspan(M)=ker(B)`. The mismatch is a normalization convention, not a defect.

---

## 4. Independent replication numbers

Mandated validation gate — my constructor vs **both** engines: **700 triples,
537 nonzero, 0 mismatches** (constructor reproduces 18 rows / 15 distinct
primitive normals / 99 nonparallel pairs from the definition; the mandated
triple gives 50 from engine A, engine B, and my count).

| Test | Population | Result | Mismatches |
|------|-----------|--------|-----------|
| Direct theorem (`6a1 = 3(c+i) − V`, own counter) | 502 genuine dim‑3 hives, weights ≤ 40 (+ ~1300 lower‑dim) | 0 negative coefficients; identity held every time | **0 / 502** |
| Certificate out‑of‑sample `Λ·μ = a1` (a1 from independent interpolation) | 91 **fresh** dim‑3 hives (not among the 72), weights ≤ 20 | `Λ·μ = a1` and `B·Λ = 0` every time; 0 negative a1; 0 non‑integral vertices; min a1 = **11/6** | **0 / 91** |
| Structural `a1 = Λ·α` (Gram‑formula atlas) | 113 fresh dim‑3 hives + the disputed hive, weights ≤ 18 | `a1 = Λ·α` every time; all 99 α ∈ [1/9, 7/18] | **0 / 114** |
| Certificate linear algebra (own code) | the artifact | `rank B=27`, `ker=72`, `rank M=72`, `rowspan M = ker B`, `μ` min 0 / no negatives, `M·μ = a`, each witness `a1 = interp = Λ·μ` | **0** |
| Edge extractor validation | 72 recorded witnesses | reproduced every recorded 99‑edge vector exactly | **0 / 72** |

Total non‑witness polytopes on which `Λ·μ = a1` (or `a1 = Λ·α`) was checked and
held: **205**, with **0** mismatches; total dim‑3 hives on which the theorem
`a1 ≥ 0` was directly verified: **>600**, **0** negatives. This is consistent
with (and independent of) the referees' larger runs (referee 2: 34.5M exhaustive
triples).

---

## 5. External‑dependency status

Two literature inputs are load‑bearing and neither is proved on disk.

**Buch integrality (Route A only).** The size convention is correct — r = 4 =
Buch's n = 4 (confirmed four ways, incl. the exact 18‑row / 15‑normal / 99‑pair
match from the definition and the first failure at n = 5). But the *only*
justification for "corners are integral for n ≤ 4" is the four words "it is not
hard to show" in an expository paper — **no proof, sketch, or citation**.
Integrality does **not** follow from the constraint matrix alone (the r = 4
rhombus arrangement has non‑unimodular row triples: of C(18,3)=816 triples, 468
have |det|=1, 48 have |det|=2, 1 has |det|=4). A self‑contained writeup that
keeps Route A **must** supply this proof. **Route B removes this dependency
entirely** via the rational‑scaling argument (B1), which is the strongest reason
to prefer it.

**McMullen / Berline–Vergne locality (both routes).** That `a1` is a linear
functional of the edge lattice‑length vector with a coefficient depending only
on the edge's transverse cone is the published local Ehrhart formula
(Berline–Vergne 2007; McMullen; Ring–Schürmann 2020). Its **existence** is a
theorem one may cite. Its **correct application here** I verified empirically to
high confidence (`a1 = Λ·α` exactly on 114 independent hives; cube ↦ ¼), and
referee 2 independently rebuilt the BV functional and agreed (min 1/9). But the
supplied checker `q2_verify_r4_certificate.py` verifies **only the linear‑algebra
scaffolding** (rank B, span, μ ≥ 0, M·μ = a); it does **not** verify the
locality step. A reader who sees `PASS` could wrongly believe the theorem is
machine‑checked end to end — **it is not.** A self‑contained writeup must either
cite BV/Ring–Schürmann precisely for the 2‑D constant‑term formula (B3) or
reprove it; the elementary `α ≥ 1/12` bound (`C ≤ min(A,B)` ⇒ `C(1/A+1/B) ≤ 2`)
is then a clean self‑contained step **given** that formula.

---

## 6. Novelty (with citations)

- **The target conjecture is open.** Coefficient‑nonnegativity of the stretched
  LR polynomial (King–Tollu–Toumazet; the "LR(iv)" item) is open in general —
  Gao, *Newell–Littlewood numbers* (arXiv:2101.00984); De Loera–McAllister
  Conj. 4.7. What is *proved* in the literature is a different property:
  **polynomiality** (Derksen–Weyman via quiver semi‑invariants; Rassart,
  arXiv:math/0308101), and a **different KTT conjecture** — the value‑2 case
  `c=2 ⇒ P(N)=N+1` (Chindris/others, "Geometric Proof of a Conjecture of King,
  Tollu, and Toumazet," arXiv:1505.06551, where the polytope is a segment).
  Neither addresses coefficient positivity.
- **Not a corollary of any general dimension theorem.** Ehrhart positivity is
  **false** for general lattice — even smooth — 3‑polytopes (Castillo–Liu–Nill–
  Paffenholz, *Smooth polytopes with negative Ehrhart coefficients*, JCTA 160
  (2018), arXiv:1704.05532; `BRIDGE_LEMMA.md` reproduces a family with `a1<0`).
  So the r = 4 result genuinely uses the fixed rhombus normal set; it is the
  **first nontrivial case** of KTT positivity (dim ≤ 2 is automatic, dim 3 first
  occurs at r = 4).
- **Coquereaux–Zuber** (*From orbital measures to Littlewood–Richardson
  coefficients and hive polytopes*, AIHPD 2018, arXiv:1706.02793) is the closest
  prior art: they compute hive‑polytope Ehrhart polynomials for SU(n),
  n = 2…6, and connect stretched LR coefficients to Ehrhart polynomials. Their
  treatment is **example‑driven**; I found **no general proof of positivity for
  all length‑≤4 triples** attributable to them, and they (and the CLNP line)
  document that Ehrhart coefficients turn negative at higher rank — consistent
  with a small‑rank positivity phenomenon. **A dedicated priority check against
  Coquereaux–Zuber and the KTT/Rassart papers is required before any novelty
  claim** (see §7.5): the *method* here (BV local formula + fixed normal set +
  a uniform `α ≥ 1/12` edge‑coefficient bound) is in the spirit of the
  Ehrhart‑positivity program (Berline–Vergne; McMullen; Ring–Schürmann;
  Castillo–Liu survey), and its novel piece is the hive‑specific uniform bound.

**Assessment:** if the priority check comes back clean, this is a genuine new
result — the first proof of KTT positivity for all triples of length ≤ 4 — but
its interest is bounded: it is the smallest open case, and the same method does
**not** extend to positivity of the lower coefficients at higher rank (it proves
only the codimension‑two coefficient).

---

## 7. Ranked to‑do before this could be submitted anywhere

1. **Decide on one proof and delete/relegate the other.** The directory ships
   two "canonical" narratives (`R4_KTT_THEOREM.md`: certificate is the proof;
   `R4_THEOREM_REPLACEMENT_NOTE.md`: structural is now canonical, certificate
   "not load‑bearing"). A referee seeing both will reject on presentation.
   **Recommendation: submit Route B** (structural) — it removes the Buch gap and
   the 72‑witness apparatus, and its r = 4 content is fully verified here.
2. **Prove or precisely cite the BV 2‑D constant‑term formula (B3).** Neither
   writeup derives `α = 1/4 − (C/12)(1/A+1/B)` from Berline–Vergne's definition.
   A reviewer will demand a derivation or an exact citation (BV 2007, or
   Ring–Schürmann Def. 1 / Eq. (1)). It is empirically correct (114 hives, cube).
3. **Fix `uniform_codim2_gate.py`.** It aborts at rank 3 (`assert minimum is not
   None` on the not‑applicable rank), so the documented `PASS observed_min=1/9`
   is not reproducible as committed. Add the skip for ranks with no codim‑2
   pairs. (The math is fine: ranks 4–20 give min 1/9; the compact index‑2 form
   `1/4 − c/(12q)(1/A+1/B)` agrees with the §4 formula on every valid pair
   because index‑2 pairs always have A=B.)
4. **If Route A is retained instead:** (a) supply a real proof (or exact
   machine certificate) of Buch's n ≤ 4 corner‑integrality — do not rest on "it
   is not hard to show"; and (b) make the checker actually verify the locality
   step (add the α atlas and check `a1 = Λ·α` on the witnesses), so `PASS`
   means what a reader will assume it means.
5. **Priority / literature check** against Coquereaux–Zuber (arXiv:1706.02793),
   King–Tollu–Toumazet (SLC 54A, 2006), and Rassart, to confirm the length‑≤4
   positivity theorem is unpublished before claiming novelty.
6. **Write out the dim ≤ 2 cases** (point / segment / Pick) and the `a0=1`,
   `a2>0` (half boundary area), `a3>0` steps explicitly; they are asserted now.
7. **State scope honestly:** this proves only the codimension‑two coefficient
   (hence the full r = 4 theorem, since dim ≤ 3), and does **not** extend to
   positivity of lower coefficients at higher rank.

---

## 8. Exact replay commands

From the repository root (`E:/Projects/ErdosProblems`):

```powershell
# Author's certificate checker (Route A linear-algebra spine)
python problems_external\ktt_lr_negativity\r4_reeve\q2_verify_r4_certificate.py
#   -> PASS
#      certificate_sha256=c13f8f47dcaa907f4e80616cb88f847d4790113938227ede26c6fe11b6ce0148
#      witnesses=72 witness_rank=72 balance_rank=27 kernel_dimension=72 min_mu=0
#      r4_normal_set=PASS

# Author's structural gate (Route B) -- CURRENTLY ABORTS at rank 3 (guard bug)
python problems_external\ktt_lr_negativity\uniform_codim2_gate.py
#   -> AssertionError (line 102); ranks 4..20 give min alpha = 1/9 once the
#      not-applicable rank-3 case is skipped.

# Engines (calibration): both print 50
problems_external\ktt_lr_negativity\engine\lr_hive.exe "12,8,4,0" "12,8,4,0" "18,14,10,6"
python problems_external\ktt_lr_negativity\engine\engineB_lrrule.py "12,8,4,0" "12,8,4,0" "18,14,10,6"
```

My independent audit scripts (persisted, run with that directory as CWD):

```powershell
cd problems_external\ktt_lr_negativity\r4_reeve\audit_final
python validate.py 700 5        # constructor vs both engines: 700/0 mismatches, 537 nonzero
python scan.py 2000 10          # direct theorem: 0 negative coeffs, identity holds
python cert_verify.py           # certificate linear algebra (sign-canonical B; see note in §3)
python edges.py                 # edge extractor: 72/72 recorded vectors reproduced
python out_of_sample.py 500 20  # fresh hives: Lambda.mu = a1, 0 fails, min a1 = 11/6
python alpha.py                 # alpha atlas [1/9,7/18], a1 = Lambda.alpha, 0 fails
```

---

*End of verdict.*
