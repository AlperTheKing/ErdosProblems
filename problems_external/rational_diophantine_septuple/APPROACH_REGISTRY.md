# Rational Diophantine septuple — approach registry

Status date: 2026-07-20. Target: decide positively whether a rational Diophantine septuple exists by constructing one.

## DIRECT ROUTE — induced elliptic curve and compatibility clique

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals

`A = {a, b, c, d, e, f, g}`

such that `uv + 1` is a square in `Q` for every unordered pair `{u,v}` in `A`. The certificate must include the 21 rational square roots and pass two independent exact-arithmetic verifiers. One such certificate proves existence.

### 2. Current frontier lemma / finite certificate

For one rational Diophantine triple `{a,b,c}`, find four distinct nonzero extension values `d,e,f,g` that are pairwise compatible:

- `ax+1`, `bx+1`, and `cx+1` are rational squares for each `x` in `{d,e,f,g}`; and
- `xy+1` is a rational square for all six pairs among `{d,e,f,g}`.

Equivalently, on

`E_{a,b,c}: y^2 = (a x + 1)(b x + 1)(c x + 1)`,

the four x-coordinates come from the extension coset `P + 2E(Q)`, where `P=(0,1)`, and form a 4-clique in the exact compatibility graph `x ~ z iff xz+1` is a rational square.

### 3. Explicit logical bridge to the final deliverable

Dujella's induced-curve criterion states that `x(T)` extends `{a,b,c}` exactly when `T-P` lies in `2E(Q)`. Therefore every vertex supplies the three required square conditions against `a,b,c`. Every graph edge supplies one required square condition between two extension values. A 4-clique supplies all `3*4+6=18` new conditions; the original triple supplies the remaining three, hence all 21 conditions for a septuple. Distinctness and nonzero checks complete the certificate.

### 4. Next falsifiable action

Build an exact rational harness and require these calibration gates before any large search:

1. verify a published sextuple and all of its 15 square conditions;
2. verify Dujella's published almost-septuple has exactly one failing pair;
3. reconstruct extension points on the induced curve and check the elliptic group law independently;
4. from a declared set of induced triples with known extension points, enumerate a finite Mordell-Weil lattice box, retain only points in `P+2E(Q)`, and search the compatibility graph for a 4-clique.

The first search box, triples, generators, sign conventions, and height/coordinate caps must be written to a run manifest before launch. Any hit is rechecked from the seven rationals alone by two independent verifiers.

### 5. Exit condition

- A verified 4-clique closes the positive existence problem.
- A consumed finite lattice box with no clique is only `NO_HIT`, never nonexistence.
- If the point generator cannot be shown to stay in the extension coset, stop that lane.
- If a lane merely re-enumerates the order-3 construction of Dujella–Kazalicki–Mikić–Szikszai, stop it: their Remark 5 proves its natural seventh value repeats an existing value.
- Do not branch into unrelated parametric sextuple families unless each has a declared complete finite search region and a direct 4-clique bridge. Otherwise log `DEAD: reformulation maze — no bridge from the restricted family to a septuple`.

## DIRECT ROUTE — Gibbs double-extension replacement on the ACE curve

### 1. Exact final deliverable

The same seven-value, 21-root certificate defined above, accepted only after two independent exact-arithmetic verifiers pass.

### 2. Current frontier lemma / finite certificate

Let A=243/560, B=1147/5040, C=1100/63, D=7820/567, E=95/112, and G=196/45.

On E_ACE: y^2=(A*x+1)(C*x+1)(E*x+1), find a point H in the extension coset P+2E_ACE(Q), with P=(0,1), such that h=x(H) is nonzero, distinct from the six fixed values, and each of B*h+1, D*h+1, and G*h+1 is a rational square.

The proof-grade Mordell--Weil gate passed on the integral model

`Y^2 = X^3 + 2568913*X^2 + 1535181310080*X + 59427518261760000`.

Workspace-local eclib/mwrank proved rank 4 and completed automatic all-prime saturation. A certified free basis is

- `F1=(-861840,65622960)`;
- `F2=(-860928,60830400)`;
- `F3=(-855520,10311840)`;
- `F4=(-1506120,-397614360)`.

The decisive transcript excerpt is `runs/gibbs_ace_eclib_20260720T083033/mwrank_response.txt`, SHA-256 `4148E99C041F4E33E13CD32EC03889FD06D986A4AB5289F9F252EB3BE1DB5229`.

The 200- and 400-bit height-pairing computations agree. Exact group law gives

`Q0 - F1 - F2 - F3 - 2*F4 = (-1672000,0)`,

and this residual point has order 2. Thus every point in the target coset has free coordinate vector `k=(odd,odd,odd,even)` and is `T+k1*F1+k2*F2+k3*F3+k4*F4`, where `T=(-1672000,0)`.

### 3. Explicit logical bridge to the final deliverable

The fixed triple {A,C,E} is Diophantine. The values {B,D,G} extend that triple and form a compatibility 3-clique, with roots sqrt(BD+1)=769/378, sqrt(BG+1)=127/90, and sqrt(DG+1)=211/27. Membership of H in P+2E_ACE(Q) supplies the three square conditions against {A,C,E}. Compatibility with {B,D,G} supplies the remaining three conditions involving h. Hence {A,C,E,B,D,G,h} satisfies all 21 pair conditions.

### 4. Next falsifiable action

Run the single declared quantized height-matrix region `q12(k)<=1000`, where `q12` uses the symmetric height-pairing matrix rounded to 12 decimal places and integer scale `10^12`. The exact matrix and inequality are fixed in the run manifest. Sylvester's criterion applied to `M12-0.33*10^12*I` has four positive leading minors, so every vector in the region lies in `[-55,55]^4`; enumerate the full parity class `(odd,odd,odd,even)` in that box and test compatibility with B, D, and G exactly.

The exact finite scope is the quantized region, not a claim that every point of true canonical height at most 1000 is covered. The search harness must reject a candidate unless two separate processes verify exactly seven distinct nonzero rationals and all 21 pairs. The matrix, rounding rule, boundary rule, generator signs, and resource limits must be written to a run manifest before launch.

### 5. Exit condition

- A candidate passing both independent 21-pair verifiers is a positive solution.
- Failure to obtain proven rank equality or certified generators stops the proof-grade basis lane.
- A consumed canonical-height region with no candidate is only NO_HIT within that region.
- Do not continue through an unbounded sequence of coefficient boxes. Without a certified basis and a declared height region, stop with DEAD: reformulation maze — no global bridge from lattice boxes to septuple existence.

The declared B-D-G replacement region was consumed with independently matching counts `48714/48706/6/2/0`; its status is `NO_HIT` in that exact q12 scope.

## DIRECT ROUTE — ACE q12 full compatibility graph

### 1. Exact final deliverable

Seven distinct nonzero rationals passing both independent exact verifiers on all 21 unordered pairs.

### 2. Current frontier lemma / finite certificate

The certified q12 region has 48,714 parity vectors. The involution `k -> -k` gives the same extension value, and `k1>0` selects one representative because `k1` is odd. Removing the single zero value leaves exactly 24,356 ACE extension vertices and 296,595,190 unordered pairs.

The only earlier complete ACE graph used 53 vertices and 1,378 pairs, all contained in this region. Together with the fixed B-D-G replacement tests, prior work covered 25,683 distinct pairs, leaving 296,569,507 pair relations unevaluated.

### 3. Explicit logical bridge to the final deliverable

Every vertex lies in the extension coset for the Diophantine triple `{A,C,E}`. Therefore each vertex is compatible with A, C, and E. A 4-clique supplies all six pair conditions among four distinct extension values, so the triple plus the clique is a rational Diophantine septuple.

### 4. Next falsifiable action

Generate all 24,356 normalized nonzero vertices exactly and process every one of the 296,595,190 pairs. For `h_i=a/b`, `h_j=c/d`, with positive denominators, set `W=(ac+bd)(bd)`. Reject a pair only when `W` is a nonsquare residue modulo a fixed declared modulus; exact-test every survivor by integer square root. Store a one-byte rejection certificate for every pair, build the complete exact graph, and search it for a 4-clique. Independently replay the certificate and clique check.

### 5. Exit condition

- A 4-clique accepted by both seven-value verifiers proves existence.
- Exhaustion with a replayed certificate and no 4-clique is only `NO_HIT` for these 24,356 vertices.
- Do not enlarge q12 after a no-hit; without a new theorem-closing bridge, record `DEAD: reformulation maze — larger height regions give only more finite exclusions`.

