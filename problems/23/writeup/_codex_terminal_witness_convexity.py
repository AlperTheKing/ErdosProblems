"""Mine convexity of full witness graphs for neutral terminal-shadow switches."""

import argparse, itertools, subprocess
from collections import Counter
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details, max_bipartite_matching


def consecutive_for_order(order, sets):
    pos={x:i for i,x in enumerate(order)}
    for s in sets:
        if not s: continue
        idx=sorted(pos[x] for x in s)
        if idx[-1]-idx[0]+1 != len(idx): return False
    return True

def has_order(univ, sets, cap):
    univ=tuple(univ)
    if len(univ)>cap: return None
    for order in itertools.permutations(univ):
        if consecutive_for_order(order,sets): return True
    return False

def scan_graph(name,n,edges,acc,cap):
    adj=adj_from_edges(n,edges)
    for side in maxcut_all(n,adj):
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        for mask in range(1,(1<<n)-1):
            if boundary_delta(n,adj,side,mask)!=0: continue
            det=terminal_shadow_details(n,adj,side,st,mask)
            if det is None or not det['cross_m'] or len(det['cross_m']) != len(det['bdy_b']):
                continue
            F=tuple(sorted(det['cross_m'])); E=tuple(sorted(det['bdy_b']))
            witnesses={e:set(fs) for e,fs in det['witnesses'].items()}
            fsets=[]
            for f in F:
                fsets.append({e for e in E if f in witnesses[e]})
            esets=[witnesses[e] for e in E]
            fconv=has_order(E,fsets,cap)
            econv=has_order(F,esets,cap)
            msize,_=max_bipartite_matching(E,F,{e:witnesses[e] for e in E})
            acc['switches']+=1
            acc['fconv'][fconv]+=1; acc['econv'][econv]+=1; acc['both'][(fconv,econv)]+=1
            acc['sdr'][msize==len(E)]+=1
            if (fconv is False or econv is False) and acc['first_fail'] is None:
                acc['first_fail']=(name,n,''.join(map(str,side)),tuple(i for i in range(n) if (mask>>i)&1),F,E,fsets,esets,fconv,econv,msize)
                return

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--min-n',type=int,default=5); ap.add_argument('--max-n',type=int,default=9); ap.add_argument('--cap',type=int,default=8)
    args=ap.parse_args(); acc={'switches':0,'fconv':Counter(),'econv':Counter(),'both':Counter(),'sdr':Counter(),'first_fail':None}
    for nn in range(args.min_n,args.max_n+1):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,edges=dec(g6); scan_graph(g6,n,edges,acc,args.cap)
            if acc['first_fail']: break
        print('N',nn,'switches',acc['switches'],'fconv',dict(acc['fconv']),'econv',dict(acc['econv']),'sdr',dict(acc['sdr']),flush=True)
        if acc['first_fail']: break
    print('both',dict(acc['both']))
    print('first_fail',acc['first_fail'])

if __name__=='__main__': main()
