R8 entropy/counting lane — progress log (kept inside round8/; the task scope forbade
writing to the repo-level PROGRESS.md).

[2026-07-26T00:00Z] ► R8-SURVEY | NEXT: read round1/f3.md, round3/G8.md, round7/Q1.md to find what the entropy lane has already killed
[2026-07-26T00:00Z] ✔ R8-SURVEY | DID: read APPROACH_REGISTRY.md + f3/G8/Q1 | RESULT: A6 arithmetic averaging dead at 1/20; G8 §6.3 blocks fixed GM families on And(4); f3 §5 says the fix must be "a min or a geometric mean"; registry lists "entropy/counting on the cut structure" as UNDEREXPLORED | Δ: target set = x-adapted Z5-rotation GM certificate (PRGM)
[2026-07-26T00:00Z] ► R8-PRGM | NEXT: implement PRGM = min over phi:V->Z5 of (prod_r m_r)^{1/5} exactly and test on C5,C7,K33,Wagner,C5[2],C5[3,1,2,2,1],C5[3,1,2,2,0],Petersen,Grotzsch,And(4)
[2026-07-26T00:00Z] ✔ R8-PRGM | DID: exhaustive numpy + pure-python enumeration of all 5^(n-1) maps | RESULT: FAILS on Wagner (5^10*162=1582031250 > 8^10=1073741824), Grotzsch (3750>2656), And(4) (3456>2656) | Δ: PRGM DEAD
[2026-07-26T00:00Z] ► R8-RIGID | NEXT: prove and test the rigidity condition forced on any fixed cut distribution by the induced-C5 maximisers
[2026-07-26T00:00Z] ✔ R8-RIGID | DID: proved THEOREM R8-2 for every strictly monotone aggregator incl. Gibbs free energy; enumerated rainbow-1 cuts | RESULT: And(4)/And(5)/And(6)/N=14-extremal have R=empty; Grotzsch/Clebsch have |R|=5 | Δ: all averaging certificates blocked on those graphs
[2026-07-26T00:00Z] ✘ R8-VERIFY-1 | DID: second implementation of the Grotzsch computation | RESULT: DISAGREED (22 vs 31 induced C5) — edge (4,0) stored unnormalised in the second implementation; bug fixed, both now give 31 induced C5 and |R|=5
[2026-07-26T00:00Z] ✔ R8-STAR | DID: proved THEOREM R8-4 (star kill) and exhibited exact witnesses | RESULT: Grotzsch a=(0,0,0,0,0,1,1,1,1,1,5) gives min=5/100=1/20>1/25 while psi=0; Clebsch a(0)=5,a(N(0))=1 gives 1/20 | Δ: fixed certificates dead on two graphs that pass the G8 test
[2026-07-26T00:00Z] ✔ R8-COUNT | DID: computed pentagon degrees p(e) and the subset-sum condition sum_{e in F} p(e) = P | RESULT: And(4) has p(e) in {5,10} and P=33, and 5 does not divide 33 -> counting PROOF that R(And(4))=empty | Δ: G8's exhaustive blocking replaced by a divisibility argument
[2026-07-26T00:00Z] ✔ R8-CENSUS | DID: geng census, all connected triangle-free n<=9 and delta>=4 n<=12 | RESULT: 0 kills for n<=10; n=11: 1 of 8; n=12: 5 of 124 | Δ: kills start exactly where graphs become pentagon-rich
[2026-07-26T00:00Z] ✔ R8-WRITEUP | DID: wrote round8/R8_entropy.md | RESULT: file exists, 10 sections, every headline claim double-implemented | Δ: entropy lane closed on the fixed-distribution branch
