"""Exact all-anchor R29 half-singleton vertexSlack audit."""
from collections import Counter
from fractions import Fraction
import hashlib, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = HERE.parents[2] / "r29_gate" / "lead" / "r29_lead_gate.py"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(u,v): return (u,v) if u<v else (v,u)

spec=importlib.util.spec_from_file_location("r29lead",LEAD)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d=m.build(); n=d["n"]
rows=list(d["rows"])
for j,meta in enumerate(d["selectorMeta"]):
    rows[d["selectorStart"]+j]=tuple(meta["anchorRow"])
rows=tuple(rows)
C={v for r in rows for v in r}
F={norm(u,v) for r in rows for u,v in zip(r,r[1:])}
S={e for e in d["bad"] if e[0] in C and e[1] in C}
O=set(d["blue"])-F
Oi={e for e in O if e[0] in C and e[1] in C}
Ob={e for e in O if (e[0] in C) ^ (e[1] in C)}
O0=O-Oi-Ob
row_inc=Counter(v for r in rows for v in r)
T={v:5*row_inc[v] for v in C}
odeg=Counter(v for e in O for v in e if v in C)
records=[]
for v in sorted(C):
    cap=max(0,n-T[v]); load=Fraction(odeg[v],2); margin=Fraction(cap)-load
    records.append({"v":v,"row_incidence":row_inc[v],"T":T[v],"cap":cap,
                    "O_incidence":odeg[v],"load_num":load.numerator,
                    "load_den":load.denominator,"margin_num":margin.numerator,
                    "margin_den":margin.denominator})

# Global source audit: one source key per (off-support edge, incident core endpoint).
sources=[(e[0],e[1],v) for e in sorted(O) for v in e if v in C]
assert len(sources)==len(set(sources))==sum(odeg.values())
assert F.isdisjoint(O) and S.issubset(d["bad"])
assert all(e in d["blue"] for e in O)
assert all((sum(v in C for v in e)==2 if e in Oi else
            sum(v in C for v in e)==1 if e in Ob else
            sum(v in C for v in e)==0) for e in O)
failed=[r for r in records if r["margin_num"]<0]
payload={
 "schema":"r29-all-anchor-half-singleton-vertexSlack-v1",
 "input":{"lead":str(LEAD),"lead_sha256":sha(LEAD),"n":n},
 "counts":{"rows":len(rows),"C":len(C),"F":len(F),"S":len(S),"O":len(O),
           "O_internal":len(Oi),"O_boundary":len(Ob),"O_disjoint":len(O0),
           "source_keys":len(sources),"total_O_incidence":sum(odeg.values())},
 "selected_rows":[list(r) for r in rows],
 "sets":{"C":sorted(C),"F":sorted(F),"S":sorted(S),"O":sorted(O),
         "O_internal":sorted(Oi),"O_boundary":sorted(Ob)},
 "vertices":records,
 "checks":{"all_rows_length_5":all(len(r)==5 for r in rows),
   "F_O_disjoint":F.isdisjoint(O),"unique_source_keys":len(sources)==len(set(sources)),
   "no_edge_endpoint_double_spend":len(sources)==sum(odeg.values()),
   "numeric_vertexSlack_feasible":not failed,
   "compiled_incidence_licensed_from_graph_data":False},
 "failed_vertices":failed,
 "smallest_statement":("Conditional on the compiled incidence hypothesis for every (e,v) with "
   "e in O, v in C, v incident to e, the all-anchor half-singleton vertexSlack "
   "constructor is feasible iff every recorded margin is nonnegative; graph data alone "
   "does not discharge that incidence hypothesis.")}
out=HERE/"result.json"
out.write_text(json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
print(json.dumps({"counts":payload["counts"],"checks":payload["checks"],
 "min_margin":min((Fraction(r["margin_num"],r["margin_den"]) for r in records),default=0),
 "failed_vertices":len(failed),"result_sha256":sha(out)},default=str,sort_keys=True))
