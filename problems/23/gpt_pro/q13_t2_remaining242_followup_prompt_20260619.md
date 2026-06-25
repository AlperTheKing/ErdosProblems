CONTEXT: Erdős Problem #23, finite n=30 reduction toward a(30)=36.

We are in the q=13, r0=8, t=2 rooted branch with the five-label support

  c0=c1=c6=0,
  labels: S2={2}, D12={1,2}, S3={3}, D13={1,3}, T={1,2,3}.

R-edges occur only in the blocks

  S2-D13, D12-S3, and optionally S2-S3.

The exact-state verifier uses:

1. triangle-free exact A/B state law:
   A_i B_j is an edge iff X_i cap Y_j is empty, and |X_i cap Y_j|=1 is forbidden;
2. full R/R nonedge codegree >=2 and edge codegree =0;
3. A/R, B/R, A/A, B/B codegree checks;
4. root-side visibility;
5. cap M=sum_R m_r and exact p/e_R row;
6. Psi rooted cut inequalities, sometimes restricted to label-class-uniform masks;
7. the safe H14 anti-tightness cut:

   for r notin U_i:
     D(r)+|U_i|+d_R(r,U_i) >= 17,
   where D(r)=alpha_r+beta_r+d_R(r)+|L(r)|.

Important correction: your previous answer correctly rejected the stronger terminal-reroot/terminal-touch equality. We are NOT using:

  d_R(r,U_i)=2 ==> D(r)=8,
  or touched terminal s ==> D(s)=8.

Those are considered unsafe/circular unless separately justified. Please do not use them.

CURRENT COMPUTATIONAL FACTS:

Starting from 257 exact p/e_R/M rows in this five-label q13/t2 branch:

- anti-tightness only closed 5 rows, 252 remained UNKNOWN.
- an R-skeleton M-lower optimizer explains 4 of those 5 closures.
- the remaining anti-tightness closure, profile 6191

    cnt=(0,0,3,2,3,2,0,3), e_R=12, p=27, M=57..58,

  is a Psi rooted-cut phenomenon, not anti-tightness:

    local only: UNKNOWN at 60s
    local + anti-tightness: UNKNOWN at 60s
    Phi only: UNKNOWN at 60s
    Psi only: INFEASIBLE in 16.8s
    Phi/Psi: INFEASIBLE in 18.4s

- class-uniform Psi cuts (at most 32 masks) on the 252 UNKNOWN rows closed 8 more:

    4965 eR=11 p=26 M=55..56 cnt=(0,0,2,2,2,2,0,5)
    4999 eR=11 p=27 M=57..57 cnt=(0,0,2,2,3,2,0,4)
    5222 eR=15 p=23 M=54..62 cnt=(0,0,2,3,5,2,0,1)
    5222 eR=15 p=22 M=54..63 cnt=(0,0,2,3,5,2,0,1)
    5344 eR=15 p=23 M=54..62 cnt=(0,0,2,4,4,3,0,0)
    5344 eR=15 p=22 M=54..63 cnt=(0,0,2,4,4,3,0,0)
    6165 eR=11 p=27 M=57..57 cnt=(0,0,3,2,2,2,0,4)
    5350 eR=15 p=22 M=55..64 cnt=(0,0,2,4,5,2,0,0)

- I then added a safe isolated-support separation for the static isolated T vertices.

  If t is isolated in R and r != t:

    if B_r \ B_t is nonempty, then |A_t \ A_r| >= 2;
    if A_r \ A_t is nonempty, then |B_t \ B_r| >= 2.

  Proof sketch: for b in B_r \ B_t, the nonedge (b,t) needs two common
  neighbours. They cannot come from R/roots/C/B; they must be A-vertices
  adjacent to t and b. If such an A-vertex were also in A_r, then the exact
  A/B law would make ab a nonedge via common R-neighbour r. Hence the two
  common neighbours lie in A_t \ A_r. Symmetric for A_r \ A_t.

  With class-uniform Psi + isolated-support on the 244 remaining rows:

    2 INFEASIBLE, 242 UNKNOWN, 0 SAT.

  The two new closures were:

    6170 eR=11 p=27 M=58..58 cnt=(0,0,3,2,2,3,0,3)
    6165 eR=11 p=26 M=57..58 cnt=(0,0,3,2,2,2,0,4)

QUESTION:

Find the next smallest mathematically safe strengthening for the remaining 242 UNKNOWN rows.

Requirements:

1. No terminal-reroot equality or terminal-touch equality unless you prove a non-circular frontier closure that justifies it.
2. Prefer P-free / fixed-P-free lemmas: R-skeleton, exact M, state-support, class-Psi, or projected rooted-cut constraints.
3. Give a rigorous proof of any proposed lemma, with explicit assumptions.
4. Give exact CP-SAT/C++ encoding advice.
5. If a hand row reduction is possible, state exactly which profiles or structural family it closes.
6. If no broad lemma is visible, pick the single most informative next finite experiment and explain why.

Please be adversarial: first check whether the isolated-support lemma or anti-tightness cut has hidden assumptions; then propose the next move.
