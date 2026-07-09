import Erdos23Delta0.O14.Generated.ChartKeys

/-!
# O14 listed-shape classifier

Generated from the accepted v108 ledger.  Unlike the pilot classifier, this
module does not pretend that the bound predicate alone covers exactly the 108
certified charts.  It classifies only the subtype of instances whose
`O14Shape` has one of the certified `(kIdx,dIdx)` pairs.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open CertGraph
open ODLFull
open EQODL1CoverInterface

/-- Certified v108 slot 0: k=5, dominant=13. -/
def listedDomain000 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 13

/-- Certified v108 slot 1: k=6, dominant=13. -/
def listedDomain001 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 13

/-- Certified v108 slot 2: k=8, dominant=13. -/
def listedDomain002 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 13

/-- Certified v108 slot 3: k=8, dominant=10. -/
def listedDomain003 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 10

/-- Certified v108 slot 4: k=5, dominant=10. -/
def listedDomain004 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 10

/-- Certified v108 slot 5: k=6, dominant=10. -/
def listedDomain005 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 10

/-- Certified v108 slot 6: k=6, dominant=0. -/
def listedDomain006 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 0

/-- Certified v108 slot 7: k=5, dominant=1. -/
def listedDomain007 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 1

/-- Certified v108 slot 8: k=6, dominant=7. -/
def listedDomain008 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 7

/-- Certified v108 slot 9: k=5, dominant=3. -/
def listedDomain009 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 3

/-- Certified v108 slot 10: k=5, dominant=12. -/
def listedDomain010 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 12

/-- Certified v108 slot 11: k=5, dominant=7. -/
def listedDomain011 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 7

/-- Certified v108 slot 12: k=6, dominant=2. -/
def listedDomain012 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 2

/-- Certified v108 slot 13: k=5, dominant=14. -/
def listedDomain013 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 14

/-- Certified v108 slot 14: k=8, dominant=3. -/
def listedDomain014 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 3

/-- Certified v108 slot 15: k=8, dominant=2. -/
def listedDomain015 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 2

/-- Certified v108 slot 16: k=6, dominant=12. -/
def listedDomain016 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 12

/-- Certified v108 slot 17: k=6, dominant=3. -/
def listedDomain017 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 3

/-- Certified v108 slot 18: k=6, dominant=5. -/
def listedDomain018 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 5

/-- Certified v108 slot 19: k=5, dominant=0. -/
def listedDomain019 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 0

/-- Certified v108 slot 20: k=6, dominant=1. -/
def listedDomain020 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 1

/-- Certified v108 slot 21: k=6, dominant=14. -/
def listedDomain021 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 14

/-- Certified v108 slot 22: k=5, dominant=11. -/
def listedDomain022 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 11

/-- Certified v108 slot 23: k=5, dominant=8. -/
def listedDomain023 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 8

/-- Certified v108 slot 24: k=5, dominant=2. -/
def listedDomain024 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 2

/-- Certified v108 slot 25: k=6, dominant=11. -/
def listedDomain025 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 11

/-- Certified v108 slot 26: k=6, dominant=8. -/
def listedDomain026 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 8

/-- Certified v108 slot 27: k=6, dominant=9. -/
def listedDomain027 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 9

/-- Certified v108 slot 28: k=8, dominant=1. -/
def listedDomain028 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 1

/-- Certified v108 slot 29: k=5, dominant=5. -/
def listedDomain029 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 5

/-- Certified v108 slot 30: k=8, dominant=14. -/
def listedDomain030 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 14

/-- Certified v108 slot 31: k=6, dominant=4. -/
def listedDomain031 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 4

/-- Certified v108 slot 32: k=8, dominant=0. -/
def listedDomain032 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 0

/-- Certified v108 slot 33: k=5, dominant=9. -/
def listedDomain033 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 9

/-- Certified v108 slot 34: k=8, dominant=7. -/
def listedDomain034 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 7

/-- Certified v108 slot 35: k=8, dominant=11. -/
def listedDomain035 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 11

/-- Certified v108 slot 36: k=6, dominant=6. -/
def listedDomain036 (s : O14Shape) : Bool :=
  natEqB s.kIdx 6 && natEqB s.dIdx 6

/-- Certified v108 slot 37: k=5, dominant=6. -/
def listedDomain037 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 6

/-- Certified v108 slot 38: k=5, dominant=4. -/
def listedDomain038 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 4

/-- Certified v108 slot 39: k=8, dominant=12. -/
def listedDomain039 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 12

