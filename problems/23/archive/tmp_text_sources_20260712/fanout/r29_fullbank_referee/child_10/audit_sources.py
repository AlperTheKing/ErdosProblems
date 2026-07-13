#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[4]
F=['problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean','problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean','problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean','problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean','problems/23/lean/Erdos23Delta0/DisjointPetalHalfSqueeze.lean','problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean']
T={n:(R/n).read_text(encoding='utf-8') for n in F}
def sec(t,a,b): return t[t.index(a):t.index(b,t.index(a))]
agg=sec(T[F[0]],'structure FullBankGlobalPackage','namespace FullBankGlobalPackage'); chk=sec(T[F[0]],'structure Checked (P : FullBankGlobalPackage','theorem localSurplus_le_localDemand')
dat=sec(T[F[1]],'structure OwnEdgeDoorSourceData','namespace OwnEdgeDoorSourceData'); dchk=sec(T[F[1]],'def Checked : Prop :=','/-- Kernel-decidable'); ada=sec(T[F[2]],'structure DoorWallAdapter','/-- The graph-shore'); geo=sec(T[F[2]],'structure TypedPetalGeometry','/-- Accepted typed')
for x in ['portEdge','doorOf','CapSource','sinkOf','legal']: assert x not in agg
for x in ['portEdge','doorOf','doorLegal','sinkOf']: assert x not in chk
for x in ['portEdge','token','doorOf']: assert x in dat
for x in ['Injective D.portEdge','CapSource.door (D.portEdge p)','25 ≤']: assert x in dchk
for x in ['sinkOf','sinkOf_injective','legal_of_door_source','cap_eq_hallCapQ']: assert x in ada
for x in ['shore','shortEdge','petals_disjoint','short_is_boundary','port_is_boundary']: assert x in geo
lean=[p for p in (R/'problems/23/lean/Erdos23Delta0').rglob('*.lean') if 'O14/Generated' not in p.relative_to(R).as_posix()]; hits={}
for s in ['OwnEdgeDoorSourceData','DoorWallAdapter','TypedPetalGeometry']:
 hits[s]=[{'file':p.relative_to(R).as_posix(),'line':i,'text':l.strip()} for p in lean for i,l in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if s in l]
 assert hits[s] and not any('r29' in h['file'].lower() for h in hits[s])
o={'verdict':'provider_missing','reason':'FullBankGlobalPackage stores aggregate (comp,kind,sourceId,capQ) only; typed port-edge incidence and wall-sink interpretation are separate uninstantiated inputs.','sha256':{n:hashlib.sha256(T[n].encode()).hexdigest() for n in F},'aggregate_missing':['portEdge','typed token source','doorOf','wall sinkOf','wall legal incidence'],'typed_required':{'OwnEdgeDoorSourceData':['portEdge','token','doorOf'],'OwnEdgeDoorSourceData.Checked':['Injective portEdge','token[doorOf p].source = door(portEdge p)','token[doorOf p].capQ >= 25'],'DoorWallAdapter':['sinkOf','sinkOf_injective','legal_of_door_source','cap_eq_hallCapQ','sink_capacity_nonneg'],'TypedPetalGeometry':['shore','shortEdge','petals_disjoint','short_is_boundary','port_is_boundary']},'symbol_hits':hits}
out=Path(__file__).with_name('audit_sources.json'); out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps({'verdict':o['verdict'],'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},sort_keys=True))

