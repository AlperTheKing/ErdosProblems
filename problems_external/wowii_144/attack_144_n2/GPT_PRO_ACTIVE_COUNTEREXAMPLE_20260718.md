# Counterexample to the active-component surplus lemma

This is a counterexample only to the former auxiliary lemma, not to WOWII/Graffiti.pc 144.
It was proposed by GPT Pro and independently recomputed by
`verify_gptpro_active_counterexample.py`.

The graph has vertices `0,...,31` and adjacency list

```text
0: 1 2 18
1: 0 3
2: 0 5 14
3: 1 4 26
4: 3 6 11 17 19 28
5: 2 27
6: 4 7 8 10
7: 6 9
8: 6 21 30
9: 7 12 25
10: 6 24
11: 4
12: 9 13
13: 12 15 16 20 31
14: 2
15: 13 23
16: 13 22
17: 4
18: 0 20
19: 4
20: 13 18
21: 8 22
22: 16 21
23: 15
24: 10
25: 9
26: 3
27: 5
28: 4 29
29: 28
30: 8
31: 13
```

Take the shortest cycle

`K=(6,8,21,22,16,13,12,9,7,6)`.

The independent calculation gives

```text
g=9, r=6, D=9, C={0,1}, e=6, e-realizers={25}
x=25, h=1, m=9, delta=5, H_x={25}, W=V(K)
q_x=0, max(0,2*delta-g)=1
mu_7(H_x)=mu_12(H_x)=1
```

Thus for either neighbor `z` of `m` on `K`,

`q_x+max(0,2*delta-g)=1>0=2*(mu_z(H_x)-h)`.