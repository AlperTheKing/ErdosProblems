/-
Toy instantiation (M6.5 validation, EXTREMAL case): the OddCyclePacking TRUE-max-cut
checker certifies the maximum cut of the blow-up C5[5] — the actual extremal graph for
Erdős #23, where β = N²/25 is tight (N = 25, β = 25). Evaluated WITHOUT kernel-bypassing automation
(honest `decide` on concrete n = 25 data).

C5[5]: 5 blocks B0..B4 of 5 vertices each (Bi = {5i,…,5i+4}); consecutive blocks are
complete-bipartite (the C5 adjacency pattern blown up). 25 vertices, 125 edges,
10-regular.

Cut: block-alternating side = [F×5, T×5, F×5, T×5, F×5]. The only monochromatic block
pair is B4–B0, so badCount = 25 = β, and maxcut = 125 − 25 = 100 = 4·5².

Pack: the 25 modular transversal 5-cycles  cycle(s,d) = (0,s)(1,s+d)(2,s+2d)(3,s+3d)(4,s+4d)
for (s,d) ∈ Z₅×Z₅ edge-disjointly DECOMPOSE C5[5] (each block-pair's K₅,₅ is hit once
per cycle). Each is an odd 5-cycle carrying exactly one B4–B0 bad edge, so the packing
is edge-disjoint with k = 25 = badCount ⟹ the cut is TRUE-max (IsMaxCut) by
`checkOddCyclePacking_sound`. Construction verified exactly in Python before emission.
-/
import Erdos23Delta0.CertGraph

namespace Erdos23Delta0
namespace CertGraph

open OddCyclePacking

set_option maxRecDepth 100000

def c5b5Graph : GraphData :=
  ⟨25,
   [(0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
    (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),
    (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, 10), (5, 11), (5, 12), (5, 13), (5, 14),
    (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (7, 10), (7, 11), (7, 12), (7, 13), (7, 14),
    (8, 10), (8, 11), (8, 12), (8, 13), (8, 14), (9, 10), (9, 11), (9, 12), (9, 13), (9, 14),
    (10, 15), (10, 16), (10, 17), (10, 18), (10, 19), (11, 15), (11, 16), (11, 17), (11, 18), (11, 19),
    (12, 15), (12, 16), (12, 17), (12, 18), (12, 19), (13, 15), (13, 16), (13, 17), (13, 18), (13, 19),
    (14, 15), (14, 16), (14, 17), (14, 18), (14, 19), (15, 20), (15, 21), (15, 22), (15, 23), (15, 24),
    (16, 20), (16, 21), (16, 22), (16, 23), (16, 24), (17, 20), (17, 21), (17, 22), (17, 23), (17, 24),
    (18, 20), (18, 21), (18, 22), (18, 23), (18, 24), (19, 20), (19, 21), (19, 22), (19, 23), (19, 24),
    (0, 20), (1, 20), (2, 20), (3, 20), (4, 20), (0, 21), (1, 21), (2, 21), (3, 21), (4, 21),
    (0, 22), (1, 22), (2, 22), (3, 22), (4, 22), (0, 23), (1, 23), (2, 23), (3, 23), (4, 23),
    (0, 24), (1, 24), (2, 24), (3, 24), (4, 24)]⟩

def c5b5Cut : CutData :=
  ⟨[false, false, false, false, false, true, true, true, true, true,
    false, false, false, false, false, true, true, true, true, true,
    false, false, false, false, false]⟩

def c5b5Cert : OddCyclePackingCert :=
  ⟨25,
   [[0, 5, 10, 15, 20, 0], [0, 6, 12, 18, 24, 0], [0, 7, 14, 16, 23, 0], [0, 8, 11, 19, 22, 0],
    [0, 9, 13, 17, 21, 0], [1, 6, 11, 16, 21, 1], [1, 7, 13, 19, 20, 1], [1, 8, 10, 17, 24, 1],
    [1, 9, 12, 15, 23, 1], [1, 5, 14, 18, 22, 1], [2, 7, 12, 17, 22, 2], [2, 8, 14, 15, 21, 2],
    [2, 9, 11, 18, 20, 2], [2, 5, 13, 16, 24, 2], [2, 6, 10, 19, 23, 2], [3, 8, 13, 18, 23, 3],
    [3, 9, 10, 16, 22, 3], [3, 5, 12, 19, 21, 3], [3, 6, 14, 17, 20, 3], [3, 7, 11, 15, 24, 3],
    [4, 9, 14, 19, 24, 4], [4, 5, 11, 17, 23, 4], [4, 6, 13, 15, 22, 4], [4, 7, 10, 18, 21, 4],
    [4, 8, 12, 16, 20, 4]]⟩

/-- The odd-cycle-packing checker accepts the C5[5] block-alternating cut (concrete
    Boolean evaluation, no kernel-bypassing automation). -/
theorem c5b5_checkOddCyclePacking :
    checkOddCyclePacking c5b5Graph c5b5Cut c5b5Cert = true := by decide

/-- Extremal-case validation of the M6.5 provider path: the C5[5] block-alternating cut
    is TRUE-max. Here β = badCount = 25 = N²/25 with N = 25, so this exhibits the
    tightness configuration of Erdős #23 as a certified maximum cut. -/
theorem c5b5_isMaxCut : IsMaxCut c5b5Graph c5b5Cut :=
  checkOddCyclePacking_sound c5b5_checkOddCyclePacking

end CertGraph
end Erdos23Delta0