/-- Certified v108 slot 40: k=7, dominant=2. -/
def listedDomain040 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 2

/-- Certified v108 slot 41: k=7, dominant=0. -/
def listedDomain041 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 0

/-- Certified v108 slot 42: k=9, dominant=3. -/
def listedDomain042 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 3

/-- Certified v108 slot 43: k=3, dominant=13. -/
def listedDomain043 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 13

/-- Certified v108 slot 44: k=9, dominant=1. -/
def listedDomain044 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 1

/-- Certified v108 slot 45: k=4, dominant=13. -/
def listedDomain045 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 13

/-- Certified v108 slot 46: k=8, dominant=9. -/
def listedDomain046 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 9

/-- Certified v108 slot 47: k=7, dominant=13. -/
def listedDomain047 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 13

/-- Certified v108 slot 48: k=9, dominant=13. -/
def listedDomain048 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 13

/-- Certified v108 slot 49: k=8, dominant=5. -/
def listedDomain049 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 5

/-- Certified v108 slot 50: k=8, dominant=6. -/
def listedDomain050 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 6

/-- Certified v108 slot 51: k=7, dominant=10. -/
def listedDomain051 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 10

/-- Certified v108 slot 52: k=8, dominant=4. -/
def listedDomain052 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 4

/-- Certified v108 slot 53: k=7, dominant=1. -/
def listedDomain053 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 1

/-- Certified v108 slot 54: k=9, dominant=10. -/
def listedDomain054 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 10

/-- Certified v108 slot 55: k=8, dominant=8. -/
def listedDomain055 (s : O14Shape) : Bool :=
  natEqB s.kIdx 8 && natEqB s.dIdx 8

/-- Certified v108 slot 56: k=9, dominant=0. -/
def listedDomain056 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 0

/-- Certified v108 slot 57: k=9, dominant=5. -/
def listedDomain057 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 5

/-- Certified v108 slot 58: k=4, dominant=10. -/
def listedDomain058 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 10

/-- Certified v108 slot 59: k=7, dominant=6. -/
def listedDomain059 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 6

/-- Certified v108 slot 60: k=9, dominant=4. -/
def listedDomain060 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 4

/-- Certified v108 slot 61: k=0, dominant=13. -/
def listedDomain061 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 13

/-- Certified v108 slot 62: k=3, dominant=10. -/
def listedDomain062 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 10

/-- Certified v108 slot 63: k=7, dominant=8. -/
def listedDomain063 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 8

/-- Certified v108 slot 64: k=9, dominant=9. -/
def listedDomain064 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 9

/-- Certified v108 slot 65: k=9, dominant=12. -/
def listedDomain065 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 12

/-- Certified v108 slot 66: k=7, dominant=11. -/
def listedDomain066 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 11

/-- Certified v108 slot 67: k=9, dominant=2. -/
def listedDomain067 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 2

/-- Certified v108 slot 68: k=7, dominant=12. -/
def listedDomain068 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 12

/-- Certified v108 slot 69: k=9, dominant=8. -/
def listedDomain069 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 8

/-- Certified v108 slot 70: k=7, dominant=4. -/
def listedDomain070 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 4

/-- Certified v108 slot 71: k=7, dominant=5. -/
def listedDomain071 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 5

/-- Certified v108 slot 72: k=9, dominant=11. -/
def listedDomain072 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 11

/-- Certified v108 slot 73: k=4, dominant=14. -/
def listedDomain073 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 14

/-- Certified v108 slot 74: k=9, dominant=6. -/
def listedDomain074 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 6

/-- Certified v108 slot 75: k=7, dominant=3. -/
def listedDomain075 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 3

/-- Certified v108 slot 76: k=4, dominant=7. -/
def listedDomain076 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 7

/-- Certified v108 slot 77: k=7, dominant=14. -/
def listedDomain077 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 14

/-- Certified v108 slot 78: k=3, dominant=14. -/
def listedDomain078 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 14

/-- Certified v108 slot 79: k=3, dominant=7. -/
def listedDomain079 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 7

/-- Certified v108 slot 80: k=9, dominant=14. -/
def listedDomain080 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 14

/-- Certified v108 slot 81: k=3, dominant=1. -/
def listedDomain081 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 1

/-- Certified v108 slot 82: k=4, dominant=0. -/
def listedDomain082 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 0

/-- Certified v108 slot 83: k=0, dominant=7. -/
def listedDomain083 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 7

/-- Certified v108 slot 84: k=3, dominant=3. -/
def listedDomain084 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 3

