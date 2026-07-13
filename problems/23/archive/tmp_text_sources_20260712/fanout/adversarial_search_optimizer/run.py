import json,sys
from optimizer import solve,verify
I=json.load(open(sys.argv[1]))
if len(sys.argv)>3 and sys.argv[3]=='verify':verify(I,json.load(open(sys.argv[2])));print('VERIFIED')
else:
 z=solve(I);open(sys.argv[2],'w').write(json.dumps(z,sort_keys=True,indent=2)+'\n');print(z['best_score'],z['best_picks'],len(z['terminal_scores']))
