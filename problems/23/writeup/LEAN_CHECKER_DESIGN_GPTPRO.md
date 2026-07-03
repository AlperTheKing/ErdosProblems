# Poly/ConeCert Checker Design (GPT-Pro compact reply, 2026-07-04, sibling 6a45e152)

N-PARAMETRIC PRINCIPLE: Var.N is an ORDINARY polynomial variable — never specialized
during checking; coefficients like (75+2N) are Poly, not Q.
Var := Nat (N=0; w i = 1+i for Fin 10; aux i = 1000+i). Poly.eval env : Q.
ConeDomain {nAtom, atom : Fin -> Poly (known-nonneg), nSlack, slack : Fin -> Poly
(cone generators), nEq, eqPoly : Fin -> Poly (equality ideal)}.
ConeSem D env : Prop {atom_nonneg, slack_nonneg, eq_zero} — the semantic assumptions
consumers must discharge (e.g. from CutState hypotheses).
ConeCert D {target : Poly; base + baseCert : PosCert (nonneg-cert for base);
slackMult j : Poly each with its own PosCert; eqMult k : Poly FREE (no sign)}.
rhs = base + Sigma slackMult_j * slack_j + Sigma eqMult_k * eqPoly_k.
check = baseCert.check AND all multCerts.check AND Poly.checkEq target rhs.
SOUNDNESS: ConeSem + check = true ==> 0 <= target[env]. (checkEq_sound gives target=rhs
pointwise; base and mults nonneg via PosCert.sound; slacks nonneg via sem; eq terms
vanish.) checkEq canonical-form contract: emitter outputs both sides pre-normalized
(sorted monomial lists) so checkEq is list equality decided by rfl/decide.
FOLLOW-UP PENDING: Bernstein simplex/cube checker nesting + risks (requested).
