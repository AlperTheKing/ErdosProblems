# Verdict: the Three-Row (3x8) Order-Polytope Transfer Route

## Bottom line

**Not a counterexample. Dead route with an exact obstruction. KTT LR(iv)
remains OPEN.**

The proposal was to realize the negative-Ehrhart order polytope `O(P_{7,7})`
as an exact `3x8` transportation polytope and carry its negative Ehrhart
coefficient through `tableau -> skew-Kostka -> LR`. The three-row route does
genuinely **evade** the obstruction that this project's earlier file leaned on
as a theorem (Jochemko--Menon skew-GT Ehrhart positivity does not even cover a
fixed-both-margins transportation polytope), and it evades the two-row-specific
count obstruction and the face/product obstructions. It nonetheless **dies**,
on two independent, computationally established facts:

1. **Direct realization is impossible (decisive, rigorous).** Every
   codegree-3 `3x8` transportation polytope has base lattice count
   `L_T(1) >= 1050`, whereas the target has `L_O(1) = 255`. The Ehrhart
   polynomials disagree at `n=1`, so no `3x8` transportation polytope is
   Ehrhart-equal to `O(P_{7,7})`. Decisive number: **1050 vs 255**.
2. **No negative input exists in the family.** The entire dimension-14
   codegree-3 `3x8` transportation family is Ehrhart **positive**: the minimum
   linear coefficient is `2157/280 = 7.7036 > 0`, attained at the minimal
   member `r=(3,3,3), c=(2,1^7)`; the minimum over *all* coefficients of that
   member is `128114573/29059430400 > 0`; no member scanned has any negative
   coefficient. There is no negative Ehrhart input for the (valid) transfer to
   carry.

Because no negative transportation input survives, no partition triple is
produced, and the direct stretched-LR test is never reached: there is nothing
to feed the LR engines. The two-engine + interpolation discipline is satisfied
vacuously (no candidate negative was ever reported).

---

## 1. The object and the genuine gap

A `3xN` transportation polytope
`T(r,c) = { x in R_{>=0}^{3xN} : row sums = r, column sums = c }`
with all-positive integer margins is full-dimensional of dimension
`(3-1)(N-1) = 2(N-1)`; degree 14 forces `N=8` uniquely. Its Ehrhart function
`L_T(n)` counts nonnegative integer `3x8` matrices with margins `(n r, n c)`.

The two-row obstruction in
`NEGATIVE_ORDER_POLYTOPE_LR_TRANSFER_OBSTRUCTION.md` §4 is specific to a
`2 x k` contingency table: matching degree 14 forces `k=15`, codegree-3
uniqueness forces first-row sum `A=5`, giving `L(1) >= C(15,5) = 3003 != 255`.
That argument is a two-row fact (a product of `k` interval polynomials, unique
interior coefficient only at an endpoint). The three-row transportation
polytope is a different object; it does **not** inherit the `k=15 / C(15,5)`
contradiction. This is the real gap the proposal identified.

The three-row route also sidesteps the theorem in §2 of the obstruction file.
Jochemko--Menon (arXiv:2604.08394, Thms 3.5 / 1.5) prove Ehrhart positivity for
skew Gelfand--Tsetlin / integral marked-order polytopes, which fix the boundary
shape but let the **content vary**. A transportation polytope fixes **both**
margins; it is exactly the fixed-content (weight-sliced) skew-GT object, i.e. a
linear slice of a content-varying skew-GT/marked-order polytope by global
content-sum equations. Those equations are global sums, not marked coordinates
of the underlying poset, so `T(r,c)` lies **outside** the Jochemko--Menon
class. Consequently obstruction (1) does **not** kill the three-row route as a
theorem. (Affine-invariant sanity: `O(P_{7,7})` has 63 facets; a `3x8`
transportation polytope has at most `3*8 = 24` facets, so `O(P_{7,7})` is not
itself any `3x8` transportation polytope. This rules out affine equivalence,
which is stronger than the Ehrhart equality the transfer actually needs; the
Ehrhart-equality kill is §3 below.)

---

## 2. Codegree of `3x8` transportation polytopes (derived and verified)

A relative-interior lattice point of `n T` is a strictly positive integer
`3x8` matrix with margins `(n r, n c)`. Subtracting the all-ones matrix, such a
matrix exists iff `n*min(r) >= 8` and `n*min(c) >= 3` (2D transportation
feasibility with consistent nonnegative margins is otherwise automatic). Hence

