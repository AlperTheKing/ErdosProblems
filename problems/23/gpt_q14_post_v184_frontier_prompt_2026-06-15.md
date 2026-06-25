CONTEXT: Erdős #23 / a(30)=36 low-codegree proof attempt.

Verified local setup:
- q=15 branch is closed by the shadow-count lemma and finite certificates (PROOF_STATE V123).
- q=14/t=2 branch has scalar audit constraints in `search23/q14_t2_scalar_audit.cpp`.
- Low caps through cap43 plus clean z8d6 core cuts are closed (V124--V139).
- The cap74/p12 scalar row
  `(z,s1,s2,d,p,e_R,U,cap)=(3,5,5,1,12,25,12,74)`
  is now closed by the S1-S2 reconstruction-state verifier (V141--V183).

Post-V183 scalar audit:
`search23/q14_t2_scalar_audit_post_v183.tsv` has max cap still 74, with 50 cap74 rows:
- `(z,s1,s2,d)=(2,6,6,0)`: 6 rows, `p=12..17`, `e_R=25..20`;
- `(3,5,5,1)`: 6 rows, `p=13..18`, `e_R=24..19`;
- `(4,4,4,2)`: 10 rows, `p=12..21`, `e_R=25..16`;
- `(5,3,3,3)`: 10 rows, `p=12..21`, `e_R=25..16`;
- `(6,2,2,4)`: 10 rows, `p=12..21`, `e_R=25..16`;
- `(8,0,0,6)`: 8 rows, `p=14..21`, `e_R=23..16`.

Current computation:
- Generic sound A-only category SAT triage for `(2,6,6,0,p,e_R)=(2,6,6,0,12,25)`:
  338 categories, 10k conflicts -> 311 UNSAT, 27 UNKNOWN, SAT 0.
  UNKNOWN rerun at 100k -> 6 more UNSAT, 21 UNKNOWN, SAT 0.
- Generic sound A-only category SAT triage for `(4,4,4,2,p,e_R)=(4,4,4,2,12,25)` is running at 10k/128.

Known structural tools:
- For p=12, the A-B graph P is 2-regular on 6+6 vertices.
- If P is connected C12, the maximum independent-set structure contradicts the cap74 equality in the earlier z=3 row; hence only disconnected templates `C8+C4`, `C6+C6`, `3C4` were needed there.
- V143 S1-S2 reconstruction lemma: for u in S1 and v in S2,
  `uv in E_R` iff `Z(u,v)+|X_u cap X_v|+|Y_u cap Y_v| = 0`, and value 1 is impossible.
- The V143 state verifier is currently hardcoded for `z=3,s1=s2=5,d=1`; generalizing it to other rows is possible but nontrivial.

QUESTION:
Find the highest-leverage rigorous next lemma for the remaining q=14/t=2 cap74 frontier.
Prefer a lemma that either:
1. reduces the remaining cap74 scalar rows to the already-closed `(3,5,5,1,p=12,e_R=25)` row;
2. proves a scalar exclusion eliminating all p=12 remaining rows;
3. proves a monotonic/reroot/compression lemma that lets us ignore p=13..21 once p=12 is closed; or
4. gives a clean parametrized generalization of the S1-S2 reconstruction-state verifier to arbitrary `(z,s1,s2,d)`.

REQUIREMENTS:
- Give a rigorous argument, not a sketch. If no such lemma is currently visible, say so plainly.
- State exact hypotheses and conclusion.
- Identify which of the 50 rows the lemma eliminates.
- Flag any step that relies on a condition not listed here.
- End by listing the weakest points of your own answer and one concrete experiment to test them.
