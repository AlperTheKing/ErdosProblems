UPDATE:
Your terminal-reroot audit was accepted. I removed the experimental terminal degree equalities from the proof path. I now use only your safe anti-tightness cut:

```text
for r notin U_i:
D(r)+|U_i|+d_R(r,U_i) >= 17,
D(r)=alpha_r+beta_r+d_R(r)+|L(r)|.
```

This is implemented as `--anti-tightness`, without terminal equality.

Fresh computation:

```text
Original q13/r0=8/t=2,(A,B)=(6,7) first 40 hard profiles:
anti-tightness only, timeout=60s, total_workers=100:
40 UNKNOWN, 0 SAT.
```

Then I reran exact p/e_R/M rows from the previous diagnostic core, again with terminal equality disabled and only anti-tightness enabled:

```text
rows: search23/q13_t2_r8_a6b7_row_split_unknown257.tsv
command: exact-row rerun, timeout=30s, total_workers=100, --anti-tightness
result: 5 INFEASIBLE, 252 UNKNOWN, 0 SAT
output: search23/q13_t2_r8_a6b7_exact_unknown257_anti_30.tsv
```

The five safely closed rows are:

```text
ordinal profile e_R p  M       cnt
60      5212    14  25 55..60  0,0,2,3,4,3,0,1
60      5212    14  24 55..61  0,0,2,3,4,3,0,1
61      5222    14  23 56..63  0,0,2,3,5,2,0,1
61      5222    14  24 56..62  0,0,2,3,5,2,0,1
88      6191    12  27 57..58  0,0,3,2,3,2,0,3
```

UNKNOWN distribution after the safe rerun:

```text
unknown by p:
14:1, 15:2, 16:3, 17:9, 18:14, 19:19, 20:24, 21:29,
22:30, 23:33, 24:31, 25:32, 26:21, 27:4

unknown by e_R:
11:9, 12:29, 13:27, 14:38, 15:31, 16:29, 17:30,
18:22, 19:17, 20:13, 21:4, 22:2, 23:1

top UNKNOWN profiles:
20 rows: 0,0,3,2,3,3,0,2
18 rows: 0,0,3,3,2,3,0,2
18 rows: 0,0,2,3,3,3,0,2
18 rows: 0,0,2,3,4,2,0,2
17 rows: 0,0,2,3,4,3,0,1
14 rows: 0,0,3,2,2,3,0,3
14 rows: 0,0,2,3,3,2,0,3
12 rows: 0,0,2,3,5,2,0,1
12 rows: 0,0,2,4,3,3,0,1
11 rows: 0,0,3,2,3,2,0,3
```

In all these hard rows the support has:

```text
c0=c1=c6=0.
```

So only labels occur:

```text
S2  = {2}
D12 = {1,2}
S3  = {3}
D13 = {1,3}
T   = {1,2,3}.
```

R-edges can only lie in:

```text
S2-D13, D12-S3, S2-S3.
```

T is isolated in R. Local domination gives:

```text
S2 vertices need >=2 neighbours in D13;
D13 vertices need >=2 neighbours in S2;
D12 vertices need >=2 neighbours in S3;
S3 vertices need >=2 neighbours in D12.
```

The optional block is S2-S3.

QUESTION:
Find the next mathematically safe strengthening for this q13/t2 five-label core. It must NOT use the rejected terminal degree equality. Prefer no extra frontier assumption beyond the H14 anti-tightness already used; if a new assumption is needed, state it exactly.

I need ONE complete lemma/proof or a smallest exact finite certificate.

Good targets:

1. a P-free capacity/cut lemma involving the two forced bipartite blocks S2-D13 and D12-S3 plus optional S2-S3;
2. a row-level inequality for M, p, e_R, or U that explains why the five closed rows closed and attacks the remaining p=21..25/e_R=14..17 middle band;
3. a tiny skeleton branch certificate for the top UNKNOWN profiles above.

Please give exact CP-SAT/C++ constraints to add.

If no safe hand cut is visible, say so and specify the smallest next computation: what to branch on, what variables to keep, and what certificate/checker would count as proof.

End by listing the weakest steps of your answer.
