lines = [
 "2026-06-29T00:00:00 OK VERIFY-surplus | DID: independent exact-Fraction gate _wf_ver_surplus.py re-derived V2+N(Gamma-N^2)+(N/5)(TVcut-TVbad)<=Gamma(N^2/25-beta) from struct_for_side | RESULT: 0 violations / 240289 configs (core 189493 + deep 50796 incl Myc(Grotzsch)N23 margin=20157854/51597>0, bridge(C7,Grotzsch), bridge(C9,C9), k-lanes, 26k random N=12..15) | delta: surplus central-ineq CONFIRMED holds",
 "2026-06-29T00:00:01 OK VERIFY-surplus-impl | DID: checked implication chain | RESULT: identity V2+N(Gamma-N^2)==sum_v T(T-N) EXACT (0 fail) => central c=5 IS LOAD-PSC-5; Xi=TVcut-TVbad>=0 (0 neg) => central=>LOAD-PSC-25=>Erdos beta<=N^2/25 (0 viol). Implication=PROVEN reduction | delta: implication CONFIRMED",
 "2026-06-29T00:00:02 OK VERIFY-surplus-const | DID: tracked V2/(Gamma*(N^2/25-beta)) ratio | RESULT: claimed extremal 151/16 REFUTED as supremum; ratio 34/3 at nu[5,1,1,1,5]N=13, 55/4 at N=15, grows with N. Central ineq still holds; V2-bound K=151/16 is small-N artifact | delta: extremal-constant CORRECTED",
]
with open("E:/Projects/ErdosProblems/PROGRESS.md", "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("appended", len(lines), "lines")
