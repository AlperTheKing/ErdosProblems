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

## FOLLOW-UP (2026-07-04): PosCert + Bernstein checkers (8.6k in-thread)
PosCert: NOT Bernstein — nonneg-coefficient after substituting declared nonneg atoms
(aux-variable representation: repr over Var.aux only, auxSubst maps aux i -> atom;
shifted w=1+x handled by putting x = w-1 in ConeDomain.atom; PosCert agnostic).
Checks: allCoeffNonneg + varsSubsetAux + checkEq target (repr o auxSubst).
BernsteinSimplex: total-degree basis on chart simplex; coefficient list as data; vanish
constraints (seed vertex) as eqPoly data per coefficient cert; nested CoeffCert per
Bernstein coefficient (w-cone conditions); sound (basis nonneg on simplex + coeffs
nonneg) + sound_original (chart substitution version).
BernsteinCube: TENSOR basis over [0,1]^dim; CubeChart {dim, var} (EQV2: mu34/36/54/56 +
rho); CubeSem {lower, upper}; same nested-coefficient structure.
NOTES: cube/simplex checkers prove CLEARED NUMERATOR positivity only — denominator
positivity = separate family lemma; split large expansions per row/chart (one theorem
each); no native_decide.
IMPLEMENTATION ORDER: Poly (eval, normalized ops, subst, checkEq_sound) -> coeff checks
+ soundness -> ConeDomain/ConeSem/PosCert -> ConeCert (+withExtraEqs) -> CoeffCert ->
BernsteinCube (test master cubes first) -> BernsteinSimplex (CERT-2 charts) -> family
wrappers (A1 cones, CERT-2, V2 cubes, SIB/2Door/Seed3 rows).

## AUTHORITATIVE FULL CHECKER TEXT (user-relayed): exact records
PosCert {target, nAux, atomOf : Fin nAux -> Fin D.nAtom, repr (aux-vars ONLY)};
auxSubst maps aux i -> D.atom(atomOf i); check = varsSubsetAux AND allCoeffNonneg AND
checkEq target (subst auxSubst repr); sound via: aux -> nonneg atoms, monomials nonneg,
coeffs nonneg. CoeffCert {vanish : VanishData, coeff, cone : ConeCert
(D.withExtraEqs vanish), target_eq} — SEED-VANISHING = EXTRA EQUALITY POLYS in the
coefficient's cone domain (NOT a Bernstein rule). Nesting: Bernstein coeff -> CoeffCert
-> ConeCert -> PosCert. BernsteinSimplex: EXPLICIT barycentric lambda_0 = 1 - Sigma z
(risk 4: LITERAL polynomial equality, never modulo Sigma lambda = 1); records
SimplexChart{dim, subst, bary}/SimplexSem/SimplexCoeff/BernsteinSimplexCert;
sound + sound_original. BernsteinCube: tensor basis prod binom(d_i, a_i) x^a (1-x)^(d-a);
CubeChart{dim, var} (EQV2 = mu34/36/54/56 + rho); CubeSem{lower, upper}; DegreeVec.
RISKS 1-7: N-coefficients are Poly never Q; repr aux-only (varsSubsetAux in checker);
vanishing as eqs; literal simplex identity; EVERY Bernstein coefficient needs nested
CoeffCert (no bare boolean nonneg for polynomial coefficients); cleared-numerator only
(denominator positivity separate); split per row/chart, no native_decide.
IMPLEMENTATION ORDER 1-8 (Poly eval/ops/checkEq -> coeff checks -> ConeDomain/PosCert ->
ConeCert+withExtraEqs -> CoeffCert -> BernsteinCube first -> BernsteinSimplex ->
family wrappers).
