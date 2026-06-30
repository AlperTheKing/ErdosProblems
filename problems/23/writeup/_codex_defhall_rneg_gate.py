"""Search whether Hall-deficient terminal-shadow switches can contain R<0 vertices."""

import subprocess
from collections import Counter

from _h import GENG, dec, maxcut_all, Bconn
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import test_sidedoor_for_switch


def scan(max_n=9):
    acc=Counter(); first=None
    for nn in range(5,max_n+1):
        for g6 in subprocess.run([GENG,'-tc',str(nn)], capture_output=True, text=True).stdout.split():
            n,edges=dec(g6); adj=adj_from_edges(n,edges)
            for side in maxcut_all(n,adj):
                if not Bconn(n,adj,side): continue
                st=struct_for_side(n,adj,side)
                if st is None: continue
                R=residuals(n,adj,side)
                if R is None: continue
                negmask=0
                for i,r in enumerate(R):
                    if r<0: negmask |= 1<<i
                for mask in range(1,(1<<n)-1):
                    if boundary_delta(n,adj,side,mask)!=0: continue
                    if not Bconn(n,adj,flip_side(side,mask)): continue
                    det=terminal_shadow_details(n,adj,side,st,mask)
                    if det is None: continue
                    acc['terminal']+=1
                    res=test_sidedoor_for_switch(n,adj,side,st,mask,20,False)
                    if res.get('deficient',0)>0:
                        acc['deficient']+=1
                        if mask & negmask:
                            acc['def_with_neg']+=1
                            if first is None:
                                first=(g6,n,''.join(map(str,side)),tuple(i for i in range(n) if (mask>>i)&1),[(i,str(R[i])) for i in range(n) if (mask>>i)&1 and R[i]<0],res)
        print('N',nn,dict(acc),flush=True)
    print('FINAL',dict(acc),'first',first)
    print('VERDICT', 'PASS' if acc['def_with_neg']==0 else 'FAIL')

if __name__=='__main__': scan(9)
