# P118: exact adversarial search for a P113 Hall falsifier

## Verdict

No P113 falsifier was found.  The full resource graph has a matching
saturating every loose triangle in every tested endpoint Sidon fold system.
This is an exact finite falsifier search, not a proof of P113.

The search is structurally faithful.  It first constructs an actual finite
integer Sidon set `B` with `max(B)=h-1`, reconstructs the canonical folds

\[
 (a,c,u,v),\qquad a+c+h=u+v,qquad a\le c<u\le v,
\]

and then reconstructs the loose triangles from their literal `(a,c)`,
`(a,u)`, and `(c,u)` incidences.  A triangle is adjacent to exactly its
three supporting folds and the three pairwise absolute differences of the
fold phases `q(a,c,u,v)=a+c`.  Hall deficiency is computed as

\[
 |T|-\nu(T,R),
\]

where `nu` is an exact maximum bipartite matching.

## 1. Search domains

### Complete endpoint census beyond width 30

Every Sidon ruler containing both endpoints `0,W` was enumerated for each
`31 <= W <= 35`.  For each ruler, every endpoint translation

\[
 B=\gamma+R,\qquad h=W+\gamma+1,qquad 0\le\gamma<W
\]

was checked.

| width | Sidon rulers | endpoint systems | systems with triangles | P113 failures |
|---:|---:|---:|---:|---:|
| 31 | 8,267 | 256,277 | 1,342 | 0 |
| 32 | 9,443 | 302,176 | 1,711 | 0 |
| 33 | 12,887 | 425,271 | 2,350 | 0 |
| 34 | 14,069 | 478,346 | 2,525 | 0 |
| 35 | 19,229 | 673,015 | 3,899 | 0 |

Thus this lane checks 2,135,085 endpoint systems, including 11,827 systems
with at least one loose triangle.  Unlike the original P113 width-30 gate,
none of these rows is imported from an archive.

### Welch--Costas endpoint systems

For primes `29,31,37,43,47,53`, four primitive roots, up to eight cyclic
shifts, and both orientations were used to form scalar Sidon rulers

\[
 B_i=2p\,i+\pi(i).
\]

The radix `2p` makes scalar difference equality force equality of the Costas
displacement, so every accepted row is exactly Sidon.  All translations at
which at least three folds exist were checked.  This produced:

```text
384 distinct oriented bases
773,438 fold-producing endpoint systems
328,327 systems with loose triangles
0 P113 failures
```

These systems have widths in the thousands and are arithmetically unrelated
to the width-30 census and the P88/P110 named rows.

### CP-SAT fold-density discovery

At widths `36,40,48,56,64`, three exact CP-SAT runs were made.  Boolean mark
variables include both endpoints.  Conjunction variables encode every
unordered selected pair, each sum has multiplicity at most one, and the
primary integer objective is the number of occupied sum pairs separated by
`h=W+1`, i.e. the fold count.  Cardinality and a deterministic seeded linear
tie-break are lower-priority terms.

CP-SAT proposes candidates only.  Every incumbent is rechecked from scratch
using integer sums, differences, folds, triangles, and the full Hall graph.
Nine runs ended `OPTIMAL` and six ended `FEASIBLE` at the 30-second cap.  The
15 runs retained 167 distinct incumbents; 53 had loose triangles and none
failed P113.

## 2. Aggregate exact result

Across the new complete and generated domains:

```text
complete width-31..35 systems       2,135,085
Costas fold-producing systems         773,438
CP-SAT incumbents                         167
systems with loose triangles           340,207
full-resource Hall failures                  0
```

The search objective is lexicographic: full Hall deficiency, peel-core
excess, difference-only deficiency, negative resource slack, triangle count,
and fold count.  All comparisons use integers.

## 3. Named hard-row controls

The same implementation gives the following controls.

| row | `C_S` | `T_F` | full match | difference match | support match |
|---|---:|---:|---:|---:|---:|
| P88, gamma 7 | 190 | 176 | 176 | 175 | 157 |
| P106 positive-RM97 falsifier | 199 | 221 | 221 | 221 | 176 |
| P110 smallest dimension falsifier | 579 | 1,104 | 1,104 | 1,104 | 541 |
| P110 strongest dimension falsifier | 1,159 | 2,696 | 2,696 | 2,696 | 1,105 |

The P88 row is the only listed control requiring a fold resource after a
maximum difference-only matching.  This exactly reproduces the earlier P113
gate and checks that the new implementation has not silently weakened the
resource graph.

## 4. Independent verification

The search uses Hopcroft--Karp.  The independent verifier reconstructs all
arithmetic objects without importing the search code and computes matching
by unit-capacity Dinic max flow.  It checked 305 distinct retained rows and
reported `PASS`.  If a falsifier is ever emitted, the search serializes the
alternating-path Hall witness `X,N(X)`, and the verifier checks the literal
neighborhood equality and `|X|>|N(X)|`.

Artifacts:

```text
compute/p118/search_p113_falsifier.py
  SHA256 D0C098BF961D3BF18BB42B81CA9302A43C653010E39FF5EB53EE956D832C6C9D
compute/p118/verify_p113_falsifier.py
  SHA256 1CE32D6D6D3F00B1DD138CCF20211751C6BF76809D3F76F5A17B1EB8E94F20A0
compute/p118/p113_falsifier_search.json
  SHA256 6AEC361DEC4FF5BB2421F3862B71E5A893AC96143CEE9BE5966F07817CEBC338
compute/p118/verification.json
  SHA256 25FA8897F7DF8028F84D0836BAB84076BB157D3BF0B5ED1AD7FE750F82366EAB
compute/p118/named_hard_rows.json
```

Reproduction:

```powershell
python -B problems/864/compute/p118/search_p113_falsifier.py `
  --min-width 31 --max-width 35 `
  --costas-primes 29,31,37,43,47,53 `
  --cpsat-widths 36,40,48,56,64 `
  --cpsat-seeds 3 --cpsat-seconds 30 --workers 16 --keep 24 `
  --output problems/864/compute/p118/p113_falsifier_search.json

python -B problems/864/compute/p118/verify_p113_falsifier.py `
  --input problems/864/compute/p118/p113_falsifier_search.json `
  --output problems/864/compute/p118/verification.json
```

## 5. Claim boundary

The zero-failure result substantially enlarges the exact gate for P113, but
does not establish the universal Hall inequality.  CP-SAT optimality applies
only to the finite fold-count objectives at the five stated widths, and six
runs were time-limited.  The complete statement

\[
 |X|\le |\operatorname{suppFold}(X)|
       +|\operatorname{phaseDiff}(X)|
\]

for every family of loose triangles in every endpoint Sidon fold system
remains a proof obligation.
