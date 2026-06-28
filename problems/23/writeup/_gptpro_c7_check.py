"""DECISIVE check of GPT-Pro's ROW-SUM counterexample (C7 blow-up, N=1212, too big for vertex enumeration).
   C7[n0..n6]=(3,423,173,7,176,7,423). Cut X={0,2,3,5}, Y={1,4,6}: bad edge class V2-V3 (min product 1211),
   ell=7, B-geodesic path parts [2,1,0,6,5,4,3]. QUOTIENT-level exact computation (Fraction).
   For a bad edge f=(u in V2, w in V3): p_f = 1 on its two endpoints u,w; p_f = 1/n_i uniform on intermediate
   parts i in {1,0,6,5,4}; 0 elsewhere. |M| = n2*n3 = 173*7 = 1211 bad edges.
   Compute per-part: T_i, K[o][q] (o in V0 overloaded), R_q, s_q, then ROW-SUM(o), STAR-K-multi PSD on O=V0,
   and the FULL-inverse cond3 margin -- to see exactly which holds/fails."""
from fractions import Fraction as F

n=[3,423,173,7,176,7,423]; N=sum(n)   # =1212
ell=7; nbad=n[2]*n[3]                  # 1211
inter=[1,0,6,5,4]                      # intermediate parts on the geodesic (between endpoints V2,V3)
endpts=[2,3]

# p-contribution sum_f p_f(v) for a vertex in part i (call it Pi := sum over all bad edges of p_f(v))
# intermediate part i: each f gives 1/n[i] -> Pi = nbad / n[i]
# endpoint part 2 (V2): a vertex u in V2 is endpoint of n[3] bad edges (u,w), w in V3 -> p_f(u)=1 for those -> Pi = n[3]
# endpoint part 3 (V3): Pi = n[2]
def Pi(i):
    if i in inter: return F(nbad, n[i])
    if i==2: return F(n[3])
    if i==3: return F(n[2])
    return F(0)
T=[ell*Pi(i) for i in range(7)]        # T_i = ell * sum_f p_f(v)
print("part sizes", n, "N", N, "ell", ell, "|M|", nbad)
print("loads T_i:", [str(t) for t in T], "floats:", [round(float(t),3) for t in T])
O=[i for i in range(7) if T[i]>N]
print("overloaded parts O:", O, " (each has", [n[i] for i in O], "vertices)")

# K[o][q] for o in V0 (part 0), q in part j:
# K[o][q] = sum_f p_f(o) p_f(q).  p_f(o)=1/n0 for ALL f (part 0 is intermediate).
#  q in intermediate part j != 0:  p_f(q)=1/n[j] -> K = nbad/(n0 n[j])
#  q in part 0, q != o or =o:      p_f(q)=1/n0   -> K = nbad/(n0 n0)
#  q in V2 (endpoint): for fixed q, p_f(q)=1 on the n3 edges (q,*) -> K = sum over those f of (1/n0)*1 = n3/n0
#  q in V3:            K = n2/n0
n0=n[0]
def Koq(j):
    if j==0: return F(nbad, n0*n0)
    if j in inter: return F(nbad, n0*n[j])
    if j==2: return F(n[3], n0)
    if j==3: return F(n[2], n0)
    return F(0)

# ROW-SUM(o) for o in V0: sum over q in Q (parts not in O) of K[o][q] R_q/(R_q+s_q), s_q = sum_{o' in O} K[o'][q]
# O = part 0 (n0=3 vertices); for q not in V0, K[o'][q] same for all o' in V0 -> s_q = n0 * Koq(j).
# (Q excludes all of V0.)
D_o = T[0]-N
print("o in V0: T(o)=", T[0], "=", round(float(T[0]),4), " D_o=T(o)-N=", D_o, "=", round(float(D_o),4))
lhs=F(0)
for j in range(7):
    if j in O: continue            # q must be in Q
    Rq=F(N)-T[j]
    if Rq<=0: continue
    K_=Koq(j); s_q=n0*K_
    term = K_*Rq/(Rq+s_q)
    lhs += n[j]*term               # n[j] vertices in part j, each same
print("ROW-SUM LHS:", lhs, "=", round(float(lhs),4))
print("ROW-SUM:", "HOLDS" if lhs>=D_o else "***FAILS***", " (LHS-D_o =", lhs-D_o, "=", round(float(lhs-D_o),4),")")

# STAR-K-multi (Z PSD on O=V0, 3 symmetric vertices): Z = N I_3 - c J_3, eigenvalue N-3c (= ROW-SUM margin) on 1_3.
c = F(nbad, n0*n0)
for j in range(7):
    if j in O: continue
    Rq=F(N)-T[j]
    if Rq<=0: continue
    K_=Koq(j); s_q=n0*K_
    c += n[j]*K_*K_/(Rq+s_q)
zmin = F(N)-3*c
print("STAR-K-multi: c=", round(float(c),4), " min-eig N-3c=", round(float(zmin),4),
      "->", "PSD" if zmin>=0 else "***NOT PSD (STAR-K-multi FAILS)***")

# cond3 full inverse via part-symmetric closed form: every geodesic hits each part once so reduced K-action
# sum_{v' in part j}K[v][v'] = Pi(i) for all j. Solve N g_i - Pi(i) S = N-T_i, S=sum_Q g_j => S=A/(N-B).
Qparts=[j for j in range(7) if j not in O]
A=sum(F(N)-T[i] for i in Qparts); B=sum(Pi(i) for i in Qparts)
S=A/(F(N)-B); P0=Pi(0)
orow = F(N)-T[0] + P0*S
print("cond3 (full inverse): O-row margin = N-T(o)+P0*S =", round(float(orow),4),
      "->", "HOLDS" if orow>=0 else "***cond3 FAILS***")
print("VERDICT: ROW-SUM", "FAILS" if lhs<D_o else "holds", "| STAR-K-multi", "FAILS" if zmin<0 else "holds",
      "| cond3(full-inv)", "HOLDS" if orow>=0 else "FAILS")
