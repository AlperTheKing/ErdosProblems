# Finite LP/Farkas referee result

The R29 wrapper's logical core uses a finite nonempty choice type, natural-valued scoped score, global minimality, Matching, and critically HallFailureHasScopedScoreGlobalDescent. TriangleFree, IsMaxCut, BConnected, and CompleteShortestRowDB only specialize the real descent premise; the core proof never unfolds them.

Exact countermodel without descent: choices w0,w1 have scores 1,1 and w0 is canonical. At w0, one demand and one source have availability matrix [0], hence shore size 1 > neighborhood size 0. At w1 use [1]. Thus w0 is a Hall-failing global minimizer. All data are exact integers/rationals. This is abstract, not claimed graph-realizable.

Exact Farkas certificate with descent: global minimality gives s0-s1 <= 0. Strict Nat descent gives -s0+s1 <= -1. Multipliers (1,1) sum to 0 <= -1. Thus no model satisfies the full wrapper premises while having a Hall-failing global minimizer.

Explicit gap: prove RealHallFailureHasScopedScoreGlobalDescent for graph-derived databases. R29's 2,943-vertex strict local minimum settles neither direction until globally minimized over simultaneous selector trades.

Run: python tmp/fanout/referee_alt/child_04/finite_wrapper_farkas.py
