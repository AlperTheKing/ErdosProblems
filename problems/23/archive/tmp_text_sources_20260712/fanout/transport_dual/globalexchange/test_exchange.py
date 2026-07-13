from fractions import Fraction
from itertools import product
import json, sys
sys.path.insert(0, "problems/23/writeup")
from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_scoped_variation_anatomy import scoped_state, owner_shore_source_count
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow

def main(g6="I?`fBO]]?", choice=(1,1,1)):
 n, es=dec(g6); info=loads(n,es); blue,bad=info["Bset"],info["Mset"]
 fam=shortest_row_families(info); oldrows=tuple(fam[i][choice[i]] for i in range(len(fam)))
 old=scoped_state(n,blue,bad,oldrows); flow=full_owner_flow(n,blue,bad,oldrows,g6,require_full=False,quiet=True,scope="active",include_outside=False)
 shore=flow["deficientOwners"]; cap,_,_=owner_shore_source_count(n,blue,bad,old,shore)
 defect=sum(old["demand"].get(v,0) for v in shore)-cap; scores=[]
 for ix in product(*(range(len(f)) for f in fam)):
  scores.append(scoped_state(n,blue,bad,tuple(fam[i][ix[i]] for i in range(len(fam))))["score"])
 uniform=sum(map(Fraction,scores),Fraction())/len(scores)
 result={"fixture":g6,"choice":list(choice),"family_sizes":[len(f) for f in fam],"tuples":len(scores),"old_score":old["score"],"shore":shore,"defect":defect,"uniform_expectation":str(uniform),"minimum_score":min(scores),"uniform_bound_holds":uniform<=old["score"]-defect,"uniform_margin":str(old["score"]-defect-uniform)}
 print(json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__": main()

