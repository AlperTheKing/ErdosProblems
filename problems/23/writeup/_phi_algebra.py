"""Exact-gate Codex's algebra (block 13): the supersolution phi's two 'easy' conditions are proven.
Verify exactly (Fraction):
 (i)  phi[q] = T[q]/N - (K_QQ u)[q]/N^2   for q in Q   (identity);
 (ii) (K_QQ u)[q] <= N*T[q]  => phi[q] >= 0   (so (A) phi>=0 on Q holds);
 (iii) N*phi[q] - (K phi)[q] = (K_QQ^2 u)[q]/N^2  (>=0)  for q in Q   (so (B) on Q holds, residual manifestly nonneg).
If all exact, then (A) and (B-on-Q) are PROVEN and the whole certificate reduces to (k2) = (B-on-O)."""
from fractions import Fraction as F
from _h import dec, loads
from _superphi import build, phivec, blow

def check(g6, info):
    K,T,N,n=build(info)
    phi,O,Q=phivec(K,T,N,n)
    Qs=set(Q); u={q:F(N)-T[q] for q in Q}
    bad=[]
    for q in Q:
        # (i) identity
        KQQu=sum(K[q][q2]*u[q2] for q2 in Q)
        rhs_i = T[q]/N - KQQu/(N*N)
        if phi[q]!=rhs_i: bad.append(('i',q,phi[q]-rhs_i))
        # (ii) phi>=0  and (K_QQ u)<=N T[q]
        if phi[q]<0: bad.append(('phi<0',q,phi[q]))
        if KQQu > N*T[q]: bad.append(('KQQu>NT',q))
        # (iii) N phi[q]-(K phi)[q] = (K_QQ^2 u)[q]/N^2
        Kphi=sum(K[q][w]*phi[w] for w in range(n))
        lhs=N*phi[q]-Kphi
        KQQ2u=sum(K[q][q2]*sum(K[q2][q3]*u[q3] for q3 in Q) for q2 in Q)
        rhs_iii=KQQ2u/(N*N)
        if lhs!=rhs_iii: bad.append(('iii',q,lhs-rhs_iii))
        if rhs_iii<0: bad.append(('iii<0',q))
    return bad,len(O),len(Q)

if __name__=="__main__":
    print("=== exact gate of Codex's phi algebra (A + B-on-Q proven) ===")
    cases=[("G?bF`w",1),("I?BD@g]Qo",1),("I?ABCc]}?",1),("J?AEB?oE?W?",1)]
    for g6,t in cases:
        n,E=dec(g6); info=loads(n,E)
        bad,no,nq=check(g6,info)
        print(f"  {g6:13} N={n} |O|={no} |Q|={nq}: {'ALL IDENTITIES EXACT, phi>=0 ok' if not bad else 'MISMATCH: '+str(bad[:3])}")
    for g6,t in [("J???E?pNu\\?",2),("I?BD@g]Qo",2),("J?`@C_W{Ck?",2)]:
        nn,EE=blow(g6,t)
        if nn>22: continue
        info=loads(nn,EE)
        if info is None: continue
        bad,no,nq=check(g6,info)
        print(f"  {g6}[{t}] N={nn} |O|={no}: {'ALL EXACT' if not bad else 'MISMATCH: '+str(bad[:3])}")
