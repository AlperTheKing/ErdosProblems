# A1-Proper Slack Dictionary + Lean Build Design (GPT-Pro MAIN, 2026-07-06, Claude-verified)

Companion to A1PROPER_SIX_CONE_DESIGN_GPTPRO.md. This is the COMPLETE buildable Lean design.
Reuses PolyCert.ConeCert / ConeCert.sound directly (thin A1 wrapper; no new algebra engine).

## 1. Cleared defect (the wrapper target)
D_j := (75 + 2N)·η − 3N·X_j.   D_j ≥ 0  ⟺  X_j ≤ (25/N + 2/3)·η   [since 25/N + 2/3 = (75+2N)/(3N)].
The ConeCert for canonical mask j proves  D_j = P_0 + Σ_r P_r·Σ_r  (P_0,P_r Bernstein-nonneg; Σ_r a valid A1 slack).

## 2. A1 slack dictionary (FIXED enum — Codex + Lean must agree; every cone term cites one)
```lean
inductive A1SlackId
| eta                     -- η ≥ 0           ← A1SlackHypotheses.etaNonneg
| sigma (sid : Nat)       -- σ(S_sid) ≥ 0    ← A1SlackHypotheses.sigmaNonneg  (bundle carries literal switch set S_sid)
| nuK (sid : Nat)         -- νK(S_sid) ≥ 0   ← CompletedSwitchCert.sound + GammaMinimalConnected (flipBConnected=true); OMIT if unused
| atomNonneg (aid : Nat)  -- row-atom mass≥0 ← RowDBFactsAll5.atomDBSound
| closureResidual (rid : Nat) -- PMTS/closure residual ≥ 0 ← checkClosureResidual rid = true → 0 ≤ residualVal rid
deriving DecidableEq, Repr
```
No arbitrary unnamed slacks. Each closureResidual has a concrete checked value + soundness lemma.

## 3. Canonical masks (bit-code; VERIFIED 30/30 by Claude cross-check, 6 rotation-orbits)
M0=1={0}(sz1)  M1=3={0,1}(sz2adj)  M2=5={0,2}(sz2dist2)  M3=7={0,1,2}(sz3consec)  M4=11={0,1,3}(sz3noncon)  M5=15={0,1,2,3}(sz4).
code(A) = Σ_{i∈A} 2^i. Full code→(id,rot) table in problems/23/writeup/a1_mask_symmetry_table.json (schema v2_MAIN_authoritative).
```lean
def maskCode (A : Finset (Fin 5)) : Nat := ∑ i in A, 2 ^ i.val
def canonicalMaskCode : Fin 6 → Nat | 0=>1 | 1=>3 | 2=>5 | 3=>7 | 4=>11 | 5=>15
def maskOfCode (code : Nat) : Finset (Fin 5) := Finset.univ.filter (fun i => decide (((code / 2^i.val) % 2) = 1))
def canonicalMask (j : Fin 6) : Finset (Fin 5) := maskOfCode (canonicalMaskCode j)
def canonicalMaskIdOfCode : Nat → Fin 6  -- 30-case finite table (from a1_mask_symmetry_table.json .id)
def canonicalRotOfCode : Nat → Fin 5     -- 30-case finite table (from .rot)
def rotBack (r i : Fin 5) : Fin 5 := ⟨(i.val + 5 - r.val) % 5, by omega⟩
theorem rotBack_injective (r : Fin 5) : Function.Injective (rotBack r)  -- finite fin_cases/omega
```

## 4. Mask symmetry (rotation ONLY suffices — each orbit is a single rotation-orbit)
```lean
structure MaskSymmetryData (A : Finset (Fin 5)) where
  id : Fin 6 ; rot : Fin 5 ; mask_eq : A = (canonicalMask id).image (rotBack rot)
theorem maskSymmetryData_of_proper (A)(hAne : A.Nonempty)(hAproper : A ≠ Finset.univ) : MaskSymmetryData A
  -- finite proof by cases on maskCode A, using the verified table (fin_cases/decide)
def XMaskCanonical (G c rows Q) {A} (sd : MaskSymmetryData A) : ℚ :=
  ∑ i in canonicalMask sd.id, rowSurplusAt G c rows Q (rotBack sd.rot i)
theorem mask_symmetry_sound (G c rows Q) {A} (sd : MaskSymmetryData A) :
    XMask G c rows Q A = XMaskCanonical G c rows Q sd := by
  classical; unfold XMask XMaskCanonical; rw [sd.mask_eq, Finset.sum_image]
  · rfl
  · intro a _ b _ h; exact rotBack_injective sd.rot h
```

