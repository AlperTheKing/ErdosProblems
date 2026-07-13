# Minimal-deficient-shore reduction for `CommonBlueExtendedMatching`

## Result

The exact useful reduction is to **owner shores**, but not by claiming that an inclusion-minimal demand shore is owner-complete.

For fixed `G,c,omega`, define the owner fiber `D_v = {d | demandOwner d = v}` and

`N(v) = {s | ExtendedAvailable G c d s}` for any `d in D_v`.

This is well-defined because the production definition uses `d` only through `demandOwner d`; `ScopedReserved G c omega s` is independent of `d`. Hence demands with the same owner have identical neighborhoods.

**Owner projection theorem (exact, no graph hypotheses):** `HallCondition G c omega` is equivalent to

`forall W : Finset (Fin G.n), card (univ.filter (fun d => demandOwner d in W)) <= card (univ.filter (fun s => exists v in W, exists d, demandOwner d=v and ExtendedAvailable d s))`.

Proof of the nontrivial direction: if a demand shore `A` is deficient, let `W=owner(A)` and replace `A` by `D(W)=union_{v in W} D_v`. Then `A subset D(W)`, while `N(A)=N(D(W))` because every owner in `W` already occurs in `A` and all members of one owner fiber have identical neighborhoods. Thus `|D(W)| >= |A| > |N(A)|=|N(D(W))|`.

Consequently a universal proof need only exclude deficient full owner shores. This reduction needs neither `CompleteShortestRowDB` nor selector descent/PHT; the DB hypotheses enter only in proving the owner inequalities.

## Inclusion-minimal structure and uncrossing

Put `d(W)=sum_{v in W}|D_v|`, `N(W)=union N(v)`, and integer defect `delta(W)=d(W)-|N(W)|`.

- `delta` is supermodular: `delta(A)+delta(B) <= delta(A union B)+delta(A intersection B)`. Demand is modular; neighborhood cardinality is submodular, using `N(A union B)=N(A) union N(B)` and `N(A intersection B) subset N(A) intersection N(B)`.
- If `W` is inclusion-minimal deficient, every proper `U subset W` has `delta(U)<=0`. For each `v in W`, the number of sources private to `v` relative to `W` is at most `|D_v|-delta(W)`, and `delta(W)<=|D_v|`.
- A safe canonical closure is neighborhood saturation `sat(W)=W union {v | N(v) subset N(W)}`. It has exactly the same neighborhood and defect at least `delta(W)`. Iteration is unnecessary because its neighborhood is unchanged.
- If minimal deficient `A` and deficient `B` cross with `A intersection B` proper in `A`, supermodularity gives `delta(A union B) >= delta(A)+delta(B)-delta(A intersection B) >= delta(A)+delta(B)`.

These conclusions do not supply a matching or a common-blue source; they only normalize the shore.

## Exact countermodels to stronger reductions

1. **Minimal demand shore need not contain all demands of its owners.** One owner has three demands, all with neighborhood `{s}`. Any two demands form an inclusion-minimal deficient shore: demand 2, reach 1, defect 1; it omits the third demand. Owner completion remains deficient (demand 3, reach 1), which is exactly why the existence reduction above is valid.

2. **Arbitrary graph-component closure is false.** Put owners `a,b` in one declared component, with demands `(2,1)` and neighborhoods `N(a)={x}`, `N(b)={y,z}`. Shore `{a}` has `(demand,reach,defect)=(2,1,1)`, but component closure `{a,b}` has `(3,3,0)`. A component-closure lemma therefore requires the exact extra condition `N(v) subset N(W)` for every added owner (or another condition implying no more new sources than new demand). Production `ExtendedAvailable` contains a global common-blue disjunct, so component membership alone does not imply this.

3. Minimality gives an upper, not lower, bound on private sources. Thus it cannot by itself produce ownerwise distinct sources.

## Exact finite gates

`shore_reduction_gate.py` exhaustively checked 13,824 three-owner/three-source weighted incidence systems (owner demands 1,2,3), 110,592 owner shores, and 25,368 inclusion-minimal deficient shores. It checked supermodularity, all deletion/private-source bounds, and neighborhood saturation with integer/Fraction arithmetic only.

The same script pins and validates the available complete-DB common-blue census summaries:

- N=12: 1,144,061 generated graphs; 22,291 medium/heavy graphs; 18,961,358 complete coherent tuples; all 8,224 old failures repaired; zero remaining.
- R29 (N=2943 all-anchor complete singleton-row DB): all 8 hub owner shores pass; full shore demand/reach `19953/20141`, slack 188. The minimum slack over the eight shores is 0 because the empty shore is included.

These are finite regression gates, not evidence that the owner inequalities hold universally. No other hard fixture result was imported because no completed literal-common-blue result artifact was present in the fanout directories at execution time.

## Recommended Lean frontier

Formalize only the graph-free owner projection equivalence and supermodularity/saturation lemmas. Do **not** formalize “minimal demand shores are owner-complete” or component closure. The remaining mathematical wall is the owner-shore statement:

`forall W, d(W) <= |N(W)|`

under triangle-free, max-cut, B-connected, Gamma-minimal, complete shortest-row DB hypotheses. Shore normalization alone does not prove it.

## Replay

From this directory:

`python shore_reduction_gate.py`

The command rewrites `result.json` deterministically and exits zero after all assertions.
