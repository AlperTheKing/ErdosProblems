# A1-Proper as a Six-ConeCert Global Theorem (GPT-Pro MAIN, 2026-07-06)

## Verdict (decisive)
`a1Proper` is a **real Lean theorem, uniform in N**, discharged by **SIX fixed symbolic
A1 ConeCerts (M0–M5) + a finite mask-symmetry table** — NOT per-graph/per-row data, and
NOT a pure `nlinarith` proof from the uniform-width `w_i = N/5` heuristic (that heuristic
only consumes the result *after* the proper-mask inequality is known).

## The load-bearing inequality (A1)
For every proper active mask A (∅ ≠ A ⊊ Z/5):
  X_A = Σ_{i∈A} (s_i − τ) ≤ (25/N + 2/3)·η,   τ = 5m/N.
This is where terminal shadows, mask closure, prefix flips, and the PMTS slack cone enter;
it needs graph-side max-cut/γ-minimality info encoded as nonnegative slacks.

## The six cones
Mask complement/reversal symmetry reduces the nonempty proper masks of Z/5 to **six canonical
types M0..M5**. For each, Codex emits a symbolic certificate proving the cleared identity:
  (75 + 2N)·A1Defect_{M_j} = P_{0,j} + Σ_r P_{r,j}·Σ_r
with all P_{0,j}, P_{r,j} coefficientwise/Bernstein-nonnegative, and each Σ_r a valid
graph-side slack generator from the PMTS dictionary:
  - max-cut flip slack σ(S) ≥ 0
  - terminal-shadow slack
  - PMTS closure residual
  - noncrossing/completion residual
  - row-atom nonnegativity
  - Bank0 scalar slack (where allowed)
Lean does NOT rederive the certificate; it checks the finite ConeCert identity and invokes
the slack-dictionary soundness theorem.

## Minimal artifact family (fixed, global — NOT per graph/row)
```
A1Proper/
  M0.cone.json ... M5.cone.json
  mask_symmetry_table.json
```

## Lean interface (MAIN sketch)
```lean
structure A1ProperCertBundle where
  certs : Fin 6 → ConeCert
def checkA1ProperCertBundle (B) : Bool := Fin.all (fun j => checkConeCert (B.certs j))
def canonicalProperMaskId (A : Finset (Fin 5)) : Fin 6       -- finite table (plumbing, not a math gap)
def applyMaskSymmetry (A : Finset (Fin 5)) : MaskSymmetryData  -- finite table
-- mask_symmetry_sound : XMask A = XMaskCanonical (canonicalProperMaskId A)
structure A1SlackHypotheses (G c rows) : Prop where
  sigmaNonneg : sigmaNonneg G c ; etaNonneg : 0 ≤ etaQ G c ; rowsAll5 : RowDBFactsAll5 G c rows
theorem A1ProperCertBundle.sound (B)(hcheck : checkA1ProperCertBundle B = true)(G c rows)
    (hSlack : A1SlackHypotheses G c rows) :
  ∀ Q, RowInDB rows Q → Q.length = 5 → ∀ A : Finset (Fin 5), A.Nonempty → A ≠ univ →
    XMask G c rows Q A ≤ (25/(G.n:ℚ) + 2/3) * etaQ G c
  -- proof: reduce A→canonical j (mask_symmetry_sound); read checked ConeCert j;
  --        A1CanonicalCone.sound (the slack-dictionary soundness); transfer back.
structure BranchAProviderInputs (G c rows) : Type where
  etaNonneg : 0 ≤ etaQ G c
  a1Bundle : A1ProperCertBundle
  a1Check  : checkA1ProperCertBundle a1Bundle = true
  odlFullProvider : ∀ Q, RowInDB rows Q → Q.length = 5 → rowSum G c rows Q ≤ (G.n:ℚ) + etaQ G c
theorem BranchAProviderInputs.toBranchAInputs (P)(hGraph)(hCut)(hRows)(hSigma)(Q)(hQ)(hLen) :
    BranchAInputs G c rows Q :=
  { hLen, hNpos := ..., etaNonneg := P.etaNonneg,
    a1Proper := A1ProperCertBundle.sound P.a1Bundle P.a1Check G c rows ⟨hSigma,P.etaNonneg,hRows⟩ Q hQ hLen,
    odlFull  := P.odlFullProvider Q hQ hLen }
```
The `sorry`s in the sketch are FINITE-TABLE PLUMBING (canonicalProperMaskId, applyMaskSymmetry,
mask_symmetry_sound, per-cone checker) — literal finite tables, NOT mathematical gaps.

