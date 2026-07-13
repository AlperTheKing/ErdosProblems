# P70 finite extension: all natural Ruzsa cuts through p=293

## Result

Every natural cyclic cut was scanned exactly at the seven primes
`263, 269, 271, 277, 281, 283, 293`.

For each cut, the program found the first center `M` in
`[2 max(B)+1, 3|B|^2)` absent from `S(B)+Delta^+(B)`, with diagonal sums
included. The best and worst ratios over all cuts are:

| p | cuts | best M/|B|^2 | best e | worst M/|B|^2 |
|---:|---:|---:|---:|---:|
| 263 | 262 | 190041/68644 = 2.768501252841 | 167 | 200883/68644 = 2.926446594021 |
| 269 | 268 | 99215/35912 = 2.762725551348 | 202 | 52489/17956 = 2.923201158387 |
| 271 | 270 | 6707/2430 = 2.760082304527 | 255 | 214637/72900 = 2.944266117970 |
| 277 | 276 | 26575/9522 = 2.790905272002 | 175 | 13922/4761 = 2.924175593363 |
| 281 | 280 | 109701/39200 = 2.798494897959 | 273 | 115533/39200 = 2.947270408163 |
| 283 | 282 | 37355/13254 = 2.818394446959 | 20 | 117343/39762 = 2.951134248780 |
| 293 | 292 | 239055/85264 = 2.803703790580 | 212 | 250891/85264 = 2.942519703509 |

Thus the p=257 obstruction to the fixed coefficient `14/5` is not
persistent: p=263,269,271,277,281 each have a natural cut below `14/5`.
The ratios are nonmonotone and this finite table gives no infinite family.

## Independent verification

`compute/p70/verify_all_cut_records.py` does not import the scanner. It
reconstructs each CRT lift from

`x_i = d_i + p(i-d_i mod p-1)`, `d_i=e(g^i-1) mod p`,

rebuilds all unordered pair sums including diagonals and all positive
differences, forms the full bitset `S+Delta`, checks that every earlier
candidate center is represented, and performs the complete unordered-sum
census of `B union (M-B)`. It verified the best and worst records at p=257
and all seven new primes. In every case, the sole repeated sum is `M`, with
exactly `|B|` representations.

The exact artifacts are `compute/p70/all_cuts_p*.json` and
`compute/p70/verified_extrema_p257_p293.json`.

## Claim boundary

This is evidence for a carry-distribution question, not a disproof of the
conjectured constant. A negative resolution still requires a fixed
`epsilon>0` and infinitely many parameters with center at most
`(3-epsilon)|B|^2`.
