from _h import dec, loads
from _schur_spec import test
def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE
print("=== Schur cert on OVERLOADED-graph blow-ups (t=2, where O is nonempty) ===")
for g6 in ["I?BD@g]Qo","I?ABCc]}?","J?`@C_W{Ck?","J?AA@AW^?}?","H?AFBo]","I?ABCc]}?"]:
    nn,EE=blow(g6,2)
    if nn>22: print(f"  {g6}[2] N={nn}: skip(maxcut)"); continue
    info=loads(nn,EE)
    if info is None: print(f"  {g6}[2]: skip"); continue
    st,d=test(info)
    mr=float(d['minrow']) if (d and 'minrow' in d and d['minrow'] is not None) else None
    print(f"  {g6}[2] N={nn}: {st} O={d['O'] if d else None} minrow={round(mr,3) if mr is not None else None} fails={d['fails'] if (d and 'fails' in d) else None}")
