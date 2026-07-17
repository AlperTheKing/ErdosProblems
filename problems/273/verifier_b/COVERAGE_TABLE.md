# Independent half-cover certificate

The full period is 360.  The leaf `0 (mod 2)` covers the even fiber.  Every
odd integer has a unique representation `x = 2n + 1`; reducing `n` modulo 180
is therefore a bijection from the odd residues modulo 360 to `Z/180Z`.

For each row, `U_before` is the residual set in `Z/180Z`, `new` is its
intersection with the stated reduced class, and `U_after = U_before \\ new`.
The hexadecimal masks in the JSON certificate store bit `n` for residue `n`.
The verifier reconstructs each class mask as an arithmetic progression and
checks all three masks and counts exactly.

| step | reduced leaf for `n` | lifted leaf for `x` | before | new | after | exact newly assigned residues in `[0,180)` |
|---:|:---:|:---:|---:|---:|---:|:---|
| R1 | `0 (mod 2)` | `1 (mod 4)` | 180 | 90 | 90 | `2j`, `0 <= j < 90` |
| R2 | `0 (mod 3)` | `1 (mod 6)` | 90 | 30 | 60 | `3+6j`, `0 <= j < 30` |
| R3 | `1 (mod 5)` | `3 (mod 10)` | 60 | 12 | 48 | `1+30j, 11+30j`, `0 <= j < 6` |
| R4 | `1 (mod 6)` | `3 (mod 12)` | 48 | 24 | 24 | `r+30j`, `r in {7,13,19,25}`, `0 <= j < 6` |
| R5 | `5 (mod 9)` | `11 (mod 18)` | 24 | 8 | 16 | `r+90j`, `r in {5,23,59,77}`, `0 <= j < 2` |
| R6 | `8 (mod 15)` | `17 (mod 30)` | 16 | 4 | 12 | `{53,83,143,173}` |
| R7 | `11 (mod 18)` | `23 (mod 36)` | 12 | 6 | 6 | `{29,47,65,119,137,155}` |
| R8 | `17 (mod 20)` | `35 (mod 40)` | 6 | 1 | 5 | `{17}` |
| R9 | `5 (mod 30)` | `11 (mod 60)` | 5 | 2 | 3 | `{35,125}` |
| R10 | `35 (mod 36)` | `71 (mod 72)` | 3 | 2 | 1 | `{107,179}` |
| R11 | `89 (mod 90)` | `179 (mod 180)` | 1 | 1 | 0 | `{89}` |

Thus the residual cardinalities are

`180 -> 90 -> 60 -> 48 -> 24 -> 16 -> 12 -> 6 -> 5 -> 3 -> 1 -> 0`.

For a row `n = a (mod m)`, multiplication by two and addition of one gives
`x = 2a + 1 (mod 2m)`.  This proves containment of the entire reduced leaf in
the lifted leaf, for positive and negative integers alike.  Together with the
even leaf, the chain proves exact coverage of every integer.

The resulting baseline system is

`0 (mod 2), 1 (mod 4), 1 (mod 6), 3 (mod 10), 3 (mod 12), 11 (mod 18),`

`17 (mod 30), 23 (mod 36), 35 (mod 40), 11 (mod 60), 71 (mod 72), 179 (mod 180)`.

Its moduli are pairwise distinct and have LCM 360.

## Exact primality certificates

For each `p=m+1`, the certificate records every remainder `p mod d` for
`2 <= d <= floor(sqrt(p))`.  All are nonzero; this is an exact primality proof.

| `m` | `p=m+1` | `floor(sqrt(p))` | remainders for consecutive `d=2,...` |
|---:|---:|---:|:---|
| 2 | 3 | 1 | empty |
| 4 | 5 | 2 | `1` |
| 6 | 7 | 2 | `1` |
| 10 | 11 | 3 | `1,2` |
| 12 | 13 | 3 | `1,1` |
| 18 | 19 | 4 | `1,1,3` |
| 30 | 31 | 5 | `1,1,3,1` |
| 36 | 37 | 6 | `1,1,1,2,1` |
| 40 | 41 | 6 | `1,2,1,1,5` |
| 60 | 61 | 7 | `1,1,1,1,1,5` |
| 72 | 73 | 8 | `1,1,1,3,1,3,1` |
| 180 | 181 | 13 | `1,1,1,1,1,6,5,1,1,5,1,12` |