/-- Certified v108 slot 85: k=4, dominant=1. -/
def listedDomain085 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 1

/-- Certified v108 slot 86: k=4, dominant=12. -/
def listedDomain086 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 12

/-- Certified v108 slot 87: k=3, dominant=11. -/
def listedDomain087 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 11

/-- Certified v108 slot 88: k=3, dominant=2. -/
def listedDomain088 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 2

/-- Certified v108 slot 89: k=3, dominant=12. -/
def listedDomain089 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 12

/-- Certified v108 slot 90: k=0, dominant=14. -/
def listedDomain090 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 14

/-- Certified v108 slot 91: k=4, dominant=9. -/
def listedDomain091 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 9

/-- Certified v108 slot 92: k=4, dominant=8. -/
def listedDomain092 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 8

/-- Certified v108 slot 93: k=3, dominant=5. -/
def listedDomain093 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 5

/-- Certified v108 slot 94: k=4, dominant=6. -/
def listedDomain094 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 6

/-- Certified v108 slot 95: k=3, dominant=4. -/
def listedDomain095 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 4

/-- Certified v108 slot 96: k=4, dominant=5. -/
def listedDomain096 (s : O14Shape) : Bool :=
  natEqB s.kIdx 4 && natEqB s.dIdx 5

/-- Certified v108 slot 97: k=0, dominant=0. -/
def listedDomain097 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 0

/-- Certified v108 slot 98: k=3, dominant=9. -/
def listedDomain098 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 9

/-- Certified v108 slot 99: k=3, dominant=8. -/
def listedDomain099 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 8

/-- Certified v108 slot 100: k=0, dominant=11. -/
def listedDomain100 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 11

/-- Certified v108 slot 101: k=3, dominant=6. -/
def listedDomain101 (s : O14Shape) : Bool :=
  natEqB s.kIdx 3 && natEqB s.dIdx 6

/-- Certified v108 slot 102: k=9, dominant=7. -/
def listedDomain102 (s : O14Shape) : Bool :=
  natEqB s.kIdx 9 && natEqB s.dIdx 7

/-- Certified v108 slot 103: k=7, dominant=7. -/
def listedDomain103 (s : O14Shape) : Bool :=
  natEqB s.kIdx 7 && natEqB s.dIdx 7

/-- Certified v108 slot 104: k=0, dominant=4. -/
def listedDomain104 (s : O14Shape) : Bool :=
  natEqB s.kIdx 0 && natEqB s.dIdx 4

/-- Certified v108 slot 105: k=1, dominant=13. -/
def listedDomain105 (s : O14Shape) : Bool :=
  natEqB s.kIdx 1 && natEqB s.dIdx 13

/-- Certified v108 slot 106: k=2, dominant=13. -/
def listedDomain106 (s : O14Shape) : Bool :=
  natEqB s.kIdx 2 && natEqB s.dIdx 13

/-- Certified v108 slot 107: k=1, dominant=14. -/
def listedDomain107 (s : O14Shape) : Bool :=
  natEqB s.kIdx 1 && natEqB s.dIdx 14

/-- Propositional listed-shape predicate for the 108 certified ledger slots. -/
def ListedShape (s : O14Shape) : Prop :=
  (s.kIdx = 5 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 6 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 5 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 8 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 10)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 3)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 1)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 2)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 12)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 14)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 4 ∧ s.dIdx = 5)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 0)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 9)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 8)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 11)
    ∨ (s.kIdx = 3 ∧ s.dIdx = 6)
    ∨ (s.kIdx = 9 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 7 ∧ s.dIdx = 7)
    ∨ (s.kIdx = 0 ∧ s.dIdx = 4)
    ∨ (s.kIdx = 1 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 2 ∧ s.dIdx = 13)
    ∨ (s.kIdx = 1 ∧ s.dIdx = 14)

