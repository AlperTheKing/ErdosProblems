# R44 Live Endpoint Source Atom

Only the live R37 geometry is used:

```text
Q = (a,x,m,y,b) -> Q' = (a,x,v,y,b),
xv old active, vy old selected support.
```

No two-new-edge support-monotonicity statement is used.

## Exact Formula

Let `c_a = pairCount_omega(m,a)`.  Only `Q` is changed, so

```text
pairCount_omega'(m,a) = c_a - 1.
```

The row has blue edges `a-x` and `x-m`, hence `x` is a common blue neighbour
of `m,a`.  A blue `ma` edge shortens the four-edge blue geodesic, while a bad
`ma` edge makes the triangle `a-x-m`.  Thus `m,a` are distinct, same-side,
nonadjacent, and both zero-pair half keys are unreserved once `c_a=1`.

Therefore the literal production P2 terminal has the exact equivalence

```text
P2_x(m,a) at omega' <=> c_a = 1 and sigma_G,c({m,a}) >= 2.
```

The symmetric formula holds for `(m,b)` with common-blue owner `y`.  The
threshold is exact because P2 checks `dM({m,a}) + 2 <= dB({m,a})`.

For `c_a >= 2`, `(m,a)` is not free after the move.  Instead each orientation
loses one two-half collision fiber, so the paired raw collision-fiber drop is
`4`.

## N=8 Canonical-Minimum Falsifier

The replayed graph6 cage `GCQb\`o` uses row `(0,3,7,2,5)` and replacement
`(0,3,6,2,5)`.  It is triangle-free, its displayed cut equals the brute-force
maximum cut, and the selected tuple has minimum coherent collision defect 0.
It has `xv` active, `vy` selected support, and support is constant.  Both
endpoint pairs have old count 1, target count 0, common-blue owners, and are
unreserved, but both have `sigma=1`.  Hence neither is a production P2 source.

This refutes any forced-strongness assertion (`sigma>=2`) for the live
support-constant endpoint atom.  It does not refute the exact iff above.

Replay:

```powershell
python tmp/fanout/r44_endpoint_credit/verify_n8_weak_endpoint_witness.py
python tmp/fanout/r44_endpoint_credit/canonical_endpoint_atom_census.py --n-min 5 --n-max 8 --workers 4 --output tmp/fanout/r44_endpoint_credit/canonical_endpoint_atom_n5_n8.json
```
