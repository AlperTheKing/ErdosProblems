# Lean signature audit: universal common-blue Hall

## Verdict

The smallest compiling target is pointwise universal Hall for `ExtendedAvailable`, quantified over every `RowChoice bads`. The real wrapper needs literal graph validity, triangle-freeness, maximum-cut status, B-connectivity, the Type-valued gamma-minimal carrier, and `CompleteShortestRowDB`. `IsMaxCut.valid` already contains `checkCut G c = true`.

Exact proposed signature is in `UniversalCommonBlueAudit.lean:19-22` (`RealUniversalCommonBlueHall`). The matching conclusion and reduction are at lines 24-33.

## Smallest lemma tree

1. OPEN SEMANTIC LEMMA: under the six real hypotheses, prove `forall omega, HallCondition G c omega`.
2. EXISTING LOGICAL LEMMA: `matching_nonempty_iff_hall` (`problems/23/lean/Erdos23Delta0/Gamma/CommonBlueExtendedMatching.lean:85`).
3. COMPILED POINTWISE LIFT: `universalCommonBlueMatching_iff_hall` (`UniversalCommonBlueAudit.lean:11`).
4. COMPILED REAL WRAPPER: `realUniversalCommonBlueMatching_of_hall` (`UniversalCommonBlueAudit.lean:24`).

No minimizer/descent/canonical-choice lemma is required for this universal statement.

## API audit

- Corrected semantic edge: `CommonBlueOwner`, production lines 37-41.
- Relation including old eligibility and exact reservation: `ExtendedAvailable`, lines 53-61.
- Matching/Hall definitions: lines 68-81.
- Terminal validity yields only checker replay/nonnegative adjusted surplus: lines 120-137; neither theorem supplies distinct global capacity.
- Complete database fields: `MinimumDemandCollisionHall.lean:33-47`; row nonemptiness API: lines 49-52.
- Existing real API precedent omits gamma-minimality: `MinimumDemandCollisionHall.lean:193-199`; this is weaker than the actual selected-cut bundle.
- `IsMaxCut`: `CertGraph.lean:2393-2396`; `TriangleFree`: 2399-2402; `BConnected`: 2423-2425.
- `GammaMinimalConnected` is Type-valued: `CertGraph.lean:2430-2434`; therefore the signature takes a term, not a Prop proof.
- Full selected cut bundle confirms maxCut/gammaMin/bConnected: `CertGraph.lean:2673-2677`.
- Connectedness-to-BConnected theorem: `CertGraph.lean:3655-3658`.

## First genuinely open graph semantics

The first open statement is exactly the Hall cardinal inequality for arbitrary `omega` and arbitrary demand shore `A`:

`A.card <= card {s | exists d in A, ExtendedAvailable G c d s}`.

The compiled common-blue API proves each new arc is a valid nonnegative-surplus terminal, but provides no shore-level injectivity/capacity argument. `GammaMinimalConnected` also carries an abstract `gammaOfCut`; its API has no theorem connecting that field to `ExtendedAvailable` neighborhoods. Thus no further logical unfolding closes this step.

## Build and axiom evidence

Command: `lake env lean --root=../problems/23/lean ../tmp/fanout/common_blue_proof/child_06_lean/UniversalCommonBlueAudit.lean`, with `LEAN_PATH=tmp/claude_lean_o_base_v1;problems/23/lean`.

Result: `EXIT_CODE=0`. Both printed theorems depend exactly on `[propext, Classical.choice, Quot.sound]`. No `sorry`, `admit`, or `native_decide` occurs.

- Scratch SHA-256: E7751CDE8FE66C706D356EEFF843771E95E815F7C885A9560CD566DF6E8374B3
- Build-log SHA-256: 6559C1EB64FF91D64DAC035E4A980CA3FB0036913018F002D77E2A1F0049BFE3
