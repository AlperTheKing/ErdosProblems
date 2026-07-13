# Direct N=12 full-product heat-bath gate

## Exact statement tested

Fix an order-12 connected triangle-free graph `G`, the Gamma-minimum
connected maximum cut selected by the existing census, and its `m` complete
shortest-row families `R_0,...,R_{m-1}` (all bad-edge lengths are five).  The
full simultaneous heat-bath space is

`Omega_G := product_{i=0}^{m-1} {0,...,|R_i|-1}`,

so `K_G := |Omega_G| = product_i |R_i|`.  For `eta in Omega_G`, `S(eta)` is
the exact active-scoped collision-plus-HitNeed score used by the scoped owner
flow.

For every `omega in Omega_G`, let `O(omega)` be its scoped demand owners.  For
**every** owner shore `A subseteq O(omega)`, put

`defect_omega(A) := D_omega(A) - C_omega(N_omega(A))`,

where `D_omega(A)` is the sum of owner-demand units and
`C_omega(N_omega(A))` is the total capacity of the union of available source
cells adjacent to `A`.  The tested claim, for every deficient shore
`A` with `defect_omega(A)>0`, is

`sum_{eta in Omega_G} S(eta)`
`  <= K_G * (S(omega) - defect_omega(A)).`                 `(PHT)`

The exact owner max-flow returns

`Delta_omega = max_{A subseteq O(omega)} defect_omega(A)`.

Thus the runner tests the strongest shore instance, with `Delta_omega`, for
every failing `omega`.  Since every deficient `A` has
`defect_omega(A) <= Delta_omega`, a pass quantifies over every deficient owner
shore, not only the residual min-cut shore printed in the witness record.

The checked integer residual is

`rho(G,omega) = K_G*(S(omega)-Delta_omega) - sum_eta S(eta)`.

PHT is exactly `rho>=0`.  Fractions are used only to reduce `rho/K_G`; no
floating-point arithmetic or acceptance threshold occurs.

## N=12 exhaustive result

No falsifier exists in the available N=12 scoped Hall-failure population.

| Product band | Eligible graphs | Row tuples | Hall failures | PHT failures | Minimum `rho/K` |
|---|---:|---:|---:|---:|---:|
| medium, `257<=K<=4096` | 21,841 | 14,160,291 | 1,080 | 0 | `25569/1000` |
| heavy, `K>=4097` | 450 | 4,801,067 | 7,144 | 0 | `94289/12500` |
| combined | 22,291 | 18,961,358 | 8,224 | 0 | `94289/12500` |

The preflight independently regenerated 1,144,061 connected triangle-free
order-12 graphs: 921,910 eligible, 212,780 without the required cut, and
9,371 not all-length-five.  It also recounted the light band as 899,619
eligible graphs / 20,181,461 tuples.  The available light census has zero
scoped Hall failures, hence there are no light PHT instances; light tuples
were preflight-counted but not flow-retested here.

The smallest normalized residual is the heavy record:

- graph6 `K?ABBBwerwBw`, family sizes `(10,10,10,10,10)`, `K=100000`;
- tuple index `74648`, choice `(7,4,6,4,8)`, owner shore `{8}`;
- `S(omega)=18`, `Delta=6`, `sum_eta S(eta)=445688`;
- `rho=754312`, so `rho/K=754312/100000=94289/12500`.

The smallest raw residual numerator is a different medium record:

- graph6 ``K?AADb_i`k@{``, family sizes `(7,3,8,6)`, `K=1008`;
- tuple index `720`, choice `(5,0,0,0)`, residual shore `{9,11}`;
- `S(omega)=35`, `Delta=6`, `sum_eta S(eta)=606`;
- `rho=28626`, so `rho/K=4771/168`.

## R29 abstractions

No 2,943-vertex graph was constructed or inferred.  The exact test uses only
the archived reconstructible aggregate abstraction:

`Omega_abs = {0,...,679}^{676}`, baseline score `30811`, and conditional
archived owner-shore defect `28` for `{r,cL,cR}`.

The two archived-consistent landscapes from the existing R29 indeterminacy
gate give opposite PHT verdicts under exact full-product summation:

- Model A, `S=30811+2k` for `k` changed selectors: PHT fails, with normalized
  residual `-117131/85`.
- Model B, equal to A except score zero when all selectors change: PHT holds.

Therefore the surviving R29 abstractions do not determine PHT.  An
instance-level R29 result requires the missing authenticated graph, cut,
complete row families, and selected tuple.  Model A is an abstraction-level
PHT falsifier, not a claimed graph witness.

## Reproduction and hashes

Run:

`python n12_pht.py --workers 32`

`python r29_abstractions.py`

- N=12 runner SHA-256: `44a686b10724fe4e67c6a53cc32672ca5ae4e00286bf7f04357ea7c09b4eef9e`
- N=12 canonical payload SHA-256: `0a137de5c545be4ea14cda11337caba4845a9eb5df939495685afa84a929de80`
- N=12 result-file SHA-256: `e35701944ac188fd20e4839b19257d6c27fd7ea935b4cfe40c497383974c39e0`
- N=12 graph-stream SHA-256: `f2001d31898e37c5098937c8ec435f6df8dc3227dc791a02118cfc5a15306efc`
- R29 abstraction runner SHA-256: `72c457f49fe44d497ad3cb4b15bc08a9983b854ca7a60c901c1c5b10ae71fee7`
- R29 canonical payload SHA-256: `189fd68fc7b56cc33b7d0d61d829966f581d408f96615b759fc7a69c84a1a48b`
- R29 result-file SHA-256: `608af6c4e2214fdac7ab8f5db26c111b9448b1467a12d0abc71104b10522d54e`

All imported machinery hashes and archived R29 source hashes are embedded in
the two result JSON files.  Independent canonical-payload recomputation
matched both stored payload hashes.
