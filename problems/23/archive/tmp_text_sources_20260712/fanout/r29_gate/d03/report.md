# R29 maximum-cut gate (d03)

## Verdict

**The archived claim `MaxCut(G)=7039` is not rigorously gated from the workspace evidence.** The numerical five-class certificate is internally consistent, and the complete 4,786-edge traffic-class upper bound is independently proved below. However, the R29 archive supplies neither an edge list/deterministic constructor nor the 235-edge circuit certificate nor an explicit 2,943-bit attaining cut. Consequently the five classes cannot be audited as a partition, the circuit bound 207 cannot be checked, and simultaneous attainment cannot be proved. Treat 7039 as **conditional/ungated**, not established.

## Exact certified portion

The recovered class accounting is

| class | edges | cut upper bound | forced uncut deficit |
|---|---:|---:|---:|
| traffic block | 4786 | 4110 | 676 |
| 676 selector C5s | 3380 | 2704 | 676 |
| 3 private C5s | 15 | 12 | 3 |
| 28/27 circuit | 235 | 207 | 28 |
| cable | 6 | 6 | 0 |

Thus the advertised arithmetic is exact: edge counts sum to 8422, deficits sum to 1383, and upper bounds sum to `4110+2704+12+207+6=7039`.

For the traffic class, let `p,q` count switched leaves on its two 26-leaf shores and let `hr,hL,hR` be the three hub switch bits. Optimizing every private length-3 lock arm exactly, the loss relative to the displayed cut is

`26(p+q) + [hr!=hL]+[hr!=hR] + (hL ? 26-p : p) + (hR ? 26-q : q) - p(26-q) - (26-p)q`.

`gate_maxcut.py` exhausts all `8*27*27=5832` symmetry-quotient states. Its minimum is 0, uniquely at `(0,0,0,0,0)`. Hence the displayed traffic cut is the unique maximum modulo the quotient and cuts all 4110 blue edges while leaving all 676 `K_26,26` edges uncut. This proves `MaxCut(traffic)=4110` without heuristic optimization.

For each asserted C5, the rigorous generic bound is 4, attained by alternating four of its five edges. The cable bound 6 is the trivial edge-count bound. The aggregate upper bound 7039 follows **only if** the advertised edge-disjoint class partition exists and the circuit has max-cut at most 207.

## Partition audit and explicit failure tests

The two archives contain only prose totals. They contain no endpoint list, vertex labels for the lock/selector C5 edges, circuit incidence list, or side bit-vector. Therefore these mandatory tests have no input and were not claimed as passed:

1. Normalize every edge `(min(u,v),max(u,v))`; reject with the first duplicate `(edge,class_i,class_j)`.
2. Compare union size with 8422; reject with the first graph edge absent from all classes or class edge absent from the graph.
3. Check class cardinalities exactly `(4786,3380,15,235,6)`; the first mismatching class/count is a falsifier.
4. Check every one of the claimed 679 C5 edge sets has five distinct edges and odd-cycle incidence degree 2; the first repeated vertex/edge or wrong degree is a falsifier.
5. Evaluate the supplied side bit-vector classwise; any class total below `(4110,2704,12,207,6)` falsifies attainment of 7039.
6. Independently certify the circuit upper bound; any circuit cut of size 208 is an explicit falsifier of the asserted 207 bound.

No concrete endpoint falsifier can honestly be emitted because no endpoint data were archived. The missing data itself blocks the requested audit; it is not evidence that the partition is correct.

## Attaining cut status

An attaining traffic cut is explicit at the quotient level: hubs and all leaves remain on the archived displayed sides; lock-arm internal vertices alternate to cut all three arm edges. Each C5 class individually has an attaining 4-edge cut, and all six cable edges can individually be cut. But shared vertices can make these choices incompatible. With no common vertex labeling and no circuit cut, there is no rigorous global attaining cut certificate in the workspace. **Proof gap: simultaneous compatibility/attainment.**

## Reproduction and hashes

Run `python gate_maxcut.py > gate_output.json` in this directory. The checker uses integers only.

- `gate_maxcut.py`: `c909377c954893b96d052e45d48334e8f76aaf3a18e85ece0885899bad1ba391`
- `gate_output.json`: `a22e8306d4afd1aca25ea4c489c87a775591e23172ee9c2c776676b64dedea45`
- relied-on R28 archive: `819d6a3bb2da534beb7ac86f8b50e9ab936942893671bca12c61e027069e42b9`
- relied-on R29 archive: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`

## Proof gaps

1. Deterministic R29 graph constructor or canonical 8422-edge serialization.
2. Machine-readable five-class membership certificate and disjoint-cover audit.
3. Exact proof/certificate that the 235-edge circuit has maximum cut 207.
4. Explicit 2943-bit side vector attaining every class bound simultaneously.