/-- Certified slot lookup.  Unlisted shapes default to slot 0; downstream code
uses this only on `ListedShapeInst`, where the semantic layer supplies the
listed-shape proof. -/
def certifiedPairSlot (s : O14Shape) : Fin ChartCount :=
  if listedDomain000 s then ⟨0, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain001 s then ⟨1, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain002 s then ⟨2, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain003 s then ⟨3, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain004 s then ⟨4, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain005 s then ⟨5, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain006 s then ⟨6, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain007 s then ⟨7, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain008 s then ⟨8, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain009 s then ⟨9, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain010 s then ⟨10, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain011 s then ⟨11, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain012 s then ⟨12, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain013 s then ⟨13, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain014 s then ⟨14, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain015 s then ⟨15, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain016 s then ⟨16, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain017 s then ⟨17, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain018 s then ⟨18, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain019 s then ⟨19, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain020 s then ⟨20, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain021 s then ⟨21, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain022 s then ⟨22, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain023 s then ⟨23, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain024 s then ⟨24, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain025 s then ⟨25, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain026 s then ⟨26, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain027 s then ⟨27, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain028 s then ⟨28, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain029 s then ⟨29, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain030 s then ⟨30, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain031 s then ⟨31, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain032 s then ⟨32, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain033 s then ⟨33, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain034 s then ⟨34, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain035 s then ⟨35, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain036 s then ⟨36, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain037 s then ⟨37, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain038 s then ⟨38, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain039 s then ⟨39, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain040 s then ⟨40, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain041 s then ⟨41, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain042 s then ⟨42, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain043 s then ⟨43, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain044 s then ⟨44, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain045 s then ⟨45, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain046 s then ⟨46, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain047 s then ⟨47, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain048 s then ⟨48, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain049 s then ⟨49, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain050 s then ⟨50, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain051 s then ⟨51, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain052 s then ⟨52, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain053 s then ⟨53, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain054 s then ⟨54, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain055 s then ⟨55, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain056 s then ⟨56, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain057 s then ⟨57, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain058 s then ⟨58, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain059 s then ⟨59, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain060 s then ⟨60, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain061 s then ⟨61, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain062 s then ⟨62, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain063 s then ⟨63, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain064 s then ⟨64, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain065 s then ⟨65, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain066 s then ⟨66, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain067 s then ⟨67, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain068 s then ⟨68, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain069 s then ⟨69, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain070 s then ⟨70, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain071 s then ⟨71, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain072 s then ⟨72, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain073 s then ⟨73, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain074 s then ⟨74, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain075 s then ⟨75, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain076 s then ⟨76, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain077 s then ⟨77, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain078 s then ⟨78, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain079 s then ⟨79, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain080 s then ⟨80, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain081 s then ⟨81, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain082 s then ⟨82, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain083 s then ⟨83, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain084 s then ⟨84, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain085 s then ⟨85, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain086 s then ⟨86, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain087 s then ⟨87, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain088 s then ⟨88, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain089 s then ⟨89, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain090 s then ⟨90, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain091 s then ⟨91, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain092 s then ⟨92, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain093 s then ⟨93, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain094 s then ⟨94, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain095 s then ⟨95, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain096 s then ⟨96, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain097 s then ⟨97, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain098 s then ⟨98, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain099 s then ⟨99, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain100 s then ⟨100, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain101 s then ⟨101, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain102 s then ⟨102, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain103 s then ⟨103, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain104 s then ⟨104, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain105 s then ⟨105, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain106 s then ⟨106, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else if listedDomain107 s then ⟨107, by norm_num [EQODL1CoverInterface.ChartCount]⟩
  else ⟨0, by norm_num [EQODL1CoverInterface.ChartCount]⟩

/-- Numeric chart slot of a listed shape. -/
def chartOfListedShape (s : O14Shape) : Nat :=
  (certifiedPairSlot s).val

theorem chartOfListedShape_lt (s : O14Shape) :
    chartOfListedShape s < ChartCount :=
  (certifiedPairSlot s).isLt

/-- EQ-ODL1 instances whose structural shape is one of the 108 certified
ledger slots.  Proving that real EQ-ODL1 instances inhabit this subtype is the
remaining structural extraction/coverage obligation. -/
structure ListedShapeInst (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) where
  inst : EQODL1ShapeInst G c rows Q
  listed : ListedShape inst.shape

/-- Core accessor for the listed-instance subtype. -/
def listedCore {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert}
    (I : ListedShapeInst G c rows Q) : ODLCoreData G c rows Q :=
  I.inst.core

/-- The total classifier on listed EQ-ODL1 instances. -/
def listedClassifier {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert} :
    EQODL1Classifier (ListedShapeInst G c rows Q) := {
  chartOf := fun I => chartOfListedShape I.inst.shape,
  chartOf_lt := fun I => chartOfListedShape_lt I.inst.shape
}

end Generated
end O14
end Erdos23Delta0