The declared graph was consumed in `runs/ace_q12_fullgraph_20260720T094801`. Independent replay checked all 296,595,190 certificate bytes with zero mismatches and found 22,366 edges, exactly two triangles, and no 4-clique. The triangles are `{196/45,1147/5040,7820/567}` and `{1147/5040,7820/567,38269/6480}`. Status: `NO_HIT`; q12 enlargement is closed.

## DIRECT ROUTE — fixed-sextuple elliptic quotient gate

### 1. Exact final deliverable

Seven distinct nonzero rationals accepted by both exact 21-pair verifiers.

### 2. Current frontier lemma / finite certificate

Let

- `S_G={243/560,1147/5040,1100/63,7820/567,95/112,196/45}`; and
- `S_H={243/560,1147/5040,1100/63,7820/567,95/112,38269/6480}`.

For either sextuple `S={a1,...,a6}`, a seventh value is a rational point on

`C_S: u_i^2=a_i*x+1 (1<=i<=6)`.

This genus-49 multiquadratic curve maps to 35 genus-1 quotients:

`E_I: y^2=product_{i in I}(a_i*x+1), |I| in {3,4}`.

There are 70 quotient records for `S_G` and `S_H`, comprising 55 distinct curves after the common quintuple is deduplicated. The finite gate is to determine every rank. A quotient of certified rank zero gives a finite torsion list of possible `x`-coordinates containing every completion of that sextuple.

### 3. Explicit logical bridge to the final deliverable

If `x` extends `S`, multiplying the three relevant square roots gives a rational point with x-coordinate `x` on every `E_I`. Thus an exhaustive rank-zero torsion list cannot omit a completion. Every listed x-coordinate is tested against all six factors; any surviving distinct nonzero value supplies the seventh element and is passed to both full verifiers.

### 4. Next falsifiable action

Generate all 55 distinct integral Weierstrass/Jacobian models exactly, calibrate the ACE triple against its certified rank-4 model, and run workspace-local eclib/mwrank on every model. For a quartic `f=a*x^4+b*x^3+c*x^2+d*x+e`, use `I=12*a*e-3*b*d+c^2`, `J=72*a*c*e+9*b*c*d-27*a*d^2-27*b^2*e-2*c^3`, and Jacobian `Y^2=X^3-27*I*X-27*J`; the point `(x,y)=(0,1)` makes the torsor trivial. Accept `rank=0` only when mwrank proves equal lower and upper bounds. For each such quotient, certify the birational map, enumerate its complete torsion subgroup, and map every x-coordinate back exactly. Do not enumerate Mordell-Weil coefficient or height boxes.

### 5. Exit condition

- A candidate passing both full verifiers proves existence.
- A certified rank-zero quotient with no surviving x proves only that its fixed sextuple is nonextendible.
- If neither sextuple has a certified rank-zero quotient, stop this route; do not replace it with positive-rank height boxes.
- A negative result for these two sextuples is not global nonexistence.

The gate was consumed in `runs/fixed_sextuple_quotients_20260720T101501`. Two exact implementations agreed on all 70 records and all 55 distinct ranks. The rank histogram is `3:3, 4:21, 5:28, 6:3`; no rank-zero quotient exists. This route is closed and no positive-rank height box will be used.

## DIRECT ROUTE — ACE triangle genus-2 rank gate

### 1. Exact final deliverable

Seven distinct nonzero rationals accepted by both exact 21-pair verifiers.

### 2. Current frontier lemma / finite certificate

For `T_G={B,D,G}` and `T_H={B,D,H}`, let

`f_ACE(x)=(1+A*x)(1+C*x)(1+E*x)` and `f_T(x)=product_{s in T}(1+s*x)`.

The ACE-coset completion curve imposes `y^2=f_ACE(x)`, `v_s^2=1+s*x` for all `s in T`, and `(x,y)-(0,1) in 2*E_ACE(Q)`. Its genus-2 quotients are

- `w^2=f_ACE(x)(1+s_i*x)(1+s_j*x)` for the three pairs in `T`; and
- `w^2=f_ACE(x)f_T(x)`.

Across both triangles there are seven distinct quotient curves because `ACEBD` is shared.

### 3. Explicit logical bridge to the final deliverable

Every completion x maps to a rational point on every listed quotient. If any quotient Jacobian has proven rank at most one, Coleman-Chabauty plus a Mordell-Weil sieve can give its complete rational x-list. Exact testing of that finite list against all six fixed values and the ACE coset cannot omit a completion. Any survivor gives the seventh value and is sent to both full verifiers.

### 4. Next falsifiable action

Generate the seven curves exactly and submit frozen Magma V2.29-8 code to the official public calculator for `RankBounds(Jacobian(C))`, one curve per 60-second job. Preserve each input, output, and hash. If any proven upper bound is at most one, compute a saturated Mordell-Weil subgroup and complete Chabauty/sieve. A timeout or unequal bounds is `INCONCLUSIVE`, never a rank claim.

### 5. Exit condition

- A dual-verified candidate proves existence.
- A complete quotient point list with no candidate proves only that its triangle is nonextendible.
- If every proven lower rank is at least two, or no quotient has an upper bound at most one, stop this lane; do not start height searches.
- Failure of the public calculator to certify bounds stops the lane without inference.

The gate was consumed in `runs/ace_triangle_genus2_20260720T103143`. Magma V2.29-8 returned bounds `1..5, 0..5, 1..4, 1..5, 1..6, 0..3, 1..5`; an independent exact audit matched all seven inputs, models, scales, hashes, and transcripts. No upper bound is at most one. Status: `INCONCLUSIVE`; this route stops without an exact-rank, rational-point, nonextendibility, or septuple conclusion.

## DIRECT ROUTE — records 501/502 common-quintuple curve

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by two independent exact-arithmetic verifiers.

### 2. Current frontier lemma / finite certificate

Let

`Q={17/120,122/255,728/2295,1325/408,5643/680}`.

Every rational extension of `Q` maps to the genus-2 curve

`C_Q: Y^2=2(120+17x)(255+122x)(2295+728x)(408+1325x)(680+5643x)`.

The frontier is a proved complete list `C_Q(Q)`. The integral normalization uses `Y=6242400*y` because the product of the five denominators is `2*3121200^2`. Catalogue records 501 and 502 give the known extension values `f=-237800/2019651` and `g=35224/15`; they are incompatible because `f*g+1=-98187911/356409<0`.

### 3. Explicit logical bridge to the final deliverable

If `h` extends `Q`, multiplying its five rational square roots gives a rational point on `C_Q`, so a complete point list cannot omit `h`. Filter every affine x-coordinate exactly by requiring all five individual values `1+q*x` to be rational squares, then build the exact graph `x~z` iff `x*z+1` is a rational square. Any edge gives `Q` plus two compatible extensions and therefore all 21 conditions of a septuple. Both full verifiers must accept the seven values.

### 4. Next falsifiable action

Freeze and hash the exact integral model and one Magma V2.29-8 input. Submit `RankBounds(Jacobian(C_Q))` and `RationalPointsGenus2(C_Q)` to the official public calculator. Accept a rational-point list only when its returned completeness flag is `true`; when it is `false`, the third return is only a searched height bound and is ignored. An upper rank at most one advances to a saturated Mordell--Weil computation and Coleman--Chabauty/Mordell--Weil sieve. Independently replay all returned points, the model map, the five square tests, and the compatibility graph.

### 5. Exit condition

- A compatibility edge passing both full verifiers proves existence.
- A complete rational-point list with no edge proves only that no septuple contains `Q`.
- Rank lower bound at least two, unequal bounds with upper above one, timeout, incomplete point output, or failure to saturate stops this lane as `INCONCLUSIVE`.
- This is the final catalogue-quintuple lane. Do not test further catalogue quintuples or increase height bounds after it; that would be `DEAD: reformulation maze — serial fixed-family exclusions do not bridge to global existence`.

The rank gate was consumed in `runs/records501_common_curve_20260720T110150`. Magma V2.29-8 returned `1 <= rank(J(C_Q)) <= 6`; an independent audit matched the full transcript, exact model, coefficients, and hashes. The upper bound exceeds one, so the conditional rational-point job was not submitted. Status: `INCONCLUSIVE`. This final catalogue lane is closed, and serial testing of further fixed quintuples is prohibited by the guard.

## DIRECT ROUTE — retain the omitted second regular extension

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals `{a1,...,a7}` with exact roots for all 21 values `ai*aj+1`, accepted by two independent exact-arithmetic verifiers.

### 2. Current frontier lemma / finite certificate

