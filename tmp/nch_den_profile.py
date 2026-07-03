import sys
sys.path.insert(0, 'problems/23/writeup')
from math import gcd
from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string

def lcm(a,b): return a//gcd(a,b)*b
for name,n,edges in named_graphs(11):
    if name not in ('MycC11','MycGrotzsch'):
        continue
    best, structs = gamma_min_structs(name,n,edges)
    print(name,'n',n,'cuts',len(structs))
    use = structs[:3] if name=='MycC11' else structs
    for side_int,side,st,gamma in use:
        M,ell,T,mu,cyc=st
        den=1; rows=0; max_cyc=0
        for rs in cyc.values():
            den=lcm(den,len(rs)); rows += len(rs); max_cyc=max(max_cyc,len(rs))
        print(' side',side_string(n,side_int),'bad',len(M),'rows',rows,'max_cyc',max_cyc,'lcm',den,'bits',den.bit_length())
