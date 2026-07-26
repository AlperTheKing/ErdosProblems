# Erdos 686 — opening note (target selected 2026-07-26)

## Why this target

Selected by a fresh easy-first scan after #23 was stopped by user directive. The scan ranked all 622
OPEN Erdos problems, then re-ranked the 290 with a local Lean statement by the LOGICAL FORM of that
statement rather than by tags — penalising `atTop`, `Tendsto`, `~[`, `IsBigO`, `≪`, `log`,
`Set.Infinite` and `∃ c > 0`, since asymptotic shape is what the previous campaign died inside.

That filter rejected the tag-ranked leaders: 562 is `log^[r-1] R_r(n) ~[atTop] n`; 566/567 are `≪ m`;
595 is infinite/set-theoretic; 701 is Chvatal's conjecture (open since 1974); 1052 and 1108 are
finiteness statements needing effective bounds.

**686 survives because one of its three parts is a single concrete EXISTENCE question**, and an
existence question is closed outright by exhibiting a witness — a genuine finite closure.

## Statement

`N = prod_{1<=i<=k}(m+i) / prod_{1<=i<=k}(n+i)`, with `k >= 2` and `m >= n+k`.
Three parts, all `@[category research open]` in `formal-conjectures/.../686.lean`:
every `N >= 2`; every square `N`; and the single case **`N = 4`**.

## First result (mine, exact integer arithmetic)

`tools/claude_erdos686_search.py`, bounds `k <= 12`, `n <= 4000`:

**Every `N` in `2..40` has an explicit representation EXCEPT `4` and `25`.**

Each hit is a complete certificate for that `N`. Samples:

```
        N = 2   k=2  n=13  m=19     2 * 210 = 420
        N = 3   k=2  n= 4  m= 8     3 * 30  = 90
        N = 9   k=3  n=11  m=25     9 * 2184 = 19656
        N = 16  k=3  n= 4  m=13    16 * 210 = 3360
        N = 36  k=2  n= 0  m= 7    36 * 2   = 72
```

Note `9`, `16` and `36` ARE representable, so the obstruction is not "squares" — it is specific to
`4` and `25`.

## The k = 2 case for N = 4, settled by hand

`4(n+1)(n+2) = (m+1)(m+2)` with `a = n+1`, `b = m+1` gives `b(b+1) = 4a(a+1)`. Multiplying by 4 and
setting `X = 2b+1`, `Y = 2a+1` gives `X^2 - 4Y^2 = -3`, i.e. `(X-2Y)(X+2Y) = -3`. With `X, Y > 0`
this forces `X - 2Y = -1` and `X + 2Y = 3`, so `X = Y = 1` and `a = b = 0`. **No admissible
solution at k = 2.** So any representation of 4 needs `k >= 3`.

## Discipline carried over from #23

* exact integer arithmetic on every acceptance path; a hit is a certificate, a miss is only a search
  bound and NEVER a proof of impossibility;
* no asymptotic reformulation — if the work turns into a chain of reductions to unproved statements,
  stop, as #23 was stopped;
* a negative resolution would need a genuine impossibility argument (the `k = 2` computation above is
  the model), not an exhausted search.
