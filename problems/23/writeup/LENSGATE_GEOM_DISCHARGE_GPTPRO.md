# LensGates geometry discharge design (MAIN thread, 2026-07-06) — SCAFFOLD, in-thread full text

Source: MAIN reply (15162c, thread 6a450f06). Structural summary; full Lean text re-extract
from thread at graft time (transform @EQ@/@PL@/@AM@; base64 blocked).

## What it is
A REDUCTION layer, NOT a geometry proof. Adds:
- Lookup helpers: lensAt?, lensTypeAt, lensOSCAt.
- Mechanical outcome projections: checkOutcome_cross_switch, checkOutcome_label_cert, ...
  (extract the payload-cert = true from checkOutcome; use `Bool.and_eq_true` — NB the term
  form `Bool.and_eq_true.mp` must be converted to `rw [Bool.and_eq_true] at h; .1/.2` for our
  Lean pin, same fix as Seed3RouteTree).
- `structure PrimitiveLensGeomDischarge (G c D) : Prop` = the geometric obligations as
  HYPOTHESIS FIELDS, one per family, quantified over lens type:
    forbid_by_lens : forall ty i F, outcome=forbid i F -> lensTypeAt D i = ty ->
      LensGateCheckFacts -> checkOutcome=true -> sigmaNonneg -> LensNuKNonneg ->
      TriangleFree -> LensRowsAllLengthFive -> False
    osc0_by_lens, osc1_by_lens, ... (per OSCKind) : analogous -> conclusion.
- `def lensGateGeomSound_of_discharge (geom : PrimitiveLensGeomDischarge) : LensGateGeomSound`:
    cross_sound  = MECHANICAL (checkOutcome_cross_switch => LensGateConclusion.cross sw hsw;
                   no geometry — the switch cert IS the cross conclusion).
    label_sound  = MECHANICAL (label cert => LabelWellDefined => LensGateConclusion.label).
    forbid_sound = uses geom.forbid_by_lens (hypothesis) -> False -> absurd.
    osc_sound    = uses geom.oscN_by_lens (hypotheses).

## Assessment (Claude, 2026-07-06)
SOUND reduction: LensGateGeomSound <= PrimitiveLensGeomDischarge, with cross/label closed
mechanically. But the ASSUMPTION STRENGTH is unchanged — the irreducible primitive-lens
geometry (forbid_by_lens / oscN_by_lens per RR/RB/RD/DD/TTsame/TTopposite/TR) is still a
hypothesis. This does NOT advance the unconditional proof; it only refactors.

## Graft decision: DEFERRED until anchored
Do NOT graft this pure refactor yet (would be a build cycle + churn with no new PROVEN
content, and under the anti-fake-progress gate it adds no unconditional theorem). Graft the
whole geometry layer once MAIN proves at least the mechanically-dischargeable geometric
fields, so the layer lands with real content:
- ForbidKind.triangle: a checked triangle witness (3 mutually adjacent verts) CONTRADICTS
  TriangleFree G directly => forbid_by_lens for the triangle kind is GENUINELY PROVABLE.
- ForbidKind.shorterOdd: a certified shorter odd closed walk contradicts AllLengthFive /
  Gamma-minimality => provable from the OddCyclePacking parity machinery already compiled.
- The RR/RB/RD/DD/TT/TR head-on osculation cases = the irreducible geometric core; keep as
  clearly-named sub-lemma hypotheses until real geometric proofs exist.

## UPDATE 2026-07-06T12:55Z — MAIN delivered REAL mechanical geometry fields (no sorry)
MAIN reply (11453c, code-fenced Lean, in-thread) — verified head + triangle region:
- TriangleForbidPayload {u,v,w, edgeUV/VW/UW} + trianglePayload? extractor + checkTriangleForbidPayload
  (recomputes vertex bounds + normEdge identities + adjb u v / v w / u w) + checkForbidTriangleFromCert.
- ne_of_adjb_true (adjb=true -> u != v) + triangle_forbid_payload_false (a checked triangle payload +
  TriangleFree G -> False). = GENUINE discharge of the triangle-forbid field (not a hypothesis).
- (shorterOdd field + GeomDischarge assembly at ~9736 also present; no sorry/admit anywhere.)
GRAFT DECISION REVISED: the scaffold now has PROVEN content to anchor. Next Lean increment =
graft the geometry SCAFFOLD (PrimitiveLensGeomDischarge from the 15KB reply) TOGETHER WITH these
triangle-forbid + shorterOdd proofs, so the graft lands real unconditional content (2 of the
forbid/osc geometric fields proven; the RR/RB/RD/DD/TT/TR head-on osculation core stays hypothesis).
Full Lean text in-thread 6a450f06 (both replies) — extract at graft time (@EQ@/@PL@/@AM@ transform;
Lean is code-fenced so clean). Uses Bool.and_eq_true in TERM form in places -> convert to rw form.


