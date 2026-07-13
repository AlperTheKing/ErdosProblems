# R29 selector-support structural audit

## Verdict

Literal selector invariance of `U_omega` and `I_omega` is **false**.  The
correct invariant, relative to the certified all-anchor tuple, is:

1. changing one selector never removes a vertex from `U_omega` and adds
   exactly 1, 2, or 3 vertices for an anchor row, or 2, 3, or 4 for a local
   row;
2. an anchor replacement adds no edge to `I_omega` and deletes zero or one;
   a local replacement adds exactly two and deletes zero or one;
3. despite those support changes, the active-component partition is exactly
   invariant: it consists of one 19-vertex active component, and that component
   contains all three hubs `0,1,2`, for every one-row selector change.

Thus the corrected invariant is **active-component and hub-shore invariance,
not selected-union or active-edge-set invariance**.

The reference here is the all-anchor tuple used by the R29 global-minimum and
d05/d09 retry2 certificates.  It is not the older displayed/local tuple whose
archived active component had size 2775.

## Exact row classification

Every one of the 676 selector atoms has the same eight-class distribution.
The class key is

`kind | |U+| | |U-| | |I+| | |I-|`.

| class | rows per atom | rows over all atoms |
|---|---:|---:|
| `anchor|1|0|0|0` | 337 | 227812 |
| `anchor|1|0|0|1` | 336 | 227136 |
| `anchor|2|0|0|1` | 2 | 1352 |
| `anchor|3|0|0|0` | 1 | 676 |
| `local|2|0|2|0` | 1 | 676 |
| `local|2|0|2|1` | 1 | 676 |
| `local|3|0|2|1` | 1 | 676 |
| `local|4|0|2|0` | 1 | 676 |

Hence each family has exactly 676 anchor rows and four local rows.  The full
per-atom classification, including atom endpoints and region, is in
`result.json`; it checks `676*680 = 459680` rows.

## Exact delta law

Let `P` be the old anchor row and `Q` the replacement.  Let `m_V(v)` and
`m_S(e)` be vertex and support-edge multiplicities in the all-anchor tuple.
With row multiplicities `p_V,q_V,p_S,q_S`, the verifier computes

```text
U+ = {v in Q : m_V(v)-p_V(v)=0}
U- = {v in P : m_V(v)-p_V(v)>0 and m_V(v)-p_V(v)+q_V(v)=0}
S+ = {e in Q : m_S(e)-p_S(e)=0}
S- = {e in P : m_S(e)-p_S(e)>0 and m_S(e)-p_S(e)+q_S(e)=0}
U' = (U union U+) minus U-
S' = (S union S+) minus S-
I' = {uv in B : u,v in U' and uv not in S'}.
```

This is an identity, not a sampled rule.  It proves the stated effects on
`U_omega` and `I_omega` without considering any selector tuple product.

## Components and hub shore

For anchor alternatives, `I+` is empty.  Taking the union of every possible
single-row deletion removes 676 edges from the reference `I`, but the common
surviving subgraph still contains the complete reference 19-vertex active hub
component.  Therefore no anchor choice can split it, and deletion cannot
create another active component.

For the 2704 local rows, the verifier applies the exact delta and independently
rebuilds the disjoint-set components.  Every case has active-component size
multiset `(19)` and the root of hub 0 also contains hubs 1 and 2.  Changed
reference vertices meet no other active component.  Therefore the active
component partition and hub shore `{0,1,2}` are exact invariants under every
single-selector change from the all-anchor tuple.

## Reproduction and scope

Run `python verify.py`.  It uses Python integer, counter, and finite-set
operations only; there are no floats.  It imports the deterministic R29
constructor from `r29_lead_gate.py`, reconstructs every shortest-row family,
and does not enumerate `680^676` tuples.

Inputs audited: mandated R20/R23/R28/R29 wall documents, the R29 global-minimum
falsifier, `r29_lead_gate.py`, and the d05/d09 artifacts including retry2.

- `verify.py` SHA256:
  `e6c684124552f05607aab4dd11789c3b27f616f94ec01b373842d5211a2e1c65`
- `result.json` SHA256:
  `c25c90eb0cb687d665409be5f0657e77401b31f982d0c165eedd62c908eb93f5`
- imported lead constructor SHA256:
  `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`

This audit proves one-coordinate changes from the all-anchor tuple.  It does
not assert the same component invariant for arbitrary simultaneous selector
changes; such a claim would require a different universal-core argument.
