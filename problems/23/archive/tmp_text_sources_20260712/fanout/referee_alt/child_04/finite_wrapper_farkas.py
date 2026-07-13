from fractions import Fraction as F
from hashlib import sha256
import json
model={"choices":["w0","w1"],"scores":[F(1),F(1)],"hall_incidence":{"w0":[[F(0)]],"w1":[[F(1)]]},"canonical":"w0"}
s0,s1=model["scores"]
checks={"scores_nonnegative":min(s0,s1)>=0,"canonical_global_minimum":s0<=s1,"hall_fails_at_canonical":F(1)>sum(model["hall_incidence"]["w0"][0]),"hall_holds_at_other":F(1)<=sum(model["hall_incidence"]["w1"][0])}
ineq=[([F(1),F(-1)],F(0)),([F(-1),F(1)],F(-1))]; mult=[F(1),F(1)]
coeff=[sum(mult[j]*ineq[j][0][i] for j in range(2)) for i in range(2)]; rhs=sum(mult[j]*ineq[j][1] for j in range(2))
checks["farkas_coeff_zero"]=coeff==[F(0),F(0)]; checks["farkas_rhs_negative"]=rhs<0
def enc(x):
 if isinstance(x,F): return f"{x.numerator}/{x.denominator}"
 raise TypeError(type(x).__name__)
out={"model":model,"checks":checks,"farkas":{"inequalities":ineq,"multipliers":mult,"summed_lhs_coeff_s0_s1":coeff,"summed_rhs":rhs},"conclusion":"Base hypotheses admit a Hall-failing global minimizer; adding global descent is infeasible."}
payload=json.dumps(out,default=enc,sort_keys=True,indent=2); print(payload); assert all(checks.values()); print("certificate_sha256="+sha256(payload.encode()).hexdigest())
