"""Exact symbolic quotient gate for R29."""
from fractions import Fraction
from dataclasses import dataclass
KINDS=("door","vertexSlack","c5Base","prune"); DEMAND=19953; REACH=19925; DEFECT=DEMAND-REACH
@dataclass(frozen=True)
class Token: component:str; kind:str; source:str; cap:Fraction; legal:bool
def audit(ts):
 seen=set(); by={k:Fraction(0) for k in KINDS}
 for t in ts:
  assert t.kind in KINDS and t.cap>=0
  key=(t.component,t.kind,t.source); assert key not in seen
  seen.add(key)
  if t.legal: by[t.kind]+=t.cap
 return sum(by.values(),Fraction(0)),by
def absorbed(ts): return audit(ts)[0]>=DEFECT
assert DEFECT==28 and len({(k,"x") for k in KINDS})==4
assert not absorbed([Token("hub","door","d",Fraction(27),True)])
assert absorbed([Token("hub","door","d",Fraction(28),True)])
assert not absorbed([Token("hub","door","d",Fraction(28),False)])
print("PASS demand=19953 legacyReach=19925 defect=28")
print("PASS absorbed iff certified added legal capacity/reach >= 28")
print("UNDECIDED R29: missing concrete four-kind hub-shore provider table")