Use the two-parameter rational Diophantine quintuple `{a1,...,a5}` in Dujella--Kazalicki--Petricevic (2019). Their `a6` and the omitted second root `a7` independently extend the quadruple `{a1,a3,a4,a5}`. If

`A=a1*a3*a4*a5`, `B=2*a1*a3*a4+a1+a3+a4-a5`, and `K=(a1*a3+1)(a1*a4+1)(a3*a4+1)`,

then their regular-root quadratic is

`((A-1)*x+B)^2-4*K*(a5*x+1)=0`,

and Vieta gives

`a7=(B^2-4*K)/((A-1)^2*a6)`

away from the saturated bad locus. Let `H(u,t)=z6^2` be the paper's quartic condition that `a2*a6+1` is a square. Impose the Piezas condition

`G=(A-3)^2-4*(a1*a3+a4*a5+3)=0`,

which makes `a6*a7+1` a square, and impose

`z7^2=a2*a7+1`.

The numerator of `G` has four Q-irreducible factors `Fi(u,t)`, each of bidegree `(10,4)`. The frontier is a nondegenerate rational point on one normalized component of

`Fi(u,t)=0`, `H(u,t)=z6^2`, `a2(u,t)*a7(u,t)+1=z7^2`.

### 3. Explicit logical bridge to the final deliverable

The published quintuple supplies 10 pair conditions. Each of `a6` and `a7` supplies four conditions against `{a1,a3,a4,a5}`. The equation `H=z6^2` supplies `(a2,a6)`; `G=0` and the Piezas proposition supply `(a6,a7)`; the final square cover supplies `(a2,a7)`. Thus `10+4+4+1+1+1=21`. Removing denominator, zero, equality, and discriminant loci ensures seven distinct nonzero values. Any surviving point is sent directly to both full verifiers.

### 4. Next falsifiable action

Reconstruct all formulas from the arXiv TeX; verify the published quintuple identities and `u=-1` sextuple; reconstruct `a7` by Vieta; factor `numerator(G)` over Q and independently confirm its four branches. For each branch, form the saturated ideal with the two square-cover equations, determine its dimension, primary components, normalization, singularities, and genera. Continue only on a Q-defined one-dimensional component that is rational with a Q-point, genus one with an exact rational point, or genus two with a certified rank below two and a complete Chabauty/sieve route.

### 5. Exit condition

- A rational point producing a candidate accepted by both full verifiers proves existence.
- If every Q-defined component has a complete rational-point determination and only bad-locus points, this restricted family is closed.
- If decomposition or normalization is infeasible, no Q-defined curve survives, or all surviving components lie outside the stated genus/rank gate, record `INCONCLUSIVE` and stop this route.
- Do not add height boxes, fixed fibers, denominator scans, or another related sextuple family.

Primary sources: https://arxiv.org/abs/1904.00348 for the quintuple, regular-root quadratic, `a6`, and the explicit statement that `a7` is not used; and https://arxiv.org/abs/1609.06986, Proposition 1, for `G=0`. A targeted primary-source audit found no published treatment of these two remaining compatibility conditions; the 2026 survey still lists septuple existence as open.

### Closure (2026-07-20)

Exact reconstruction and an independent audit agree that `numerator(G)` has four multiplicity-one Q-irreducible factors of bidegree `(10,4)`. The exact `P1 x P1` audit finds the complete singular support `(0,0)`, `(infinity,0)`, `(-8,infinity)`, `(-2,infinity)` with delta invariants `7,7,4,4`; each normalization therefore has genus `27-22=5`. A separate Magma V2.29-8 projective-closure replay returns `IsIrreducible=true` and `Genus=5` for all four factors.

After bad-locus saturation, every normalized horizontal component of the two square covers maps finitely and surjectively to one of these genus-5 curves. Riemann--Hurwitz gives genus at least `5`, so no component satisfies the registered genus-at-most-2 continuation gate. Status: `INCONCLUSIVE`; route closed without parameter, height, or fixed-fiber scans.

Artifacts: `runs/dkp_omitted_extension_20260720T121511/independent_factor_audit.json` (SHA-256 `42D263921D75C46313A66ABF9ACF00D2AC8BA9CC880B714D7B170A4A3B05D27E`), `base_geometry_audit.json` (SHA-256 `9CC9815FE76A611AEE8BC6B2DE2AF7F3BB61D1C4D070767D9693F982C224884C`), and `magma_base_geometry_referee/magma_base_geometry_referee.json` (SHA-256 `3A061FF7243AD76AD79AEF9E0DF4ACC698FE82B3F94AD1E2DBC76D2CEEFBF1D0`).

## Novelty and current-status gate

## DIRECT ROUTE — reverse induced-curve canonical shift

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by the two independent exact-arithmetic verifiers.

### 2. Current frontier lemma / finite certificate

Let `Sigma(t)={a(t),b(t),c(t),d(t),e(t),f(t)}` be the explicit one-parameter sextuple in Dujella--Kazalicki--Mikic--Szikszai (2017), and use the reverse induced curve

`E*: y^2=(d*x+1)(e*x+1)(f*x+1)`.

Write `P*=(0,1)`, `L=d*e*f`, `M=d*e+d*f+e*f`, and let `S*=(1/L,yS)` be the canonical point, where

`yS^2=((d*e+1)(d*f+1)(e*f+1))/L^2`.

Let `A*=(a,yA)`, where `yA^2=(d*a+1)(e*a+1)(f*a+1)`, with signs fixed by the published pair roots. Define

`g_plus=x(A*+S*)` and `g_minus=x(A*-S*)`.

With `s=1/L`, their exact group-law formulas are

`m_plus=(yA-yS)/(a-s)`, `m_minus=(yA+yS)/(a-s)`, and

`g_plus=(m_plus^2-M)/L-a-s`, `g_minus=(m_minus^2-M)/L-a-s`.

The frontier is the rational-point problem on the two residual biquadratic covers

`X_plus: U^2=1+b*g_plus, V^2=1+c*g_plus`,

`X_minus: U^2=1+b*g_minus, V^2=1+c*g_minus`.

### 3. Explicit logical bridge to the final deliverable

Because `a` extends `{d,e,f}`, the induced-curve criterion gives `A*-P* in 2E*(Q(t))`. The canonical point satisfies `S* in 2E*(Q(t))`. Hence `A*+-S*-P*` lies in `2E*(Q(t))`, so each `g_+-` is compatible with `d,e,f`. The canonical-shift identity gives `a*g_+-+1` as a square. A nondegenerate rational point on either residual cover supplies the two remaining conditions against `b` and `c`; together with the published sextuple identities, this gives all 21 conditions. Exact distinctness and nonzero checks plus both full verifiers complete the certificate.

This is not the order-three forward-shift lane rejected by DKMS Remark 5. Their Remark 4 proves that on this reverse curve the sections with x-coordinates `0,1/(def),a,b,c` are generically independent, while Remark 5 concerns repetition on the original induced curve.

### 4. Next falsifiable action

Reconstruct the published rational functions and pair roots exactly; independently verify all 15 sextuple identities; compute both `g` functions by two exact group-law implementations; factor the square classes of `1+b*g` and `1+c*g` in `Q(t)^*/Q(t)^{*2}`; normalize each fiber product; and certify its branch sets, singularities, components, and genera. Continue to rational-point determination only for a rational component, a genus-zero component with a certified rational point, a genus-one component with an exact rational point, or a genus-two component with a certified rank below two and a complete Chabauty/sieve result.

### 5. Exit condition

- A nondegenerate parameter yielding a candidate accepted by both full verifiers proves existence.
- An identity square or a certified rational low-genus component advances directly to specialization and verification.
- If both normalized covers have genus above two, no certified low-genus component, or fail the stated completeness gates, record `INCONCLUSIVE` and stop this family.
- Do not scan rational parameters, increase height bounds, or replace this with a sequence of related sextuple families.

The exact gate was consumed in `runs/dkms_reverse_shift_20260720T115557`. Both residual covers are connected V4 covers with 178 branch points and genus 175. The independent replay matched the published `t=6` sextuple, 15 published identities, 2 reverse points, 2 group-law candidates, 8 automatic identities, 4 residual decompositions, and both genus counts. Reduction SHA-256: `0580CFAFAC10C3378F7CBAF26C4F09FE8903F1F1D28613BC540F7ACBF70D60F2`; audit SHA-256: `4C3AB75E8F7A048FF2855022D0520E351C0415782E5B9908C4D8422FACE0D334`. Status: `INCONCLUSIVE`; this family is closed and parameter scans are forbidden.

Primary route source: https://arxiv.org/abs/1507.00569, especially the induced-curve criterion and canonical shift in Section 2 and Remarks 4--5. A targeted primary-source search found no published use of these reverse-shift residual covers; the 2026 survey still lists rational septuple existence as open.

