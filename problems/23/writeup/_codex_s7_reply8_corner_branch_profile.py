from __future__ import annotations
from fractions import Fraction
from collections import defaultdict
import argparse, json
from pathlib import Path
from importlib.machinery import SourceFileLoader
mod = SourceFileLoader('corner','problems/23/writeup/_codex_s7_reply8_corner_probe.py').load_module()

def classify(bound):
    out={fam:{str(j):defaultdict(lambda:{'count':0,'min_pi':None,'min_point':None}) for j in range(4,8)} for fam in ('YXCOR','YCOR')}
    for a in range(1,bound+1):
      for b in range(1,bound+1):
       for c in range(1,bound+1):
        for d in range(1,bound+1):
         for e in range(1,bound+1):
          for f in range(1,bound+1):
            Y,R,D,Z,A,B,S,Ms=mod.invariants(a,b,c,d,e,f)
            for q in range(1,D+1):
              for j,M in Ms.items():
                if not mod.feasible_other_slacks(Ms,j):
                    continue
                # YXCOR true interval data
                x=1; v=M-q; u=q-v
                if v>=1 and u>=1 and v<=e:
                    lows={'u':Fraction(M+1,2),'vE':Fraction(M-e,1),'one':Fraction(1,1)}
                    ups={'v':Fraction(M-1,1),'D':Fraction(D,1)}
                    L=max(lows.values()); U=min(ups.values())
                    lname='+'.join(sorted(k for k,val in lows.items() if val==L))
                    uname='+'.join(sorted(k for k,val in ups.items() if val==U))
                    pi=mod.cleared_phi(Y,Z,A,B,S,M,S+2+q,x,q,v,e)
                    key=lname+'|'+uname
                    rec=out['YXCOR'][str(j)][key]; rec['count']+=1
                    if rec['min_pi'] is None or pi<rec['min_pi']:
                        rec['min_pi']=pi; rec['min_point']=[a,b,c,d,e,f,q,x,u,v]
                # YCOR true interval data
                x=R-1; v=M-x*q; u=q-v
                if v>=1 and u>=1 and v<=e:
                    lows={'u':Fraction(M+1,R),'vE':Fraction(M-e,R-1),'one':Fraction(1,1)}
                    ups={'v':Fraction(M-1,R-1),'D':Fraction(D,1)}
                    L=max(lows.values()); U=min(ups.values())
                    lname='+'.join(sorted(k for k,val in lows.items() if val==L))
                    uname='+'.join(sorted(k for k,val in ups.items() if val==U))
                    pi=mod.cleared_phi(Y,Z,A,B,S,M,S+R+q,x,q,v,e)
                    key=lname+'|'+uname
                    rec=out['YCOR'][str(j)][key]; rec['count']+=1
                    if rec['min_pi'] is None or pi<rec['min_pi']:
                        rec['min_pi']=pi; rec['min_point']=[a,b,c,d,e,f,q,x,u,v]
    # normal json dict
    return {fam:{j:dict(branches) for j,branches in out[fam].items()} for fam in out}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--bound',type=int,default=12); ap.add_argument('--summary',default='')
    args=ap.parse_args(); out=classify(args.bound)
    for fam in ('YCOR','YXCOR'):
        for j in range(4,8):
            print(fam,j)
            for key,rec in sorted(out[fam][str(j)].items(), key=lambda kv:-kv[1]['count']):
                print(' ',key,'count',rec['count'],'min',rec['min_pi'],'pt',rec['min_point'])
    if args.summary:
        Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True))
