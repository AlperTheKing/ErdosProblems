# W144: exact counterexample to the registered ordinary metric-window lemma

Date: 2026-07-18.

This note refutes the auxiliary lemma `(MW)` from
`ORDINARY_TRIAMETER_REPORT_20260718.md`. It does **not** refute Conjecture 144
and does not refute the weaker capacity inequality `(O)`.

## Graph and registered data

The graph has order 25 and graph6 string

    XhCGGC@?G?_@?@??o?G??A?C??G??G??C??@???G?G?_??@_???

Vertices `0,...,14` form a shortest cycle `K=C15`. Vertices `15,...,23`
form a path, with extra edges `4-16` and `11-22`; vertex `24` is a leaf at
`0`. Exact calculation gives

    g=15, r=7, D=9, C(G)={6,9}, e=7.

Vertex `x=24` is the unique `e`-realizer. Its height over `K` is `h=1`, its
unique anchor is `m=0`, and `delta=e-h=6`. Hence

    W={0,1,2,3,4,5,10,11,12,13,14}.

Both residual inequalities hold: `D<=e+floor(g/2)-1` and `e<=r`. Choose the
safe adjacent reserved vertex `z=14`. The ordinary component

    H={15,16,...,23}

does not contain `x`, has legal attachment set `{4,11}`, and therefore lies in
the two-legal-root case. Its exact registered cover is `E_H=W`, so `q_H=11`.

## Failure of `(MW)`

In `J_z(H)`, the apex is adjacent exactly to `16` and `22`. Thus its core is
the 8-cycle

    rho-16-17-18-19-20-21-22-rho,

with pendant vertices `15` and `23`. Exhausting all pairs in `H` gives

    P_z(H)=10.

Also `lambda=2r+1-g=0`. Consequently

    q_H+lambda=11>10=P_z(H).

For comparison, exhaustive induced-subset calculation gives `mu_z(H)=8`, so
the actual capacity target `(O)` still holds: `11<=16`. Therefore only the
rooted-triameter bridge `(MW)` is dead; W144 and the active deletion route are
unaffected.

Run `python verify_registered_mw_counterexample.py` for an independent exact
check of the graph, all registered hypotheses, the cover, `P_z(H)`, and
`mu_z(H)`.
