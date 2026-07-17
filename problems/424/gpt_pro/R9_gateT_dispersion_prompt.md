We are studying a concrete finite-product question arising in Erdos Problem 424. Work only on the single asymptotic statement below.

In translated coordinates define
L_2(t)=2t, L_3(t)=3t+1, L_5(t)=5t+3.
Fix the ray (a,b,c)=(3,2,1) and Q=2^3*3^2*5=360. Let D_k be the set of offsets d of all affine words containing exactly 3k copies of L_2, 2k copies of L_3, and k copies of L_5, so each word is t -> Q^k t+d. Put
H_k={8Q^k+d+1:d in D_k}.
Choose rho_k in {0,2} so that C_k={h in H_k:h mod 3=rho_k} is larger, ties to 2. Define
U_k={2h-1:h in C_k} if rho_k=2, and U_k={4h-3:h in C_k} if rho_k=0;
V_k={3h-1:h in C_k}.
For K>=2 let I_K={ceil(K/3),...,floor(2K/3)} and take the labelled edge multiset
E_K = disjoint union over i in I_K of U_i x V_{K-i}.
For z>=1 let r_K(z)=#{(i,u,v):uv=z} and N_K=sum_z r_K(z).

Exact computation gives, at K=4, N_K=60,512,841 and exactly 60,512,829 edges lie on products with r_K(z)<=2. This is finite evidence only.

Please prove or refute the following precise gate:
There exist fixed integers L>=1,K0 and eta>0 such that for every K>=K0,
  sum_{z:r_K(z)<=L} r_K(z) >= eta N_K.

A proof should use the exact arithmetic of affine offsets and product equalities, not assume positive density, a bounded full second moment, or pointwise injectivity. A refutation must give an explicit infinite collision family showing that for every fixed L the retained edge fraction has liminf zero. Track labelled cross-scale edges exactly. Do not return an equivalent reformulation or finite experiment. If the full gate is out of reach, give one genuinely proved asymptotic collision lemma that advances or obstructs it, with all quantifiers.
Show more