## CRITICAL SPLIT (do not mix)
- **Proper mask (∅≠P⊊Z/5)** → `a1Proper` = A1ProperCertBundle.sound (six cones). NO EQ/SIB/Seed3/four-door.
- **Full mask (P=Z/5)** → `odlFull` = ODLFullProvider.sound. THIS is where EQ-ODL1 charts, SIB-S7,
  Seed3 route-tree, q<3 two-door, q≥4 five-mask absorption, NCH/corridor enter — i.e. the 108 CHARTS
  feed `odlFull`, NOT `a1Proper`.

## NEXT STEPS
1. CODEX: emit the six symbolic A1 ConeCerts (M0..M5) + mask_symmetry_table (the (75+2N) identities,
   Bernstein-nonneg, PMTS slack dictionary). Exact/rational.
2. CLAUDE: exact-verify the six cone identities (coefficientwise nonneg + slack validity, Fraction-only).
3. LEAN: build A1ProperCertBundle + checkConeCert/checkA1ProperCertBundle + A1CanonicalCone.sound
   (slack-dictionary soundness) + the finite mask-symmetry table + A1ProperCertBundle.sound +
   BranchAProviderInputs + toBranchAInputs. Closes the PROPER-MASK branch of Branch-A as a general theorem.
4. The ODL full-mask (odlFull) provider is the SEPARATE obligation fed by the 108 charts + Seed3/EQ/SIB.

## UPDATE 2026-07-06T19:45Z — ConeCert.sound ALREADY EXISTS (PolyCert.lean:379) = the A1-cone bridge
Verified: PolyCert.lean has ConeCert{target,base,mults,slacks,hid:checkEq target (comboNF base mults slacks)=true,
hbase:allCoeffNonneg,hmults:all allCoeffNonneg} + ConeCert.sound (c)(env)(hvars:forall v,0<=env v)(hslacks:
forall s in slacks,0<=eval env s) : 0<=eval env target. Docstring: "the machine-certificate bridge for THE A1
CONES, seed banks, CrossCap". => A1CanonicalCone.sound REUSES ConeCert.sound DIRECTLY. So the a1Proper Lean
plumbing is LARGELY DONE. Remaining to close proper-mask branch:
  (a) Codex emits six A1 cones as ConeCert data (target=(75+2N)*A1Defect_Mj, base=P0, mults=P_r, slacks=Sigma_r).
  (b) SLACK DISCHARGE: prove each slack Sigma_r >= 0 (eval env) from A1SlackHypotheses (sigmaNonneg gives
      sigma(S)>=0; etaNonneg; row-atom nonneg; terminal-shadow/PMTS/noncrossing residuals) = the slack-dictionary
      soundness. This is the one nontrivial new Lean piece (the env->graph-quantity binding + each generator>=0).
  (c) mask-symmetry finite table (canonicalProperMaskId + mask_symmetry_sound) + XMaskCanonical + env wiring.
  (d) (75+2N)*A1Defect>=0 => A1Defect>=0 (trivial, 75+2N>0) => XMask<=(25/N+2/3)eta.
NOTE FOR MAIN: use ConeCert.sound directly; the design question narrows to the SLACK DICTIONARY (env binding +
each Sigma_r>=0 lemma) + the mask table. This is the real remaining Lean work for a1Proper.
