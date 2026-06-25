# GPT Pro prompt draft — Erdős #23 q14/t2 cap74 frontier after V257

CONTEXT:
We are attacking Erdős #23 / a(30)=36 through the low-codegree q=14,t=2,cap=74 branch. q15 is closed. In q14/t2, all p>=17 cap74 rows are now closed. Current verified frontier from `q14_t2_scalar_audit_post_v257.tsv` is exactly 17 scalar rows, all with U=12:

(p,e_R)=(16,21):
- z=3,s1=5,s2=5,d=1
- z=4,s1=4,s2=4,d=2
- z=5,s1=3,s2=3,d=3
- z=6,s1=2,s2=2,d=4
- z=8,s1=0,s2=0,d=6

(p,e_R)=(15,22):
- z=2,s1=6,s2=6,d=0
- z=3,s1=5,s2=5,d=1
- z=4,s1=4,s2=4,d=2
- z=5,s1=3,s2=3,d=3
- z=6,s1=2,s2=2,d=4
- z=8,s1=0,s2=0,d=6

(p,e_R)=(14,23): same six z rows as p15.

Known verified tools/lemmas:
- cap=74 means M=sum_R m_r=74, with 14 R vertices.
- p+e_R=37 throughout these remaining rows.
- For p17/eR20 we used x_r=8-m_r, sum x=38 and R-edge x_u+x_v>=4, C-tight equalities, plus terminal/RR/exact-M finite certificates.
- For p<=16 we still have M=74 and p+e_R=37. Need be careful with any universal bound on m_r: previously for p17 we used m_r<=8; for p13 special rows we had m_r<=6 from P degree sequence. Do not assume stronger m_r<=k without proof.
- Label structure: z zeros, s1 singletons label {1}, s2 singletons label {2}, d doubletons label {1,2}; U=s1+s2+2d=12 in all remaining rows.
- Local domination floors: zeros need d_D(z)+d_S1(z)>=2 and d_D(z)+d_S2(z)>=2; singletons need at least two opposite-singleton neighbours when opposite side exists; R triangle-free constraints apply. For z5 with s1=s2=3 missing S1S2 graph is a matching; for z6 S1S2=K2,2; for z8 only Z-D/Z-Z categories.

STATUS:
Need close all 17 remaining cap74 rows. We want NEW proof/finite certificate, not cosmetic brute force. Current solver can run terminal/RR/exact-M category or fixed-P C++ SAT, but we want the smallest mathematical/skeleton cuts first.

QUESTION:
Give the highest-leverage next reduction for the remaining p16/p15/p14 frontier. Prefer a rigorous row-wide scalar/skeleton lemma. If not possible, specify the smallest finite certificate to run first, with exact category equations, forced tight vertices, and constraints. Start with p16/e_R=21 unless another row is strictly easier. Be adversarial: do not assume m_r bounds not proven. End with weakest steps and what must be verified in C++.