- Andrej Dujella, *Open problems on Diophantine m-tuples and elliptic curves* (2026), Problem 3.2: “Is there any rational Diophantine septuple?”
- Dujella–Kazalicki–Mikić–Szikszai, *There are infinitely many rational Diophantine sextuples*, IMRN 2017: induced elliptic curve criterion and explicit statement that the septuple question remains open.
- Rathbun's 2024 distributed search and low-height sextuple catalogue are prior computational lanes; their covered regions must be excluded or used only for calibration.

Current sources:

- https://web.math.pmf.unizg.hr/~duje/pdf/open2.pdf
- https://arxiv.org/abs/1507.00569
- https://dujella.github.io/ratio.html
- http://www.numbertheory.org/ntw/pdfs/search_for_Diophantine_sextuples.pdf

## DIRECT ROUTE — strong-pair adjacent odd orbits

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by two independent exact-arithmetic verifiers.

### 2. Current frontier lemma / finite certificate

Use the first family in Dujella--Kazalicki--Petricevic (2025):

`a=2u/(u^2-1)`, `b=2v/(v^2-1)`, and

`c=2(u^2-1)(v^2-1)/(uv-u-v-1)^2`,

on the affine genus-one curve `C: p(u,v)=0`, where

`p=3u^4v^4-8u^4v^3+6u^4v^2-u^4-8u^3v^4+4u^3v^3-8u^3v^2+12u^3v+6u^2v^4-8u^2v^3+4u^2v^2+8u^2v+6u^2+12uv^3+8uv^2+4uv+8u-v^4+6v^2+8v+3`.

The paper proves that `C` is birational to `y^2+xy+y=x^3-33x+68`, with torsion `Z/6Z` and free rank one, and that `{a,b,c}` is Diophantine with order-three canonical point. On

`E_(a,b,c): Y^2=(X+ab)(X+ac)(X+bc)`, let `P=(0,abc)` and `S=(1,rst)`. With `D=uv-u-v-1`, exact roots on `C` are

`r=2(uv+1)D/((u^2-1)(v^2-1))`, `s=(uv-u+v+1)/D`, and `t=(uv+u-v+1)/D`;

the family has `3S=O`.

Fix only the adjacent odd orbits

`d0=x(3P)/(abc)`, `d+=x(3P+S)/(abc)`, `d-=x(3P-S)/(abc)`, and `g=x(5P)/(abc)`.

The frontier is a nondegenerate rational point on the single Kummer cover of `C`

`z0^2=1+g*d0`, `z+^2=1+g*d+`, `z-^2=1+g*d-`.

### 3. Explicit logical bridge to the final deliverable

The published order-three theorem makes `{a,b,c,d0,d+,d-}` a rational Diophantine sextuple. Since `5P-P=4P=2(2P)`, the induced-curve descent criterion makes `g` compatible with `a,b,c`. The three Kummer equations make `g` compatible with `d0,d+,d-`. Thus `15+3+3=21` pair conditions hold. Bad-locus saturation plus exact nonzero and distinctness checks completes the certificate, which is then sent to both full verifiers.

This is not the same-orbit repetition in DKMS Remark 5: that repetition is `x(T+2S)=x(T-S)`, whereas `g` belongs to the fixed adjacent odd-multiple orbit and all three cross-orbit conditions are imposed.

### 4. Next falsifiable action

Reconstruct `C`, the three pair roots, `P`, `S`, `3P`, `5P`, and the four extension values exactly from the source. Calibrate on the actual `p=0` point `(-128/119,135/169)`, the image of the paper's printed `s1=0` example under `sigma(u,v)=(1/u,-v)`. In `K=Q(C)`, reduce the three residual functions, compute their classes in `K*/K*2`, and certify all horizontal components, branch divisors, singularities, normalizations, and genera of the saturated Kummer cover. Independently replay the function-field identities and Riemann--Hurwitz calculation. Continue only for a rational component, a genus-zero component with a Q-point, a genus-one component with an exact Q-point, or a genus-two component with certified rank below two and a complete Chabauty/sieve route.

### 5. Exit condition

- A nondegenerate rational point producing a candidate accepted by both full verifiers proves existence.
- An identity square or a certified low-genus component advances directly to exact rational-point determination.
- If every Q-defined horizontal component has genus above two, no horizontal component survives saturation, or exact normalization is infeasible, record `INCONCLUSIVE` and close the route.
- Do not replace `3P,5P`, move to the other two published families, scan rational parameters, or enumerate odd multiples.

Primary sources: https://arxiv.org/abs/2403.17959 for `C`, the family, its rank-one model, and the order-three sextuple construction; https://arxiv.org/abs/1507.00569 for the induced-curve criterion and the same-orbit repetition. Exact audit corrects three source-convention issues: the printed example lies on the isomorphic `s1=0` branch; the displayed identity has `p+t=4(uv+1)^2D^2`; and the printed half point needs `x(R)=1+rs+rt+st`. A targeted primary-source audit found no treatment of this fixed three-function adjacent-orbit cover; the June 2026 survey still lists rational septuple existence as open.

### Closure (2026-07-20)

Two smooth transverse points modulo 109 certify independent geometric square classes. At `(u,v)=(12,48)`, the residual values are `(3,0,59)` with tangent derivatives `(83,32,96)`, giving parity row `(0,1,0)`. At `(u,v)=(9,84)`, they are `(3,59,0)` with derivatives `(34,17,42)`, giving `(0,0,1)`. All group-law denominators are units and the seven residue values are nonzero and distinct. Multivariate Hensel lifting therefore gives two distinct characteristic-zero branch points at which exactly `f+` or `f-` has odd valuation. Hence the geometric Kummer rank is at least two.

For geometric rank `r`, each horizontal component has degree `2^r` over the genus-one base and at least two branch points. Riemann--Hurwitz gives `2g(X)-2 >= 2^(r-1)*2`; thus `g(X)>=3` for `r=2` and `g(X)>=5` for `r=3`. Every horizontal component is above the registered genus-two cutoff. Status: `INCONCLUSIVE`; the route is closed without a parameter scan or a septuple claim.

Artifacts: `runs/strongpair_kummer_geometry_local_20260720T133733/local_branch_witnesses.json` (SHA-256 `66FD6762F0A92C68EAC3EEF8989607B32C45FC8520B011375930DDAD624DE1D9`), public Magma V2.29-8 referee `local_branch_referee.json` (SHA-256 `7A26DA096D4FF71C7F25582A3D6539AE31C00EB295011A2E90A1AB73F940CB96`), and independent local replay `local_branch_replay.json` (SHA-256 `F5DDA95241FFE187CE87399915A43174BB7D04211829AD7ADD7BBA37478149BD`).

## DIRECT ROUTE — fixed `Z/6 x Z/2` maximum-extension region

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and the independent `verify_septuple_independent.py` implementation.

### 2. Current frontier lemma / finite certificate

Fix the catalogue triple

`(a,b,c)=(-6656/61215,1155/1696,795/154)`,

whose pair roots are `(51/53,51/77,17/8)`, and the induced curve

`E: y^2=(1+a*x)(1+b*x)(1+c*x)`.

Let `P=(0,1)` and `R3=(-4081/1560,14739/4160)`. Exact group arithmetic gives `3R3=O`. Catalogue records 1735--1745 provide 33 distinct extension values. Their complete compatibility graph is the disjoint union of eleven triangles, one per record, and each triangle is the `R3` orbit of the positive-y lift of its least x-coordinate.

Let `Ti` be that lift for record `1735+i`, set `D0=2T0`, and set `Di=Ti-T0` for `1<=i<=10`. The frontier is the exhaustive finite region

`Q(j,n)=T0+j*R3+sum_(i=0)^10 n_i*D_i`,

with `j in {0,1,2}` and every `n_i in {-1,0,1}`. It contains exactly `3*3^11=531441` group expressions, before point or x-coordinate deduplication. The finite certificate is either one x-coordinate completing a fixed triangle or a complete independently replayed `NO_HIT` ledger for all expressions and all eleven triangles.

### 3. Explicit logical bridge to the final deliverable

The induced-curve criterion says that `x(T)` extends `{a,b,c}` exactly when `T-P` lies in `2E(Q)`. Every `Ti-P` does. Hence every `Di` and `D0` lies in `2E(Q)`. Since `R3` has order three, `R3=2*(2R3)` also lies in `2E(Q)`. Therefore every finite `Q(j,n)` lies in `P+2E(Q)` and its x-coordinate extends the base triple; this is also checked directly by three exact square tests.

