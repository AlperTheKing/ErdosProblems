from importlib.machinery import SourceFileLoader
mod = SourceFileLoader('corner','problems/23/writeup/_codex_s7_reply8_corner_probe.py').load_module()

def search(bound=8):
    first=[]
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
                x=1; v=M-q; N=S+2+q
                pi=mod.cleared_phi(Y,Z,A,B,S,M,N,x,q,v,e)
                if pi<0:
                    first.append(('YXCOR',j,pi,(a,b,c,d,e,f,q,M-q,q-(M-q))))
                    return first
                x=R-1; v=M-x*q; N=S+R+q
                pi=mod.cleared_phi(Y,Z,A,B,S,M,N,x,q,v,e)
                if pi<0:
                    first.append(('YCOR',j,pi,(a,b,c,d,e,f,q,x,M-x*q,q-(M-x*q))))
                    return first
    return first
print(search(8))
