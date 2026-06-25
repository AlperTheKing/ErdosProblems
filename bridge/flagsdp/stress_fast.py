import sys
from stress_qfc_atoms import (subdivided_complete, theta_graph, gen_petersen, c5q_perturb, check)
worst=0.0; viol=0; tested=0
builders=[]
for k in [4,5]:
    for sub in [1,2,3]:
        builders.append((f"K{k}sub{sub}", subdivided_complete(k,sub)))
for lens in [[4,6],[4,4,4],[4,6,6],[5,5,5],[4,4,6],[6,6,6],[4,6,8],[4,4,4,4],[6,4,4]]:
    builders.append((f"theta{lens}", theta_graph(lens)))
for (n,k) in [(5,2),(7,2),(8,3),(9,2),(10,2),(10,3),(11,2),(12,5),(7,3)]:
    builders.append((f"GP({n},{k})", gen_petersen(n,k)))
for q in [2,3,4]:
    for s in range(8):
        builders.append((f"C5[{q}]p{s}", c5q_perturb(q,s)))
for label,b in builders:
    if b[0] > 16:  # skip very large (2^N signature enum)
        continue
    res=check(label,b)
    if res is not None:
        tested+=1; worst=max(worst,res[0]); viol+=int(res[1])
print(f"\n>>> tested {tested} structured atoms; spread-congestion VIOLATIONS={viol}; worst ratio={worst:.4f}")