## UPDATE 2026-07-06T16:45Z — LensGateGeomSound is NOT a free total constructor (MAIN finding, GATED)
KEY FINDING (honest, reduces but does not close the obligation):
- A no-argument `lensGateGeomSound_default : forall G c D, LensGateGeomSound G c D` is UNSOUND.
  The forbid and osc outcomes are NOT mechanically contradictory from checkLensGates alone.
- Mechanical (dischargeable for free): cross_sound (via checkLensSwitch + checkOutcome_cross_switch
  -> LensGateConclusion.cross), label_sound (via checkLabelCert + checkOutcome_label_cert ->
  LensGateConclusion.label). forbid.triangle + forbid.shorterOdd dischargeable via mechanical lemmas.
- IRREDUCIBLE (remaining geometric obligation): the primitive OSC / head-on geometry, isolated in a
  new subcertificate structure `IrreducibleLensGeomFacts`. LensGateGeomSound becomes constructible
  ONLY with (cert : LensGateGeomSubcert) + (facts : IrreducibleLensGeomFacts) attached as DATA.
DEF-EXISTENCE CHECK (CertGraph.lean): checkForbidTriangleFromCert EXISTS (L5025) + soundness (L5062).
MISSING (MAIN must emit): AllLengthFiveOddClosedWitnesses, checkForbidShorterOddFromCert,
  triangle_forbid_lens_conclusion, shorterOdd_forbid_lens_conclusion, IrreducibleLensGeomFacts,
  checkLensGateGeomSubcert, the constructor.
STATUS: LensGates checker soundness NARROWED from "all 4 outcomes' geometry" to "IrreducibleLensGeomFacts
  (OSC/head-on primitive)". Full Lean code proposal persists in MAIN thread (7601c); re-extract at graft.
RETASK: MAIN to emit the FULL self-contained helper layer + minimal IrreducibleLensGeomFacts.


## UPDATE 2026-07-06T17:05Z — MAIN helper layer LANDED (9637c, in-thread); LensGates obligation NARROWED to 2 fields
The full "Mechanical and irreducible LensGate geometry layer" is in the MAIN thread (asst msg #9,
9637 chars; re-extract via @EQ@/@PL@/@AM@ transform, ~10 slices due to display cap). Contents:
- checkForbidShorterOddFromCert (new): decide kind=shorterOdd && OddCyclePacking.checkOddClosedWalk
  witness && edgeCount<5 && witnessEdges match.
- LensGateGeomSubcert (new inductive, 6 ctors): cross | label | forbidTriangle | forbidShorterOdd |
  osc1 _ | osc4HeadOn _.
- checkLensGateGeomSubcert (dispatch on outcome x subcert: cross/label->true, forbid*->checkForbid*,
  osc1->decide O.osc.kind=OSC1, osc4HeadOn->decide kind=OSC4 && headOn=true, else false).
- LensGateGeomSound CONSTRUCTOR (cert : subcert)(facts : IrreducibleLensGeomFacts): cross via
  checkOutcome_cross_switch->LensGateConclusion.cross; label via checkOutcome_label_cert; forbid via
  triangle_forbid_lens_conclusion / shorterOdd_forbid_lens_conclusion; osc via facts.
- **IrreducibleLensGeomFacts = EXACTLY 2 fields**: osc1_sound (OSC1 primitive-lens residual, types
  RR/RB/RD/DD/TTsame/TTopposite/TR) + osc4_head_on_sound (OSC4 head-on residual). THAT IS THE ENTIRE
  remaining LensGates geometric obligation.
- Needs existence-check at graft: OSCKind(OSC1/OSC4), O.osc.kind/headOn, ForbidKind.shorterOdd,
  F.witnessVertices/witnessEdges, triangle_forbid_lens_conclusion, shorterOdd_forbid_lens_conclusion
  (MAIN to also supply the 2 forbid *_lens_conclusion lemmas + AllLengthFiveOddClosedWitnesses if missing).
NEXT-TICK FIRST ACTION: extract full layer (slices) -> existence-check referenced types -> graft into
CertGraph LensGates namespace -> honest build (expect multi-round like beta_bipartization) -> the 2
IrreducibleLensGeomFacts fields become the named remaining LensGates obligation (route to MAIN geometry).