Each catalogue triangle and the base triple already form a verified sextuple. If a new finite x-coordinate is nonzero, distinct from those six values, and compatible with all three triangle vertices, then the base triple supplies 3 conditions, the triangle and its cross-pairs supply 12, and the new coordinate supplies 6, for all 21 conditions. Both full verifiers must accept it.

### 4. Next falsifiable action

Freeze a manifest containing the catalogue hash, all eleven triangles, `R3`, the lift convention, the eleven directions, coefficient ranges, expression count, and a deterministic shard map. Before enumeration, assert all 15 conditions for each source sextuple, `3R3=O`, the eleven exact orbit identities, 33 graph edges, and no cross-triangle edge. Enumerate every declared expression, deduplicate finite x-coordinates, use only sound unit-denominator modular rejections, and exact-test every modular survivor against every fixed triangle. Send every hit to both final verifiers. Independently replay the fixed region and its terminal ledger with a separately implemented group law.

### 5. Exit condition

- A candidate accepted by both full verifiers proves existence.
- Matching exhaustive ledgers with no candidate give only `NO_HIT` for this exact 531441-expression, eleven-triangle scope.
- Any expression-count mismatch, orbit failure, verifier disagreement, lost shard, or incomplete ledger is `FAILED`, not `NO_HIT`.
- After verified `NO_HIT`, close this route. Do not enlarge coefficients, move to another `Z/6 x Z/2` seed, or search new-only four-cliques.

Frozen evidence: `sources/2001.sextuples.txt` has SHA-256 `426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933`; `runs/catalog_scan_20260720T0643/summary.json` has SHA-256 `A281BF2AC54433E7D80F013BB4BF63D1B8843C9763213BF8A27E58B12F8DF656` and identifies this as the unique 33-extension maximum; `runs/catalog_multiseed_box1_20260720T0655/manifest.json` has SHA-256 `593063D5FCD0BAC94EE3D3F15FA9E18B4ACC65B90C95C992C34DF13CD0C56860` and explicitly excluded `Z6x2`. Exact-string searches for the triple and `R3` found no published treatment of this region; the March 2026 survey still lists rational septuple existence as open. The theorem source is DKMS 2017, Section 2.

### Closure (2026-07-20)

The initial manifest `5A08D1C7...` was rejected before full search because its primary hit path passed `Fraction` objects to the standalone string/integer verifier. After correcting that interface, the final frozen manifest is `runs/z6x2_max_region_20260720T142412/manifest.json`, SHA-256 `C9965E2FC2E1D82FF080155A4C575E20B689F320E04EFB3BCA867BA82B2B85E6`. The primary engine has SHA-256 `FF21336750E8C1A35E37C48065F2E0F9E0CBC152410890CD392442382F2B20D1`; the independently implemented parser and group law have SHA-256 `EBE6073D80BC7D74BB8C74DF8EDF481E55725A3B67B033567BF9879AAA945C55`.

All 27 primary and 27 independent shards completed. Each implementation enumerated exactly 531441 expressions. Every one of the 27 terminal ledger digests matched, no expression set a completion bit, and no candidate was emitted. The 531441 expressions reduced to 6570 distinct finite x-coordinates. The primary aggregate is `primary_full/summary.json`, SHA-256 `7902D2AE2586E26026B125050C7B864DEF396342515D697A0B8E89246D807613`; the independent comparison is `independent_full/comparison.json`, SHA-256 `47DCC13546977EC21139F4A8EA17143B3D13D93D921220624677D57BE6E769E4`. The aggregate ledger digest is `9B6AB1C617338AAA78FAC0A0FF19DAB9A69255A09BAB2C0EEE8AC146F30CB3AF`.

Status: verified `NO_HIT` only for the frozen 531441-expression, eleven-triangle scope. This is not a nonexistence result for rational Diophantine septuples. The route is closed; its coefficients, seed, and target graph will not be enlarged.

## DIRECT ROUTE — fixed rank-12 Boolean cube

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and the separately implemented `verify_septuple_independent.py`.

### 2. Current frontier lemma / finite certificate

Fix the rank-12 triple from Dujella--Peral (2020)

`a=6125241375/11907531272`,

`b=5535371271425/14277129995128`,

`c=-273138178560/153430695649`,

and the induced scaled curve `E': Y^2=(X+ab)(X+ac)(X+bc)`. Let `Emin` be the paper's minimal model

`y^2+x*y+y=x^3-x^2-A*x+B`,

where

`A=1444491707528591356856089186460491195711268950880` and

`B=559921583779625421248683584939561762456224290170437461555851482041439747`.

Put `U=7138564997564` and `m=955655055996458012197251`. The origin-preserving isomorphism `psi:Emin->E'` is

`X=25*(x+m)/U^2`, `Y=125*(2*y+x+1)/(2*U^3)`.

The distinguished point `(0,abc)` pulls back to

`P0=(-m,-1033237630189640270243631944200109375)`.

Let `P1,...,P12` be the twelve published independent points in source lines 411--422. For every `eps in {0,1}^12`, form

`Q_eps=P0+2*sum_i eps_i*Pi`.

For finite `Q_eps=(x,y)`, its extension value is

`d_eps=-6735029*(x+m)/4874148659847186464642623440000`.

The fixed region has exactly `2^12=4096` declared group expressions. The finite certificate is either four pairwise-compatible distinct nonzero extension values or matching complete `NO_HIT` ledgers for all 4096 expressions and their full compatibility graph.

### 3. Explicit logical bridge to the final deliverable

For every `eps`, `Q_eps-P0` lies in `2*Emin(Q)`. Transporting through `psi` gives `psi(Q_eps)-(0,abc) in 2*E'(Q)`. The induced-curve criterion therefore makes every finite `d_eps` compatible with each of `a,b,c`; three direct exact square tests independently check this implication.

After removing zero, infinity, duplicates, and the three base values, build the complete exact graph on the remaining `d_eps`, with an edge exactly when `d_i*d_j+1` is a rational square. A `K4` supplies six mutual conditions, while its four vertices supply twelve conditions against the fixed triple and the triple supplies three conditions. Thus `6+12+3=21`; both full verifiers then check the resulting septuple.

### 4. Next falsifiable action

Freeze a manifest containing the source hash, triple, pair roots, model, isomorphism, `P0`, all twelve points, Boolean ordering, and expression count. Before enumeration, use two separately implemented general-Weierstrass group laws to verify the triple, all twelve points, the model transformation, the three torsion images, `P0`, and separated calibration subsets. Enumerate all 4096 expressions in each engine, emit canonical value and terminal ledgers, compare the deduplicated value sets exactly, then build and compare the complete compatibility graph and `K4` result. Send every `K4` candidate to both final verifiers.

### 5. Exit condition

- A `K4` candidate accepted by both full verifiers proves existence.
- Matching exhaustive ledgers and graph results with no `K4` give only `NO_HIT` for this fixed 4096-expression cube.
- Any point, map, expression-count, ledger, graph, or verifier disagreement is `FAILED`, not `NO_HIT`.
- After verified `NO_HIT`, close this route. Do not translate the cube, enlarge coefficients, add other rank-12 examples, or scan rank families.

Primary source: Dujella--Peral, *High rank elliptic curves induced by rational Diophantine triples*, arXiv:2005.10706. The frozen gzip source is `sources/highranktriples_2020_source.tar`, SHA-256 `3C0F200A895B4460E5A206112321AE05CBD7EA58263B369753FC68B1A7B8218E`; decompressed lines 185--192 define `E'` and `(0,abc)`, and lines 396--422 give the triple, minimal model, torsion, and twelve independent points. Exact-string searches found only the original paper and author record pages, not this Boolean cube. Dujella's 2026 survey still lists rational septuple existence as Problem 3.2.

### Closure (2026-07-20)

The corrected route specification has SHA-256 `67BF4C3DBBC59FC2D4DAE30B2A89D4C9A4C29D4B50595275C5C928F55F76EA45`; the final manifest has SHA-256 `0D757177AE3B036E7E42BFE0EEF3AE0B83FDE6A1A1983A52B850E434391B2C5A`. The primary engine has SHA-256 `8DDF66E09E64D86608A2A22C3445838853DC96E5140D2D8E62FFC614E9DC1086`, and the separately implemented engine has SHA-256 `D3D79A1BF45E2B40245FBAC2CF502072966FE12440CB9443964BFC7709CC9DA6`.