## 5. The wrapper + global theorem (reuses ConeCert.sound)
```lean
theorem A1CanonicalCone.sound (cert : ConeCert)(hcheck)(G c rows Q){A}(sd : MaskSymmetryData A)
    (hSlack : A1SlackHypotheses G c rows Q sd) :
    XMaskCanonical G c rows Q sd ≤ ((25:ℚ)/(G.n:ℚ) + (2:ℚ)/3) * etaQ G c
  -- uses ConeCert.sound (0 ≤ D_j via env = named A1 slacks, all ≥0) + hNpos (0<N) + divide by 3N>0.
  -- env for the cone: x_i := rowSurplusAt G c rows Q (rotBack sd.rot i)  (rotated coords, no whole-graph reindex)
theorem A1ProperCertBundle.sound (B : A1ProperCertBundle)(hcheck)(G c rows Q)
    (hSlack0 : A1GlobalSlackHypotheses G c rows Q) :
    ∀ A, A.Nonempty → A ≠ Finset.univ → XMask G c rows Q A ≤ ((25:ℚ)/(G.n:ℚ) + 2/3) * etaQ G c := by
  intro A hAne hAproper
  let sd := maskSymmetryData_of_proper A hAne hAproper
  rw [mask_symmetry_sound G c rows Q sd]
  exact A1CanonicalCone.sound (B.certs sd.id) (bundle_check_extract B hcheck sd.id) G c rows Q sd (hSlack0.toLocal sd)
```
Then BranchAInputs.a1Proper := A1ProperCertBundle.sound ... (per A1PROPER_SIX_CONE_DESIGN toBranchAInputs).

## 6. INTERFACE NOTE (Claude): ConeCert is PROOF-CARRYING (no checkConeCert exists)
MAIN's sketch writes `checkConeCert cert = true`; the existing ConeCert embeds hid/hbase/hmults=true as fields,
so either (a) drop hcheck and pass the proof-carrying cert directly to ConeCert.sound, OR (b) add a Bool-field
RawConeCert + checkRawConeCert + a `= true → ConeCert` soundness. Resolve at build. Cones built by `decide`
(native_decide FORBIDDEN) → keep cone NFs compact.

## 7. What Codex emits (6 cones, corrected labeling per a1_mask_symmetry_table.json v2)
For j=0..5: A1_Mj.cone with target D_j = (75+2N)η − 3N·X_j, citing ONLY {eta, sigma(sid), nuK(sid),
atomNonneg(aid), closureResidual(rid)}; artifact includes switch sets S_sid, completed switches (nuK),
atom ids, checked residual values, the exact polynomial identity, nonneg certs for every multiplier.

## BUILD ORDER (Claude, next focused step)
1. Finite mask-symmetry Lean layer (GRAPH-INDEPENDENT, buildable NOW from the verified table):
   maskCode/canonicalMaskCode/maskOfCode/canonicalMask/canonicalMaskIdOfCode/canonicalRotOfCode/rotBack/
   rotBack_injective/MaskSymmetryData/maskSymmetryData_of_proper. Honest build (decide on finite Fin 5).
2. XMaskCanonical + mask_symmetry_sound (needs XMask/rowSurplusAt defs — confirm they exist in CertGraph).
3. A1SlackId + A1SlackHypotheses + slack-nonneg lemmas (from sigmaNonneg/etaQ/RowDBFactsAll5/closure checkers).
4. A1CanonicalCone.sound wrapper + A1ProperCertBundle + .sound + toBranchAInputs.
5. Instantiate B.certs from Codex's six cones (proof-carrying ConeCerts, by decide).
