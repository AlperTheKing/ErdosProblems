import json
for k in range(1,9):
 A=[]
 for i in range(k):
  b={'vertices':[10+2*i,11+2*i],'support_edges':[[10+2*i,11+2*i]]};A.append({'endpoints':[0,1],'rows':[{'vertices':[0,1,2+i],'support_edges':[[0,2+i],[1,2+i]]},b,b]})
 I={'name':f'cable-{k}','base_edges':[[0,1]],'atoms':A,'default_cost':[0,0,1,3,6,10,15,21,28],'cost_tables':{'0':[0,1,4,9,16,25,36,49,64],'1':[0,1,4,9,16,25,36,49,64]},'overflow_slope':100};open(f'toy{k}.json','w').write(json.dumps(I,sort_keys=True,indent=2)+'\n')
