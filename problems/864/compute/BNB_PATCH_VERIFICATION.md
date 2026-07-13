# Root-publication patch verification

Audit `BNB_AUDIT.md` found that `--n 2 --heuristic-restarts 0` omitted the
two-element root from the incumbent even though the exact search was complete.
The production OEIS endpoints, all at `N>=70`, were unaffected.

The repair publishes each exact-search root immediately after selecting its
two elements and before recursion. Patched source SHA-256:

```text
39E9FDB7D692EB7BA368373BAA16AF271FC99CEF935F019B0DAE82A68D6EF082
```

Strict rebuild flags:

```text
-std=c++20 -O3 -DNDEBUG -pthread -Wall -Wextra -Wpedantic
-Wconversion -Wshadow
```

Regression results with heuristics disabled:

```text
N=2:  proof-complete, F(2)=2, witness {1,2}
N=18: proof-complete, F(18)=7
```

The endpoint audit remains the optimality certificate for `N=70,80,81,85,86,100`.
The patch changes only incumbent publication, never a pruning bound or search
branch, so it cannot invalidate those completed upper bounds.