```
codegree = max( ceil(8 / min r), ceil(3 / min c) ).
```

`codegree = 3` iff `[ min r = 3 ]` OR `[ min r >= 4 and min c = 1 ]`
(two cases: (A) `min r = 3`, any column margins; (B) `min r >= 4`,
`min c = 1`). Verified directly:

| member | case | codegree (interior counts `n=0..3`) | `L(1)` | `a_1` |
|---|---|---|---|---|
| `r=(3,3,3), c=(2,1^7)` | A (minimal) | 3 (`0,0,0,1`) | 1050 | `2157/280` |
| `r=(4,4,4), c=(5,1^7)` | B | 3 | 1890 | `317/35` |
| `r=(5,5,5), c=(8,1^7)` | B | 3 | 2142 | `275/28` |

The minimal member has a **unique** interior point at dilation 3 (interior
counts `0,0,0,1`), exactly matching `L_O(-3)=1` and `h*_12 = 1`; its
`h*`-polynomial has degree 12 and codegree 3 — the same `(dim, codegree,
h*-degree)` shape as `O(P_{7,7})`, but different `h*` entries and a different
base count.

---

## 3. Kill 1 — the count/codegree contradiction (three-row analogue, exact)

**Claim.** `L_T(1) >= 1050` for **every** codegree-3 `3x8` transportation
polytope, for any margins (not only the proposal's `c=(N-7,1^7)`).

**Proof.** Ehrhart / lattice count is invariant under permuting rows and
columns, so sort margins ascending. Codegree 3 forces `min r >= 3`, so the
sorted row margin dominates `(3,3,3)` componentwise. It also forces the total
`S = sum r >= 9` over 8 positive column parts, so the largest column part is
`>= 2` and the sorted column margin dominates `(1,1,1,1,1,1,1,2)`
componentwise. Adding 1 to a single matrix cell `(i,j)` is an injection
`T(r,c) -> T(r+e_i, c+e_j)` (undo by subtracting 1 from cell `(i,j)`), so
`L(r,c) <= L(r+e_i, c+e_j)`. Composing `S-9` such cell increments — the
matched row-token / column-token increments taking `(3,3,3),(2,1^7)` up to any
dominating `(r,c)` — gives
`L_T(1) = L(r,c) >= L((3,3,3),(2,1^7)) = 1050`. QED.

The target has `L_O(1) = 255 < 1050`. Two Ehrhart polynomials that disagree at
`n=1` are different polynomials, so **no `3x8` transportation polytope is
Ehrhart-equal to `O(P_{7,7})`**. The direct proposal dies here.

Verification (independent):
- `L((3,3,3),(2,1^7)) = 1050` confirmed by three independent counters
  (per-column DP, region-sum DP, partial-row-sum DP): all agree.
- Componentwise sorted-domination and `L(1) >= 1050` checked on all 107
  codegree-3 members with rowsum `<= 14`; cell-increment monotonicity checked
  on 200 randomized trials — all held.

---

## 4. Kill 2 — the family is Ehrhart positive (no negative input at all)

The escape "use a *different* negative `3xN` transportation polytope, not
`O(P_{7,7})`" also fails. Scanning all 107 codegree-3 `3x8` members with rowsum
`<= 14` (exact Ehrhart polynomial by interpolation from `n=0..14`, held-out
verified at `n=15,16`, `L(0)=1` enforced):

- **No member has any negative Ehrhart coefficient.**
- Minimum **linear** coefficient over the family: `2157/280 = 7.7036 > 0`,
  attained uniquely at the minimal member `(3,3,3),(2,1^7)`; the coefficient
  grows or saturates away from it (`a_1 = 317/35` at `(4,4,4),(5,1^7)`,
  `275/28` at `(5,5,5),(8,1^7)`, etc.).
- Minimum over **all** coefficients of the minimal member:
  `128114573/29059430400 > 0`.

So the transfer, even though its bridge is valid, has no negative Ehrhart input
in the three-row transportation family to transport.

Scope note: Kill 2 is a computational fact over the scanned range (plus the
proven family-wide `L(1) >= 1050` of Kill 1). Kill 1 alone is a complete,
range-independent refutation of the literal proposal (realizing `O(P_{7,7})`);
Kill 2 closes the "some other negative transportation polytope" escape over the
scanned region and exhibits the positive minimum.

---

## 5. No triple, no stretched-LR test; engines calibrated

Because no negative transportation input survives Kills 1--2, the chain never
produces a partition triple, so the direct stretched-LR test
`P(t) = c(t nu; t lam, t mu)` is not reached. For the record, both LR engines
were confirmed alive and cross-calibrated on the `c=2` control triple
`lam = mu = (2,1), nu = (3,2,1)` (stretched value must be `P(n) = n+1`):

```
engine B  (n=1,2,3): 2, 3, 4
engine A  (n=1,2,3): 2, 3, 4      # engine/lr_hive.exe, agrees
```

Had a negative candidate appeared it would have been re-verified with both
engines plus independent interpolation before any report; none appeared.

---

## 6. Relation to `NEGATIVE_ORDER_POLYTOPE_LR_TRANSFER_OBSTRUCTION.md`

That file's verdict (direct transfer of `O(P_{7,7})` is dead) stands, and this
document extends it to the three-row case rather than superseding it:

- **Obstruction (1)** (skew-GT/marked-order Ehrhart positivity, Jochemko--Menon):
  does **not** reach the three-row transportation object as a theorem — a
  fixed-both-margins transportation polytope is a content-slice outside the
  J--M class. The route evades (1) as stated. Positivity for this specific
  family is instead re-established here computationally (§4).
- **Obstruction (2)** (fixed content is a non-marked global fibre): consistent
  with this verdict — the transportation route supplies fixed content directly,
  so this is not what kills it.
- **Obstruction (3)** (two-row parsimonious Kostka reduction, `k=15`,
  `C(15,5)=3003 != 255`): two-row specific. Its **three-row analogue is
  supplied here**: `L_T(1) >= 1050 != 255` for every codegree-3 `3x8`
  transportation polytope (§3). This is the decisive kill of the direct
  proposal.
- **Obstructions (4),(5)** (proper faces / nontrivial products change the
  count): unchanged; the three-row route uses a full-dimensional polytope, not
  a face or product, so they are not what kills it.

The exact negative order polytope `O(P_{7,7})` remains a genuine obstruction to
generic `h*`-shape and alcoved-positivity arguments. It is still not an LR
counterexample: producing one requires an LR hive polytope with a negative
Ehrhart coefficient, which the three-row transportation family does not deliver.

---

## 7. Reproduction

```
# target order polytope (unchanged checker) -> PASS
python problems_external/ktt_lr_negativity/order_polytope_lr_transfer_obstruction.py

# three-row transportation Ehrhart engine self-test (naive == fast counters)
python problems_external/ktt_lr_negativity/transport3xN_ehrhart.py

# decisive numbers: minimal member + codegree-3 family scan
python problems_external/ktt_lr_negativity/verdict_3row_driver.py

# rigorous L(1) >= 1050 monotonicity + engine calibration inputs
python problems_external/ktt_lr_negativity/transport3row_monotone_check.py
```

File SHA-256:

```
transport3xN_ehrhart.py            cb4c512b0e1a3a31aa1256c1f957f27b427beb0f99a00f21da2fd1a4e3cfca7d
verdict_3row_driver.py             9b86e8f174ac2af4f68a75c1ebc1c1cc22e31251057928e6ed198cb1bc859973
transport3row_monotone_check.py    a2e89b2f4e054a23b7420c7f3d4f428bd26bae70e0db6d8311e3ae9d60e03d56
order_polytope_lr_transfer_obstruction.py  4b79741bcfb710a2540e80f9927d24592f70310fa4a6a8055aa65fc5393b116f
```

Exact data reconciled:
`O(P_{7,7})`: dim 14, 63 facets, 255 vertices, `h* = A_7(z)^2`, `h*`-deg 12,
codegree 3, `L(1)=255`, `a_1 = -3041/1430`, `L(-1)=L(-2)=0`, `L(-3)=1`.
Minimal `3x8` transportation member `(3,3,3),(2,1^7)`: dim 14, codegree 3
(interior `0,0,0,1`), `L(1)=1050`, `a_1 = 2157/280`, min coeff
`128114573/29059430400`, `h*`-deg 12.
