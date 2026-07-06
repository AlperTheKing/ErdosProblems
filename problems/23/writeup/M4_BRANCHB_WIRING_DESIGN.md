# M4: BranchBData -> BranchBCertBundle wiring — design (Claude, 2026-07-06, scoped from the compiled tree)

## Interface (both sides already compiled)
EMITTED (Cert/BranchBSupport.lean + BranchBData/Shard*.lean, transpiler audit-green 14247 rows/29 shards):
- `RowPilot { name, n, m, L : Nat, caseTag : BranchBCase, gateBCandidate,
    pressure : ScaledEqCert, finiteMargin : ScaledGeCert, gateBDominance : ScaledGeCert,
    opSteps : List OpStepPilot }`.
- `OpStepPilot { opClass, eB_XS, eM_XS, eB_XO, eM_XO, q, rho, pieceCount, pieceContribs, pieceSum }`
  with `expectedQ = eB_XS - eM_XS - eB_XO + eM_XO` (the E2 exchange quadruple) and
  `expectedRho = if q<0 then 0 else 25*q` (E2 rho_a = 25*max(0,q_a)); check ties rho to the
  24-signature dictionary piece sum (pieceContribs sum = pieceSum = rho).
- `ScaledEqCert.check = den!=0 && sum terms == target`; `ScaledGeCert.check = den!=0 && lhs+margin == rhs`.
- `RowPilot.check` = all four certs check + opSteps check.

TARGET (CertGraph.lean 2617): `BranchBInputs G c rows Q : Prop` needs THREE fields:
- hLen : 5 < Q.length
- bankL : 2 * rhoQ Q.length <= etaQ G c
- bankedUPO : rowSum G c rows Q <= (G.n:Q) + etaQ G c / 2 - rhoQ Q.length
and `BranchBCertBundle` wraps `BranchBInputs`.

## The M4 bridge (compiled-lemma deliverable, isolates arithmetic from provider)
```
structure RowPilotBinding (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) (r : RowPilot) : Prop where
  len_eq   : Q.length = r.L
  n_eq     : G.n = r.n
  -- pressure scaled-eq encodes the Banked-UPO identity for THIS row:
  --   rowSum*den = pressure.target-side  (den = pressure.den), and analogous for eta/rho scaling
  rowSum_scale  : (r.pressure.den : Q) * rowSum G c rows Q = <linear combo of pressure terms>
  eta_scale     : (r.finiteMargin.den : Q) * etaQ G c = <finiteMargin rhs-lhs form>
  rho_binding   : rhoQ Q.length = <rho from opSteps telescope, scaled>
theorem branchBInputs_of_rowPilot
    (binding : RowPilotBinding G c rows Q r)
    (hcheck : RowPilot.check r = true)
    (hL : 5 < r.L) :
    BranchBInputs G c rows Q
```
Proof shape:
- hLen: rw [binding.len_eq]; exact hL.
- bankL: from gateBDominance/finiteMargin ScaledGeCert.check (lhs+margin=rhs => lhs<=rhs over Int),
  divide by den (>0), transport via eta_scale + rho_binding to the Q inequality.
- bankedUPO: from pressure ScaledEqCert.check (sum terms = target => the exact scaled Banked-UPO
  identity), divide by pressure.den, transport via rowSum_scale + eta_scale + rho_binding; the
  opSteps telescope (E2) supplies the rho decomposition, CombinedHBD (E6) supplies the eta/2 bank.

## Honest boundary (anti-fake-progress)
The BRIDGE (checked Int data => Q inequalities, given the binding) is pure arithmetic and IS an
M4 compiled lemma. The BINDING (that a given RowPilot IS the certificate for a given graph row Q)
is the PROVIDER obligation = M6/M7 (the emitter must produce RowPilotBinding per instance). So M4
delivers `branchBInputs_of_rowPilot`; wiring it into Delta0CertBundles.branchB needs the per-row
RowPilotBinding from the (research) provider. Route the bridge-theorem arithmetic to MAIN after
the geometry fields; I formalize the scaling once MAIN returns the exact ScaledEq/Ge -> Q lemmas.
```
```
NEXT: (1) MAIN designs branchBInputs_of_rowPilot (the ScaledEqCert/ScaledGeCert -> Q scaling
lemmas are the crux — den>0 division + Int<=; a few clean lemmas). (2) I graft + build. (3) The
RowPilotBinding provider stays M6/M7 (research, compiled-lemma gate).
```
