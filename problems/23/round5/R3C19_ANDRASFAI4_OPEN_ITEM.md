# R3-C19 — OPEN VERIFICATION ITEM: is `And(4)` weakly bipartite after all?

Root-agent entry, 2026-07-26. To be merged into `round3/CLAUDE_GATE_R3.md` when tooling permits.

Round 7 (family Q5, its auditor concurring) reported that `And(4) = Γ_11` carries an explicit
odd-`K5` minor with branch sets `{0,4,8}, {1,5,9}, {2,6,10}, {3}, {7}`, and concluded that the
Guenin route "is provably unavailable from `And(4)` on". By Guenin's theorem an odd-`K5` minor means
the signed graph is **not** weakly bipartite, i.e. **some** weight `w ≥ 0` must satisfy
`τ_w > τ*_w` — an integrality gap in the odd-cycle covering LP.

## My own searches find no such gap, on three fronts

| test on `And(4) = Γ_11` (22 edges, 451 odd cycles of length 5,7,9) | trials | gaps found |
|---|---|---|
| arbitrary random integer edge weights: exact `τ` (min over all 1024 cuts) vs LP `τ*` | 4000 | **0** |
| product weights `w_uv = x_u x_v` — the only ones `ψ` ever sees | 1500 | **0** |
| random objectives, inspecting whether the optimal LP **vertex** is fractional | 3000 | **0** |

The same three tests on `And(3)` and `And(5)` also produce nothing fractional (`And(5)`: 6890 odd
cycles, 3000 objectives, zero fractional vertices). And integrality is certified *positively* at four
weightings on `And(4)` by exhibiting a fractional odd-cycle **packing** whose value equals `ψ`
exactly — LP duality then forces `packing ≤ τ* ≤ τ = packing`:

```
        uniform              psi = 4/121   packing = 4/121
        a C5-concentration   psi = 1/25    packing = 1/25
        random               psi = 13/500  packing = 13/500
        random               psi = 9/968   packing = 9/968
```

## These cannot both be right

Either the claimed odd-`K5` minor is not one — the signed-minor conditions (branch sets balanced
after switching, the contracted `K5` odd) were **not** re-derived by me, and the branch sets are
merely connected with pairwise edges, which is a plain `K5` minor, not an odd one — or the gap
weights lie in a set that all three of my searches systematically miss.

## Why it matters, sharply

If `And(4)` is weakly bipartite, Guenin gives `ψ = Λ` there, and with the fractional bound
`Λ ≤ 1/25` the ceiling `max_x ψ(And(4)) = 1/25` is **proved** — extending R3-C17 from `k ≤ 3` to
`k = 4`, and turning the whole Andrásfai side into the question *which `And(k)` are weakly
bipartite* rather than an open inequality of unknown character. If instead the minor is genuine, the
route stops at `k = 3` exactly as reported, and the witnessing gap weight is an explicit object
worth extracting.

## Next step to settle it

1. Verify the signed-minor conditions of the claimed odd-`K5` by hand: each branch set must induce a
   **balanced** (switching-equivalent to all-positive) connected subgraph, and the contracted `K5`
   must be odd. `{0,4,8}` induces the path `0–4–8` (`0 ≁ 8`, since `3·3 = 9 < 11`), so it is
   balanced; the question is the parity of the contracted `K5`.
2. Test idealness of the odd-cycle clutter of `Γ_11` over **0/1** weights rather than random ones —
   by Lehman's theorem idealness is decided there, and the gap, if it exists, must show up.

Recorded as an open item, not as a result in either direction.