Both engines accounted for all 4096 masks and produced identical canonical expression, value, and edge ledgers with SHA-256 values `DC21CAB8C2D6F45E8A8F732E36E2748E4968C8D529412715963848A21E233623`, `D70BF32D49EDB92AA941A98F95FF8A66219081D4219608FA1CC31DDF68E78407`, and `A966061287F75B54EC5375E6A246FB4A02CD0B9D3337038479E1D4A689D743AB`. Mask zero gives the excluded value zero; the other 4095 masks give 4095 distinct retained values.

The complete graph has 8382465 tested pairs and 2047 edges. Its degree histogram is one vertex of degree zero and 4094 vertices of degree one. In provenance-mask terms, mask 1 is isolated and the edges are exactly `{2t,2t+1}` for `1<=t<=2047`. Thus the graph has no triangle and no `K4`.

The standalone comparison is `runs/rank12_boolean_cube_20260720T144330/comparison.json`, SHA-256 `CC2C3BDA5717093EBEAC72460E8ECAC558F4DDB161C8DDD97F52501FF9B42AF9`; the terminal referee is `terminal_referee.json`, SHA-256 `A9B3C54059E4944134C8D1E18A36FB24214D8453277BA2513014B8F2036C0CE8`.

Status: verified `NO_HIT` only for the frozen 4096-expression cube and its complete retained graph. This is not a nonexistence result for rational Diophantine septuples. The route is closed; no translation, coefficient enlargement, other rank-12 example, or rank-family scan will be performed.

## DIRECT ROUTE — terminal embedded-triple canonical shift

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and `verify_septuple_independent.py`.

### 2. Current frontier lemma / finite certificate

Freeze all 2001 sextuples in `sources/2001.sextuples.txt`. For each record and each of its `C(6,3)=20` position triples `(a,b,c)`, choose the nonnegative exact roots

`r^2=ab+1`, `s^2=ac+1`, `t^2=bc+1`,

and form the two canonical regular extensions

`d_eps=a+b+c+2abc+eps*2rst`, `eps in {-1,+1}`.

This gives exactly `2001*20*2=80040` signed contexts. There are 39490 distinct unordered triple keys and 530 repeated triple contexts, but every record/position/sign context remains in the ledger because repeated triples can have different complementary sextuple elements.

The finite certificate is either a distinct nonzero `d_eps` compatible with all three complementary sextuple values, or two matching exhaustive ledgers for all 80040 contexts.

### 3. Explicit logical bridge to the final deliverable

The exact identities

`a*d_eps+1=(a*t+eps*r*s)^2`,

`b*d_eps+1=(b*s+eps*r*t)^2`,

`c*d_eps+1=(c*r+eps*s*t)^2`

make `d_eps` compatible with the selected triple. The source sextuple supplies its 15 pair conditions. Exact square tests against the three complementary elements supply the only remaining three conditions. Hence `15+3+3=21`; a nonzero value distinct from all six source entries yields a septuple and is sent to both full verifiers.

Changing an odd number of signs of `r,s,t` only exchanges `d_+` and `d_-`; changing an even number leaves their labels fixed. Thus choosing the nonnegative roots and retaining both signs is complete.

### 4. Next falsifiable action

Freeze a manifest with the catalogue hash, parser contract, all record identifiers, the 20 lexicographic position triples, both signs, the exact 80040 count, degeneracy categories, canonical ledger format, and the two full-verifier hashes. Validate every source sextuple's 15 conditions. Use a `Fraction`/`isqrt` primary implementation and a separately coded normalized-integer rational implementation. Each must retain every `(record,position-mask,sign)` row, exact candidate, degeneracy class, and the three complement-test bits. Compare the full ledgers and send every survivor to both full verifiers.

### 5. Exit condition

- A survivor accepted by both full verifiers proves existence.
- Matching exhaustive ledgers with no survivor give only `NO_HIT` for these 80040 canonical-shift contexts.
- Any record, count, root, identity, ledger, or verifier disagreement is `FAILED`, not `NO_HIT`.
- This is the final catalogue-derived construction screen. After verified `NO_HIT`, do not run another catalogue transform or bounded catalogue family.

Frozen source evidence: `sources/2001.sextuples.txt` has SHA-256 `426551F283946C238E0B2FF54B8D2C1454B1717F701DCA7862FD8C98892AF933`. The earlier `catalog_scan.py` tested only catalogue-listed remaining values for each triple and did not generate these two canonical extensions. The multiseed route covered 341 selected shared non-`Z6x2` triples in declared lattice boxes; the closed `Z6x2` route covered one fixed triple. No prior workspace manifest exhausts all 80040 signed contexts. The construction is the regular Diophantine-triple extension, equivalently the canonical induced-curve shift. Dujella's 2026 survey still lists rational septuple existence as Problem 3.2.

### Closure (2026-07-20)

The final manifest is `runs/canonical_shift_all_20260720T151354/manifest.json`, SHA-256 `A10D6B34810E94D8362D976639778053F1ACA70A744F49B7DFED17266F670385`. The primary engine has SHA-256 `4DEA410B63DFD262077110F4A60B5CD2B3650CF35F294A530D57DCC15A35C92B`; the independent C++ source and executable have SHA-256 values `75924F8E3EA717FBB6E9A84F3E6385EF746A824CB439A305E8BDF146800C16DF` and `FE03B527B917133AD63A3513D346D419F9B6507590570E6DA2DBF7A8A8A695AD`.

Both engines and the independent terminal referee accounted for all 80040 signed contexts. Their canonical ledgers are byte-identical, contain 7,814,761 bytes, and have SHA-256 `E3FEAEB89D84656046C04E5D1310D20C328C00464F4813959DCD3C4561E856CF`. The degeneracy counts are 291 zero, 102 selected duplicate, 8416 complementary duplicate, and 71231 distinct nonzero candidates. No candidate passed all three complementary square tests while remaining distinct and nonzero.

The standalone comparison is `comparison.json`, SHA-256 `685241E0AC82371BB8648C50B53F684C1A57E3E91FE2DE98BBF04C8513C5438D`. The terminal referee is `terminal_referee.json`, SHA-256 `4CBE81A5E4A7C6E6960E290818EF944FC39D7F67C0945D7B2D17B95696C23BD8`; it independently reconstructed every row and matched both ledgers, summaries, and survivor files. There were zero survivors, so no full-verifier invocation was required.

Status: verified `NO_HIT` only for the frozen 80040 canonical-shift contexts. This is not a nonexistence result for rational Diophantine septuples. The catalogue-derived construction route is closed; no further catalogue transform or bounded catalogue family will be run.

## DIRECT ROUTE — exotic regular-conjugate Kummer cover

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and the separately implemented `verify_septuple_independent.py`.

### 2. Current frontier lemma / finite certificate

Use the Dujella--Kazalicki--Petričević exotic-triple curve

`C: 3*r^2*s^2 - 4*r^2 - 2*r*s - 4*s^2 + 7 = 0`,

with

`a=r^2-1`, `b=s^2-1`, and `c=(-r^2*s^2+2*s^2+2*r^2-5)/2`.

Then `{1,a,b,c}` is a regular Diophantine quadruple and `{1,ab,c}` is a regular triple. Put

`L=abc-1`, `K=2ab+1+a+b-c`, `M=(a+1)(b+1)(ab+1)`,

and let

`e=(4*M*c-2*L*K)/L^2`.

Away from the bad locus, `Q={1,a,b,c,e}` is a regular Diophantine quintuple.

For an ordered quadruple `(p,q,u,v)` and a known regular-quintuple root `x`, define its conjugate root

`Phi(p,q,u,v;x)=(B^2-4*N)/(A^2*x)`,

where `A=p*q*u*v-1`, `B=2*p*q*u+p+q+u-v`, and `N=(p*q+1)(p*u+1)(q*u+1)`.

Fix only

`f=Phi(a,b,c,e;1)` and `g=Phi(1,a,b,e;c)`.

The frontier is a nondegenerate rational point on the single Kummer cover of `C`

`z1^2=f+1`, `z2^2=c*g+1`, `z3^2=f*g+1`.

### 3. Explicit logical bridge to the final deliverable

The quintuple `Q` supplies ten pair conditions. By the regular-conjugate equation, `f` is compatible with `{a,b,c,e}` and `g` is compatible with `{1,a,b,e}`. The first two Kummer equations supply the omitted pairs `(1,f)` and `(c,g)`, while the third supplies `(f,g)`. Hence `Q union {f,g}` has all `10+4+1+4+1+1=21` required square conditions. Bad-locus saturation enforces seven distinct nonzero values, and both full verifiers check the certificate from the seven rationals alone.

### 4. Next falsifiable action

