"""Exact integer arithmetic for the archival R29 all-anchor hub shore."""
from hashlib import sha256
import json
terminal = {"sameFirst_after_three_reservations":17325,"commonBad":0,"rowCompanion":2600,"outsideAttachment":0}
demand=19953; capacity=sum(terminal.values()); defect=demand-capacity
assert capacity == 19925 and defect == 28
cert={"shore":[0,1,2],"demand":demand,"terminal_counts":terminal,"auxiliary_legal_capacity":capacity,"defect":defect,
 "fullbank_graph_derived_c5Base_capacity":None,"fullbank_graph_derived_prune_capacity":None,
 "verdict":"FullBank capacity indeterminate from current production hypotheses"}
blob=json.dumps(cert,sort_keys=True,separators=(",",":")).encode()
print(json.dumps(cert,sort_keys=True,indent=2)); print("certificate_sha256="+sha256(blob).hexdigest())
print("PASS exact auxiliary capacity 19925; exact shortfall 28")
