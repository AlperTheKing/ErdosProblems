"""Independent exact R29 vertexSlack audit."""
from fractions import Fraction
N,DEFECT,SCALE=2943,28,25
HUBS=(0,1,2)
RIGID_DOUBLE_STAR_ROWS,ROW_LENGTH=26*26,5
def main():
 t=ROW_LENGTH*RIGID_DOUBLE_STAR_ROWS
 assert RIGID_DOUBLE_STAR_ROWS==676 and t==3380 and t-N==437
 cap={v:max(Fraction(0),Fraction(N-t)) for v in HUBS}
 raw=sum(cap.values(),Fraction(0)); scaled=raw/SCALE
 assert cap=={0:Fraction(0),1:Fraction(0),2:Fraction(0)}
 assert raw==scaled==0 and min(Fraction(DEFECT),scaled)==0
 print(f"N={N}\nrigidDoubleStarRows={RIGID_DOUBLE_STAR_ROWS}")
 print(f"T_hub_lower={t}\nT_hub_lower_minus_N={t-N}")
 print("vertexSlackCap_hubs=0,0,0")
 print(f"aggregateRawVertexSlackCap={raw}\naggregateHallScaledCap={scaled}")
 print(f"defectUnits={DEFECT}\npayableDefectUnits=0")
if __name__=="__main__": main()