Reconstruct `C,a,b,c,e,f,g` in `Q(C)` from the two primary papers and independently verify the regular identities and all automatically supplied square conditions. Reduce the three residual functions to exact square classes. Certify their geometric Kummer rank and branch divisors using exact function-field algebra plus independent smooth local witnesses. Apply Riemann--Hurwitz to every horizontal component. Continue to rational-point determination only for a rational component, a genus-zero component with a Q-point, a genus-one component with an exact Q-point, or a genus-two component with certified Jacobian rank below two and a complete Chabauty/sieve route.

### 5. Exit condition

- A nondegenerate rational point producing a candidate accepted by both full verifiers proves existence.
- An identity square or a certified component of genus at most two advances directly to exact rational-point determination.
- If every Q-defined horizontal component has genus above two, geometric certification is infeasible, or verifier identities disagree, record `INCONCLUSIVE` and close this route.
- Do not switch to any of the other five conjugate pairs, scan rational parameters, enumerate Mordell--Weil coefficients, or enlarge this construction after closure.

Primary sources: https://arxiv.org/abs/2604.08729 for the exotic family and its rank-one parameter curve, and https://arxiv.org/abs/1904.00348 for the regular-quintuple conjugate equation. Exact audits of all five examples in the 2026 paper show that neither regularity alone supplies a sixth element: the four nonzero conjugates each fail exactly their omitted pair, and the fifth conjugate is zero. A targeted current-source search found no treatment of this fixed three-square conjugate cover. The June 2026 survey and the source paper both state that no rational Diophantine septuple is known.

### Closure (2026-07-20)

The primary exact function-field engine is `engine/exotic_conjugate_primary.py`, SHA-256 `B237F6A69154F89FEE4F287D93EB01E9E748AC472D41CC09A1F801BD238580D8`. It verifies six family identities modulo `C`, seven source square identities, the generic conjugate-root transfer, and every source/quintuple/automatic pair identity in all five printed examples. Its canonical and replay artifacts are byte-identical. The primary summary is `runs/exotic_conjugate_kummer_20260720T162430/primary/summary.json`, SHA-256 `44A5D5A2C787C5D097C55B10139EDB575AFFF9607B11B39D762AD9B5A920490E`; the three residual normal forms have combined SHA-256 `3BC14C9BA6A1FC4FFC792B9E3D2D82FD5BC615ABAEC7EB885EC209847B77324D`.

An independent direct dual-number engine found three smooth transverse characteristic-zero branch places, certified by the reductions `(p,r,s)=(139,24,111),(223,70,97),(163,44,53)`, with odd-valuation rows `(1,0,0),(0,1,0),(0,0,1)`. All registered denominators and bad-locus factors are units at the reductions. The canonical and replay witness reports are byte-identical with SHA-256 `37DD1F6B3D8CC3302ECBEEB54AB1DBC6C732186216CB7EB15BE8BB2A04F6D875`.

The independent referee verifies that `C` is a smooth geometrically irreducible genus-one curve and that the three residual square classes have geometric rank three. Hence the normalized Kummer cover is geometrically connected of degree eight. Each principal divisor has even total odd-valuation parity; since the three witnessed rows xor to `(1,1,1)`, there is at least one further branch place. Thus the total branch count satisfies `B>=4`, and Riemann--Hurwitz gives `2*g(X)-2=4*B`, so `g(X)=1+2*B>=9`. The referee report is SHA-256 `30CD1736D023478527B0DA5F37C8F3B712AD90C9E087E766BCFDCC4058873A4C`; the terminal referee is SHA-256 `45BB748C1157A2551C3239FD34E141B72980BBDB41100754ED64AB2883FFD642`.

Status: `INCONCLUSIVE` for rational points on this fixed cover. No septuple candidate was produced, and no global nonexistence statement follows. The registered genus-at-most-two continuation gate fails, so this route is closed. No other conjugate pair, rational-parameter scan, Mordell--Weil coefficient enumeration, or enlarged version of this construction will be run.

## DIRECT ROUTE — fixed canonical-order-four genus-two quotient

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and the separately implemented `verify_septuple_independent.py`.

### 2. Current frontier lemma / finite certificate

Fix the published Dujella--Peral regular triple

`a=1884586446094351/25415891646864180`,

`b=14442883687791636/7402559392524605`,

`c=60340495895762708555/14487505263205637124`.

On the scaled induced curve

`E: y^2=(x+p)(x+q)(x+r)`, with `p=ab`, `q=ac`, `r=bc`,

put `P=(0,abc)` and `S=(1,r_ab*r_ac*r_bc)`. Exact group law gives `S` order four and, after the displayed labeling, `H=2S=(-p,0)`.

For a variable point `T`, the four values

`d_i=x(T+iS)/(abc)`, `i=0,1,2,3`,

have the four cyclic compatibility edges automatically. The first diagonal descends through `E/<H>` to the genus-two curve

`C2: V^2=U*(U^2-2*A0*U+A0^2-4*(1+p)^2), Z^2=p*(U0-U)`,

where `A0=q+r-2p` and `U0=(1+p)*q*r/p`.

The frontier is a proved complete list of `C2(Q)`, followed by exact lift and coset tests.

### 3. Explicit logical bridge to the final deliverable

Every point on the full two-diagonal cover maps to `C2(Q)`. A point `(U,V,Z)` with `U=t^2 != 0` lifts to `E(Q)` by

`u=(U-A0-V/t)/2`, `x=u-p`, `y=t*u`,

using both signs of `t`; `U=0` is tested separately. With `j=q+r+2`, translation by the image of `S` gives

`U_J=j+4*j*(1+p)/(U-j)`,

and the second diagonal is exactly the test `p*(U0-U_J) in Q^2`. Requiring `T-P in 2E(Q)` makes all four `d_i` extensions of `{a,b,c}`. The base triple supplies three conditions, the four extensions supply twelve, the automatic cycle supplies four, and the two diagonal tests supply the remaining two: `3+12+4+2=21`. Distinctness, nonzero checks, and both full verifiers complete the certificate.

### 4. Next falsifiable action

Freeze the exact triple, pair roots, curve, quotient map, `C2` model, and both lift formulas. Replay `4S=O`, `2S=(-p,0)`, the four automatic edges, and the quotient identities in two exact implementations. Submit one frozen Magma V2.29-8 job for `RankBounds(Jacobian(C2))`. Continue only if the proven upper rank is at most one: then obtain a complete `RationalPointsGenus2`/Chabauty--sieve list, replay every point and lift, test the extension coset and both diagonals, and send every survivor to both 21-pair verifiers.

### 5. Exit condition

- A candidate accepted by both full verifiers proves existence.
- A complete rational-point list with no surviving lift proves only that this fixed triple yields no septuple through the order-four orbit.
- Rank upper bound above one, unequal bounds, incomplete point output, timeout, or verifier disagreement is `INCONCLUSIVE` and closes the route.
- Do not change the triple, scan the order-four parameter curve, enumerate Mordell--Weil coefficients, or replace the quotient by a height box.

Primary source: Dujella--Peral, https://arxiv.org/abs/1712.02082, Section 5. The quotient derivation and the proof that its putative elliptic degeneration is impossible are preserved in `runs/next_route_audit_20260720T171905/order4_genus2_quotient.md`, SHA-256 `7909C6EB9741F7C6560243E3BDA343B5D738ABD1DE4F1DD401BE85F34A71625C`. The fixed-source checker is `engine/order4_fixed_triple_check.py`, SHA-256 `F88A731BC57547D3E6D18D51B039953477E53C539E4E0216436EF37DFA36FC39`.

### Closure (2026-07-20)

The primary exact engine produced the smooth genus-two model and replayed all registered identities. Its model and check hashes are `F243AA665B520CFFF7DC6355A01BEC46625EB35CE39EA5E6A0AD131E5B1C575E` and `0265736814552239E95DF8975181E37A9408AD3FE14DC802BF291D8E47C6DE17`. The frozen public Magma V2.29-8 `RankBounds` job for the first elliptic quotient exceeded its 60-second limit without returning a bound. Under this route's exit condition the direct genus-two rank job is `INCONCLUSIVE` and closed. No rational-point or septuple conclusion follows.

## DIRECT ROUTE — fixed order-four bielliptic rank-zero gate

### 1. Exact final deliverable

Seven pairwise distinct nonzero rationals with exact roots for all 21 products-plus-one, accepted by `verify_tuple.py` and the separately implemented `verify_septuple_independent.py`.

### 2. Current frontier lemma / finite certificate

For the same fixed triple and genus-two curve, exact elimination gives an even sextic

