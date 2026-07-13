# R29 arbitrary-selector hub-shore source audit

## Verdict

The claimed count is exact and selector-invariant for the canonical reconstructed `N=2943` cage:

`sameFirst = 17325`, `rowCompanion = 2600`, and their disjoint union has `total reach = 19925` for shore `{0,1,2}`.

There are no selector choices that alter these counts. The checker enumerates all `680` shortest rows in each of the `676` selector families (`459680` rows, including the currently displayed rows) and finds zero rows meeting a hub. This is a universal family check, not sampling and not enumeration of `680^676` tuples: independence follows because each selected row separately contributes no hub incidence.

## Exact derivation from row supports and reservations

The fixed traffic rows are

`(u,1,0,2,v)`, with `u` one of 26 left leaves and `v` one of 26 right leaves.

Consequently the pair-support of each hub is exactly the same 55 vertices: the hub itself, the other two hubs, and all 52 traffic leaves. Selector rows add none because every one of their 680 alternatives is hub-free. Thus, for each owner `o`, exactly `2943-55=2888` vertices `y` satisfy `pair(o,y)=0`. Each ordered source `(o,y)` has two halves, giving `2*2888=5776` raw sameFirst halves.

Exactly one half is reserved per hub. These are the `h=0` halves on the permanent active cable edges `(0,55)`, `(1,2929)`, and `(2,2930)`. Their endpoints are permanently selected by rigid traffic/seed/circuit rows; no selector row supports a cable edge; and the cable joins the hubs to the rigid active circuit component. Hence each owner contributes

`2*(2943-55)-1 = 5775`,

and `3*5775 = 17325`.

For the companion source pool, the common hub-companion support is the same 55 vertices. The only ordered distinct zero-co-occurrence pairs in it are two distinct leaves on the same side: `2 sides * 26*25 = 1300` ordered pairs. Both halves are available (there are no same-side leaf blue/active edges), so this contributes `2*1300=2600`. These sources have first coordinates in `3..54`, whereas sameFirst sources have first coordinate in `{0,1,2}`; the pools are disjoint. Therefore `17325+2600=19925`.

The names in the archived Hall checker are `sameFirst` and `rowCompanion`; “sameOwner/sameFirst” in the assignment refers to the hub-owned first-coordinate pool. Sources are ordered triples `(x,y,half)`.

## Selector-invariance certificate

The checker reconstructs the canonical 2704 lock-arm vertices and both selector fragments from their deterministic numbering. Exact BFS enumerates each selector atom's length-four rows. Every family has shape `676 anchor + 4 local = 680`, all 676 families pass, and none of the 459680 rows contains a hub. Since the three reservations and all traffic rows are rigid, arbitrary independent selection from the families cannot alter either pool.

## Replay

Run from this directory:

`python check.py`

Expected exit code and complete stdout are in `output.txt`. Python integers and sets are used exclusively; there are no floats, randomness, third-party packages, or reads outside this directory.

## Scope

This audits the deterministic canonical reconstruction with payload SHA256 `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`. It does not establish identity with the absent historical artifact whose advertised hash began `00186166`.

## Hashes

Hashes are recorded in `sha256.txt`; verify with `Get-FileHash -Algorithm SHA256 check.py,output.txt,report.md`.
