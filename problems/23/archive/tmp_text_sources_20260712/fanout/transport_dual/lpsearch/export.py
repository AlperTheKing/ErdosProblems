import json
from pathlib import Path
p=Path(__file__).parent
b=json.loads((p/'base_shores.json').read_text())
w=b['fixtures'][0]['inclusionMinimalDeficientShores'][0].copy();w.update({'g6':'I?`fBO]]?','tupleIndex':43,'choice':[1,1,1],'exactFlowOptimum':17,'totalDemand':19})
(p/'smallest_witness.json').write_text(json.dumps(w,sort_keys=True,separators=(',',':'))+'\n')
r=json.loads((p/'results.json').read_text())
s={'survivors':[{'family':'coordinate component-aware scaled Hall/Farkas','survived':r['survivors']['coordinate_scaled_hall'],'tested':r['counts']['coordinateTests'],'qualification':'alternative demand-group count was zero in every tested coordinate'},{'family':'all-coordinate component-aware scaled Hall/Farkas','survived':r['survivors']['all_coordinate_scaled_hall'],'tested':r['counts']['multiCoordinateTests'],'qualification':'combined alternative demand-group count was zero in every tested tuple'},{'family':'singleton owner Hall','survived':4,'tested':4,'minimumSlack':0},{'family':'full deficient-owner shore Hall','survived':0,'tested':2,'maximumExactGap':2}]}
(p/'survivors.json').write_text(json.dumps(s,sort_keys=True,separators=(',',':'))+'\n')