`C: W^2=g(X^2)`, where `g(u)=c3*u^3+c2*u^2+c1*u+c0`.

It has two degree-two elliptic quotients

`E_plus: y^2=g(u)`, with `(X,W) -> (u,y)=(X^2,W)`, and

`E_minus: v^2=u*g(u)`, with `(X,W) -> (u,v)=(X^2,X*W)`.

The Jacobian of `C` is Q-isogenous to `E_plus x E_minus`. The frontier is a certified rank-zero result for either fixed quotient, followed by its complete torsion list and every rational square-coordinate lift back to `C`.

### 3. Explicit logical bridge to the final deliverable

Every rational point of `C` maps to both elliptic quotients. If either quotient has rank zero, its rational points are exactly its finite torsion subgroup. Testing every torsion image for the required rational square `u=X^2` therefore gives a complete list of rational lifts to `C`; it cannot omit a two-diagonal orbit. Each lift is mapped back to `(U,V,Z)`, then through the registered lift to `E`. Exact tests of `T-P in 2E(Q)`, the second diagonal, distinctness, and nonzero values leave exactly the septuple candidates, which must pass both 21-pair verifiers.

### 4. Next falsifiable action

Freeze direct Weierstrass and minimal integral models for `E_plus` and `E_minus` and replay their maps in two exact implementations. Run eclib 20231211 on each fixed minimal model with `mwrank -q -v 2 -p 80 -b 4 -x 15 -S -1`, one single-thread process per quotient, with TERM at 3600 seconds and forced KILL after a 10-second grace period. The `b=4` step is the internal finite quartic-representative search in the descent, not a Mordell--Weil height box. Independently run the bundled open-source PARI 2.15.4 `ellrank(E_plus,0)` on the same frozen minimal model, one thread with the same termination policy; effort zero disables randomized extra point search and returns unconditional algebraic lower and upper bounds. Accept rank zero only when a proof-grade output has both bounds equal to zero and the exact model matches both frozen reconstructions. If either quotient has certified rank zero, enumerate its complete torsion subgroup in two implementations and exhaust all rational square-coordinate lifts. Do not enumerate free Mordell--Weil coefficients, point heights, triples, or parameters.

### 5. Exit condition

- A candidate accepted by both full verifiers proves existence.
- A complete torsion-lift list with no survivor proves only that this fixed order-four orbit yields no septuple.
- After both eclib runs and the fixed PARI `E_plus` run terminate, positive certified lower rank for both quotients, bounds that do not certify rank zero, timeouts, or tool failure close this gate as `INCONCLUSIVE`.
- Do not change the fixed triple, scan parameters, start a point-height search, or add another quotient after closure.

The canonical exact model is `runs/order4_genus2_quotient_20260720T175340/model.json`, SHA-256 `F243AA665B520CFFF7DC6355A01BEC46625EB35CE39EA5E6A0AD131E5B1C575E`. The primary engine is `engine/order4_genus2_primary.py`, SHA-256 `BEBE050B14E9A637D586497D779A4D82B2B093103052E99CF9E723B4EB6628CF`.

### Closure (2026-07-20)

The direct and minimal quotient models were replayed exactly. The transform audit is `runs/order4_genus2_quotient_20260720T175340/open_source_rank/minimal_transform_audit.json`, SHA-256 `69437067910BF995C2597145AE2680AA4EBD1DECE045ACBBF8897BF9F1EBAE7F`. Completed eclib Selmer-only runs give unconditional bounds `0 <= rank(E_plus) <= 2` and `0 <= rank(E_minus) <= 4`; their transcript SHA-256 values are `299EDD59FED88650C2EE66D22ADF7F2EDDFFA29EC6DBBFBA144669915AC1A7CD` and `8BF8FC95FE19CF107C444E902E8663F0AF3D1BABEADDB680CFF20412F858193F`.

Both fixed full eclib descents terminated at the registered wall limit with exit code 124 and no final rank line. Their stdout SHA-256 values are `6E1F91D4B33DFBC92F6F5D90195063E6082BE1F57E8CD946746906AB8E2AEADB` and `263DBB2A74DF10565EEF6BB42AAE1DBEF7982E97FF8F10395269A86EB624E304`. The independent PARI `ellrank(E_plus,0)` run also terminated with exit code 124 and empty stdout/stderr; its manifest has SHA-256 `72869CBD6607A9C37D2833A55BDDCFC61E7BDF1A112AAB22D1B5973A7C4AA6C6`.

An exact independent replay exhausted all 1024 second-descent squareclasses for the sole residual `E_plus` class. It excluded 960 by Hilbert symbols, 32 over the reals, and 30 by finite modular certificates. The two uneliminated classes are `132824558855468387` and `126343745097312156441529487`; therefore neither rank zero nor rank two is certified. The audit and pure-Python verifier have SHA-256 values `9F3A5675E081FBE6955D544EF4E2367FEDAF30857FE725E1DF1FB36CEF4DBC3A` and `309BB6BEB00A60E44212F3A7FBB78401FA21781478AC1272273B6A885ABD9AEF`.

Conditionally on `rank(E_plus)=0`, two independent exact implementations exhausted its torsion lifts and found 8 signed lifts to `C`, 16 raw lifts to the induced curve, 8 unique extension values, and zero septuple candidates. The primary and referee reports have SHA-256 values `911BA5B5B3E0A86D502AF04030FF05F8B0504FBF906990C1B04265141FD181F1` and `3489E7D5BE5129E75E9DEA37826A7C3875553F3A27CC5BCCF450C3FCF13375AC`.

Status: `INCONCLUSIVE`. No quotient rank-zero certificate, complete rational-point list, or septuple certificate was obtained. The fixed order-four bielliptic gate is closed under its registered exit condition; its conditional torsion computation is not an unconditional negative result. No fixed-triple, parameter, Mordell--Weil-height, or additional-quotient continuation is authorized by this route.

## Terminal direct-route audit (2026-07-20)

No further direct elliptic-curve route is registered. Exact reduction of the induced-curve translation identity shows that compatibility is forced identically only for a translation point with `x(R)=1`. That fiber contains at most the two points `R` and `-R`, so the identity-forced compatibility graph has maximum degree two and cannot contain the required `K4`. The order-four construction therefore supplies only a cycle and leaves two independent diagonal conditions.

The audited regular-extension mutations do not replace this missing bridge: their residual square conditions give genus-three, genus-four, or genus-seventeen covers rather than a single genus-at-most-two gate. The literature audit found no parametric common-quintuple construction with two compatible sixth elements that would supply a direct seven-value certificate.

The specific missing bridge is a theorem or identity that makes one finite low-genus rational-point computation sufficient for all six compatibility edges among four extensions. Without such a bridge, another fixed triple, parameter scan, height box, quotient, or catalogue family would be a sequence of restricted exclusions rather than a route to the global deliverable. Under the DIRECT-PROOF GUARD, work stops here unless a new direct route satisfying all five registry fields is supplied.

The terminal obstruction was strengthened by an exact isogeny-rigidity audit. For `D in 2E(K)`, the compatibility function `F_D(T)=x(T)x(T+D)+alpha^2` becomes a square after an arbitrary characteristic-zero isogeny pullback exactly when `x(D)=1`; otherwise its compatibility cover has genus 3, and degree-`n` pullback has genus `1+2n`. The omitted regular-extension-root construction was also audited on all four `G=0` components: its two residual square classes are geometrically independent, its three intermediate covers have genus at least 9, and its connected `V4` cover has genus at least 17. The preserved proof is `runs/terminal_route_audit_20260720T200600/elliptic_identity_and_double_extension_audit.md`, SHA-256 `549C5D1CBB41396B7FA6E6DA8DB001F65C171FC5141AE6928DCCB2F9029B0AB8`. These strengthen the missing-bridge certificate but do not prove global nonexistence.

## Rejected alternatives

- 3x3 magic square of distinct squares: more publicly famous and exactly equivalent to an arithmetic progression of doubled x-coordinates on congruent-number curves, but it requires ranging over infinitely many twists and has a heavily saturated direct search.
- Perfect cuboid: elliptic curves parametrize fibers, but extra simultaneous-square lift conditions carry the unsolved difficulty; bounded fiber exclusions do not close the global problem.
- Unit-square four rational distances: current geometry is a higher-dimensional surface; elliptic curves control slices rather than the complete target.
- Canonical order-four orbit: DKMS Proposition 1 supplies a `C4`, not a `K4`. The published regular branch collapses to two repeated values (one zero); an independent point leaves a genus-nine two-diagonal cover without a complete rational-point bridge. Audit: `runs/next_route_audit_20260720T171905/audit.md`.
